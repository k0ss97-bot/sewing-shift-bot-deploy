from __future__ import annotations

import tempfile
import unittest
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from scripts import replicate_backups_offsite as offsite


class OffsiteBackupTests(unittest.TestCase):
    def test_replication_requires_mount_on_a_separate_filesystem(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            sqlite = root / "sqlite"
            wms = root / "wms"
            target = root / "target"
            sqlite.mkdir()
            wms.mkdir()
            target.mkdir()
            (sqlite / "webapp_20260809T090000Z.db").write_bytes(b"sqlite")
            (wms / "wms_20260809T090000Z.dump").write_bytes(b"wms")

            with patch("scripts.replicate_backups_offsite.os.path.ismount", return_value=False):
                with self.assertRaisesRegex(RuntimeError, "mount point"):
                    offsite.replicate(sqlite, wms, target)

            with patch("scripts.replicate_backups_offsite.os.path.ismount", return_value=True):
                with self.assertRaisesRegex(RuntimeError, "shares a filesystem"):
                    offsite.replicate(sqlite, wms, target)

    def test_recent_encryption_attestation_is_mandatory(self):
        now = datetime(2026, 8, 9, 9, 0, tzinfo=timezone.utc)
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            with self.assertRaisesRegex(RuntimeError, "missing"):
                offsite.encryption_attestation(root, now=now)
            marker = root / ".encryption-at-rest.json"
            marker.write_text(json.dumps({
                "encrypted": True,
                "provider": "luks2",
                "evidence_id": "change-42",
                "verified_at": (now - timedelta(days=91)).isoformat(),
            }), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "stale"):
                offsite.encryption_attestation(root, now=now)
            marker.write_text(json.dumps({
                "encrypted": True,
                "provider": "luks2",
                "evidence_id": "change-42",
                "verified_at": now.isoformat(),
            }), encoding="utf-8")
            result = offsite.encryption_attestation(root, now=now)
            self.assertTrue(result["encryption_at_rest"])
            self.assertEqual(result["encryption_provider"], "luks2")

    def test_copy_is_atomic_and_checksum_verified(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "wms_20260809T090000Z.dump"
            destination = root / "remote"
            source.write_bytes(b"verified-wms")

            result = offsite.copy_verified(source, destination)

            self.assertEqual((destination / source.name).read_bytes(), b"verified-wms")
            self.assertEqual(result["artifact_size"], len(b"verified-wms"))
            self.assertRegex(str(result["artifact_sha256"]), r"^[0-9a-f]{64}$")
            self.assertFalse((destination / f".{source.name}.tmp").exists())


if __name__ == "__main__":
    unittest.main()
