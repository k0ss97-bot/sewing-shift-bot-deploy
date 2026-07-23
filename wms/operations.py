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
        raise ValueError(f"no location in zone '{zone_code}' — create one first")
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
) -> OperationResult:
    """Accept finished/semi-finished goods into the RECEIVE zone.

    Creates a ``production_receipt`` movement and increments stock.  Idempotent
    on ``request_key``.
    """
    if quantity <= 0:
        return OperationResult(False, reason="quantity must be positive")
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
        return OperationResult(False, reason="quantity must be positive")
    request_key = request_key or _new_request_key("putaway")
    conn = get_pg_connection()
    try:
        target = repo.get_location_by_code(conn, to_location_code)
        if target is None:
            conn.rollback()
            return OperationResult(False, reason=f"unknown location '{to_location_code}'")
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
                     AND item_state='SELLABLE' AND location_id=%s
                   FOR UPDATE""",
                (*product_key.to_dict().values(), receive_loc.id),
            )
            row = cur.fetchone()
        if row is None or int(row[1]) < quantity:
            conn.rollback()
            return OperationResult(False, reason="insufficient stock in RECEIVE zone")
        # Move: decrement source, increment target.
        repo.upsert_stock(conn, product_key, delta=-quantity, location_id=receive_loc.id)
        repo.upsert_stock(conn, product_key, delta=quantity, location_id=target.id)
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
    employee_id: int | None = None,
    request_key: str | None = None,
    reason: str | None = None,
    tsd_device_id: str | None = None,
) -> OperationResult:
    """Move goods between two arbitrary locations."""
    if quantity <= 0:
        return OperationResult(False, reason="quantity must be positive")
    if from_location_code == to_location_code:
        return OperationResult(False, reason="source and destination are the same")
    request_key = request_key or _new_request_key("transfer")
    conn = get_pg_connection()
    try:
        src = repo.get_location_by_code(conn, from_location_code)
        dst = repo.get_location_by_code(conn, to_location_code)
        if src is None:
            return OperationResult(False, reason=f"unknown source location '{from_location_code}'")
        if dst is None:
            return OperationResult(False, reason=f"unknown destination location '{to_location_code}'")
        if repo.movement_exists(conn, request_key):
            conn.rollback()
            return OperationResult(True, skipped_duplicate=True)

        with conn.cursor() as cur:
            cur.execute(
                """SELECT id, quantity FROM warehouse_stock
                   WHERE item_type=%s AND product_name=%s AND product_size=%s
                     AND product_color=%s AND stage_name=%s AND ready_for_position=%s
                     AND item_state='SELLABLE' AND location_id=%s
                   FOR UPDATE""",
                (*product_key.to_dict().values(), src.id),
            )
            row = cur.fetchone()
        if row is None or int(row[1]) < quantity:
            conn.rollback()
            return OperationResult(False, reason="insufficient stock at source location")
        repo.upsert_stock(conn, product_key, delta=-quantity, location_id=src.id)
        repo.upsert_stock(conn, product_key, delta=quantity, location_id=dst.id)
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
# scrap (Списание: SELLABLE → DAMAGED/SCRAPPED)
# ──────────────────────────────────────────────────────────────────────


def scrap(
    product_key: ProductKey,
    quantity: int,
    *,
    reason: str,
    target_state: str = "SCRAPPED",
    employee_id: int | None = None,
    request_key: str | None = None,
    tsd_device_id: str | None = None,
) -> OperationResult:
    """Remove goods from sellable stock and mark them DAMAGED/SCRAPPED."""
    if quantity <= 0:
        return OperationResult(False, reason="quantity must be positive")
    if target_state not in ("DAMAGED", "SCRAPPED", "QUARANTINE"):
        return OperationResult(False, reason=f"invalid target_state '{target_state}'")
    request_key = request_key or _new_request_key("scrap")
    conn = get_pg_connection()
    try:
        if repo.movement_exists(conn, request_key):
            conn.rollback()
            return OperationResult(True, skipped_duplicate=True)
        with conn.cursor() as cur:
            cur.execute(
                """SELECT id, quantity FROM warehouse_stock
                   WHERE item_type=%s AND product_name=%s AND product_size=%s
                     AND product_color=%s AND stage_name=%s AND ready_for_position=%s
                     AND item_state='SELLABLE'
                   FOR UPDATE""",
                product_key.to_dict().values(),
            )
            row = cur.fetchone()
        if row is None or int(row[1]) < quantity:
            conn.rollback()
            return OperationResult(False, reason="insufficient sellable stock")
        repo.upsert_stock(conn, product_key, delta=-quantity, item_state="SELLABLE")
        repo.upsert_stock(conn, product_key, delta=quantity, item_state=target_state)
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
            return OperationResult(False, reason=f"unknown location '{location_code}'")
        if repo.movement_exists(conn, request_key):
            conn.rollback()
            return OperationResult(True, skipped_duplicate=True)

        # Create the inventory-count header.
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO wms_inventory_counts (location_id, counted_by_employee_id, counted_at)
                   VALUES (%s, %s, now()) RETURNING id""",
                (loc.id, employee_id),
            )
            count_id = int(cur.fetchone()[0])

        adjustments = 0
        for entry in counted:
            pk = ProductKey.from_dict(entry["product_key"])
            counted_qty = int(entry["counted_quantity"])
            stock = repo.find_stock(conn, pk)
            expected = stock.quantity if stock and stock.location_id == loc.id else 0
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
                    request_key=f"{request_key}:{pk.product_name}:{pk.product_size}:{pk.product_color}",
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
