#!/usr/bin/env python3
"""Create and verify a consistent SQLite backup with bounded retention."""

from __future__ import annotations

import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path


def database_path() -> Path:
    db_dir = Path(os.environ.get("DB_DIR") or "").expanduser()
    if not db_dir.is_absolute():
        raise RuntimeError("DB_DIR must be an absolute path.")
    return db_dir / "bot.db"


def retention_count() -> int:
    try:
        value = int(os.environ.get("WEBAPP_BACKUP_RETENTION", "14"))
    except ValueError as error:
        raise RuntimeError("WEBAPP_BACKUP_RETENTION must be an integer.") from error
    return max(3, min(value, 90))


def create_backup(source: Path) -> Path:
    if not source.is_file():
        raise RuntimeError(f"Database does not exist: {source}")
    backup_dir = source.parent / "backups"
    backup_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    destination = backup_dir / f"webapp_{timestamp}.db"
    temporary = destination.with_suffix(".tmp")

    source_connection = sqlite3.connect(f"file:{source}?mode=ro", uri=True)
    destination_connection = sqlite3.connect(temporary)
    try:
        source_connection.backup(destination_connection)
        result = destination_connection.execute("PRAGMA integrity_check").fetchone()
        if not result or result[0] != "ok":
            raise RuntimeError("SQLite backup integrity check failed.")
        destination_connection.commit()
    finally:
        destination_connection.close()
        source_connection.close()

    temporary.chmod(0o600)
    temporary.replace(destination)
    backups = sorted(backup_dir.glob("webapp_*.db"), reverse=True)
    for expired in backups[retention_count():]:
        expired.unlink()
    return destination


def main() -> int:
    try:
        destination = create_backup(database_path())
    except Exception as error:
        print(f"Backup failed: {error}", file=sys.stderr)
        return 1
    print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
