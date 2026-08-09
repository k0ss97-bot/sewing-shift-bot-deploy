#!/usr/bin/env python3
"""Restore the newest production backups into disposable targets.

The script never replaces either live database and never prints backup names
or contents. PostgreSQL is restored only into a generated database containing
``test``; SQLite is copied only into a private temporary directory.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import pwd
import shutil
import sqlite3
import subprocess
import tempfile
import time


def _latest(directory: Path, pattern: str) -> Path:
    candidates = sorted(directory.glob(pattern), key=lambda path: path.stat().st_mtime, reverse=True)
    if not candidates:
        raise RuntimeError("A verified backup artifact is unavailable.")
    selected = candidates[0].resolve()
    if selected.parent != directory.resolve() or not selected.is_file() or selected.stat().st_size <= 0:
        raise RuntimeError("The selected backup artifact is invalid.")
    return selected


def verify_sqlite_restore() -> dict[str, int | str]:
    source_path = Path(os.environ.get("DB_NAME", "/var/lib/sewing-web/bot.db")).resolve()
    backup = _latest(source_path.parent / "backups", "webapp_*.db")
    with tempfile.TemporaryDirectory(prefix="sewing-sqlite-restore-test-") as temporary:
        restored = Path(temporary) / "restored-test.db"
        shutil.copy2(backup, restored)
        connection = sqlite3.connect(f"file:{restored}?mode=ro", uri=True)
        try:
            integrity = str(connection.execute("PRAGMA integrity_check").fetchone()[0])
            if integrity != "ok":
                raise RuntimeError("SQLite restore integrity check failed.")
            table_count = int(
                connection.execute(
                    "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
                ).fetchone()[0]
            )
        finally:
            connection.close()
    return {"status": "PASS", "tables": table_count}


def _postgres(*arguments: str, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["runuser", "-u", "postgres", "--", *arguments],
        check=True,
        capture_output=capture,
        text=True,
    )


def verify_postgres_restore(*, critical_only: bool = False) -> dict[str, int | str]:
    backup_dir = Path(os.environ.get("WMS_BACKUP_DIR", "/var/backups/sewing-wms")).resolve()
    backup = _latest(backup_dir, "wms_*.dump")
    database_name = f"sewing_restore_test_{int(time.time())}_{os.getpid()}"
    if "test" not in database_name or not database_name.replace("_", "").isalnum():
        raise RuntimeError("Unsafe restore database name.")
    _postgres("createdb", database_name)
    try:
        postgres_account = pwd.getpwnam("postgres")
        with tempfile.TemporaryDirectory(prefix="sewing-postgres-restore-test-") as temporary:
            temporary_path = Path(temporary)
            os.chown(temporary_path, postgres_account.pw_uid, postgres_account.pw_gid)
            temporary_path.chmod(0o700)
            restore_copy = temporary_path / "restore-test.dump"
            shutil.copyfile(backup, restore_copy)
            os.chown(restore_copy, postgres_account.pw_uid, postgres_account.pw_gid)
            restore_copy.chmod(0o400)
            common = (
                "pg_restore", "--exit-on-error", "--no-owner", "--no-acl",
                "--dbname", database_name,
            )
            if critical_only:
                _postgres(*common, "--schema-only", str(restore_copy))
                _postgres(
                    *common,
                    "--data-only", "--disable-triggers",
                    "--table", "schema_migrations",
                    "--table", "wms_zones",
                    "--table", "wms_item_states",
                    "--table", "wms_locations",
                    "--table", "warehouse_stock",
                    str(restore_copy),
                )
            else:
                _postgres(*common, str(restore_copy))
        migrations = int(
            _postgres(
                "psql", "--no-psqlrc", "--tuples-only", "--no-align",
                "--dbname", database_name, "--command", "SELECT COUNT(*) FROM schema_migrations",
                capture=True,
            ).stdout.strip()
        )
        invalid_balances = int(
            _postgres(
                "psql", "--no-psqlrc", "--tuples-only", "--no-align",
                "--dbname", database_name,
                "--command",
                "SELECT COUNT(*) FROM warehouse_stock "
                "WHERE quantity < 0 OR reserved_quantity < 0 OR reserved_quantity > quantity",
                capture=True,
            ).stdout.strip()
        )
        zones = int(
            _postgres(
                "psql", "--no-psqlrc", "--tuples-only", "--no-align",
                "--dbname", database_name, "--command", "SELECT COUNT(*) FROM wms_zones",
                capture=True,
            ).stdout.strip()
        )
        if migrations <= 0 or zones <= 0 or invalid_balances:
            raise RuntimeError("PostgreSQL restore invariant check failed.")
        return {
            "status": "PARTIAL_PASS" if critical_only else "PASS",
            "migrations": migrations,
            "zones": zones,
            "invalid_balances": invalid_balances,
        }
    finally:
        _postgres("dropdb", "--if-exists", database_name)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--critical-only",
        action="store_true",
        help="restore all schemas plus critical WMS reference/balance data when a full second database cannot fit",
    )
    arguments = parser.parse_args()
    sqlite_result = verify_sqlite_restore()
    postgres_result = verify_postgres_restore(critical_only=arguments.critical_only)
    print(f"SQLite restore: {sqlite_result['status']} tables={sqlite_result['tables']}")
    print(
        "PostgreSQL restore: "
        f"{postgres_result['status']} migrations={postgres_result['migrations']} "
        f"zones={postgres_result['zones']} invalid_balances={postgres_result['invalid_balances']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
