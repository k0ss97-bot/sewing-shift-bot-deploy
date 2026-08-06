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

    def test_general_dashboard_does_not_send_server_only_sales_cubes(self):
        snapshot = {
            "ok": True,
            "supplies": [{"marketplace": "ozon", "external_supply_id": "1", "items": [{"sku": "large"}]}],
            "products_rows": [{"id": "1", "name": "Товар", "attributes_json": [{"large": True}]}],
            "analytics": {"sales_daily": [1], "sales_by_product_daily": [2], "sales_by_region_product_daily": [5]},
            "wildberries": {"analytics": {"sales_daily": [3], "sales_by_warehouse_daily": [4]}},
        }

        result = miniapp_server._marketplace_dashboard_client_payload(snapshot)

        self.assertEqual(result["analytics"]["sales_daily"], [1])
        self.assertNotIn("sales_by_product_daily", result["analytics"])
        self.assertNotIn("sales_by_region_product_daily", result["analytics"])
        self.assertEqual(result["wildberries"]["analytics"]["sales_daily"], [3])
        self.assertNotIn("sales_by_warehouse_daily", result["wildberries"]["analytics"])
        self.assertIn("sales_by_product_daily", snapshot["analytics"])
        self.assertIn("sales_by_region_product_daily", snapshot["analytics"])
        self.assertNotIn("items", result["supplies"][0])
        self.assertEqual(result["products_rows"], [{"id": "1", "name": "Товар"}])


if __name__ == "__main__":
    unittest.main()
