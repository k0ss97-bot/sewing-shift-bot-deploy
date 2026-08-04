import unittest
from unittest.mock import patch

import marketplace_sync_cli


class MarketplaceSyncCliTests(unittest.TestCase):
    def test_phase1a_disables_legacy_compatibility_refresh(self):
        phase_result = {"ok": True, "status": "success", "datasets": ["catalog"]}
        with patch.object(marketplace_sync_cli, "phase1a_enabled", return_value=True), \
             patch.object(marketplace_sync_cli, "run_phase1a_sync", return_value=phase_result), \
             patch.object(marketplace_sync_cli, "sync_ozon") as legacy_sync:
            result = marketplace_sync_cli._ozon_sync()

        self.assertTrue(result["ok"], result)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["phase1a"], phase_result)
        self.assertEqual(
            result["compatibility"],
            {"enabled": False, "reason": "postgresql_authoritative"},
        )
        legacy_sync.assert_not_called()

    def test_phase1a_not_due_still_keeps_legacy_disabled(self):
        with patch.object(marketplace_sync_cli, "phase1a_enabled", return_value=True), \
             patch.object(
                 marketplace_sync_cli,
                 "run_phase1a_sync",
                 return_value={"ok": True, "status": "not_due"},
             ), \
             patch.object(marketplace_sync_cli, "sync_ozon") as legacy_sync:
            result = marketplace_sync_cli._ozon_sync()

        self.assertTrue(result["ok"], result)
        self.assertFalse(result["compatibility"]["enabled"])
        legacy_sync.assert_not_called()

    def test_phase1a_failure_is_not_masked_by_legacy_sqlite(self):
        with patch.object(marketplace_sync_cli, "phase1a_enabled", return_value=True), \
             patch.object(
                 marketplace_sync_cli,
                 "run_phase1a_sync",
                 return_value={"ok": False, "status": "failed", "code": "provider_error"},
             ), \
             patch.object(marketplace_sync_cli, "sync_ozon") as legacy_sync:
            result = marketplace_sync_cli._ozon_sync()

        self.assertFalse(result["ok"])
        self.assertEqual(result["status"], "failed")
        self.assertEqual(marketplace_sync_cli.cli_exit_code(result), 1)
        legacy_sync.assert_not_called()


if __name__ == "__main__":
    unittest.main()
