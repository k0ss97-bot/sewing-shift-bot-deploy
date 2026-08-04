import unittest
from unittest.mock import patch

import marketplace_sync_cli


class MarketplaceSyncCliTests(unittest.TestCase):
    def test_phase1a_also_refreshes_compatibility_model_when_due(self):
        phase_result = {"ok": True, "status": "success", "datasets": ["catalog"]}
        legacy_result = {"ok": True, "products": 10, "orders": 2}
        with patch.object(marketplace_sync_cli, "phase1a_enabled", return_value=True), \
             patch.object(marketplace_sync_cli, "run_phase1a_sync", return_value=phase_result), \
             patch.object(marketplace_sync_cli, "_legacy_sync_due", return_value=True), \
             patch.object(marketplace_sync_cli, "sync_ozon", return_value=legacy_result) as legacy_sync:
            result = marketplace_sync_cli._ozon_sync()

        self.assertTrue(result["ok"], result)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["phase1a"], phase_result)
        self.assertEqual(result["compatibility"], legacy_result)
        legacy_sync.assert_called_once_with()

    def test_phase1a_skips_fresh_compatibility_model(self):
        with patch.object(marketplace_sync_cli, "phase1a_enabled", return_value=True), \
             patch.object(
                 marketplace_sync_cli,
                 "run_phase1a_sync",
                 return_value={"ok": True, "status": "not_due"},
             ), \
             patch.object(marketplace_sync_cli, "_legacy_sync_due", return_value=False), \
             patch.object(marketplace_sync_cli, "sync_ozon") as legacy_sync:
            result = marketplace_sync_cli._ozon_sync()

        self.assertTrue(result["ok"], result)
        self.assertEqual(result["compatibility"]["status"], "not_due")
        legacy_sync.assert_not_called()

    def test_phase1a_failure_keeps_successful_compatibility_refresh_visible(self):
        with patch.object(marketplace_sync_cli, "phase1a_enabled", return_value=True), \
             patch.object(
                 marketplace_sync_cli,
                 "run_phase1a_sync",
                 return_value={"ok": False, "status": "failed", "code": "provider_error"},
             ), \
             patch.object(marketplace_sync_cli, "_legacy_sync_due", return_value=True), \
             patch.object(
                 marketplace_sync_cli,
                 "sync_ozon",
                 return_value={"ok": True, "products": 10, "orders": 2},
             ):
            result = marketplace_sync_cli._ozon_sync()

        self.assertFalse(result["ok"])
        self.assertEqual(result["status"], "partial")
        self.assertEqual(marketplace_sync_cli.cli_exit_code(result), 0)


if __name__ == "__main__":
    unittest.main()
