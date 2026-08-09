#!/usr/bin/env python3
"""Create, verify and publish health metadata for a PostgreSQL WMS backup."""

from __future__ import annotations

import hashlib
import json
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


def backup_status_path() -> Path:
    value = os.environ.get(
        "WMS_BACKUP_STATUS_PATH",
        "/var/lib/sewing-web/monitor/wms-backup-status.json",
    )
    path = Path(value).expanduser()
    if not path.is_absolute():
        raise RuntimeError("WMS_BACKUP_STATUS_PATH must be an absolute path.")
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


def migration_manifest(url: str) -> dict[str, object]:
    """Return the schema identity saved alongside the verified artifact."""
    import psycopg2

    connection = psycopg2.connect(url)
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT filename FROM schema_migrations ORDER BY filename")
            migrations = [str(row[0]) for row in cursor.fetchall()]
        connection.rollback()
    finally:
        connection.close()
    if not migrations:
        raise RuntimeError("WMS schema_migrations is empty.")
    return {
        "migration_count": len(migrations),
        "latest_migration": migrations[-1],
        "migration_manifest_sha256": hashlib.sha256(
            "\n".join(migrations).encode("utf-8")
        ).hexdigest(),
    }


def artifact_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def success_status(
    destination: Path,
    manifest: dict[str, object],
    *,
    now: datetime | None = None,
) -> dict[str, object]:
    timestamp = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    return {
        "ok": True,
        "created_at": timestamp.isoformat().replace("+00:00", "Z"),
        "artifact_name": destination.name,
        "artifact_size": destination.stat().st_size,
        "artifact_sha256": artifact_sha256(destination),
        "verified": True,
        "verified_by": "pg_restore --list",
        **manifest,
    }


def write_status(path: Path, payload: dict[str, object]) -> None:
    """Publish non-secret status atomically for the unprivileged monitor."""
    path.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.chmod(0o644)
    temporary.replace(path)


def main() -> int:
    status_path = backup_status_path()
    try:
        url = database_url()
        destination = create_backup(url, backup_dir())
        write_status(status_path, success_status(destination, migration_manifest(url)))
    except Exception as error:
        try:
            write_status(
                status_path,
                {
                    "ok": False,
                    "failed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                    "error_type": type(error).__name__,
                },
            )
        except Exception:
            pass
        print(f"WMS backup failed: {error}", file=sys.stderr)
        return 1
    print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
