"""Bridge: mirror SQLite ``warehouse_stock`` into Postgres.

The legacy sewing-shift-bot keeps ``warehouse_stock`` in SQLite. The WMS layer
uses Postgres as its master. This module performs a one-way sync (SQLite →
Postgres) so the WMS sees current legacy stock without modifying
``database.py``.

Run once after the initial Postgres migration. Existing Postgres rows are not
overwritten unless ``overwrite_existing=True`` is passed explicitly; blind
periodic overwrite would destroy location-aware TSD changes.
"""

from __future__ import annotations

import logging
from typing import Any

from .connection import get_pg_connection
from .models import ProductKey

log = logging.getLogger(__name__)

_LEGACY_SELECT = (
    "SELECT id, item_type, product_name, product_size, product_color, "
    "stage_name, ready_for_position, quantity, reserved_quantity, unit "
    "FROM warehouse_stock"
)

_PG_INSERT = """
    INSERT INTO warehouse_stock
      (legacy_sqlite_id, item_type, product_name, product_size, product_color,
       stage_name, ready_for_position, quantity, reserved_quantity, unit,
       item_state, updated_at)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'SELLABLE',now())
    ON CONFLICT (legacy_sqlite_id) WHERE legacy_sqlite_id IS NOT NULL
    DO NOTHING
"""

_PG_UPSERT = _PG_INSERT.replace(
    "DO NOTHING",
    "DO UPDATE SET quantity = EXCLUDED.quantity, "
    "reserved_quantity = EXCLUDED.reserved_quantity, updated_at = now()",
)


def sync_warehouse_stock_from_sqlite(
    sqlite_conn, *, overwrite_existing: bool = False
) -> dict[str, int]:
    """Copy all warehouse_stock rows from SQLite into Postgres.

    ``sqlite_conn`` is an open ``sqlite3.Connection`` (from the legacy
    ``database.get_db_connection()``).  Returns a summary dict.
    """
    pg = get_pg_connection()
    synced = 0
    skipped = 0
    try:
        cur = sqlite_conn.cursor()
        try:
            cur.execute(_LEGACY_SELECT)
            rows = cur.fetchall()
        finally:
            cur.close()
        with pg.cursor() as pcur:
            for row in rows:
                try:
                    pcur.execute(_PG_UPSERT if overwrite_existing else _PG_INSERT, row)
                    if pcur.rowcount:
                        synced += 1
                    else:
                        skipped += 1
                except Exception as exc:  # pragma: no cover - defensive
                    log.warning("skip legacy row %s: %s", row[0], exc)
                    skipped += 1
        pg.commit()
    except Exception:
        pg.rollback()
        raise
    return {"synced": synced, "skipped": skipped, "total": len(rows)}


def compare_warehouse_totals(sqlite_conn) -> dict[str, Any]:
    """Compare legacy sellable totals with all location-aware Postgres totals.

    This is read-only and is intended as a deployment/cutover gate.
    """
    cursor = sqlite_conn.cursor()
    try:
        cursor.execute(_LEGACY_SELECT)
        legacy_rows = cursor.fetchall()
    finally:
        cursor.close()

    legacy = {
        (row[1], row[2], row[3], row[4], row[5], row[6], row[9]): int(row[7])
        for row in legacy_rows
    }
    pg = get_pg_connection()
    with pg.cursor() as cursor:
        cursor.execute(
            """SELECT item_type, product_name, product_size, product_color,
                      stage_name, ready_for_position, unit, SUM(quantity)
                 FROM warehouse_stock
                WHERE item_state = 'SELLABLE'
                GROUP BY item_type, product_name, product_size, product_color,
                         stage_name, ready_for_position, unit"""
        )
        pg_rows = cursor.fetchall()
    postgres = {tuple(row[:7]): int(row[7]) for row in pg_rows}

    mismatches = []
    for key in sorted(set(legacy) | set(postgres)):
        legacy_quantity = legacy.get(key, 0)
        postgres_quantity = postgres.get(key, 0)
        if legacy_quantity != postgres_quantity:
            mismatches.append(
                {
                    "product_key": key,
                    "sqlite_quantity": legacy_quantity,
                    "postgres_quantity": postgres_quantity,
                    "difference": postgres_quantity - legacy_quantity,
                }
            )
    return {
        "ok": not mismatches,
        "sqlite_rows": len(legacy),
        "postgres_rows": len(postgres),
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
    }
