import os
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

import marketplaces


class FakeOzonClient:
    def products(self):
        return [{"id": "100", "offer_id": "CARD-122-BLUE", "sku": "9001", "name": "Кардиган", "size": "122", "color": "Синий", "barcode": "460000000001"}]

    def prices(self):
        return [{"product_id": "100", "offer_id": "CARD-122-BLUE", "price": {"price": "2490", "old_price": "2990", "currency_code": "RUB"}}]

    def stocks(self):
        return [{"product_id": "100", "offer_id": "CARD-122-BLUE", "stocks": [{"warehouse_name": "FBO Москва", "present": 8, "reserved": 2}]}]

    def fbs_postings(self):
        return [{"order_id": "700", "posting_number": "700-1", "status": "awaiting_packaging", "shipment_date": "2026-07-30", "products": [{"product_id": "100", "offer_id": "CARD-122-BLUE", "sku": "9001", "name": "Кардиган", "quantity": 2}]}]


class MarketplaceTests(unittest.TestCase):
    def test_product_group_uses_article_and_name_without_variant_split(self):
        self.assertEqual(
            marketplaces.product_group_for("Брюки со стрелками детские", "BR-122-СИНИЕ"),
            ("trousers-arrows", "Брюки со стрелками"),
        )
        self.assertEqual(
            marketplaces.product_group_for("Кардиган подростковый", "CARD-146-BLACK"),
            ("cardigans-teens", "Кардиганы подростковые"),
        )
        self.assertEqual(
            marketplaces.product_group_for("Кардиган детский", "CARD-122-BLUE"),
            ("cardigans-children", "Кардиганы детские"),
        )

    def test_dashboard_without_credentials_does_not_call_network(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "bot.db")
            with patch.dict(os.environ, {"OZON_CLIENT_ID": "", "OZON_API_KEY": ""}, clear=False):
                with patch.object(marketplaces, "get_db_connection", side_effect=lambda: sqlite3.connect(path)):
                    payload = marketplaces.dashboard()
                    result = marketplaces.sync_ozon()
            self.assertFalse(payload["configured"])
            self.assertTrue(payload["read_only"])
            self.assertEqual({item["marketplace"] for item in payload["connectors"]}, {"ozon", "wildberries"})
            self.assertEqual(result["code"], "not_configured")

    def test_read_only_snapshot_upserts_products_prices_stock_and_orders(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "bot.db")
            def connection():
                conn = sqlite3.connect(path)
                conn.execute("PRAGMA foreign_keys = ON")
                return conn

            with patch.dict(os.environ, {"OZON_CLIENT_ID": "client", "OZON_API_KEY": "secret"}, clear=False):
                with patch.object(marketplaces, "get_db_connection", side_effect=connection):
                    with patch.object(marketplaces, "OzonClient", return_value=FakeOzonClient()):
                        result = marketplaces.sync_ozon()
                    payload = marketplaces.dashboard()
            self.assertTrue(result["ok"], result)
            self.assertEqual(result["products"], 1)
            self.assertEqual(result["stocks"], 1)
            self.assertEqual(result["orders"], 1)
            self.assertEqual(payload["summary"]["products"], 1)
            self.assertEqual(payload["products_rows"][0]["available"], 6)
            self.assertEqual(payload["product_groups"][0]["name"], "Кардиганы детские")
            self.assertEqual(payload["orders_rows"][0]["posting_number"], "700-1")
            with sqlite3.connect(path) as conn:
                item_count = conn.execute("SELECT COUNT(*) FROM marketplace_order_items").fetchone()[0]
            self.assertEqual(item_count, 1)


if __name__ == "__main__":
    unittest.main()
