"""PostgreSQL connection for the WMS module.

The legacy sewing-shift-bot runs on SQLite. The WMS layer uses a separate
PostgreSQL database (the "hybrid" architecture decision): ``warehouse_stock``
is mirrored here as the WMS master, while employees/shifts/fabric remain in
SQLite and are referenced by integer id without a cross-database FK.

Connection is configured via the ``WMS_DATABASE_URL`` env var (falling back to
``DATABASE_URL``, then a localhost default). A global connection cache keeps a
single open connection per URL, matching the project's minimal-dependency style.
"""

from __future__ import annotations

import os
from typing import Any

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:  # pragma: no cover - psycopg2 is the one approved new dep
    psycopg2 = None
    RealDictCursor = None


_DEFAULT_URL = "postgresql://wms:wms@localhost:5432/wms"
_connection_cache: dict[str, Any] = {}


def database_url() -> str:
    """Resolve the Postgres URL from env."""
    return (
        os.environ.get("WMS_DATABASE_URL")
        or os.environ.get("DATABASE_URL")
        or _DEFAULT_URL
    )


def get_pg_connection():
    """Return a cached psycopg2 connection (autocommit OFF by default).

    Callers manage their own transactions (BEGIN / COMMIT / ROLLBACK) to match
    the existing SQLite ``BEGIN IMMEDIATE`` pattern. Use ``set_autocommit`` for
    DDL that should run outside a transaction.
    """
    if psycopg2 is None:
        raise RuntimeError(
            "psycopg2 is not installed. Install with: pip install psycopg2-binary"
        )
    url = database_url()
    conn = _connection_cache.get(url)
    if conn is None or conn.closed:
        conn = psycopg2.connect(url)
        conn.autocommit = False
        _connection_cache[url] = conn
    return conn


def reset_connection() -> None:
    """Close and forget the cached connection (used by tests)."""
    url = database_url()
    conn = _connection_cache.pop(url, None)
    if conn is not None and not conn.closed:
        conn.close()


def dict_cursor(conn):
    """Return a cursor yielding RealDictRows."""
    return conn.cursor(cursor_factory=RealDictCursor)
