"""Private, content-addressed storage for operational binary evidence.

The database stores only an opaque key and checksum.  Files live outside the
SQLite database with owner-only permissions, which keeps backups small and
allows a lifecycle policy to remove expired evidence independently.
"""

from __future__ import annotations

import base64
import hashlib
import os
from pathlib import Path


ALLOWED_NAMESPACES = {"defect-photos", "task-attachments"}
MIME_EXTENSIONS = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "application/pdf": ".pdf",
}


def _storage_root(root_dir: str | os.PathLike[str]) -> Path:
    root = Path(root_dir).resolve() / "private-blobs"
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(root, 0o700)
    return root


def _safe_namespace(namespace: str) -> str:
    value = str(namespace or "").strip().lower()
    if value not in ALLOWED_NAMESPACES:
        raise ValueError("unsupported private blob namespace")
    return value


def store_base64_blob(
    content_base64: str,
    *,
    mime_type: str,
    namespace: str,
    root_dir: str | os.PathLike[str],
    max_bytes: int,
) -> dict:
    """Persist a validated base64 payload atomically and return DB metadata."""

    try:
        content = base64.b64decode(str(content_base64 or ""), validate=True)
    except (TypeError, ValueError) as error:
        raise ValueError("invalid base64 private blob") from error
    if not content or len(content) > int(max_bytes):
        raise ValueError("private blob size is outside the allowed range")

    namespace = _safe_namespace(namespace)
    digest = hashlib.sha256(content).hexdigest()
    extension = MIME_EXTENSIONS.get(str(mime_type or "").lower(), ".bin")
    key = f"{namespace}/{digest[:2]}/{digest}{extension}"
    root = _storage_root(root_dir)
    destination = root / key
    destination.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(destination.parent, 0o700)

    if not destination.exists():
        temporary = destination.with_name(f".{destination.name}.{os.getpid()}.tmp")
        try:
            with temporary.open("xb") as handle:
                os.chmod(temporary, 0o600)
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, destination)
        finally:
            if temporary.exists():
                temporary.unlink()
    os.chmod(destination, 0o600)
    return {"storage_key": key, "sha256": digest, "size_bytes": len(content)}


def read_blob(
    storage_key: str,
    *,
    root_dir: str | os.PathLike[str],
    expected_sha256: str = "",
    max_bytes: int = 12 * 1024 * 1024,
) -> bytes:
    """Read one opaque key without allowing path traversal or oversized data."""

    key = str(storage_key or "").strip()
    if not key or key.startswith("/") or ".." in Path(key).parts:
        raise ValueError("invalid private blob key")
    root = _storage_root(root_dir)
    path = (root / key).resolve()
    if root not in path.parents:
        raise ValueError("private blob key escapes storage root")
    content = path.read_bytes()
    if not content or len(content) > int(max_bytes):
        raise ValueError("private blob size is outside the allowed range")
    digest = hashlib.sha256(content).hexdigest()
    if expected_sha256 and digest != str(expected_sha256).lower():
        raise ValueError("private blob checksum mismatch")
    return content


def delete_blob(storage_key: str, *, root_dir: str | os.PathLike[str]) -> bool:
    key = str(storage_key or "").strip()
    if not key or key.startswith("/") or ".." in Path(key).parts:
        return False
    root = _storage_root(root_dir)
    path = (root / key).resolve()
    if root not in path.parents or not path.is_file():
        return False
    path.unlink()
    return True
