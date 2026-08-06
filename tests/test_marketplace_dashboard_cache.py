import unittest
from unittest.mock import patch

import miniapp_server


class MarketplaceDashboardCacheTests(unittest.TestCase):
    def setUp(self):
        miniapp_server._reset_marketplace_dashboard_cache_for_tests()

    def tearDown(self):
        miniapp_server._reset_marketplace_dashboard_cache_for_tests()

    def test_reuses_heavy_dashboard_inside_ttl(self):
        snapshot = {"ok": True, "summary": {"products": 791}}
        with patch.object(miniapp_server, "_build_marketplace_dashboard_payload", return_value=snapshot) as build:
            first = miniapp_server._cached_marketplace_dashboard_payload()
            second = miniapp_server._cached_marketplace_dashboard_payload()

        self.assertIs(first, snapshot)
        self.assertIs(second, snapshot)
        build.assert_called_once_with()

    def test_expiration_keeps_last_snapshot_available(self):
        snapshot = {"ok": True, "summary": {"products": 791}}
        miniapp_server._store_marketplace_dashboard_cache(snapshot)
        miniapp_server._expire_marketplace_dashboard_cache()

        with patch.object(miniapp_server, "_start_marketplace_dashboard_cache_refresh", return_value=True) as refresh:
            result = miniapp_server._cached_marketplace_dashboard_payload()

        self.assertIs(result, snapshot)
        refresh.assert_called_once_with()

    def test_supply_merge_keeps_postgres_ozon_and_independent_wb_rows(self):
        primary = [{"marketplace": "ozon", "external_supply_id": "OZ-1", "source": "postgres"}]
        supplement = [
            {"marketplace": "ozon", "external_supply_id": "OZ-1", "source": "projection"},
            {"marketplace": "wildberries", "external_supply_id": "WB-1", "source": "sqlite"},
        ]

        result = miniapp_server._merge_marketplace_supplies(primary, supplement)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["source"], "postgres")
        self.assertEqual(result[1]["marketplace"], "wildberries")


if __name__ == "__main__":
    unittest.main()
