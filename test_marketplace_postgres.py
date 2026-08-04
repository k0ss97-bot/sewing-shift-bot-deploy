from datetime import date, datetime, timezone
import unittest
from unittest.mock import patch

from marketplace_ozon_client import OzonPaginationError, OzonReadOnlyClient, _RequestResult
from marketplace_pg import (
    MarketplacePGRepository,
    _json_value,
    _production_link_fields,
    normalize_finance,
    normalize_order,
    normalize_product,
    normalize_rating,
    normalize_return,
    normalize_stock_rows,
    normalize_supply,
)


class MarketplacePostgresReadModelTest(unittest.TestCase):
    def test_release_sync_lock_accepts_connection_already_closed_by_projection(self):
        class ClosedConnection:
            closed = True

        repository = MarketplacePGRepository(connection_factory=lambda: None)
        repository._lock_connections[1] = ClosedConnection()

        repository.release_sync_lock(1)

        self.assertNotIn(1, repository._lock_connections)

    def test_json_value_serializes_postgres_dates_and_timestamps(self):
        payload = _json_value({
            "day": date(2026, 8, 4),
            "updated_at": datetime(2026, 8, 4, 8, 40, tzinfo=timezone.utc),
        })

        self.assertEqual(payload["day"], "2026-08-04")
        self.assertEqual(payload["updated_at"], "2026-08-04T08:40:00Z")

    def test_ozon_attributes_follow_last_id(self):
        client = OzonReadOnlyClient("client", "secret", page_limit=1, min_interval=0)
        responses = [
            _RequestResult({"result": [{"id": 100}], "last_id": "next"}, 0),
            _RequestResult({"result": [{"id": 101}], "last_id": ""}, 0),
        ]
        with patch.object(client, "_request", side_effect=responses) as request:
            rows = client.product_attributes()

        self.assertEqual([row["id"] for row in rows], [100, 101])
        self.assertNotIn("last_id", request.call_args_list[0].args[1])
        self.assertEqual(request.call_args_list[1].args[1]["last_id"], "next")

    def test_ozon_orders_follow_offset_and_has_next(self):
        client = OzonReadOnlyClient("client", "secret", page_limit=1, min_interval=0)
        responses = [
            _RequestResult({"result": {"postings": [{"posting_number": "1"}], "has_next": True}}, 0),
            _RequestResult({"result": {"postings": [{"posting_number": "2"}], "has_next": False}}, 0),
            _RequestResult({"postings": [{"posting_number": "3"}], "has_next": True, "cursor": "fbo-next"}, 0),
            _RequestResult({"postings": [{"posting_number": "4"}], "has_next": False, "cursor": "fbo-end"}, 0),
        ]
        with patch.object(client, "_request", side_effect=responses) as request:
            result = client.iter_order_pages(history_days=1)

        self.assertTrue(result.complete)
        self.assertEqual([row["posting_number"] for row in result.items], ["1", "2", "3", "4"])
        self.assertEqual([call.args[1]["offset"] for call in request.call_args_list[:2]], [0, 1])
        self.assertNotIn("offset", request.call_args_list[2].args[1])
        self.assertEqual(request.call_args_list[3].args[1]["cursor"], "fbo-next")
        self.assertEqual([row["warehouse_type"] for row in result.items], ["FBS", "FBS", "FBO", "FBO"])

    def test_ozon_fbo_orders_reject_a_repeated_provider_page(self):
        client = OzonReadOnlyClient("client", "secret", page_limit=100, min_interval=0)
        repeated = {"posting_number": "same-posting"}
        responses = [
            _RequestResult({"result": {"postings": [], "has_next": False}}, 0),
            _RequestResult({"postings": [repeated], "has_next": True, "cursor": "fbo-next"}, 0),
            _RequestResult({"postings": [repeated], "has_next": True, "cursor": "fbo-next-2"}, 0),
        ]

        with patch.object(client, "_request", side_effect=responses):
            with self.assertRaises(OzonPaginationError) as raised:
                client.iter_order_pages(history_days=1)

        self.assertEqual(raised.exception.code, "repeated_page")

    def test_ozon_finance_deduplicates_month_window_boundaries(self):
        client = OzonReadOnlyClient("client", "secret", page_limit=1000, min_interval=0)
        duplicate = {"operation_id": "operation-1", "amount": "10.00"}
        responses = [
            _RequestResult({"result": {"operations": [duplicate], "page_count": 1}}, 0),
            _RequestResult({"result": {"operations": [duplicate], "page_count": 1}}, 0),
        ]

        with patch.object(client, "_request", side_effect=responses) as request:
            result = client.iter_finance_pages(history_days=31)

        self.assertTrue(result.complete)
        self.assertEqual(len(request.call_args_list), 2)
        self.assertEqual([row["operation_id"] for row in result.items], ["operation-1"])
        self.assertEqual(result.total, 1)

    def test_ozon_fbo_supplies_include_order_details_and_bundle_items(self):
        client = OzonReadOnlyClient("client", "secret", page_limit=100, min_interval=0)
        responses = [
            _RequestResult({"order_ids": [700], "last_id": "end"}, 0),
            _RequestResult({"orders": [{
                "order_id": 700, "order_number": "ORDER-700", "state": "DATA_FILLING",
                "drop_off_warehouse": {"warehouse_id": 10, "name": "Тверь"},
                "supplies": [{"supply_id": 900, "bundle_id": "bundle-900", "state": "DATA_FILLING"}],
            }]}, 0),
            _RequestResult({"items": [{
                "sku": 123, "offer_id": "CARD-122-BLUE", "barcode": "460000000001",
                "quantity": 4,
            }], "has_next": False, "last_id": ""}, 0),
        ]

        with patch.object(client, "_request", side_effect=responses) as request:
            result = client.iter_supply_pages()

        self.assertTrue(result.complete)
        self.assertEqual(result.total, 1)
        self.assertEqual(result.items[0]["external_supply_id"], "900")
        self.assertEqual(result.items[0]["external_order_id"], "700")
        self.assertEqual(result.items[0]["items"][0]["quantity"], 4)
        self.assertEqual([call.args[0] for call in request.call_args_list], [
            "/v3/supply-order/list", "/v3/supply-order/get", "/v1/supply-order/bundle",
        ])

    def test_ozon_fbo_supply_details_are_requested_in_groups_of_fifty(self):
        client = OzonReadOnlyClient("client", "secret", page_limit=100, min_interval=0)
        order_ids = list(range(1, 52))
        responses = [
            _RequestResult({"order_ids": order_ids, "last_id": ""}, 0),
            _RequestResult({"orders": [
                {"order_id": order_id, "state": "DATA_FILLING", "supplies": []}
                for order_id in order_ids[:50]
            ]}, 0),
            _RequestResult({"orders": [
                {"order_id": order_ids[-1], "state": "DATA_FILLING", "supplies": []}
            ]}, 0),
        ]

        with patch.object(client, "_request", side_effect=responses) as request:
            result = client.iter_supply_pages()

        detail_calls = [
            call for call in request.call_args_list if call.args[0] == "/v3/supply-order/get"
        ]
        self.assertTrue(result.complete)
        self.assertEqual(len(result.items), 51)
        self.assertEqual([len(call.args[1]["order_ids"]) for call in detail_calls], [50, 1])

    def test_fbo_stock_normalization_preserves_real_warehouse_scope(self):
        rows = normalize_stock_rows({
            "sku": "9001", "item_code": "CARD-122-BLUE", "offer_id": "CARD-122-BLUE",
            "warehouse_type": "FBO", "warehouse_name": "Москва",
            "free_to_sell_amount": 7, "reserved_amount": 2, "promised_amount": 1,
        })

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["warehouse_type"], "FBO")
        self.assertEqual(rows[0]["stock"], 9)
        self.assertEqual(rows[0]["reserved"], 2)
        self.assertEqual(rows[0]["available"], 7)

    def test_extended_postgres_normalizers_keep_source_identities(self):
        returned = normalize_return({
            "id": 55, "posting_number": "700-1", "schema": "FBO",
            "product": {"sku": "9001", "offer_id": "CARD-122-BLUE", "name": "Кардиган", "quantity": 2, "price": 2490},
            "logistic": {"return_date": "2026-08-04T06:00:00Z"},
            "visual": {"status": {"name": "Возвращён"}},
        })
        finance = normalize_finance({
            "operation_id": 99, "operation_date": "2026-08-04T07:00:00Z",
            "operation_type": "OperationAgentDeliveredToCustomer", "amount": "-150.25",
            "posting": {"posting_number": "700-1"}, "items": [{"sku": "9001"}],
        })
        rating = normalize_rating({
            "observed_at": "2026-08-04T07:00:00Z",
            "payload": {"groups": [{"items": [{"name": "Оценка товаров", "current_value": 4.87}]}]},
        })

        self.assertEqual(returned["external_return_id"], "55")
        self.assertEqual(returned["quantity"], 2)
        self.assertEqual(finance["operation_id"], "99")
        self.assertEqual(str(finance["amount"]), "-150.25")
        self.assertEqual(str(rating["rating"]), "4.87")

    def test_supply_normalization_preserves_destination_and_contents(self):
        supply = normalize_supply({
            "external_supply_id": "900",
            "external_order_id": "700",
            "order_number": "ORDER-700",
            "state": "DATA_FILLING",
            "drop_off_warehouse": {"warehouse_id": 10, "name": "Тверь"},
            "items": [{"sku": 123, "offer_id": "CARD-122-BLUE", "quantity": 4}],
        })

        self.assertIsNotNone(supply)
        self.assertEqual(supply["external_supply_id"], "900")
        self.assertEqual(supply["dropoff_warehouse_name"], "Тверь")
        self.assertEqual(str(supply["total_quantity"]), "4")
        self.assertEqual(supply["items"][0]["sku"], "123")

    def test_rich_product_normalization_keeps_image_attributes_and_barcodes(self):
        product = normalize_product({
            "product_id": 100,
            "offer_id": "CARD-122-BLUE",
            "sku": "9001",
            "name": "Кардиган детский",
            "primary_image": "https://cdn1.ozone.ru/product.jpg",
            "barcodes": ["460000000001", "460000000002"],
            "attributes": [
                {"id": 4295, "values": [{"value": "122"}]},
                {"id": 10096, "values": [{"value": "Темно-синий"}]},
            ],
        })

        self.assertIsNotNone(product)
        self.assertEqual(product["size"], "122")
        self.assertEqual(product["color"], "Темно-синий")
        self.assertEqual(product["image_url"], "https://cdn1.ozone.ru/product.jpg")
        self.assertEqual(product["barcode"], "460000000001")
        self.assertEqual(product["barcodes"], ["460000000001", "460000000002"])
        self.assertEqual(len(product["attributes"]["attributes"]), 2)

    def test_order_normalization_keeps_posting_and_lines(self):
        order = normalize_order({
            "order_id": 700,
            "posting_number": "700-1",
            "status": "awaiting_packaging",
            "shipment_date": "2026-08-04T05:00:00Z",
            "products": [{"sku": "9001", "quantity": 2}],
        })

        self.assertIsNotNone(order)
        self.assertEqual(order["external_order_id"], "700-1")
        self.assertEqual(order["posting_number"], "700-1")
        self.assertEqual(order["warehouse_type"], "FBS")
        self.assertEqual(order["items"], [{"sku": "9001", "quantity": 2}])

    def test_production_link_uses_existing_route_contract(self):
        with patch(
            "marketplaces.production_target_for_marketplace_product",
            return_value=("Кардиган", "122", "Темно-синий"),
        ):
            link = _production_link_fields({
                "name": "Кардиган детский", "offer_id": "CARD-122-BLUE",
                "sku": "9001", "barcode": "460000000001", "size": "122",
                "color": "Темно-синий",
            })

        self.assertEqual(link["production_status"], "linked")
        self.assertEqual(link["route_configured"], 1)
        self.assertEqual(link["production_product_name"], "Кардиган")

    def test_wms_metadata_and_gs1_scan_use_postgres_catalog(self):
        repository = MarketplacePGRepository(connection_factory=lambda: None)
        product = {
            "external_product_id": "100",
            "name": "Кардиган детский",
            "group_name": "Кардиганы детские",
            "offer_id": "CARD-122-BLUE",
            "sku": "9001",
            "barcode": "460000000001",
            "barcodes_json": ["460000000001", "460000000002"],
            "size": "122",
            "color": "Темно-синий",
            "image_url": "https://cdn1.ozone.ru/product.jpg",
            "production_status": "linked",
            "route_configured": 1,
            "production_product_name": "Кардиган",
            "production_size": "122",
            "production_color": "Темно-синий",
        }
        with patch.object(
            repository,
            "warehouse_catalog",
            return_value={"ok": True, "products": [product]},
        ):
            metadata = repository.marketplace_metadata_for_wms_product_keys(
                "main",
                [{
                    "item_type": "finished",
                    "product_name": "Кардиган",
                    "product_size": "122",
                    "product_color": "Темно-синий",
                }],
            )
            resolved = repository.resolve_production_product_by_barcode(
                "main", "]C1460000000002",
            )

        self.assertEqual(metadata[0]["image_url"], "https://cdn1.ozone.ru/product.jpg")
        self.assertEqual(metadata[0]["barcodes"], ["460000000001", "460000000002"])
        self.assertEqual(resolved["product_name"], "Кардиган")
        self.assertEqual(resolved["product_size"], "122")


if __name__ == "__main__":
    unittest.main()
