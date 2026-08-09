#!/usr/bin/env python3
"""Copy verified SQLite and WMS artifacts to a separate mounted filesystem.

The destination must already be a mount point and must not share a filesystem
device with either source.  This prevents a typo from presenting another local
directory on the production disk as disaster-recovery storage.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


def absolute_path(environment_name: str, default: str) -> Path:
    path = Path(os.getenv(environment_name, default)).expanduser()
    if not path.is_absolute():
        raise RuntimeError(f"{environment_name} must be an absolute path.")
    return path


def latest_artifact(directory: Path, pattern: str) -> Path:
    artifacts = sorted(directory.glob(pattern), key=lambda path: path.stat().st_mtime)
    if not artifacts:
        raise RuntimeError(f"No backup artifact matches {pattern}.")
    artifact = artifacts[-1]
    if artifact.is_symlink() or not artifact.is_file() or artifact.stat().st_size <= 0:
        raise RuntimeError("Latest backup artifact is not a regular non-empty file.")
    return artifact


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def copy_verified(source: Path, target_directory: Path) -> dict[str, object]:
    target_directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    destination = target_directory / source.name
    temporary = target_directory / f".{source.name}.tmp"
    source_checksum = file_sha256(source)
    with source.open("rb") as source_stream, temporary.open("wb") as target_stream:
        shutil.copyfileobj(source_stream, target_stream, length=1024 * 1024)
        target_stream.flush()
        os.fsync(target_stream.fileno())
    temporary.chmod(0o600)
    if file_sha256(temporary) != source_checksum:
        temporary.unlink(missing_ok=True)
        raise RuntimeError("Off-site backup checksum mismatch.")
    temporary.replace(destination)
    return {
        "artifact_name": destination.name,
        "artifact_size": destination.stat().st_size,
        "artifact_sha256": source_checksum,
    }


def prune(directory: Path, pattern: str, keep: int = 30) -> None:
    artifacts = sorted(directory.glob(pattern), reverse=True)
    for expired in artifacts[max(3, min(int(keep), 365)):]:
        expired.unlink()


def write_status(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")
    temporary.chmod(0o644)
    temporary.replace(path)


def encryption_attestation(offsite_root: Path, *, now: datetime | None = None) -> dict[str, object]:
    """Load recent operator evidence that the independent target is encrypted."""

    marker_name = os.getenv("BACKUP_OFFSITE_ENCRYPTION_MARKER", ".encryption-at-rest.json")
    marker_candidate = offsite_root / marker_name
    marker = marker_candidate.resolve()
    if marker_candidate.is_symlink() or offsite_root.resolve() not in marker.parents or not marker.is_file():
        raise RuntimeError("Off-site encryption attestation is missing.")
    payload = json.loads(marker.read_text(encoding="utf-8"))
    provider = str(payload.get("provider") or "").strip()
    evidence_id = str(payload.get("evidence_id") or "").strip()
    verified_at = datetime.fromisoformat(str(payload.get("verified_at") or "").replace("Z", "+00:00"))
    if verified_at.tzinfo is None:
        verified_at = verified_at.replace(tzinfo=timezone.utc)
    observed_at = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    age = observed_at - verified_at.astimezone(timezone.utc)
    if payload.get("encrypted") is not True or not provider or not evidence_id:
        raise RuntimeError("Off-site encryption attestation is incomplete.")
    if age < -timedelta(minutes=5) or age > timedelta(days=90):
        raise RuntimeError("Off-site encryption attestation is stale.")
    return {
        "encryption_at_rest": True,
        "encryption_provider": provider[:80],
        "encryption_evidence_id": evidence_id[:120],
        "encryption_verified_at": verified_at.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def replicate(
    sqlite_source_dir: Path,
    wms_source_dir: Path,
    offsite_root: Path,
    *,
    encryption: dict[str, object] | None = None,
) -> dict[str, object]:
    if not offsite_root.is_dir() or not os.path.ismount(offsite_root):
        raise RuntimeError("BACKUP_OFFSITE_DIR must be an existing mount point.")
    target_device = offsite_root.stat().st_dev
    for source_directory in (sqlite_source_dir, wms_source_dir):
        if source_directory.stat().st_dev == target_device:
            raise RuntimeError("Off-site target shares a filesystem with a backup source.")
    if not encryption or encryption.get("encryption_at_rest") is not True:
        raise RuntimeError("Off-site target encryption is not attested.")

    sqlite_source = latest_artifact(sqlite_source_dir, "webapp_*.db")
    wms_source = latest_artifact(wms_source_dir, "wms_*.dump")
    sqlite_result = copy_verified(sqlite_source, offsite_root / "sqlite")
    wms_result = copy_verified(wms_source, offsite_root / "wms")
    prune(offsite_root / "sqlite", "webapp_*.db")
    prune(offsite_root / "wms", "wms_*.dump")
    return {
        "ok": True,
        "copied_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "target_is_mount": True,
        "target_device_separate": True,
        **encryption,
        "sqlite": sqlite_result,
        "wms": wms_result,
    }


def main() -> int:
    status_path = absolute_path(
        "BACKUP_OFFSITE_STATUS_PATH",
        "/var/lib/sewing-web/monitor/offsite-backup-status.json",
    )
    try:
        offsite_root = absolute_path("BACKUP_OFFSITE_DIR", "/mnt/sewing-offsite")
        result = replicate(
            absolute_path("SQLITE_BACKUP_DIR", "/var/lib/sewing-web/backups"),
            absolute_path("WMS_BACKUP_DIR", "/var/backups/sewing-wms"),
            offsite_root,
            encryption=encryption_attestation(offsite_root),
        )
        write_status(status_path, result)
    except Exception as error:
        try:
            write_status(status_path, {
                "ok": False,
                "failed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "error_type": type(error).__name__,
            })
        except Exception:
            pass
        print(f"Off-site backup failed: {error}", file=sys.stderr)
        return 1
    print("Off-site backup verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
