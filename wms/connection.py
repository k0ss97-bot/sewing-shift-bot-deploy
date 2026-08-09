"""PostgreSQL connection for the WMS module.

The legacy sewing-shift-bot runs on SQLite. The WMS layer uses a separate
PostgreSQL database (the "hybrid" architecture decision): ``warehouse_stock``
is mirrored here as the WMS master, while employees/shifts/fabric remain in
SQLite and are referenced by integer id without a cross-database FK.

Connection is configured via the ``WMS_DATABASE_URL`` env var (falling back to
``DATABASE_URL``, then a localhost default). A bounded, thread-safe pool keeps
request concurrency below PostgreSQL's connection limit. Request threads lease
one connection and return it through ``close_thread_connections()``.
"""

from __future__ import annotations

import os
import threading
import time
from typing import Any

try:
    import psycopg2
    from psycopg2 import pool as psycopg2_pool
    from psycopg2.extras import DictCursor
except ImportError:  # pragma: no cover - psycopg2 is the one approved new dep
    psycopg2 = None
    psycopg2_pool = None
    DictCursor = None


_DEFAULT_URL = "postgresql://wms:wms@localhost:5432/wms"
_thread_connections = threading.local()
_connection_registry: list[Any] = []
_connection_registry_lock = threading.Lock()
_pools: dict[str, "_BoundedPool"] = {}
_pools_lock = threading.Lock()


def _positive_int_environment(name: str, default: int) -> int:
    try:
        value = int(os.environ.get(name, str(default)))
    except (TypeError, ValueError):
        return default
    return max(1, value)


def _positive_float_environment(name: str, default: float) -> float:
    try:
        value = float(os.environ.get(name, str(default)))
    except (TypeError, ValueError):
        return default
    return max(0.1, value)


class _BoundedPool:
    def __init__(self, url: str) -> None:
        maximum = _positive_int_environment("WMS_DB_POOL_MAX", 12)
        self.maximum = maximum
        self.acquire_timeout = _positive_float_environment("WMS_DB_POOL_TIMEOUT_SECONDS", 5.0)
        self.slots = threading.BoundedSemaphore(maximum)
        self.pool = psycopg2_pool.ThreadedConnectionPool(
            1,
            maximum,
            dsn=url,
            cursor_factory=DictCursor,
        )

    def acquire(self):
        started = time.monotonic()
        if not self.slots.acquire(timeout=self.acquire_timeout):
            raise RuntimeError(
                f"WMS PostgreSQL pool exhausted after {time.monotonic() - started:.2f}s"
            )
        try:
            connection = self.pool.getconn()
            connection.autocommit = False
            return connection
        except BaseException:
            self.slots.release()
            raise

    def release(self, connection) -> None:
        close = bool(connection is None or connection.closed)
        if not close:
            try:
                # Every lease returns in an idle transaction state. This also
                # protects the next request after an exception in a read path.
                connection.rollback()
            except Exception:
                close = True
        try:
            self.pool.putconn(connection, close=close)
        finally:
            self.slots.release()

    def close(self) -> None:
        self.pool.closeall()


def database_url() -> str:
    """Resolve the Postgres URL from env."""
    return (
        os.environ.get("WMS_DATABASE_URL")
        or os.environ.get("DATABASE_URL")
        or _DEFAULT_URL
    )


def get_pg_connection():
    """Return this thread's leased psycopg2 connection (autocommit OFF).

    Callers manage their own transactions (BEGIN / COMMIT / ROLLBACK) to match
    the existing SQLite ``BEGIN IMMEDIATE`` pattern. Use ``set_autocommit`` for
    DDL that should run outside a transaction.
    """
    if psycopg2 is None:
        raise RuntimeError(
            "psycopg2 is not installed. Install with: pip install psycopg2-binary"
        )
    url = database_url()
    cache = getattr(_thread_connections, "cache", None)
    if cache is None:
        cache = {}
        _thread_connections.cache = cache
    lease = cache.get(url)
    conn = lease[1] if lease else None
    if lease is not None and conn.closed:
        lease[0].release(conn)
        cache.pop(url, None)
        with _connection_registry_lock:
            _connection_registry[:] = [item for item in _connection_registry if item is not conn]
        conn = None
    if conn is None or conn.closed:
        with _pools_lock:
            pool = _pools.get(url)
            if pool is None:
                pool = _BoundedPool(url)
                _pools[url] = pool
        conn = pool.acquire()
        cache[url] = (pool, conn)
        with _connection_registry_lock:
            _connection_registry.append(conn)
    return conn


def reset_connection() -> None:
    """Close every pool and forget cached leases (used by tests/shutdown)."""
    with _connection_registry_lock:
        _connection_registry.clear()
    with _pools_lock:
        pools = list(_pools.values())
        _pools.clear()
    for pool in pools:
        pool.close()
    _thread_connections.cache = {}


def close_thread_connections() -> None:
    """Close PostgreSQL connections cached by the current request thread.

    ``ThreadingHTTPServer`` creates short-lived worker threads.  Without an
    explicit teardown, their thread-local caches disappear while the global
    registry keeps the underlying connections alive until process shutdown.
    """
    cache = getattr(_thread_connections, "cache", None) or {}
    leases = list(cache.values())
    _thread_connections.cache = {}
    if not leases:
        return
    connections = [connection for _, connection in leases]
    connection_ids = {id(conn) for conn in connections}
    with _connection_registry_lock:
        _connection_registry[:] = [
            conn for conn in _connection_registry if id(conn) not in connection_ids
        ]
    for pool, conn in leases:
        pool.release(conn)


def dict_cursor(conn):
    """Return a cursor yielding RealDictRows."""
    return conn.cursor(cursor_factory=DictCursor)
