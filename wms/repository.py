"""Postgres CRUD for WMS entities.

Thin data-access functions used by :mod:`wms.operations`. Each function takes
an open connection (the caller owns the transaction) so multi-step operations
can compose inside a single ``BEGIN``/``COMMIT``.

Product identity reuses the legacy ``ProductKey`` 6-field tuple so WMS stock
maps 1:1 to SQLite ``warehouse_stock`` rows.
"""

from __future__ import annotations

import json
from typing import Any

from .connection import get_pg_connection
from .models import Location, Movement, ProductKey, WarehouseStock, Zone


# ──────────────────────────────────────────────────────────────────────
# zones / locations
# ──────────────────────────────────────────────────────────────────────


def get_zone_by_code(conn, code: str) -> Zone | None:
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM wms_zones WHERE code = %s", (code,))
        row = cur.fetchone()
    return _zone_from_row(row) if row else None


def get_or_create_zone(conn, *, code: str, name_ru: str, zone_type: str) -> Zone:
    zone = get_zone_by_code(conn, code)
    if zone is not None:
        return zone
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO wms_zones (code, name_ru, zone_type) VALUES (%s, %s, %s) "
            "RETURNING *",
            (code, name_ru, zone_type),
        )
        row = cur.fetchone()
    return _zone_from_row(row)


def get_location_by_code(conn, code: str) -> Location | None:
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM wms_locations WHERE code = %s", (code,))
        row = cur.fetchone()
    return _location_from_row(row) if row else None


def get_location_by_barcode(conn, barcode: str) -> Location | None:
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM wms_locations WHERE barcode = %s", (barcode,))
        row = cur.fetchone()
    return _location_from_row(row) if row else None


def create_location(
    conn,
    *,
    zone_id: int,
    code: str,
    barcode: str | None = None,
    name_ru: str | None = None,
    pick_priority: int = 0,
    route_order: int = 0,
) -> Location:
    bc = barcode or f"LOC:{code}"
    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO wms_locations
               (zone_id, code, barcode, name_ru, pick_priority, route_order)
               VALUES (%s, %s, %s, %s, %s, %s) RETURNING *""",
            (zone_id, code, bc, name_ru, pick_priority, route_order),
        )
        row = cur.fetchone()
    return _location_from_row(row)


def list_locations(conn, *, zone_code: str | None = None) -> list[Location]:
    sql = (
        "SELECT l.* FROM wms_locations l "
        + ("JOIN wms_zones z ON l.zone_id = z.id WHERE z.code = %s " if zone_code else "")
        + "ORDER BY l.code"
    )
    params: tuple[Any, ...] = (zone_code,) if zone_code else ()
    with conn.cursor() as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()
    return [_location_from_row(r) for r in rows]


# ──────────────────────────────────────────────────────────────────────
# warehouse_stock
# ──────────────────────────────────────────────────────────────────────


def find_stock(
    conn, product_key: ProductKey, *, item_state: str = "SELLABLE"
) -> WarehouseStock | None:
    """Return the single stock row for a product key + state, or None."""
    with conn.cursor() as cur:
        cur.execute(
            """SELECT * FROM warehouse_stock
               WHERE item_type=%s AND product_name=%s AND product_size=%s
                 AND product_color=%s AND stage_name=%s AND ready_for_position=%s
                 AND item_state=%s""",
            (
                product_key.item_type,
                product_key.product_name,
                product_key.product_size,
                product_key.product_color,
                product_key.stage_name,
                product_key.ready_for_position,
                item_state,
            ),
        )
        row = cur.fetchone()
    return _stock_from_row(row) if row else None


def upsert_stock(
    conn,
    product_key: ProductKey,
    *,
    delta: int,
    item_state: str = "SELLABLE",
    location_id: int | None = None,
    legacy_sqlite_id: int | None = None,
) -> int:
    """Insert or increment a stock row.  Returns the stock id.

    Uses ``ON CONFLICT … DO UPDATE`` for atomic upsert (Postgres native).
    """
    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO warehouse_stock
               (legacy_sqlite_id, item_type, product_name, product_size,
                product_color, stage_name, ready_for_position, quantity,
                item_state, location_id, updated_at)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, now())
               ON CONFLICT (item_type, product_name, product_size, product_color,
                            stage_name, ready_for_position, unit, item_state)
               DO UPDATE SET quantity = warehouse_stock.quantity + EXCLUDED.quantity,
                             location_id = COALESCE(EXCLUDED.location_id, warehouse_stock.location_id),
                             updated_at = now()
               RETURNING id""",
            (
                legacy_sqlite_id,
                product_key.item_type,
                product_key.product_name,
                product_key.product_size,
                product_key.product_color,
                product_key.stage_name,
                product_key.ready_for_position,
                delta,
                item_state,
                location_id,
            ),
        )
        row = cur.fetchone()
    return int(row[0])


