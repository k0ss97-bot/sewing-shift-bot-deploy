"""Postgres CRUD for WMS entities.

Thin data-access functions used by :mod:`wms.operations`. Each function takes
an open connection (the caller owns the transaction) so multi-step operations
can compose inside a single ``BEGIN``/``COMMIT``.

Finished-goods identity is article-first. Legacy rows without an article remain
readable, while every new marketplace-linked row carries ``product_article``.
"""

from __future__ import annotations

import json
from typing import Any

from .connection import get_pg_connection
from .models import Location, Movement, ProductKey, WarehouseStock, Zone


_LOCATION_UNSET = object()


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


def finished_production_receipts(
    conn,
    *,
    start_date: str,
    end_date: str,
    timezone_name: str = "Asia/Yekaterinburg",
) -> dict[str, Any]:
    """Return finished goods actually received from production.

    The fact comes from the immutable WMS movement journal, not route-step
    completions. This prevents one garment from being counted once per
    operation and excludes semi-finished stock.
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                (movement.occurred_at AT TIME ZONE %s)::date AS receipt_date,
                movement.product_key->>'product_article' AS product_article,
                movement.product_key->>'product_name' AS product_name,
                movement.product_key->>'product_size' AS product_size,
                movement.product_key->>'product_color' AS product_color,
                location.code AS location_code,
                movement.quantity,
                movement.occurred_at,
                movement.id
            FROM wms_movements AS movement
            JOIN wms_locations AS location ON location.id = movement.to_location_id
            JOIN wms_zones AS zone ON zone.id = location.zone_id
            WHERE movement.movement_type = 'production_receipt'
              AND movement.source_type = 'production'
              AND movement.product_key->>'item_type' = 'finished'
              AND movement.quantity > 0
              AND zone.code = 'RECEIVE'
              AND (movement.occurred_at AT TIME ZONE %s)::date BETWEEN %s::date AND %s::date
            ORDER BY movement.occurred_at DESC, movement.id DESC
            """,
            (timezone_name, timezone_name, start_date, end_date),
        )
        rows = cur.fetchall()

    daily: dict[str, int] = {}
    details: list[dict[str, Any]] = []
    latest = None
    total = 0
    for row in rows:
        receipt_date = str(row["receipt_date"])
        quantity = int(row["quantity"] or 0)
        occurred_at = row["occurred_at"]
        total += quantity
        daily[receipt_date] = daily.get(receipt_date, 0) + quantity
        if latest is None or occurred_at > latest:
            latest = occurred_at
        if len(details) < 200:
            details.append(
                {
                    "date": receipt_date,
                    "article": str(row.get("product_article") or ""),
                    "product": str(row["product_name"] or ""),
                    "size": str(row["product_size"] or ""),
                    "color": str(row["product_color"] or ""),
                    "location": str(row["location_code"] or ""),
                    "quantity": quantity,
                    "occurred_at": occurred_at.isoformat() if occurred_at else "",
                }
            )
    return {
        "quantity": total,
        "movement_count": len(rows),
        "updated_at": latest.isoformat() if latest else None,
        "daily": [{"date": day, "quantity": daily[day]} for day in sorted(daily)],
        "details": details,
    }


# ──────────────────────────────────────────────────────────────────────
# warehouse_stock
# ──────────────────────────────────────────────────────────────────────


def find_stock(
    conn,
    product_key: ProductKey,
    *,
    item_state: str = "SELLABLE",
    unit: str = "шт",
    location_id: int | None | object = _LOCATION_UNSET,
    for_update: bool = False,
) -> WarehouseStock | None:
    """Return one stock row for a product key, state and optional location.

    When ``location_id`` is omitted this compatibility helper only succeeds if
    the product exists in at most one location. Callers performing a physical
    warehouse operation must always pass the location explicitly.
    """
    if product_key.item_type == "finished" and product_key.product_article:
        sql = """SELECT * FROM warehouse_stock
                 WHERE item_type='finished' AND product_article=%s
                   AND item_state=%s AND unit=%s"""
        params: list[Any] = [product_key.product_article, item_state, unit]
    else:
        sql = """SELECT * FROM warehouse_stock
                 WHERE item_type=%s AND product_article=''
                   AND product_name=%s AND product_size=%s
                   AND product_color=%s AND stage_name=%s AND ready_for_position=%s
                   AND item_state=%s AND unit=%s"""
        params = [
            product_key.item_type,
            product_key.product_name,
            product_key.product_size,
            product_key.product_color,
            product_key.stage_name,
            product_key.ready_for_position,
            item_state,
            unit,
        ]
    if location_id is not _LOCATION_UNSET:
        sql += " AND location_id IS NOT DISTINCT FROM %s"
        params.append(location_id)
    sql += " ORDER BY id"
    if for_update:
        sql += " FOR UPDATE"
    with conn.cursor() as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()
    if len(rows) > 1:
        raise ValueError("Товар находится в нескольких ячейках — укажите исходную ячейку.")
    return _stock_from_row(rows[0]) if rows else None


