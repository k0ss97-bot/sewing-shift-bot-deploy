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
        primary = [{
            "marketplace": "ozon", "external_supply_id": "OZ-1", "source": "postgres",
            "state": "DATA_FILLING", "canonical_status": "PLANNED", "item_count": 1,
        }]
        supplement = [
            {
                "id": 25, "marketplace": "ozon", "external_supply_id": "OZ-1",
                "source": "projection", "is_actionable": True, "unmatched_count": 0,
            },
            {"marketplace": "wildberries", "external_supply_id": "WB-1", "source": "sqlite"},
        ]

        result = miniapp_server._merge_marketplace_supplies(primary, supplement)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["source"], "postgres")
        self.assertEqual(result[0]["id"], 25)
        self.assertTrue(result[0]["is_actionable"])
        self.assertEqual(result[1]["marketplace"], "wildberries")

    def test_client_payload_separates_working_supply_from_history(self):
        snapshot = {
            "ok": True,
            "supplies": [
                {
                    "id": 25, "marketplace": "ozon", "external_supply_id": "2000062450250",
                    "external_status": "DATA_FILLING", "canonical_status": "PLANNED",
                    "is_actionable": True, "item_count": 3, "total_quantity": 140,
                },
                {
                    "marketplace": "ozon", "external_supply_id": "old-completed",
                    "state": "COMPLETED", "canonical_status": "ACCEPTED", "item_count": 1,
                },
                {
                    "marketplace": "ozon", "external_supply_id": "old-error",
                    "state": "REPORT_REJECTED", "canonical_status": "SYNC_ERROR", "item_count": 0,
                },
            ],
        }

        result = miniapp_server._marketplace_dashboard_client_payload(snapshot)

        self.assertEqual(
            [row["external_supply_id"] for row in result["supplies"]],
            ["2000062450250"],
        )
        self.assertEqual(result["supplies"][0]["id"], 25)
        self.assertTrue(result["supplies"][0]["is_actionable"])
        self.assertEqual(
            {row["external_supply_id"]: row["history_category"] for row in result["supply_history"]},
            {"old-completed": "completed", "old-error": "error"},
        )

    def test_general_dashboard_does_not_send_server_only_sales_cubes(self):
        snapshot = {
            "ok": True,
            "supplies": [{
                "marketplace": "ozon", "external_supply_id": "1", "state": "DATA_FILLING",
                "canonical_status": "PLANNED", "items": [{"sku": "large"}],
            }],
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

    def test_product_cards_keep_ozon_identity_and_fill_only_missing_image_from_wb(self):
        snapshot = {
            "ok": True,
            "products_rows": [{
                "external_product_id": "oz-1", "offer_id": "АРТ-1", "sku": "OZ-1",
                "name": "Название Ozon", "size": "98", "color": "Бежевый",
                "barcode": "460000000001", "image_url": "",
                "production_product_name": "Костюм детский", "production_size": "98",
                "production_color": "Бежевый", "route_configured": True,
            }],
            "wildberries": {"products_rows": [
                {
                    "nm_id": "wb-1", "vendor_code": "АРТ-1", "name": "Название WB",
                    "size": "98", "color": "Бежевый", "barcode": "460000000009",
                    "image_url": "https://cdn.example/wb-1.jpg",
                },
                {
                    "nm_id": "wb-2", "vendor_code": "АРТ-2", "name": "Товар WB",
                    "size": "104", "color": "Синий", "barcode": "460000000002",
                    "image_url": "https://cdn.example/wb-2.jpg",
                },
            ]},
        }

        result = miniapp_server._compact_product_cards(snapshot)

        self.assertTrue(result["ok"])
        self.assertEqual(len(result["products"]), 2)
        first = next(row for row in result["products"] if row["offer_id"] == "АРТ-1")
        self.assertEqual(first["marketplace"], "ozon")
        self.assertEqual(first["name"], "Название Ozon")
        self.assertEqual(first["barcode"], "460000000001")
        self.assertEqual(first["image_url"], "https://cdn.example/wb-1.jpg")
        self.assertEqual(first["image_source"], "wildberries")
        self.assertEqual(result["quality"]["sources"], {"ozon": 1, "wildberries": 2})
        self.assertEqual(result["quality"]["priority"], "ozon")

    def test_product_cards_reject_non_https_images(self):
        result = miniapp_server._compact_product_cards({
            "ok": True,
            "products_rows": [{
                "offer_id": "АРТ-1", "name": "Товар", "size": "98", "color": "Синий",
                "barcode": "460000000001", "image_url": "javascript:alert(1)",
            }],
        })

        self.assertEqual(result["products"][0]["image_url"], "")
        self.assertEqual(result["quality"]["missing"]["image_url"], 1)


if __name__ == "__main__":
    unittest.main()
