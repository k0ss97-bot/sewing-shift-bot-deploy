from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from unified_catalog import lookup_products, merge_catalog_sources


class UnifiedCatalogTests(unittest.TestCase):
    def test_lookup_by_article_keeps_real_barcode_for_stock_receipt(self):
        connection = MagicMock()
        cursor = connection.cursor.return_value.__enter__.return_value
        cursor.fetchall.return_value = [{
            "id": 7,
            "article": "БДШВ-4/122",
            "sku": "447000122",
            "barcode": "4600000000128",
            "barcodes_json": ["4600000000128", "4600000000135"],
            "name": "Брюки для малыша",
            "size": "122",
            "color": "Капучино",
            "production_product_name": "Брюки для малыша",
            "production_size": "122",
            "production_color": "Капучино",
            "authoritative_source": "ozon",
            "validation_status": "complete",
            "source_article": "БДШВ-4/122",
            "source_sku": "447000122",
            "source_barcode": "4600000000128",
        }]
        with patch("unified_catalog.get_pg_connection", return_value=connection):
            products = lookup_products("БДШВ-4/122")
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0]["barcode"], "4600000000128")
        self.assertEqual(products[0]["product_key"]["product_size"], "122")
        connection.rollback.assert_called_once_with()

    def test_lookup_accepts_alternate_barcode(self):
        connection = MagicMock()
        cursor = connection.cursor.return_value.__enter__.return_value
        cursor.fetchall.return_value = [{
            "id": 8,
            "article": "БДШВ-4/128",
            "sku": "447000128",
            "barcode": "4600000000203",
            "barcodes_json": ["4600000000203", "4600000000210"],
            "name": "Брюки для малыша",
            "size": "128",
            "color": "Капучино",
            "production_product_name": "Брюки для малыша",
            "production_size": "128",
            "production_color": "Капучино",
            "authoritative_source": "ozon",
            "validation_status": "complete",
            "source_article": "БДШВ-4/128",
            "source_sku": "447000128",
            "source_barcode": "4600000000203",
        }]
        with patch("unified_catalog.get_pg_connection", return_value=connection):
            products = lookup_products("4600000000210")
        self.assertEqual(products[0]["barcode"], "4600000000210")

    def test_ozon_wins_conflicting_fields_and_wb_fills_missing_barcode(self):
        rows = merge_catalog_sources([
            {
                "source_type": "wildberries", "source_external_id": "wb-10",
                "article": "КДШВН-1/98", "barcode": "4600000000001",
                "name": "Старое имя WB", "size": "98", "color": "песочный",
            },
            {
                "source_type": "ozon", "source_external_id": "ozon-20",
                "article": "КДШВН-1/98", "name": "Костюм трикотажный детский",
                "size": "98", "color": "бежевый",
                "production_product_name": "Костюм трикотажный детский",
                "production_size": "98", "production_color": "Бежевый",
                "route_configured": True,
            },
        ])

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["authoritative_source"], "ozon")
        self.assertEqual(rows[0]["name"], "Костюм трикотажный детский")
        self.assertEqual(rows[0]["color"], "бежевый")
        self.assertEqual(rows[0]["barcodes"], ["4600000000001"])
        self.assertEqual(rows[0]["validation_status"], "canonicalized")
        self.assertEqual({source["source_type"] for source in rows[0]["sources"]}, {"ozon", "wildberries"})

    def test_shared_barcode_merges_different_articles(self):
        rows = merge_catalog_sources([
            {
                "source_type": "ozon", "source_external_id": "ozon-1",
                "article": "OZ-98", "barcode": "4600000000002",
                "name": "Бомбер", "size": "98", "color": "Синий",
            },
            {
                "source_type": "wildberries", "source_external_id": "wb-1",
                "article": "WB-778", "barcode": "4600000000002",
                "name": "Бомбер детский", "size": "98", "color": "синий",
            },
        ])

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["article"], "OZ-98")
        self.assertEqual(rows[0]["authoritative_source"], "ozon")

    def test_marketplace_only_variant_is_inserted_without_stock(self):
        rows = merge_catalog_sources([{
            "source_type": "ozon", "source_external_id": "new-1",
            "article": "NEW-104", "barcode": "4600000000003",
            "name": "Новая модель", "size": "104", "color": "Молочный",
        }])

        self.assertEqual(len(rows), 1)
        self.assertNotIn("quantity", rows[0])
        self.assertEqual(rows[0]["canonical_key"], "article:new104")

    def test_incomplete_sources_with_same_canonical_key_do_not_overwrite_priority(self):
        rows = merge_catalog_sources([
            {
                "source_type": "ozon", "source_external_id": "ozon-incomplete",
                "name": "Товар без варианта",
            },
            {
                "source_type": "wildberries", "source_external_id": "wb-incomplete",
                "name": "Товар без варианта",
            },
        ])

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["authoritative_source"], "ozon")
        self.assertEqual(len(rows[0]["sources"]), 2)


if __name__ == "__main__":
    unittest.main()
