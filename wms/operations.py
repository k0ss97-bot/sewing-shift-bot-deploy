"""Warehouse operations: receipt, putaway, transfer, pick, inventory, scrap.

Each operation is a single Postgres transaction that:
1. inserts an immutable movement with a UNIQUE ``request_key`` (idempotency);
2. updates ``warehouse_stock`` via atomic upsert / optimistic guards;
3. commits atomically, or rolls back on any error.

This mirrors the legacy ``consume_warehouse_stock`` pattern:
``BEGIN IMMEDIATE`` + ``WHERE quantity >= ?`` guard + ``rowcount`` check.
Postgres equivalents use ``SELECT … FOR UPDATE`` + explicit quantity checks.

Repeating the same ``request_key`` is a no-op (returns ``skipped_duplicate``).
"""

from __future__ import annotations

import uuid
from typing import Any

from .connection import get_pg_connection
from .models import OperationResult, ProductKey
from . import repository as repo


# ──────────────────────────────────────────────────────────────────────
# helpers
# ──────────────────────────────────────────────────────────────────────


def _new_request_key(prefix: str) -> str:
    return f"wms:{prefix}:{uuid.uuid4().hex[:24]}"


def _zone_location(conn, zone_code: str):
    """Find the single location in a zone, or raise."""
    locs = repo.list_locations(conn, zone_code=zone_code)
    if not locs:
        raise ValueError(f"В зоне {zone_code} нет активной ячейки.")
    if zone_code == "RECEIVE":
        return next((loc for loc in locs if loc.code == "RECEIVE-01"), locs[0])
    return locs[0]


# ──────────────────────────────────────────────────────────────────────
# receipt from production (Приёмка от производства)
# ──────────────────────────────────────────────────────────────────────


def receive_from_production(
    product_key: ProductKey,
    quantity: int,
    *,
    employee_id: int | None = None,
    request_key: str | None = None,
    reason: str | None = None,
    tsd_device_id: str | None = None,
    source_id: int | None = None,
) -> OperationResult:
    """Accept finished/semi-finished goods into the RECEIVE zone.

    Creates a ``production_receipt`` movement and increments stock.  Idempotent
    on ``request_key``.
    """
    if quantity <= 0:
        return OperationResult(False, reason="Количество должно быть больше нуля.")
    request_key = request_key or _new_request_key("receipt")
    conn = get_pg_connection()
    try:
        receive_loc = _zone_location(conn, "RECEIVE")
        existing = repo.movement_exists(conn, request_key)
        if existing:
            conn.rollback()
            return OperationResult(True, skipped_duplicate=True, reason="duplicate request_key")

        repo.upsert_stock(
            conn, product_key, delta=quantity,
            item_state="SELLABLE", location_id=receive_loc.id,
        )
        movement_id = repo.insert_movement(
            conn,
            request_key=request_key,
            movement_type="production_receipt",
            product_key=product_key,
            quantity=quantity,
            to_location_id=receive_loc.id,
            to_state="SELLABLE",
            source_type="production",
            source_id=source_id,
            reason=reason,
            actor_employee_id=employee_id,
            tsd_device_id=tsd_device_id,
        )
        conn.commit()
        return OperationResult(True, movement_id=movement_id)
    except Exception:
        conn.rollback()
        raise


def receive_material(
    product_key: ProductKey,
    quantity: int,
    *,
    unit: str = "рул",
    employee_id: int | None = None,
    request_key: str | None = None,
    reason: str | None = None,
    tsd_device_id: str | None = None,
) -> OperationResult:
    """Accept a manually entered material receipt into the RECEIVE zone."""
    if product_key.item_type != "material":
        return OperationResult(False, reason="Для приёмки материалов нужен item_type=material.")
    if quantity <= 0:
        return OperationResult(False, reason="Количество должно быть больше нуля.")
    unit = str(unit or "рул").strip()
    if unit not in {"рул", "м", "шт"}:
        return OperationResult(False, reason="Единица материала: рул, м или шт.")
    request_key = request_key or _new_request_key("material-receipt")
    conn = get_pg_connection()
    try:
        receive_loc = _zone_location(conn, "RECEIVE")
        if repo.movement_exists(conn, request_key):
            conn.rollback()
            return OperationResult(True, skipped_duplicate=True, reason="duplicate request_key")
        repo.upsert_stock(
            conn, product_key, delta=quantity, item_state="SELLABLE",
            location_id=receive_loc.id, unit=unit,
        )
        movement_id = repo.insert_movement(
            conn,
            request_key=request_key,
            movement_type="material_receipt",
            product_key=product_key,
            quantity=quantity,
            to_location_id=receive_loc.id,
            to_state="SELLABLE",
            source_type="manual",
            reason=reason,
            actor_employee_id=employee_id,
            tsd_device_id=tsd_device_id,
        )
        conn.commit()
        return OperationResult(True, movement_id=movement_id)
    except Exception:
        conn.rollback()
        raise