def upsert_stock(
    conn,
    product_key: ProductKey,
    *,
    delta: int,
    item_state: str = "SELLABLE",
    location_id: int | None = None,
    unit: str = "шт",
    legacy_sqlite_id: int | None = None,
) -> int:
    """Insert or adjust a stock row.  Returns the stock id.

    Positive deltas use ``ON CONFLICT … DO UPDATE``. Negative deltas use a
    guarded ``UPDATE`` so PostgreSQL never attempts to insert a temporary
    negative row before conflict resolution.
    """
    with conn.cursor() as cur:
        if delta < 0:
            if product_key.item_type == "finished" and product_key.product_article:
                cur.execute(
                    """UPDATE warehouse_stock
                          SET quantity = quantity + %s,
                              updated_at = now()
                        WHERE item_type='finished' AND product_article=%s
                          AND unit=%s AND item_state=%s
                          AND location_id IS NOT DISTINCT FROM %s
                          AND quantity + %s >= 0
                    RETURNING id""",
                    (delta, product_key.product_article, unit, item_state, location_id, delta),
                )
            else:
                cur.execute(
                    """UPDATE warehouse_stock
                          SET quantity = quantity + %s,
                              updated_at = now()
                        WHERE item_type=%s AND product_article=''
                          AND product_name=%s AND product_size=%s
                          AND product_color=%s AND stage_name=%s AND ready_for_position=%s
                          AND unit=%s AND item_state=%s
                          AND location_id IS NOT DISTINCT FROM %s
                          AND quantity + %s >= 0
                    RETURNING id""",
                    (
                        delta,
                        product_key.item_type,
                        product_key.product_name,
                        product_key.product_size,
                        product_key.product_color,
                        product_key.stage_name,
                        product_key.ready_for_position,
                        unit,
                        item_state,
                        location_id,
                        delta,
                    ),
                )
            row = cur.fetchone()
            if row is None:
                raise ValueError("Недостаточно товара для списания.")
            return int(row[0])

        values = (
            legacy_sqlite_id,
            product_key.item_type,
            product_key.product_article,
            product_key.product_name,
            product_key.product_size,
            product_key.product_color,
            product_key.stage_name,
            product_key.ready_for_position,
            delta,
            item_state,
            location_id,
            unit,
        )
        if product_key.item_type == "finished" and product_key.product_article:
            cur.execute(
                """INSERT INTO warehouse_stock
                   (legacy_sqlite_id, item_type, product_article, product_name, product_size,
                    product_color, stage_name, ready_for_position, quantity,
                    item_state, location_id, unit, updated_at)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, now())
                   ON CONFLICT (product_article, unit, item_state, location_id)
                     WHERE item_type='finished' AND product_article<>''
                   DO UPDATE SET quantity = warehouse_stock.quantity + EXCLUDED.quantity,
                                 product_name = EXCLUDED.product_name,
                                 product_size = EXCLUDED.product_size,
                                 product_color = EXCLUDED.product_color,
                                 stage_name = EXCLUDED.stage_name,
                                 ready_for_position = EXCLUDED.ready_for_position,
                                 legacy_sqlite_id = COALESCE(EXCLUDED.legacy_sqlite_id, warehouse_stock.legacy_sqlite_id),
                                 updated_at = now()
                   RETURNING id""",
                values,
            )
        else:
            cur.execute(
                """INSERT INTO warehouse_stock
                   (legacy_sqlite_id, item_type, product_article, product_name, product_size,
                    product_color, stage_name, ready_for_position, quantity,
                    item_state, location_id, unit, updated_at)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, now())
                   ON CONFLICT (item_type, product_name, product_size, product_color,
                                stage_name, ready_for_position, unit, item_state, location_id)
                     WHERE item_type<>'finished' OR product_article=''
                   DO UPDATE SET quantity = warehouse_stock.quantity + EXCLUDED.quantity,
                                 legacy_sqlite_id = COALESCE(EXCLUDED.legacy_sqlite_id, warehouse_stock.legacy_sqlite_id),
                                 updated_at = now()
                   RETURNING id""",
                values,
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
# stock receipt documents (Оприходование)
# ──────────────────────────────────────────────────────────────────────


def get_stock_receipt_by_request_key(conn, request_key: str) -> dict[str, Any] | None:
    with conn.cursor() as cur:
        cur.execute(
            """SELECT id,number,status,request_key,actor_employee_id,comment,
                      lines_count,total_quantity,created_at,posted_at
                 FROM wms_stock_receipts WHERE request_key=%s""",
            (request_key,),
        )
        row = cur.fetchone()
    return _stock_receipt_payload(row) if row else None


def create_stock_receipt(
    conn,
    *,
    request_key: str,
    actor_employee_id: int,
    comment: str | None = None,
) -> dict[str, Any] | None:
    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO wms_stock_receipts
                      (request_key,actor_employee_id,comment)
                 VALUES (%s,%s,%s)
                 ON CONFLICT (request_key) DO NOTHING
              RETURNING id,number,status,request_key,actor_employee_id,comment,
                        lines_count,total_quantity,created_at,posted_at""",
            (request_key, actor_employee_id, comment),
        )
        row = cur.fetchone()
    return _stock_receipt_payload(row) if row else None


def insert_stock_receipt_line(
    conn,
    *,
    receipt_id: int,
    line_no: int,
    barcode: str,
    product_key: ProductKey,
    quantity: int,
    movement_id: int,
) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO wms_stock_receipt_lines
                      (receipt_id,line_no,barcode,product_key,quantity,movement_id)
                 VALUES (%s,%s,%s,%s,%s,%s)""",
            (
                receipt_id,
                line_no,
                barcode,
                json.dumps(product_key.to_dict()),
                quantity,
                movement_id,
            ),
        )