def set_stock_location(conn, stock_id: int, location_id: int) -> None:
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE warehouse_stock SET location_id=%s, updated_at=now() WHERE id=%s",
            (location_id, stock_id),
        )


def get_stock_rows(conn, *, location_id: int | None = None) -> list[WarehouseStock]:
    sql = "SELECT * FROM warehouse_stock WHERE quantity > 0"
    params: list[Any] = []
    if location_id is not None:
        sql += " AND location_id = %s"
        params.append(location_id)
    sql += " ORDER BY product_name, product_size"
    with conn.cursor() as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()
    return [_stock_from_row(r) for r in rows]


# ──────────────────────────────────────────────────────────────────────
# movements (immutable journal)
# ──────────────────────────────────────────────────────────────────────


def insert_movement(
    conn,
    *,
    request_key: str,
    movement_type: str,
    product_key: ProductKey,
    quantity: int,
    from_location_id: int | None = None,
    to_location_id: int | None = None,
    from_state: str | None = None,
    to_state: str | None = None,
    source_type: str | None = None,
    source_id: int | None = None,
    reason: str | None = None,
    actor_employee_id: int | None = None,
    tsd_device_id: str | None = None,
) -> int | None:
    """Insert a movement if its request_key is new.  Returns id, or None if dup.

    Idempotency mirrors the legacy ``production_trace_events.request_key`` UNIQUE
    + ``INSERT OR IGNORE`` pattern.
    """
    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO wms_movements
               (request_key, movement_type, product_key, quantity,
                from_location_id, to_location_id, from_state, to_state,
                source_type, source_id, reason, actor_employee_id, tsd_device_id)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
               ON CONFLICT (request_key) DO NOTHING
               RETURNING id""",
            (
                request_key,
                movement_type,
                json.dumps(product_key.to_dict()),
                quantity,
                from_location_id,
                to_location_id,
                from_state,
                to_state,
                source_type,
                source_id,
                reason,
                actor_employee_id,
                tsd_device_id,
            ),
        )
        row = cur.fetchone()
    return int(row[0]) if row else None


def movement_exists(conn, request_key: str) -> bool:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT 1 FROM wms_movements WHERE request_key = %s", (request_key,)
        )
        return cur.fetchone() is not None


def list_movements(
    conn, *, limit: int = 100, movement_type: str | None = None
) -> list[Movement]:
    sql = "SELECT * FROM wms_movements"
    params: list[Any] = []
    if movement_type:
        sql += " WHERE movement_type = %s"
        params.append(movement_type)
    sql += " ORDER BY occurred_at DESC LIMIT %s"
    params.append(limit)
    with conn.cursor() as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()
    return [_movement_from_row(r) for r in rows]


# ──────────────────────────────────────────────────────────────────────
# row mappers
# ──────────────────────────────────────────────────────────────────────


def _zone_from_row(row) -> Zone:
    return Zone(
        id=int(row["id"]),
        code=row["code"],
        name_ru=row["name_ru"],
        zone_type=row["zone_type"],
        sort_order=int(row["sort_order"]),
        is_active=bool(row["is_active"]),
    )


def _location_from_row(row) -> Location:
    return Location(
        id=int(row["id"]),
        zone_id=int(row["zone_id"]),
        code=row["code"],
        barcode=row["barcode"],
        name_ru=row.get("name_ru"),
        pick_priority=int(row["pick_priority"]),
        route_order=int(row["route_order"]),
        status=row["status"],
    )


def _stock_from_row(row) -> WarehouseStock:
    pk = ProductKey(
        item_type=row["item_type"],
        product_name=row["product_name"],
        product_size=row["product_size"],
        product_color=row["product_color"],
        stage_name=row["stage_name"],
        ready_for_position=row["ready_for_position"],
    )
    loc = row.get("location_id")
    return WarehouseStock(
        id=int(row["id"]),
        product_key=pk,
        quantity=int(row["quantity"]),
        reserved_quantity=int(row["reserved_quantity"]),
        item_state=row["item_state"],
        location_id=int(loc) if loc is not None else None,
        unit=row["unit"],
        legacy_sqlite_id=row.get("legacy_sqlite_id"),
    )


def _movement_from_row(row) -> Movement:
    pk = ProductKey.from_dict(row["product_key"])
    return Movement(
        id=int(row["id"]),
        request_key=row["request_key"],
        movement_type=row["movement_type"],
        product_key=pk,
        quantity=int(row["quantity"]),
        from_location_id=_int_or_none(row.get("from_location_id")),
        to_location_id=_int_or_none(row.get("to_location_id")),
        from_state=row.get("from_state"),
        to_state=row.get("to_state"),
        source_type=row.get("source_type"),
        source_id=_int_or_none(row.get("source_id")),
        reason=row.get("reason"),
        actor_employee_id=_int_or_none(row.get("actor_employee_id")),
        tsd_device_id=row.get("tsd_device_id"),
        occurred_at=str(row["occurred_at"]),
    )


def _int_or_none(value) -> int | None:
    if value is None:
        return None
    return int(value)