# ──────────────────────────────────────────────────────────────────────
# putaway (Размещение: Приёмка → ячейка хранения)
# ──────────────────────────────────────────────────────────────────────


def putaway(
    product_key: ProductKey,
    quantity: int,
    *,
    to_location_code: str,
    unit: str = "шт",
    employee_id: int | None = None,
    request_key: str | None = None,
    reason: str | None = None,
    tsd_device_id: str | None = None,
) -> OperationResult:
    """Move goods from the RECEIVE zone to a storage/pick location.

    Decrements RECEIVE stock, increments the target location.  Rejects if
    RECEIVE stock is insufficient.
    """
    if quantity <= 0:
        return OperationResult(False, reason="Количество должно быть больше нуля.")
    request_key = request_key or _new_request_key("putaway")
    conn = get_pg_connection()
    try:
        target = repo.get_location_by_code(conn, to_location_code)
        if target is None:
            conn.rollback()
            return OperationResult(False, reason=f"Ячейка {to_location_code} не найдена.")
        if target.status != "active":
            conn.rollback()
            return OperationResult(False, reason=f"Ячейка {to_location_code} недоступна.")
        receive_loc = _zone_location(conn, "RECEIVE")

        if repo.movement_exists(conn, request_key):
            conn.rollback()
            return OperationResult(True, skipped_duplicate=True)

        # Check + decrement RECEIVE stock under row lock.
        with conn.cursor() as cur:
            cur.execute(
                """SELECT id, quantity FROM warehouse_stock
                   WHERE item_type=%s AND product_name=%s AND product_size=%s
                     AND product_color=%s AND stage_name=%s AND ready_for_position=%s
                     AND item_state='SELLABLE' AND location_id=%s AND unit=%s
                   FOR UPDATE""",
                (*product_key.to_dict().values(), receive_loc.id, unit),
            )
            row = cur.fetchone()
        if row is None or int(row[1]) < quantity:
            conn.rollback()
            return OperationResult(False, reason="Недостаточно товара в зоне приёмки.")
        # Move: decrement source, increment target.
        repo.upsert_stock(conn, product_key, delta=-quantity, location_id=receive_loc.id, unit=unit)
        repo.upsert_stock(conn, product_key, delta=quantity, location_id=target.id, unit=unit)
        movement_id = repo.insert_movement(
            conn,
            request_key=request_key,
            movement_type="putaway",
            product_key=product_key,
            quantity=quantity,
            from_location_id=receive_loc.id,
            to_location_id=target.id,
            reason=reason,
            actor_employee_id=employee_id,
            tsd_device_id=tsd_device_id,
        )
        conn.commit()
        return OperationResult(True, movement_id=movement_id)
    except Exception:
        conn.rollback()
        raise


# ──────────────────────────────────────────────────────────────────────
# transfer (Перемещение между ячейками)
# ──────────────────────────────────────────────────────────────────────


def transfer(
    product_key: ProductKey,
    quantity: int,
    *,
    from_location_code: str,
    to_location_code: str,
    unit: str = "шт",
    employee_id: int | None = None,
    request_key: str | None = None,
    reason: str | None = None,
    tsd_device_id: str | None = None,
) -> OperationResult:
    """Move goods between two arbitrary locations."""
    if quantity <= 0:
        return OperationResult(False, reason="Количество должно быть больше нуля.")
    if from_location_code == to_location_code:
        return OperationResult(False, reason="Исходная и целевая ячейки совпадают.")
    request_key = request_key or _new_request_key("transfer")
    conn = get_pg_connection()
    try:
        src = repo.get_location_by_code(conn, from_location_code)
        dst = repo.get_location_by_code(conn, to_location_code)
        if src is None:
            conn.rollback()
            return OperationResult(False, reason=f"Исходная ячейка {from_location_code} не найдена.")
        if dst is None:
            conn.rollback()
            return OperationResult(False, reason=f"Целевая ячейка {to_location_code} не найдена.")
        if src.status != "active" or dst.status != "active":
            conn.rollback()
            return OperationResult(False, reason="Исходная или целевая ячейка недоступна.")
        if repo.movement_exists(conn, request_key):
            conn.rollback()
            return OperationResult(True, skipped_duplicate=True)

        with conn.cursor() as cur:
            cur.execute(
                """SELECT id, quantity FROM warehouse_stock
                   WHERE item_type=%s AND product_name=%s AND product_size=%s
                     AND product_color=%s AND stage_name=%s AND ready_for_position=%s
                     AND item_state='SELLABLE' AND location_id=%s AND unit=%s
                   FOR UPDATE""",
                (*product_key.to_dict().values(), src.id, unit),
            )
            row = cur.fetchone()
        if row is None or int(row[1]) < quantity:
            conn.rollback()
            return OperationResult(False, reason="Недостаточно товара в исходной ячейке.")
        repo.upsert_stock(conn, product_key, delta=-quantity, location_id=src.id, unit=unit)
        repo.upsert_stock(conn, product_key, delta=quantity, location_id=dst.id, unit=unit)
        movement_id = repo.insert_movement(
            conn,
            request_key=request_key,
            movement_type="transfer",
            product_key=product_key,
            quantity=quantity,
            from_location_id=src.id,
            to_location_id=dst.id,
            reason=reason,
            actor_employee_id=employee_id,
            tsd_device_id=tsd_device_id,
        )
        conn.commit()
        return OperationResult(True, movement_id=movement_id)
    except Exception:
        conn.rollback()
        raise


