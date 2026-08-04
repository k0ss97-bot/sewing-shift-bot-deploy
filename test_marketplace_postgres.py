import unittest
from unittest.mock import patch

from marketplace_ozon_client import OzonReadOnlyClient, _RequestResult
from marketplace_pg import (
    MarketplacePGRepository,
    _production_link_fields,
    normalize_order,
    normalize_product,
)


class MarketplacePostgresReadModelTest(unittest.TestCase):
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
        ]
        with patch.object(client, "_request", side_effect=responses) as request:
            result = client.iter_order_pages()

        self.assertTrue(result.complete)
        self.assertEqual([row["posting_number"] for row in result.items], ["1", "2"])
        self.assertEqual([call.args[1]["offset"] for call in request.call_args_list], [0, 1])

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
        self.assertEqual(order["external_order_id"], "700")
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
