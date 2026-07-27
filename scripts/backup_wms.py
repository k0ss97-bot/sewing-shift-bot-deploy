#!/usr/bin/env python3
"""Create and verify a PostgreSQL WMS backup with bounded retention."""

from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def database_url() -> str:
    value = (os.environ.get("WMS_DATABASE_URL") or "").strip()
    if not value:
        raise RuntimeError("WMS_DATABASE_URL is not configured.")
    return value


def backup_dir() -> Path:
    value = os.environ.get("WMS_BACKUP_DIR", "/var/backups/sewing-wms")
    path = Path(value).expanduser()
    if not path.is_absolute():
        raise RuntimeError("WMS_BACKUP_DIR must be an absolute path.")
    return path


def retention_count() -> int:
    try:
        value = int(os.environ.get("WMS_BACKUP_RETENTION", "14"))
    except ValueError as error:
        raise RuntimeError("WMS_BACKUP_RETENTION must be an integer.") from error
    return max(3, min(value, 90))


def create_backup(url: str, destination_dir: Path) -> Path:
    destination_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    destination_dir.chmod(0o700)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    destination = destination_dir / f"wms_{timestamp}.dump"
    temporary = destination.with_suffix(".tmp")

    subprocess.run(
        [
            "pg_dump",
            "--format=custom",
            "--no-owner",
            "--no-acl",
            f"--file={temporary}",
            url,
        ],
        check=True,
    )
    subprocess.run(
        ["pg_restore", "--list", str(temporary)],
        check=True,
        stdout=subprocess.DEVNULL,
    )
    temporary.chmod(0o600)
    temporary.replace(destination)

    backups = sorted(destination_dir.glob("wms_*.dump"), reverse=True)
    for expired in backups[retention_count():]:
        expired.unlink()
    return destination


def main() -> int:
    try:
        destination = create_backup(database_url(), backup_dir())
    except Exception as error:
        print(f"WMS backup failed: {error}", file=sys.stderr)
        return 1
    print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