# ──────────────────────────────────────────────────────────────────────
# pick (Подбор/выдача из ячейки)
# ──────────────────────────────────────────────────────────────────────


def pick(
    product_key: ProductKey,
    quantity: int,
    *,
    from_location_code: str,
    unit: str = "шт",
    employee_id: int | None = None,
    request_key: str | None = None,
    reason: str | None = None,
    tsd_device_id: str | None = None,
) -> OperationResult:
    """Take sellable goods from an addressable location.

    The quantity leaves addressable stock and is recorded as a ``pick``
    movement. Reserved units are protected: an unbound manual pick may only
    consume the unreserved balance.
    """
    if quantity <= 0:
        return OperationResult(False, reason="Количество должно быть больше нуля.")
    request_key = request_key or _new_request_key("pick")
    conn = get_pg_connection()
    try:
        source = repo.get_location_by_code(conn, from_location_code)
        if source is None:
            conn.rollback()
            return OperationResult(False, reason=f"Ячейка {from_location_code} не найдена.")
        if source.status != "active":
            conn.rollback()
            return OperationResult(False, reason=f"Ячейка {from_location_code} недоступна.")
        if repo.movement_exists(conn, request_key):
            conn.rollback()
            return OperationResult(True, skipped_duplicate=True)

        stock = repo.find_stock(
            conn,
            product_key,
            item_state="SELLABLE",
            unit=unit,
            location_id=source.id,
            for_update=True,
        )
        available = 0 if stock is None else stock.quantity - stock.reserved_quantity
        if stock is None or available < quantity:
            conn.rollback()
            return OperationResult(
                False,
                reason=f"В ячейке доступно только {max(available, 0)} шт.",
            )

        stock_update = {
            "delta": -quantity,
            "item_state": "SELLABLE",
            "location_id": source.id,
        }
        if unit != "шт":
            stock_update["unit"] = unit
        repo.upsert_stock(conn, product_key, **stock_update)
        movement_id = repo.insert_movement(
            conn,
            request_key=request_key,
            movement_type="pick",
            product_key=product_key,
            quantity=quantity,
            from_location_id=source.id,
            from_state="SELLABLE",
            to_state="PICKED",
            source_type="manual",
            reason=reason,
            actor_employee_id=employee_id,
            tsd_device_id=tsd_device_id,
        )
        conn.commit()
        return OperationResult(True, movement_id=movement_id)
    except Exception:
        conn.rollback()
        raise


# ──────────────────────────────────────────────────────────────────────
# scrap (Списание: SELLABLE → DAMAGED/SCRAPPED)
# ──────────────────────────────────────────────────────────────────────


