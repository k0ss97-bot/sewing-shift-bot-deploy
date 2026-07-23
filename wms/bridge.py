"""Bridge: mirror SQLite ``warehouse_stock`` into Postgres.

The legacy sewing-shift-bot keeps ``warehouse_stock`` in SQLite. The WMS layer
uses Postgres as its master. This module performs a one-way sync (SQLite →
Postgres) so the WMS sees current legacy stock without modifying
``database.py``.

Run once after the initial Postgres migration, and periodically (e.g. every few
minutes) while both databases are live, until the WMS becomes the sole writer.
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

_PG_UPSERT = """
    INSERT INTO warehouse_stock
      (legacy_sqlite_id, item_type, product_name, product_size, product_color,
       stage_name, ready_for_position, quantity, reserved_quantity, unit,
       item_state, updated_at)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'SELLABLE',now())
    ON CONFLICT (legacy_sqlite_id)
    DO UPDATE SET
      quantity = EXCLUDED.quantity,
      reserved_quantity = EXCLUDED.reserved_quantity,
      updated_at = now()
"""


def sync_warehouse_stock_from_sqlite(sqlite_conn) -> dict[str, int]:
    """Copy all warehouse_stock rows from SQLite into Postgres.

    ``sqlite_conn`` is an open ``sqlite3.Connection`` (from the legacy
    ``database.get_db_connection()``).  Returns a summary dict.
    """
    pg = get_pg_connection()
    synced = 0
    skipped = 0
    try:
        with sqlite_conn.cursor() if hasattr(sqlite_conn, "cursor") else _LegacyCursor(
            sqlite_conn
        ) as cur:
            cur.execute(_LEGACY_SELECT)
            rows = cur.fetchall()
        with pg.cursor() as pcur:
            for row in rows:
                try:
                    pcur.execute(_PG_UPSERT, row)
                    synced += 1
                except Exception as exc:  # pragma: no cover - defensive
                    log.warning("skip legacy row %s: %s", row[0], exc)
                    skipped += 1
        pg.commit()
    except Exception:
        pg.rollback()
        raise
    return {"synced": synced, "skipped": skipped, "total": len(rows)}


class _LegacyCursor:
    """Adapter so the same ``with … as cur`` block works for sqlite3."""

    def __init__(self, conn):
        self._conn = conn
        self._cur = conn.cursor()

    def __enter__(self):
        return self._cur

    def __exit__(self, *exc):
        self._cur.close()
        return False
