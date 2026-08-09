from __future__ import annotations

import json
from pathlib import Path
import re
import tempfile
import unittest

from scripts import build_sbom


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class SupplyChainTests(unittest.TestCase):
    def test_sbom_is_deterministic_and_lists_every_pinned_requirement(self):
        first = build_sbom.build_sbom()
        second = build_sbom.build_sbom()

        self.assertEqual(first, second)
        self.assertEqual(first["bomFormat"], "CycloneDX")
        self.assertEqual(first["specVersion"], "1.5")
        self.assertEqual(len(first["components"]), 7)
        purls = {component["purl"] for component in first["components"]}
        self.assertIn("pkg:pypi/aiogram@3.29.0", purls)
        self.assertIn("pkg:pypi/qrcode@8.2", purls)

    def test_sbom_rejects_floating_dependency_versions(self):
        with tempfile.TemporaryDirectory() as temporary:
            requirements = Path(temporary) / "requirements.txt"
            requirements.write_text("safe==1.0\nfloating>=2\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "exact == version"):
                build_sbom.build_sbom(requirements)

    def test_sbom_write_is_atomic_valid_json(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "sbom.cdx.json"
            build_sbom.write_sbom(output, build_sbom.build_sbom())
            saved = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(saved["bomFormat"], "CycloneDX")
            self.assertFalse((output.parent / f".{output.name}.tmp").exists())

    def test_every_github_action_is_pinned_to_an_immutable_commit(self):
        workflow = (PROJECT_ROOT / ".github" / "workflows" / "quality.yml").read_text(
            encoding="utf-8"
        )
        references = re.findall(r"^\s*uses:\s*([^\s#]+)", workflow, flags=re.MULTILINE)
        self.assertGreaterEqual(len(references), 4)
        for reference in references:
            self.assertRegex(reference, r"^[^@]+@[0-9a-f]{40}$")
        self.assertIn("actions/attest@508db95dd578ae2727ebd6217d5ba78e4fbda05d", workflow)
        self.assertIn("sbom-path:", workflow)
        self.assertIn("vars.ENABLE_GITHUB_ATTESTATIONS == '1'", workflow)


if __name__ == "__main__":
    unittest.main()