def scrap(
    product_key: ProductKey,
    quantity: int,
    *,
    reason: str,
    target_state: str = "SCRAPPED",
    from_location_code: str | None = None,
    employee_id: int | None = None,
    request_key: str | None = None,
    tsd_device_id: str | None = None,
) -> OperationResult:
    """Remove goods from sellable stock and mark them DAMAGED/SCRAPPED."""
    if quantity <= 0:
        return OperationResult(False, reason="Количество должно быть больше нуля.")
    if target_state not in ("DAMAGED", "SCRAPPED", "QUARANTINE"):
        return OperationResult(False, reason="Выбрано недопустимое состояние списания.")
    request_key = request_key or _new_request_key("scrap")
    conn = get_pg_connection()
    try:
        if repo.movement_exists(conn, request_key):
            conn.rollback()
            return OperationResult(True, skipped_duplicate=True)
        location_id = None
        if from_location_code:
            location = repo.get_location_by_code(conn, from_location_code)
            if location is None:
                conn.rollback()
                return OperationResult(
                    False, reason=f"Ячейка {from_location_code} не найдена."
                )
            location_id = location.id
        stock = repo.find_stock(
            conn,
            product_key,
            item_state="SELLABLE",
            **({"location_id": location_id} if from_location_code else {}),
        )
        if stock is None:
            conn.rollback()
            return OperationResult(False, reason="Недостаточно доступного товара.")
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, quantity FROM warehouse_stock WHERE id=%s FOR UPDATE",
                (stock.id,),
            )
            row = cur.fetchone()
        if row is None or int(row[1]) < quantity:
            conn.rollback()
            return OperationResult(False, reason="Недостаточно доступного товара.")
        repo.upsert_stock(
            conn,
            product_key,
            delta=-quantity,
            item_state="SELLABLE",
            location_id=stock.location_id,
        )
        repo.upsert_stock(
            conn,
            product_key,
            delta=quantity,
            item_state=target_state,
            location_id=stock.location_id,
        )
        movement_id = repo.insert_movement(
            conn,
            request_key=request_key,
            movement_type="scrap",
            product_key=product_key,
            quantity=quantity,
            from_state="SELLABLE",
            to_state=target_state,
            reason=reason,
            actor_employee_id=employee_id,
            tsd_device_id=tsd_device_id,
        )
        conn.commit()
        return OperationResult(True, movement_id=movement_id)
    except Exception:
        conn.rollback()
        raise


# ──────────────────────────────────────────────────────────────────────
# inventory count (Инвентаризация — слепой пересчёт)
# ──────────────────────────────────────────────────────────────────────


def inventory_count(
    location_code: str,
    counted: list[dict[str, Any]],
    *,
    employee_id: int | None = None,
    request_key: str | None = None,
) -> OperationResult:
    """Blind count: compare counted quantities to system stock, adjust diffs.

    ``counted`` is a list of ``{product_key: {...}, counted_quantity: int}``.
    Adjustments are recorded as ``count`` movements with a reason.
    """
    request_key = request_key or _new_request_key("count")
    conn = get_pg_connection()
    try:
        loc = repo.get_location_by_code(conn, location_code)
        if loc is None:
            conn.rollback()
            return OperationResult(False, reason=f"Ячейка {location_code} не найдена.")

        # Create the inventory-count header.
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO wms_inventory_counts
                   (request_key, location_id, counted_by_employee_id, counted_at)
                   VALUES (%s, %s, %s, now())
                   ON CONFLICT (request_key) DO NOTHING
                   RETURNING id""",
                (request_key, loc.id, employee_id),
            )
            count_row = cur.fetchone()
        if count_row is None:
            conn.rollback()
            return OperationResult(True, skipped_duplicate=True)
        count_id = int(count_row[0])

        adjustments = 0
        seen_product_keys: set[ProductKey] = set()
        for entry_index, entry in enumerate(counted):
            pk = ProductKey.from_dict(entry["product_key"])
            if pk in seen_product_keys:
                raise ValueError("duplicate product in inventory count")
            seen_product_keys.add(pk)
            counted_qty = int(entry["counted_quantity"])
            if counted_qty < 0:
                raise ValueError("counted_quantity must be non-negative")
            stock = repo.find_stock(conn, pk, location_id=loc.id, for_update=True)
            expected = stock.quantity if stock else 0
            diff = counted_qty - expected
            # Record the line (blind: expected is captured but not shown to the counter).
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO wms_inventory_count_lines
                       (count_id, product_key, expected_quantity, counted_quantity,
                        discrepancy, counted_by_employee_id, counted_at)
                       VALUES (%s, %s, %s, %s, %s, %s, now())
                       ON CONFLICT (count_id, product_key) DO NOTHING""",
                    (
                        count_id,
                        __import__("json").dumps(pk.to_dict()),
                        expected,
                        counted_qty,
                        diff,
                        employee_id,
                    ),
                )
            if diff != 0:
                # Apply the adjustment via a per-line movement.
                repo.upsert_stock(
                    conn, pk, delta=diff, item_state="SELLABLE", location_id=loc.id,
                )
                repo.insert_movement(
                    conn,
                    request_key=f"{request_key}:line:{entry_index}",
                    movement_type="count",
                    product_key=pk,
                    quantity=diff,
                    to_location_id=loc.id,
                    source_type="inventory_count",
                    source_id=count_id,
                    reason=f"инвентаризация: ожидалось {expected}, фактически {counted_qty}",
                    actor_employee_id=employee_id,
                )
                adjustments += 1

        with conn.cursor() as cur:
            cur.execute(
                """UPDATE wms_inventory_counts
                   SET status='counted', discrepancy_count=%s WHERE id=%s""",
                (adjustments, count_id),
            )
        conn.commit()
        return OperationResult(True, reason=f"count_id={count_id}, adjustments={adjustments}")
    except Exception:
        conn.rollback()
        raise