def post_stock_receipt(
    conn,
    *,
    receipt_id: int,
    lines_count: int,
    total_quantity: int,
) -> dict[str, Any]:
    with conn.cursor() as cur:
        cur.execute(
            """UPDATE wms_stock_receipts
                  SET status='posted',lines_count=%s,total_quantity=%s,posted_at=now()
                WHERE id=%s
            RETURNING id,number,status,request_key,actor_employee_id,comment,
                      lines_count,total_quantity,created_at,posted_at""",
            (lines_count, total_quantity, receipt_id),
        )
        row = cur.fetchone()
    return _stock_receipt_payload(row)


def list_stock_receipts(conn, *, limit: int = 50) -> list[dict[str, Any]]:
    with conn.cursor() as cur:
        cur.execute(
            """SELECT id,number,status,request_key,actor_employee_id,comment,
                      lines_count,total_quantity,created_at,posted_at
                 FROM wms_stock_receipts
                ORDER BY created_at DESC LIMIT %s""",
            (limit,),
        )
        rows = cur.fetchall()
    return [_stock_receipt_payload(row) for row in rows]


def _stock_receipt_payload(row) -> dict[str, Any]:
    return {
        "id": int(row[0]),
        "number": str(row[1]),
        "status": str(row[2]),
        "request_key": str(row[3]),
        "actor_employee_id": int(row[4]) if row[4] is not None else None,
        "comment": str(row[5] or ""),
        "lines_count": int(row[6] or 0),
        "total_quantity": int(row[7] or 0),
        "created_at": str(row[8]) if row[8] is not None else None,
        "posted_at": str(row[9]) if row[9] is not None else None,
    }


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
        product_article=row.get("product_article") or "",
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
