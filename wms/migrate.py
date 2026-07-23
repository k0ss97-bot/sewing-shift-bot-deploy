"""Schema migration runner for the WMS Postgres layer.

SQL files live in ``wms_migrations/`` and are applied in filename order. Each
file is recorded in the ``schema_migrations`` table so re-runs are idempotent.
This mirrors the project's additive ``CREATE TABLE IF NOT EXISTS`` +
``ALTER TABLE`` philosophy, but for Postgres.

Usage as a CLI::

    python -m wms.migrate           # apply all pending migrations
    python -m wms.migrate --status  # show applied migrations
    python -m wms.migrate --seed    # apply only the seed migration
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .connection import get_pg_connection


_MIGRATIONS_DIR = Path(__file__).resolve().parent.parent / "wms_migrations"


def applied_migrations(conn) -> set[str]:
    """Return the set of migration filenames already applied."""
    with conn.cursor() as cur:
        cur.execute(
            "CREATE TABLE IF NOT EXISTS schema_migrations ("
            " id SERIAL PRIMARY KEY,"
            " filename TEXT NOT NULL UNIQUE,"
            " applied_at TIMESTAMPTZ NOT NULL DEFAULT now()"
            ")"
        )
        conn.commit()
        cur.execute("SELECT filename FROM schema_migrations")
        return {row[0] for row in cur.fetchall()}


def pending_migrations(conn) -> list[Path]:
    """List migration files not yet applied, in filename order."""
    applied = applied_migrations(conn)
    if not _MIGRATIONS_DIR.is_dir():
        return []
    files = sorted(_MIGRATIONS_DIR.glob("*.sql"))
    return [f for f in files if f.name not in applied]


def apply_migration(conn, path: Path) -> bool:
    """Apply one migration file.  Returns True if applied, False if skipped."""
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM schema_migrations WHERE filename = %s", (path.name,))
        if cur.fetchone():
            return False
        sql = path.read_text(encoding="utf-8")
        cur.execute(sql)
        cur.execute(
            "INSERT INTO schema_migrations (filename) VALUES (%s)", (path.name,)
        )
    conn.commit()
    return True


def migrate_all() -> list[str]:
    """Apply all pending migrations.  Returns the list of applied filenames."""
    conn = get_pg_connection()
    applied: list[str] = []
    for path in pending_migrations(conn):
        if apply_migration(conn, path):
            applied.append(path.name)
            print(f"  applied: {path.name}")
    if not applied:
        print("  (no pending migrations)")
    return applied


def migration_status() -> list[str]:
    """Print and return the list of applied migration filenames."""
    conn = get_pg_connection()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT filename FROM schema_migrations ORDER BY filename"
        )
        rows = [row[0] for row in cur.fetchall()]
    for name in rows:
        print(f"  applied: {name}")
    if not rows:
        print("  (none applied yet)")
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="wms.migrate", description="WMS Postgres schema migrations."
    )
    parser.add_argument("--status", action="store_true", help="show applied migrations")
    args = parser.parse_args()
    if args.status:
        migration_status()
        return 0
    print("applying WMS migrations...")
    migrate_all()
    print("done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
