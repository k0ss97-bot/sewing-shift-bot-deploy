from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import build_release_manifest
from scripts import build_sbom


class ReleaseManifestTests(unittest.TestCase):
    def _sbom(self, root: Path) -> Path:
        path = root / "release-sbom.cdx.json"
        build_sbom.write_sbom(path, build_sbom.build_sbom())
        return path

    def test_manifest_contains_reproducible_release_identity_without_secrets(self):
        with tempfile.TemporaryDirectory() as temporary:
            sbom = self._sbom(Path(temporary))
            with patch.dict(
                build_release_manifest.os.environ,
                {
                    "MARKETPLACE_PHASE1A_ENABLED": "1",
                    "OZON_API_KEY": "must-not-leak",
                    "WEBAPP_SERVER_SECRET": "must-not-leak-either",
                    "GITHUB_REPOSITORY": "factory/sewing",
                    "GITHUB_TOKEN": "must-not-leak-github-token",
                },
            ):
                payload = build_release_manifest.build_manifest(sbom_path=sbom)

        self.assertEqual(payload["schema_version"], 2)
        self.assertEqual(len(payload["git"]["commit"]), 40)
        self.assertGreaterEqual(len(payload["migrations"]), 12)
        self.assertEqual(payload["migrations"][-1]["filename"], "018_operational_migration_control.sql")
        self.assertTrue(payload["feature_flags"]["marketplace_phase1a"])
        self.assertIn("app.js", payload["frontend"])
        self.assertEqual(payload["sbom"]["format"], "CycloneDX")
        self.assertEqual(payload["sbom"]["components"], 7)
        self.assertEqual(payload["provenance"], {"repository": "factory/sewing"})
        self.assertEqual(len(payload["release_inputs_sha256"]), 64)
        serialized = json.dumps(payload)
        self.assertNotIn("must-not-leak", serialized)
        self.assertNotIn("OZON_API_KEY", serialized)
        self.assertNotIn("GITHUB_TOKEN", serialized)

    def test_manifest_write_is_valid_json_and_keeps_test_gate(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            report = root / "tests.json"
            report.write_text(
                json.dumps({"discovered": 10, "passed": 10, "failed": 0, "secret": "no"}),
                encoding="utf-8",
            )
            payload = build_release_manifest.build_manifest(
                sbom_path=self._sbom(root),
                test_report_path=report,
            )
            output = root / "release-manifest.json"
            build_release_manifest.write_manifest(output, payload)
            saved = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(saved["tests"], {"discovered": 10, "passed": 10, "failed": 0})
        self.assertNotIn("secret", saved["tests"])

    def test_manifest_rejects_invalid_or_empty_sbom(self):
        with tempfile.TemporaryDirectory() as temporary:
            sbom = Path(temporary) / "sbom.json"
            sbom.write_text('{"bomFormat":"SPDX","components":[]}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "CycloneDX"):
                build_release_manifest.build_manifest(sbom_path=sbom)


if __name__ == "__main__":
    unittest.main()
