from __future__ import annotations

import os
from pathlib import Path
import unittest
from unittest.mock import patch

from scripts import run_unittests_isolated as runner


class IsolatedTestRunnerTests(unittest.TestCase):
    def test_discovery_includes_root_and_namespace_test_files(self):
        relative_paths = {
            path.relative_to(runner.PROJECT_ROOT) for path in runner._test_files()
        }
        self.assertIn(Path("test_bot_core.py"), relative_paths)
        self.assertIn(Path("tests/test_wms.py"), relative_paths)
        declared = sum(runner._declared_test_count(path) for path in runner._test_files())
        self.assertGreater(declared, 230)

    def test_production_named_postgres_database_is_rejected(self):
        with patch.dict(
            os.environ,
            {"TEST_WMS_DATABASE_URL": "postgresql://db.example/sewing_wms"},
            clear=False,
        ):
            with self.assertRaisesRegex(RuntimeError, "database name contains 'test'"):
                runner._safe_test_wms_url()

    def test_production_wms_environment_is_never_inherited(self):
        environment = {
            "WMS_DATABASE_URL": "postgresql://db.example/sewing_wms",
        }
        with patch.dict(os.environ, environment, clear=True):
            self.assertEqual(runner._safe_test_wms_url(), runner.DEFAULT_TEST_WMS_URL)


if __name__ == "__main__":
    unittest.main()
