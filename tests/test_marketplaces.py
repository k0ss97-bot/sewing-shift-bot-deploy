import os
import sqlite3
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import marketplaces


class FakeOzonClient:
    def products(self):
        return [{"id": "100", "offer_id": "CARD-122-BLUE", "sku": "9001", "name": "Кардиган", "size": "122", "color": "Синий", "barcode": "460000000001"}]

    def product_details(self, _product_ids):
        return []

    def product_attributes(self):
        return []

    def prices(self):
        return [{"product_id": "100", "offer_id": "CARD-122-BLUE", "price": {"price": "2490", "old_price": "2990", "currency_code": "RUB"}}]

    def stocks(self):
        return [{"product_id": "100", "offer_id": "CARD-122-BLUE", "stocks": [{"type": "FBO", "warehouse_name": "FBO Москва", "present": 8, "reserved": 2}]}]

    def warehouse_stocks(self):
        return []

    def fbs_postings(self):
        return [{"order_id": "700", "posting_number": "700-1", "status": "awaiting_packaging", "shipment_date": "2026-07-30", "products": [{"product_id": "100", "offer_id": "CARD-122-BLUE", "sku": "9001", "name": "Кардиган", "quantity": 2}]}]


class MarketplaceTests(unittest.TestCase):
    def test_only_actionable_ozon_supplies_are_working_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "bot.db")

            def connection(**_kwargs):
                conn = sqlite3.connect(path)
                conn.row_factory = sqlite3.Row
                conn.execute("PRAGMA foreign_keys = ON")
                return conn

            with patch.dict(os.environ, {"OZON_CLIENT_ID": "client"}, clear=False):
                with patch.object(marketplaces, "get_db_connection", side_effect=connection):
                    with connection() as conn:
                        marketplaces.ensure_schema(conn)
                        account_id = marketplaces._account(conn, "ozon", "Основной Ozon", "client")
                        marketplaces.upsert_marketplace_supply(
                            conn,
                            {"id": "ACTIVE", "status": "DATA_FILLING", "items": [{"sku": "1", "quantity": 2}]},
                            marketplace="ozon",
                            account_id=account_id,
                        )
                        marketplaces.upsert_marketplace_supply(
                            conn,
                            {"id": "OLD", "status": "COMPLETED", "items": [{"sku": "2", "quantity": 3}]},
                            marketplace="ozon",
                            account_id=account_id,
                        )
                        conn.commit()
                        rows = marketplaces._supply_rows(conn, marketplace="ozon", active_only=True)
                        old_id = conn.execute("SELECT id FROM marketplace_supplies WHERE external_supply_id='OLD'").fetchone()[0]

                    rejected = marketplaces.create_internal_shipment_for_supply(old_id)

            self.assertEqual([row["external_supply_id"] for row in rows], ["ACTIVE"])
            self.assertTrue(rows[0]["is_actionable"])
            self.assertEqual(rejected["code"], "supply_not_actionable")

    def test_postgres_supply_projection_preserves_internal_shipment_link(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "bot.db")

            def connection(**_kwargs):
                conn = sqlite3.connect(path)
                conn.execute("PRAGMA foreign_keys = ON")
                return conn

            rows = [{
                "id": "900",
                "preorder_id": "ORDER-700",
                "status": "DATA_FILLING",
                "type": "FBO",
                "destination": {"type": "storage_warehouse", "id": "10", "name": "Тверь"},
                "items": [{
                    "product_id": "100", "offer_id": "CARD-122-BLUE", "sku": "9001",
                    "barcode": "460000000001", "name": "Кардиган", "quantity": 4,
                }],
            }]
            with patch.dict(os.environ, {"OZON_CLIENT_ID": "client"}, clear=False):
                with patch.object(marketplaces, "get_db_connection", side_effect=connection):
                    with connection() as conn:
                        marketplaces.ensure_schema(conn)
                        account_id = marketplaces._account(conn, "ozon", "Основной Ozon", "client")
                        conn.execute(
                            """INSERT INTO marketplace_products
                               (account_id,external_product_id,offer_id,sku,barcode,name,payload_json,updated_at)
                               VALUES (?,?,?,?,?,?,?,?)""",
                            (account_id, "100", "CARD-122-BLUE", "9001", "460000000001", "Кардиган", "{}", "2026-08-04"),
                        )
                        conn.commit()
                    projected = marketplaces.project_ozon_supplies_from_postgres(rows)
                    with connection() as conn:
                        supply_id = conn.execute("SELECT id FROM marketplace_supplies WHERE external_supply_id='900'").fetchone()[0]
                    shipment = marketplaces.create_internal_shipment_for_supply(supply_id)
                    projected_again = marketplaces.project_ozon_supplies_from_postgres(rows)
                    detail = marketplaces.marketplace_supply_detail(supply_id)
                    shipment_tasks = marketplaces.warehouse_shipment_tasks()

            self.assertEqual(projected["projected"], 1)
            self.assertTrue(shipment["created"])
            self.assertEqual(projected_again["projected"], 1)
            self.assertEqual(detail["warehouse_shipment_id"], shipment["shipment"]["id"])
            self.assertEqual(detail["items"][0]["mapped_status"], "matched")
            self.assertEqual(shipment_tasks[0]["number"], shipment["shipment"]["number"])
            self.assertTrue(shipment_tasks[0]["created_at"])

    def test_supply_uses_real_warehouse_number_and_keeps_shipped_status_during_sync(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "bot.db")

            def connection(**_kwargs):
                conn = sqlite3.connect(path)
                conn.row_factory = sqlite3.Row
                conn.execute("PRAGMA foreign_keys = ON")
                return conn

            payload = {
                "id": "SUPPLY-1", "status": "DATA_FILLING",
                "items": [{"product_id": "10", "offer_id": "CARD-122", "quantity": 2}],
            }
            with patch.object(marketplaces, "get_db_connection", side_effect=connection):
                with connection() as conn:
                    marketplaces.ensure_schema(conn)
                    account_id = marketplaces._account(conn, "ozon", "Основной Ozon", "client")
                    conn.execute(
                        """INSERT INTO marketplace_products
                           (account_id,external_product_id,offer_id,sku,barcode,name,payload_json,updated_at)
                           VALUES (?,?,?,?,?,?,?,?)""",
                        (account_id, "10", "CARD-122", "", "", "Кардиган", "{}", "2026-08-04"),
                    )
                    marketplaces.upsert_marketplace_supply(conn, payload, marketplace="ozon", account_id=account_id)
                    supply_id = conn.execute("SELECT id FROM marketplace_supplies WHERE external_supply_id='SUPPLY-1'").fetchone()[0]
                    conn.commit()

                created = marketplaces.create_internal_shipment_for_supply(supply_id)
                with connection() as conn:
                    shipment_id = created["shipment"]["id"]
                    conn.execute("UPDATE warehouse_shipments SET status='SHIPPED' WHERE id=?", (shipment_id,))
                    conn.commit()
                    marketplaces.upsert_marketplace_supply(conn, payload, marketplace="ozon", account_id=account_id)
                    rows = marketplaces._supply_rows(conn, marketplace="ozon")

            self.assertEqual(rows[0]["warehouse_shipment_number"], created["shipment"]["number"])
            self.assertEqual(rows[0]["canonical_status"], "SHIPPED_FROM_PRODUCTION")

    def test_shipment_resolves_physical_product_by_article_before_stale_product_id(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "bot.db")

            def connection(**_kwargs):
                conn = sqlite3.connect(path)
                conn.row_factory = sqlite3.Row
                return conn

            with patch.object(marketplaces, "get_db_connection", side_effect=connection):
                with connection() as conn:
                    marketplaces.ensure_schema(conn)
                    account_id = marketplaces._account(conn, "ozon", "Основной Ozon", "client")
                    now = "2026-08-04T00:00:00"
                    first = conn.execute(
                        """INSERT INTO marketplace_products
                           (account_id,external_product_id,offer_id,sku,barcode,name,payload_json,updated_at)
                           VALUES (?,?,?,?,?,?,?,?)""",
                        (account_id, "old", "OLD-ARTICLE", "", "", "Старый", "{}", now),
                    ).lastrowid
                    correct = conn.execute(
                        """INSERT INTO marketplace_products
                           (account_id,external_product_id,offer_id,sku,barcode,name,payload_json,updated_at)
                           VALUES (?,?,?,?,?,?,?,?)""",
                        (account_id, "good", "КДШВН-1/98", "2383102410", "", "Костюм", "{}", now),
                    ).lastrowid
                    for product_id, name in ((first, "Неверный"), (correct, "Костюм трикотажный детский")):
                        conn.execute(
                            """INSERT INTO marketplace_production_links
                               (marketplace_product_id,production_product_name,production_size,production_color,status,source,updated_at)
                               VALUES (?,?,?,?,?,?,?)""",
                            (product_id, name, "98", "бежевый", "linked", "test", now),
                        )
                    shipment_id = conn.execute(
                        """INSERT INTO warehouse_shipments
                           (number,status,created_at,updated_at) VALUES (?,?,?,?)""",
                        ("MP-TEST", "WAITING_RESERVATION", now, now),
                    ).lastrowid
                    item_id = conn.execute(
                        """INSERT INTO warehouse_shipment_items
                           (shipment_id,marketplace_product_id,product_key,article,name,size,color,quantity)
                           VALUES (?,?,?,?,?,?,?,?)""",
                        (shipment_id, first, "КДШВН-1/98", "КДШВН-1/98", "Костюм", "98", "бежевый", 2),
                    ).lastrowid
                    item = conn.execute("SELECT * FROM warehouse_shipment_items WHERE id=?", (item_id,)).fetchone()
                    key = marketplaces._shipment_item_product_key(conn, item)

            self.assertEqual(key["product_name"], "Костюм трикотажный детский")

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
        self.assertEqual(
            marketplaces.product_group_for("Кбшв-", "кбшв-", "1073896068"),
            ("other", "Прочие товары"),
        )

    def test_bdshv_article_links_generic_ozon_name_to_trouser_route(self):
        cases = (
            ("БДШВ-4/122", "122", "капучино", "Капучино"),
            ("БДШВ-5/104", "104", "черный", "Черный"),
        )
        for offer_id, size, source_color, production_color in cases:
            with self.subTest(offer_id=offer_id):
                row = {
                    "name": "Брюки для малыша",
                    "offer_id": offer_id,
                    "sku": "synthetic-ozon-sku",
                    "size": size,
                    "color": source_color,
                }
                self.assertEqual(
                    marketplaces.product_group_for(
                        row["name"], row["offer_id"], row["sku"], "", row["size"],
                    ),
                    ("trousers-arrows", "Брюки со стрелками"),
                )
                self.assertEqual(
                    marketplaces.production_target_for_marketplace_product(row),
                    ("Брюки со стрелками детские", size, production_color),
                )

    def test_bdshv_article_still_rejects_unsupported_route_attributes(self):
        self.assertIsNone(
            marketplaces.production_target_for_marketplace_product({
                "name": "Брюки для малыша",
                "offer_id": "БДШВ-5/104",
                "size": "104",
                "color": "Неизвестный цвет",
            })
        )

    def test_catalog_reconciliation_keeps_missing_routes_and_cells_visible(self):
        fake_connection = SimpleNamespace(rollback=lambda: None, close=lambda: None)
        location = SimpleNamespace(id=7, code="Z2-S1-P3-1")
        stock = SimpleNamespace(
            product_key=SimpleNamespace(
                item_type="finished", product_name="Бомбер", product_size="98", product_color="Бежевый",
            ),
            item_state="SELLABLE", quantity=2, reserved_quantity=0, location_id=7,
        )
        ozon = [
            {"id": "ozon-1", "offer_id": "BMB-98", "name": "Бомбер детский", "size": "98", "color": "Бежевый"},
            {"id": "ozon-2", "offer_id": "UNKNOWN-1", "name": "Редкая модель", "size": "98", "color": "Бежевый"},
        ]
        wildberries = [
            {"id": "wb-1", "offer_id": "WB-BMB-98", "name": "Бомбер детский", "size": "98", "color": "Бежевый"},
        ]
        with patch("wms.connection.get_pg_connection", return_value=fake_connection), patch(
            "wms.repository.list_locations", return_value=[location]
        ), patch("wms.repository.get_stock_rows", return_value=[stock]):
            result = marketplaces.marketplace_catalog_reconciliation(ozon, wildberries)

        self.assertTrue(result["warehouse_available"])
        self.assertEqual(result["summary"]["ozon"]["products"], 2)
        self.assertEqual(result["summary"]["ozon"]["warehouse_found"], 1)
        self.assertEqual(result["summary"]["ozon"]["route_missing"], 1)
        self.assertEqual(result["summary"]["production"]["visible_on_ozon"], 1)
        self.assertEqual(result["summary"]["production"]["visible_on_wildberries"], 1)
        ready = next(item for item in result["marketplace_items"] if item["article"] == "BMB-98")
        self.assertEqual(ready["locations"], [{"code": "Z2-S1-P3-1", "quantity": 2, "reserved_quantity": 0, "available_quantity": 2}])

    def test_dashboard_without_credentials_does_not_call_network(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "bot.db")
            with patch.dict(os.environ, {"OZON_CLIENT_ID": "", "OZON_API_KEY": ""}, clear=False):
                with patch.object(marketplaces, "get_db_connection", side_effect=lambda **_kwargs: sqlite3.connect(path)):
                    payload = marketplaces.dashboard()
                    result = marketplaces.sync_ozon()
            self.assertFalse(payload["configured"])
            self.assertTrue(payload["read_only"])
            self.assertEqual({item["marketplace"] for item in payload["connectors"]}, {"ozon", "wildberries"})
            self.assertEqual(result["code"], "not_configured")

    def test_read_only_snapshot_upserts_products_prices_stock_and_orders(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "bot.db")
            def connection(**_kwargs):
                conn = sqlite3.connect(path)
                conn.execute("PRAGMA foreign_keys = ON")
                return conn

            with patch.dict(os.environ, {"OZON_CLIENT_ID": "client", "OZON_API_KEY": "secret"}, clear=False):
                with patch.object(marketplaces, "get_db_connection", side_effect=connection):
                    with patch.object(marketplaces, "OzonClient", return_value=FakeOzonClient()):
                        with patch(
                            "marketplace_extended.sync_extended",
                            return_value={"actions": 0, "fbo": 0, "fbs": 0, "returns": 0, "rfbs_returns": 0, "finance": 0, "rating": 0},
                        ):
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
