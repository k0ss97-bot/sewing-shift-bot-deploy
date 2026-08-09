from __future__ import annotations

import base64
import tempfile
from pathlib import Path
import unittest

from private_blobs import read_blob, store_base64_blob


class PrivateBlobStorageTests(unittest.TestCase):
    def test_content_addressed_blob_is_private_and_checksum_verified(self):
        with tempfile.TemporaryDirectory() as directory:
            stored = store_base64_blob(
                base64.b64encode(b"private-evidence").decode("ascii"),
                mime_type="image/png",
                namespace="defect-photos",
                root_dir=directory,
                max_bytes=1024,
            )
            path = Path(directory) / "private-blobs" / stored["storage_key"]
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            self.assertEqual(
                read_blob(
                    stored["storage_key"],
                    root_dir=directory,
                    expected_sha256=stored["sha256"],
                    max_bytes=1024,
                ),
                b"private-evidence",
            )
            path.write_bytes(b"tampered")
            with self.assertRaisesRegex(ValueError, "checksum"):
                read_blob(
                    stored["storage_key"],
                    root_dir=directory,
                    expected_sha256=stored["sha256"],
                    max_bytes=1024,
                )

    def test_path_traversal_and_unknown_namespace_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "key"):
                read_blob("../secret", root_dir=directory)
            with self.assertRaisesRegex(ValueError, "namespace"):
                store_base64_blob(
                    base64.b64encode(b"x").decode("ascii"),
                    mime_type="image/png",
                    namespace="arbitrary",
                    root_dir=directory,
                    max_bytes=10,
                )


if __name__ == "__main__":
    unittest.main()
