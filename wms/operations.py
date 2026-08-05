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
from .models import OperationResult, ProductKey, StockReceiptResult
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
    """Accept a material directly into the non-addressable material store.

    Address cells are reserved for finished goods.  Materials still use this
    WMS movement as an idempotency anchor, but their physical balance belongs
    to the material warehouse (mirrored to legacy ``fabric_stock`` by the web
    handler), not to the finished-goods receiving zone.
    """
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
        if repo.movement_exists(conn, request_key):
            conn.rollback()
            return OperationResult(True, skipped_duplicate=True, reason="duplicate request_key")
        repo.upsert_stock(
            conn, product_key, delta=quantity, item_state="SELLABLE",
            location_id=None, unit=unit,
        )
        movement_id = repo.insert_movement(
            conn,
            request_key=request_key,
            movement_type="material_receipt",
            product_key=product_key,
            quantity=quantity,
            to_location_id=None,
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
    """Put finished goods into an address cell.

    Placement is allowed only within the available balance of the same product
    in RECEIVE. New stock must first be posted through production receipt or a
    manual stock-receipt document.
    """
    if quantity <= 0:
        return OperationResult(False, reason="Количество должно быть больше нуля.")
    if product_key.item_type != "finished":
        return OperationResult(
            False,
            reason="Адресное размещение доступно только для готовой продукции.",
        )
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

        # RECEIVE is the only valid source for address placement. Lock the row
        # so two scanners cannot place the same available quantity twice.
        with conn.cursor() as cur:
            cur.execute(
                """SELECT id, quantity, reserved_quantity FROM warehouse_stock
                   WHERE item_type=%s AND product_name=%s AND product_size=%s
                     AND product_color=%s AND stage_name=%s AND ready_for_position=%s
                     AND item_state='SELLABLE' AND location_id=%s AND unit=%s
                   FOR UPDATE""",
                (*product_key.to_dict().values(), receive_loc.id, unit),
            )
            row = cur.fetchone()
        received_quantity = int(row[1]) if row is not None else 0
        reserved_quantity = int(row[2]) if row is not None else 0
        available_quantity = max(0, received_quantity - reserved_quantity)
        if available_quantity < quantity:
            conn.rollback()
            return OperationResult(
                False,
                reason=(
                    f"В зоне приёмки доступно {available_quantity} шт. "
                    "Сначала выполните оприходование или приёмку от производства."
                ),
            )
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
# multi-line stock receipt (Оприходование → RECEIVE)
# ──────────────────────────────────────────────────────────────────────


def post_stock_receipt(
    lines: list[tuple[str, ProductKey, int]],
    *,
    employee_id: int,
    request_key: str,
    comment: str | None = None,
    tsd_device_id: str | None = None,
) -> StockReceiptResult:
    """Atomically post a multi-line manual receipt into RECEIVE."""

    request_key = str(request_key or "").strip()
    if not request_key or len(request_key) > 200:
        return StockReceiptResult(False, reason="Неверный ключ документа оприходования.")
    if not lines:
        return StockReceiptResult(False, reason="Добавьте хотя бы один товар.")
    if len(lines) > 500:
        return StockReceiptResult(False, reason="В одном документе можно оприходовать не более 500 позиций.")

    merged: dict[ProductKey, dict[str, object]] = {}
    for barcode, product_key, quantity in lines:
        if product_key.item_type != "finished":
            return StockReceiptResult(False, reason="Оприходование в зону приёмки доступно только для готовой продукции.")
        if quantity <= 0 or quantity > 1_000_000:
            return StockReceiptResult(False, reason="Количество каждой позиции должно быть от 1 до 1 000 000.")
        entry = merged.setdefault(product_key, {"barcode": barcode, "quantity": 0})
        entry["quantity"] = int(entry["quantity"]) + quantity
        if int(entry["quantity"]) > 1_000_000:
            return StockReceiptResult(False, reason="Суммарное количество одного товара не должно превышать 1 000 000.")

    conn = get_pg_connection()
    try:
        existing = repo.get_stock_receipt_by_request_key(conn, request_key)
        if existing:
            conn.rollback()
            return StockReceiptResult(
                True,
                receipt_id=existing["id"],
                number=existing["number"],
                lines_count=existing["lines_count"],
                total_quantity=existing["total_quantity"],
                skipped_duplicate=True,
            )
        receive_loc = _zone_location(conn, "RECEIVE")
        document = repo.create_stock_receipt(
            conn,
            request_key=request_key,
            actor_employee_id=employee_id,
            comment=str(comment or "").strip()[:500] or None,
        )
        if document is None:
            existing = repo.get_stock_receipt_by_request_key(conn, request_key)
            conn.rollback()
            return StockReceiptResult(
                True,
                receipt_id=existing["id"] if existing else None,
                number=existing["number"] if existing else None,
                lines_count=existing["lines_count"] if existing else 0,
                total_quantity=existing["total_quantity"] if existing else 0,
                skipped_duplicate=True,
            )

        total_quantity = 0
        for line_no, (product_key, entry) in enumerate(merged.items(), start=1):
            quantity = int(entry["quantity"])
            total_quantity += quantity
            repo.upsert_stock(
                conn,
                product_key,
                delta=quantity,
                item_state="SELLABLE",
                location_id=receive_loc.id,
                unit="шт",
            )
            movement_id = repo.insert_movement(
                conn,
                request_key=f"{request_key}:line:{line_no}",
                movement_type="stock_receipt",
                product_key=product_key,
                quantity=quantity,
                to_location_id=receive_loc.id,
                to_state="SELLABLE",
                source_type="stock_receipt",
                source_id=document["id"],
                reason="Оприходование готовой продукции",
                actor_employee_id=employee_id,
                tsd_device_id=tsd_device_id,
            )
            if movement_id is None:
                raise RuntimeError("Не удалось записать строку движения.")
            repo.insert_stock_receipt_line(
                conn,
                receipt_id=document["id"],
                line_no=line_no,
                barcode=str(entry["barcode"]),
                product_key=product_key,
                quantity=quantity,
                movement_id=movement_id,
            )
        posted = repo.post_stock_receipt(
            conn,
            receipt_id=document["id"],
            lines_count=len(merged),
            total_quantity=total_quantity,
        )
        conn.commit()
        return StockReceiptResult(
            True,
            receipt_id=posted["id"],
            number=posted["number"],
            lines_count=posted["lines_count"],
            total_quantity=posted["total_quantity"],
        )
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


def pick_reserved_for_shipment(
    product_key: ProductKey,
    quantity: int,
    *,
    from_location_code: str,
    shipment_id: int,
    employee_id: int | None = None,
    request_key: str | None = None,
    reason: str | None = None,
    tsd_device_id: str | None = None,
) -> OperationResult:
    """Pick units reserved for one marketplace shipment.

    This is deliberately distinct from :func:`pick`: an ordinary manual pick
    cannot consume a reservation, whereas this operation must decrement both
    physical and reserved balance atomically.  The movement's source makes the
    audit trail attributable to the marketplace document.
    """
    if quantity <= 0:
        return OperationResult(False, reason="Количество должно быть больше нуля.")
    request_key = request_key or _new_request_key("marketplace-pick")
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
            return OperationResult(True, skipped_duplicate=True, reason="duplicate request_key")
        stock = repo.find_stock(
            conn, product_key, item_state="SELLABLE", unit="шт",
            location_id=source.id, for_update=True,
        )
        reserved = 0 if stock is None else int(stock.reserved_quantity)
        if stock is None or reserved < quantity:
            conn.rollback()
            return OperationResult(
                False,
                reason=f"В ячейке для этой отгрузки зарезервировано только {reserved} шт.",
            )
        with conn.cursor() as cur:
            cur.execute(
                """UPDATE warehouse_stock
                      SET quantity=quantity-%s,reserved_quantity=reserved_quantity-%s,updated_at=now()
                    WHERE id=%s AND quantity >= %s AND reserved_quantity >= %s""",
                (quantity, quantity, stock.id, quantity, quantity),
            )
            if cur.rowcount != 1:
                raise ValueError("Не удалось списать зарезервированный товар из ячейки.")
        movement_id = repo.insert_movement(
            conn,
            request_key=request_key,
            movement_type="pick",
            product_key=product_key,
            quantity=quantity,
            from_location_id=source.id,
            from_state="SELLABLE",
            to_state="PICKED",
            source_type="marketplace_shipment",
            source_id=shipment_id,
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
                "SELECT id, quantity, reserved_quantity FROM warehouse_stock WHERE id=%s FOR UPDATE",
                (stock.id,),
            )
            row = cur.fetchone()
        available_quantity = 0 if row is None else max(0, int(row[1]) - int(row[2]))
        if row is None or available_quantity < quantity:
            conn.rollback()
            return OperationResult(
                False,
                reason=f"Недостаточно доступного товара: доступно только {available_quantity} шт., резерв списывать нельзя.",
            )
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
            from_location_id=stock.location_id,
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
    reason: str | None = None,
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
            reserved = stock.reserved_quantity if stock else 0
            if counted_qty < reserved:
                conn.rollback()
                return OperationResult(
                    False,
                    reason=(
                        f"Фактический остаток не может быть меньше резерва: "
                        f"зарезервировано {reserved} шт."
                    ),
                )
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
                    reason=(
                        f"инвентаризация{f' ({reason.strip()})' if reason and reason.strip() else ''}: "
                        f"ожидалось {expected}, фактически {counted_qty}"
                    ),
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
