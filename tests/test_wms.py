"""Tests for the WMS module.

DB-dependent tests create a fresh temporary PostgreSQL database via
``init_pg_for_tests()``. If Postgres is not reachable, those tests are skipped
with a clear reason — the rest (pure-Python logic) always runs, following the
project's "isolated, never touch working DB" convention.
"""

from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock, patch

# Ensure tests never touch a working DB.
os.environ.setdefault("WMS_DATABASE_URL", "postgresql://wms:wms@127.0.0.1:5432/wms_test")

from wms.barcode import (  # noqa: E402
    barcode_lookup_candidates,
    classify_barcode,
    is_location_barcode,
    location_code_from_barcode,
    normalize_scanned_barcode,
    LOCATION_PREFIX,
    CONTAINER_PREFIX,
)
from wms.models import (  # noqa: E402
    Location,
    OperationResult,
    ProductKey,
    StockReceiptResult,
    WarehouseStock,
)
from marketplaces import _marketplace_payload_barcodes  # noqa: E402


# ──────────────────────────────────────────────────────────────────────
# Pure-Python tests (no DB)
# ──────────────────────────────────────────────────────────────────────


class ProductKeyTests(unittest.TestCase):
    def test_roundtrip(self):
        pk = ProductKey(
            item_type="finished",
            product_name="Брюки",
            product_size="128",
            product_color="Черный",
            stage_name="Готово",
            ready_for_position="Склад",
        )
        d = pk.to_dict()
        self.assertEqual(ProductKey.from_dict(d), pk)

    def test_six_fields(self):
        pk = ProductKey("semifinished", "A", "S", "C", "ST", "P")
        self.assertEqual(len(pk.to_dict()), 6)

    def test_material_roundtrip(self):
        pk = ProductKey("material", "Ткань", "—", "Бежевый", "Материал", "Склад")
        self.assertEqual(ProductKey.from_dict(pk.to_dict()), pk)


class BarcodeClassifyTests(unittest.TestCase):
    def test_location(self):
        self.assertEqual(classify_barcode("LOC:A-03-02"), "location")

    def test_existing_moysklad_location_without_prefix(self):
        self.assertEqual(classify_barcode("Z1-S1-P1-1"), "location")
        self.assertTrue(is_location_barcode("z4-s2-p3-2"))

    def test_container(self):
        self.assertEqual(classify_barcode("LPN:000125"), "container")

    def test_product(self):
        self.assertEqual(classify_barcode("4600000000012"), "product")

    def test_location_code_extract(self):
        self.assertEqual(location_code_from_barcode("LOC:A-03-02"), "A-03-02")
        self.assertEqual(location_code_from_barcode("z3-s5-p2-1"), "Z3-S5-P2-1")

    def test_product_barcode_is_not_mistaken_for_location(self):
        self.assertFalse(is_location_barcode("4600000000012"))

    def test_handheld_scanner_framing_is_removed_without_losing_zeroes(self):
        self.assertEqual(normalize_scanned_barcode("]C10001234567890\r\n"), "0001234567890")
        candidates = barcode_lookup_candidates("]C14600000000012\r")
        self.assertEqual(candidates[:2], ("]C14600000000012", "4600000000012"))
        self.assertIn("04600000000012", candidates)

    def test_gs1_gtin14_and_ean13_are_safe_lookup_candidates(self):
        candidates = barcode_lookup_candidates("]C10104600000000012\r")
        self.assertIn("04600000000012", candidates)
        self.assertIn("4600000000012", candidates)

    def test_prefixes(self):
        self.assertTrue("LOC:A-01".startswith(LOCATION_PREFIX))
        self.assertTrue("LPN:1".startswith(CONTAINER_PREFIX))

    def test_marketplace_payload_keeps_alternate_product_barcodes(self):
        payload = {
            "result": {
                "barcode": "4600000000012",
                "barcodes": ["4600000000029", "]C14600000000036\r"],
            },
            "unrelated_number": 123,
        }
        self.assertEqual(
            _marketplace_payload_barcodes(payload),
            {"4600000000012", "4600000000029", "4600000000036"},
        )


class OperationResultTests(unittest.TestCase):
    def test_status_ok(self):
        r = OperationResult(ok=True, movement_id=5)
        self.assertEqual(r.status, "ok")

    def test_status_duplicate(self):
        r = OperationResult(ok=True, skipped_duplicate=True)
        self.assertEqual(r.status, "duplicate")

    def test_status_error(self):
        r = OperationResult(ok=False, reason="bad")
        self.assertEqual(r.status, "error")

    def test_stock_receipt_statuses(self):
        self.assertEqual(StockReceiptResult(ok=True).status, "posted")
        self.assertEqual(
            StockReceiptResult(ok=True, skipped_duplicate=True).status,
            "duplicate",
        )


class WmsContractTests(unittest.TestCase):
    def _payload(self):
        return {
            "product_key": ProductKey(
                "finished", "Брюки", "128", "Черный", "Готово", "Склад"
            ).to_dict(),
            "quantity": 2,
            "employee_id": 999999,
        }

    def test_api_uses_authenticated_employee_not_payload_employee(self):
        from wms import api

        with patch("wms.api.ops.receive_from_production") as receive:
            receive.return_value = OperationResult(ok=True, movement_id=10)
            status, body = api.handle(
                "/api/wms/receive", self._payload(), employee_id=17
            )
        self.assertEqual(status, 200)
        self.assertTrue(body["ok"])
        self.assertEqual(receive.call_args.kwargs["employee_id"], 17)

    def test_material_receive_api_builds_material_key_and_uses_authenticated_employee(self):
        from wms import api

        with patch("wms.api.ops.receive_material") as receive:
            receive.return_value = OperationResult(ok=True, movement_id=12)
            status, body = api.handle(
                "/api/wms/material-receive",
                {
                    "material_name": "Ткань",
                    "product_color": "Бежевый",
                    "quantity": 3,
                    "unit": "рул",
                    "request_key": "test:material:receipt",
                },
                employee_id=19,
            )
        self.assertEqual(status, 200)
        self.assertTrue(body["ok"])
        self.assertEqual(receive.call_args.args[0].item_type, "material")
        self.assertEqual(receive.call_args.args[0].product_name, "Ткань")
        self.assertEqual(receive.call_args.kwargs["employee_id"], 19)
        self.assertEqual(receive.call_args.kwargs["unit"], "рул")

    def test_stock_receipt_api_resolves_every_barcode_and_uses_authenticated_employee(self):
        from wms import api

        product = ProductKey("finished", "Брюки", "128", "Черный", "Готово", "Склад")
        result = StockReceiptResult(
            ok=True,
            receipt_id=41,
            number="OPR-000041",
            lines_count=1,
            total_quantity=7,
        )
        with patch("wms.api._resolve_known_product", return_value=product) as resolve, patch(
            "wms.api.ops.post_stock_receipt", return_value=result
        ) as post:
            status, body = api.handle(
                "/api/wms/stock-receipts/post",
                {
                    "request_key": "test:stock-receipt:41",
                    "lines": [{"barcode": "4600000000012", "quantity": 7}],
                },
                employee_id=23,
            )
        self.assertEqual(status, 201)
        self.assertEqual(body["number"], "OPR-000041")
        resolve.assert_called_once_with("4600000000012")
        self.assertEqual(post.call_args.kwargs["employee_id"], 23)

    def test_stock_receipt_api_rejects_unknown_barcode_before_posting(self):
        from wms import api

        with patch("wms.api._resolve_known_product", return_value=None), patch(
            "wms.api.ops.post_stock_receipt"
        ) as post:
            status, body = api.handle(
                "/api/wms/stock-receipts/post",
                {
                    "request_key": "test:stock-receipt:unknown",
                    "lines": [{"barcode": "9999999999999", "quantity": 1}],
                },
                employee_id=23,
            )
        self.assertEqual(status, 400)
        self.assertIn("не зарегистрирован", body["message"])
        post.assert_not_called()

    def test_stock_receipt_api_rejects_fractional_quantity(self):
        from wms import api

        product = ProductKey("finished", "Брюки", "128", "Черный", "Готово", "Склад")
        with patch("wms.api._resolve_known_product", return_value=product), patch(
            "wms.api.ops.post_stock_receipt"
        ) as post:
            status, body = api.handle(
                "/api/wms/stock-receipts/post",
                {
                    "request_key": "test:stock-receipt:fraction",
                    "lines": [{"barcode": "4600000000012", "quantity": 1.5}],
                },
                employee_id=23,
            )
        self.assertEqual(status, 400)
        self.assertIn("целым числом", body["message"])
        post.assert_not_called()

    def test_pick_api_uses_authenticated_employee_and_location(self):
        from wms import api

        payload = self._payload()
        payload["from_location_code"] = "A-01-01"
        with patch("wms.api.ops.pick") as pick:
            pick.return_value = OperationResult(ok=True, movement_id=11)
            status, body = api.handle("/api/wms/pick", payload, employee_id=23)
        self.assertEqual(status, 200)
        self.assertTrue(body["ok"])
        self.assertEqual(pick.call_args.kwargs["employee_id"], 23)
        self.assertEqual(pick.call_args.kwargs["from_location_code"], "A-01-01")

    def test_admin_scrap_alias_uses_authenticated_employee(self):
        from wms import api

        payload = self._payload()
        payload.update({"from_location_code": "A-01-01", "reason": "Повреждение"})
        with patch("wms.api.ops.scrap") as scrap:
            scrap.return_value = OperationResult(ok=True, movement_id=15)
            status, body = api.handle("/api/wms/admin/scrap", payload, employee_id=29)
        self.assertEqual(status, 200)
        self.assertTrue(body["ok"])
        self.assertEqual(scrap.call_args.kwargs["employee_id"], 29)

    def test_admin_inventory_requires_reason(self):
        from wms import api

        status, body = api.handle(
            "/api/wms/admin/inventory",
            {"location_code": "A-01-01", "counted": []},
            employee_id=29,
        )
        self.assertEqual(status, 400)
        self.assertIn("причину", body["message"])

    def test_manual_routes_are_admin_only_contract(self):
        from wms.api import WMS_ADMIN_ROUTES, WMS_ROUTES

        self.assertEqual(
            WMS_ADMIN_ROUTES,
            {"/api/wms/admin/scrap", "/api/wms/admin/inventory"},
        )
        self.assertTrue(WMS_ADMIN_ROUTES <= WMS_ROUTES)

    def test_admin_manual_adjustment_is_available_in_cell_and_menu(self):
        root = Path(__file__).resolve().parents[1]
        assets = (root / "miniapp_assets.py").read_text(encoding="utf-8")
        self.assertIn('data-wms-cell-writeoff=', assets)
        self.assertIn('"admin-stock-control"', assets)
        self.assertIn('"/api/wms/admin/inventory"', assets)
        self.assertIn('"/api/wms/admin/scrap"', assets)

    def test_stock_receipt_ui_is_wired_to_history_and_actions(self):
        root = Path(__file__).resolve().parents[1]
        assets = (root / "miniapp_assets.py").read_text(encoding="utf-8")
        self.assertIn('api("/api/wms/stock-receipts", {limit: 20})', assets)
        self.assertIn('data-wms-stock-receipt-action="add"', assets)
        self.assertIn('data-wms-stock-receipt-action="post"', assets)
        self.assertIn('removeWmsStockReceiptLine(Number(', assets)
        self.assertIn('state.wmsView === "stock-receipt") postWmsStockReceipt()', assets)
        self.assertNotIn("Приёмка не является обязательным шагом", assets)

    def test_shipment_task_ui_uses_a_position_by_position_scan_flow(self):
        root = Path(__file__).resolve().parents[1]
        assets = (root / "miniapp_assets.py").read_text(encoding="utf-8")
        self.assertIn('data-wms-task-open-allocation=', assets)
        self.assertIn('wmsShipmentTaskActiveAllocationId', assets)
        self.assertIn('data-wms-task-action="back-position"', assets)
        self.assertIn('Ячейка: ${escapeHtml(allocation.location_code)}', assets)
        self.assertIn('#wmsHardwareScannerInput, #wmsShipmentTaskCell', assets)
        self.assertIn('scannedCode === expectedCode', assets)
        self.assertIn('state.wmsShipmentTaskActiveAllocationId = "";', assets)

    def test_stock_api_passes_postgres_connection_to_repository(self):
        from wms import api

        sentinel = object()
        with patch("wms.api.get_pg_connection", return_value=sentinel), patch(
            "wms.api.repo.get_stock_rows", return_value=[]
        ) as get_rows:
            status, body = api.handle("/api/wms/stock", {}, employee_id=17)
        self.assertEqual(status, 200)
        self.assertEqual(body["stock"], [])
        get_rows.assert_called_once_with(sentinel, location_id=None)

    def test_location_barcode_resolves_to_exact_stock_key_by_sku(self):
        from wms import api

        stock_key = ProductKey(
            "finished",
            "Ozon · Костюм классический · КДШВН-6/98-104",
            "98-104",
            "Светло-серый",
            "Упаковано",
            "Склад",
        )
        location = Location(7, 2, "Z2-S1-P3-2", "Z2-S1-P3-2", None, 0, 0, "active")
        stock = WarehouseStock(3, stock_key, 14, 0, "SELLABLE", location.id, "шт")
        marketplace = {
            "sku": "447040077",
            "barcode": "",
            "barcodes": [],
        }
        with patch("wms.api.get_pg_connection"), patch(
            "wms.api.repo.get_location_by_code", return_value=location
        ), patch("wms.api.repo.get_stock_rows", return_value=[stock]), patch(
            "marketplaces.marketplace_metadata_for_wms_product_keys",
            return_value=[marketplace],
        ), patch("wms.api.resolve_product_barcode", return_value=None):
            status, body = api.handle(
                "/api/wms/barcode/resolve",
                {"barcode": "]C1447040077\r", "location_code": location.code},
                employee_id=17,
            )
        self.assertEqual(status, 200)
        self.assertTrue(body["matched_in_location"])
        self.assertEqual(body["product_key"], stock_key.to_dict())
        self.assertEqual(body["stock_row"]["quantity"], 14)
        self.assertEqual(body["stock_row"]["location_id"], location.id)

    def test_location_barcode_maps_linked_production_key_to_actual_stock_row(self):
        from wms import api

        resolved_key = ProductKey(
            "finished", "Кардиган детский", "104", "Брауни", "Упаковано", "Склад"
        )
        stock_key = ProductKey(
            "finished",
            "Ozon · Кардиган детский · КД-104-БР",
            "104",
            "Брауни",
            "Упаковано",
            "Склад",
        )
        location = Location(8, 2, "Z2-S1-P3-1", "Z2-S1-P3-1", None, 0, 0, "active")
        stock = WarehouseStock(4, stock_key, 20, 0, "SELLABLE", location.id, "шт")
        marketplace = {
            "barcode": "",
            "barcodes": [],
            "production_product_name": "Кардиган детский",
            "production_size": "104",
            "production_color": "Брауни",
        }
        with patch("wms.api.get_pg_connection"), patch(
            "wms.api.repo.get_location_by_code", return_value=location
        ), patch("wms.api.repo.get_stock_rows", return_value=[stock]), patch(
            "marketplaces.marketplace_metadata_for_wms_product_keys",
            return_value=[marketplace],
        ), patch("wms.api.resolve_product_barcode", return_value=resolved_key):
            status, body = api.handle(
                "/api/wms/barcode/resolve",
                {"barcode": "4600000000012", "location_code": location.code},
                employee_id=17,
            )
        self.assertEqual(status, 200)
        self.assertTrue(body["matched_in_location"])
        self.assertEqual(body["product_key"], stock_key.to_dict())

    def test_schema_keys_stock_by_location_and_enforces_balances(self):
        root = Path(__file__).resolve().parents[1]
        schema = (root / "wms_migrations" / "001_initial_wms.sql").read_text(
            encoding="utf-8"
        )
        self.assertIn("UNIQUE NULLS NOT DISTINCT", schema)
        self.assertIn("item_state, location_id", schema)
        self.assertIn("CHECK (quantity >= 0)", schema)
        self.assertIn("reserved_quantity <= quantity", schema)

    def test_initial_bridge_places_legacy_stock_in_receive_location(self):
        root = Path(__file__).resolve().parents[1]
        bridge = (root / "wms" / "bridge.py").read_text(encoding="utf-8")
        self.assertIn("location_id, updated_at", bridge)
        self.assertIn("code = 'RECEIVE-01'", bridge)
        self.assertIn("Сначала выполните миграции WMS", bridge)

    def test_physical_storage_migration_keeps_existing_barcode_payloads(self):
        root = Path(__file__).resolve().parents[1]
        migration = (root / "wms_migrations" / "004_seed_physical_storage.sql").read_text(
            encoding="utf-8"
        )
        self.assertIn("generate_series(1, 4)", migration)
        self.assertIn("generate_series(1, 5)", migration)
        self.assertIn("generate_series(1, 3)", migration)
        self.assertIn("generate_series(1, 2)", migration)
        self.assertIn("cells.cell_code,\n    cells.cell_code", migration)

    def test_wms_backup_creates_verified_private_dump(self):
        from scripts import backup_wms

        with tempfile.TemporaryDirectory() as temp_dir:
            destination_dir = Path(temp_dir)

            def fake_run(command, **kwargs):
                if command[0] == "pg_dump":
                    output = next(item.split("=", 1)[1] for item in command if item.startswith("--file="))
                    Path(output).write_bytes(b"test-dump")
                return None

            with patch("scripts.backup_wms.subprocess.run", side_effect=fake_run) as run:
                destination = backup_wms.create_backup(
                    "postgresql:///sewing_wms", destination_dir
                )

            self.assertTrue(destination.is_file())
            self.assertEqual(destination.stat().st_mode & 0o777, 0o600)
            self.assertEqual(run.call_count, 2)
            self.assertEqual(run.call_args_list[1].args[0][:2], ["pg_restore", "--list"])


class PickOperationTests(unittest.TestCase):
    def setUp(self):
        self.pk = ProductKey("finished", "Брюки", "128", "Черный", "Готово", "Склад")
        self.location = Location(7, 2, "A-01-01", "LOC:A-01-01", None, 0, 0, "active")
        self.conn = MagicMock()

    def test_pick_protects_reserved_balance(self):
        from wms import operations as ops

        stock = WarehouseStock(3, self.pk, 5, 2, "SELLABLE", self.location.id, "шт")
        with patch("wms.operations.get_pg_connection", return_value=self.conn), patch(
            "wms.operations.repo.get_location_by_code", return_value=self.location
        ), patch("wms.operations.repo.movement_exists", return_value=False), patch(
            "wms.operations.repo.find_stock", return_value=stock
        ), patch("wms.operations.repo.upsert_stock") as upsert:
            result = ops.pick(self.pk, 4, from_location_code=self.location.code)
        self.assertFalse(result.ok)
        self.assertIn("доступно только 3", result.reason)
        upsert.assert_not_called()
        self.conn.rollback.assert_called()

    def test_pick_decrements_scanned_location_and_records_actor(self):
        from wms import operations as ops

        stock = WarehouseStock(3, self.pk, 5, 1, "SELLABLE", self.location.id, "шт")
        with patch("wms.operations.get_pg_connection", return_value=self.conn), patch(
            "wms.operations.repo.get_location_by_code", return_value=self.location
        ), patch("wms.operations.repo.movement_exists", return_value=False), patch(
            "wms.operations.repo.find_stock", return_value=stock
        ), patch("wms.operations.repo.upsert_stock") as upsert, patch(
            "wms.operations.repo.insert_movement", return_value=91
        ) as movement:
            result = ops.pick(
                self.pk,
                2,
                from_location_code=self.location.code,
                employee_id=23,
                request_key="test:pick:unit",
            )
        self.assertTrue(result.ok)
        self.assertEqual(result.movement_id, 91)
        upsert.assert_called_once_with(
            self.conn,
            self.pk,
            delta=-2,
            item_state="SELLABLE",
            location_id=self.location.id,
        )
        self.assertEqual(movement.call_args.kwargs["movement_type"], "pick")
        self.assertEqual(movement.call_args.kwargs["actor_employee_id"], 23)
        self.conn.commit.assert_called_once()


class PutawayOperationTests(unittest.TestCase):
    def test_putaway_rejects_product_missing_from_receive(self):
        from wms import operations as ops

        product = ProductKey("finished", "Брюки", "128", "Черный", "Готово", "Склад")
        receive = Location(1, 1, "RECEIVE-01", "LOC:RECEIVE-01", None, 0, 0, "active")
        target = Location(7, 2, "Z1-S1-P1-1", "Z1-S1-P1-1", None, 0, 0, "active")
        conn = MagicMock()
        cursor = conn.cursor.return_value.__enter__.return_value
        cursor.fetchone.return_value = None
        with patch("wms.operations.get_pg_connection", return_value=conn), patch(
            "wms.operations.repo.get_location_by_code", return_value=target
        ), patch("wms.operations._zone_location", return_value=receive), patch(
            "wms.operations.repo.movement_exists", return_value=False
        ), patch("wms.operations.repo.upsert_stock") as upsert, patch(
            "wms.operations.repo.insert_movement"
        ) as movement:
            result = ops.putaway(
                product,
                2,
                to_location_code=target.code,
                request_key="test:putaway:without-receipt",
            )
        self.assertFalse(result.ok)
        self.assertIn("зоне приёмки доступно 0", result.reason)
        upsert.assert_not_called()
        movement.assert_not_called()
        conn.rollback.assert_called_once()


class StockReceiptOperationTests(unittest.TestCase):
    def setUp(self):
        self.pk = ProductKey("finished", "Брюки", "128", "Черный", "Готово", "Склад")
        self.receive = Location(1, 1, "RECEIVE-01", "LOC:RECEIVE-01", None, 0, 0, "active")
        self.conn = MagicMock()

    def test_posts_merged_lines_atomically_into_receive(self):
        from wms import operations as ops

        created = {"id": 41, "number": "OPR-000041"}
        posted = {
            "id": 41,
            "number": "OPR-000041",
            "lines_count": 1,
            "total_quantity": 5,
        }
        with patch("wms.operations.get_pg_connection", return_value=self.conn), patch(
            "wms.operations.repo.get_stock_receipt_by_request_key", return_value=None
        ), patch("wms.operations._zone_location", return_value=self.receive), patch(
            "wms.operations.repo.create_stock_receipt", return_value=created
        ), patch("wms.operations.repo.upsert_stock") as upsert, patch(
            "wms.operations.repo.insert_movement", return_value=91
        ) as movement, patch(
            "wms.operations.repo.insert_stock_receipt_line"
        ) as insert_line, patch(
            "wms.operations.repo.post_stock_receipt", return_value=posted
        ):
            result = ops.post_stock_receipt(
                [("4600000000012", self.pk, 2), ("4600000000012", self.pk, 3)],
                employee_id=23,
                request_key="test:stock-receipt:41",
            )
        self.assertTrue(result.ok)
        self.assertEqual(result.lines_count, 1)
        self.assertEqual(result.total_quantity, 5)
        upsert.assert_called_once_with(
            self.conn,
            self.pk,
            delta=5,
            item_state="SELLABLE",
            location_id=self.receive.id,
            unit="шт",
        )
        self.assertEqual(movement.call_args.kwargs["movement_type"], "stock_receipt")
        insert_line.assert_called_once()
        self.conn.commit.assert_called_once()

    def test_duplicate_request_returns_existing_document_without_stock_change(self):
        from wms import operations as ops

        existing = {
            "id": 41,
            "number": "OPR-000041",
            "lines_count": 2,
            "total_quantity": 7,
        }
        with patch("wms.operations.get_pg_connection", return_value=self.conn), patch(
            "wms.operations.repo.get_stock_receipt_by_request_key", return_value=existing
        ), patch("wms.operations.repo.upsert_stock") as upsert:
            result = ops.post_stock_receipt(
                [("4600000000012", self.pk, 7)],
                employee_id=23,
                request_key="test:stock-receipt:41",
            )
        self.assertTrue(result.skipped_duplicate)
        self.assertEqual(result.number, "OPR-000041")
        upsert.assert_not_called()
        self.conn.rollback.assert_called_once()

    def test_invalid_merged_quantity_never_opens_database(self):
        from wms import operations as ops

        with patch("wms.operations.get_pg_connection") as connect:
            result = ops.post_stock_receipt(
                [("4600000000012", self.pk, 600_000), ("4600000000012", self.pk, 600_000)],
                employee_id=23,
                request_key="test:stock-receipt:too-many",
            )
        self.assertFalse(result.ok)
        connect.assert_not_called()


class StockAdjustmentOperationTests(unittest.TestCase):
    def setUp(self):
        self.pk = ProductKey("finished", "Брюки", "128", "Черный", "Готово", "Склад")
        self.location = Location(7, 2, "A-01-01", "LOC:A-01-01", None, 0, 0, "active")
        self.stock = WarehouseStock(3, self.pk, 5, 2, "SELLABLE", self.location.id, "шт")
        self.conn = MagicMock()

    def test_scrap_cannot_consume_reserved_balance(self):
        from wms import operations as ops

        cursor = self.conn.cursor.return_value.__enter__.return_value
        cursor.fetchone.return_value = (self.stock.id, self.stock.quantity, self.stock.reserved_quantity)
        with patch("wms.operations.get_pg_connection", return_value=self.conn), patch(
            "wms.operations.repo.get_location_by_code", return_value=self.location
        ), patch("wms.operations.repo.movement_exists", return_value=False), patch(
            "wms.operations.repo.find_stock", return_value=self.stock
        ), patch("wms.operations.repo.upsert_stock") as upsert:
            result = ops.scrap(
                self.pk,
                4,
                reason="Повреждение",
                from_location_code=self.location.code,
            )
        self.assertFalse(result.ok)
        self.assertIn("доступно только 3", result.reason)
        self.assertIn("резерв", result.reason)
        upsert.assert_not_called()
        self.conn.rollback.assert_called()

    def test_inventory_cannot_reduce_quantity_below_reserve(self):
        from wms import operations as ops

        cursor = self.conn.cursor.return_value.__enter__.return_value
        cursor.fetchone.return_value = (41,)
        with patch("wms.operations.get_pg_connection", return_value=self.conn), patch(
            "wms.operations.repo.get_location_by_code", return_value=self.location
        ), patch("wms.operations.repo.find_stock", return_value=self.stock), patch(
            "wms.operations.repo.upsert_stock"
        ) as upsert:
            result = ops.inventory_count(
                self.location.code,
                [{"product_key": self.pk.to_dict(), "counted_quantity": 1}],
                employee_id=23,
                reason="Контрольный пересчёт",
            )
        self.assertFalse(result.ok)
        self.assertIn("зарезервировано 2", result.reason)
        upsert.assert_not_called()
        self.conn.rollback.assert_called()


# ──────────────────────────────────────────────────────────────────────
# DB-dependent tests (skipped if Postgres unreachable)
# ──────────────────────────────────────────────────────────────────────


def _pg_reachable() -> bool:
    try:
        import psycopg2
        conn = psycopg2.connect(os.environ["WMS_DATABASE_URL"])
        conn.close()
        return True
    except Exception:
        return False


@unittest.skipUnless(_pg_reachable(), "Postgres not reachable at WMS_DATABASE_URL")
class WmsDbTests(unittest.TestCase):
    """Schema + operations + idempotency + invariants, against a live Postgres."""

    @classmethod
    def setUpClass(cls):
        from wms.connection import get_pg_connection, reset_connection
        from wms.migrate import migrate_all
        reset_connection()
        # Drop & recreate all WMS tables for a clean slate.
        conn = get_pg_connection()
        conn.autocommit = True
        with conn.cursor() as cur:
            for t in (
                "wms_stock_receipt_lines", "wms_stock_receipts",
                "wms_inventory_count_lines", "wms_inventory_counts",
                "wms_movements", "warehouse_stock", "wms_containers",
                "wms_barcodes", "wms_locations", "wms_zones",
                "wms_item_states", "schema_migrations",
            ):
                cur.execute(f"DROP TABLE IF EXISTS {t} CASCADE")
        conn.autocommit = False
        migrate_all()

    def setUp(self):
        from wms.connection import get_pg_connection
        self.conn = get_pg_connection()

    def tearDown(self):
        try:
            self.conn.rollback()
        except Exception:
            pass

    def _pk(self, **kw):
        defaults = dict(
            item_type="finished", product_name="Брюки", product_size="128",
            product_color="Черный", stage_name="Готово", ready_for_position="Склад",
        )
        defaults.update(kw)
        return ProductKey(**defaults)

    def test_seed_zones_present(self):
        with self.conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM wms_zones")
            self.assertGreaterEqual(cur.fetchone()[0], 11)

    def test_physical_storage_cells_present_with_unchanged_barcodes(self):
        with self.conn.cursor() as cur:
            cur.execute(
                """SELECT count(*), count(DISTINCT l.barcode),
                          count(*) FILTER (WHERE l.code = l.barcode)
                     FROM wms_locations l
                     JOIN wms_zones z ON z.id = l.zone_id
                    WHERE z.code IN ('Z1', 'Z2', 'Z3', 'Z4')"""
            )
            total, unique_barcodes, unchanged = cur.fetchone()
        self.assertEqual((total, unique_barcodes, unchanged), (102, 102, 102))

    def test_seed_item_states_present(self):
        with self.conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM wms_item_states")
            self.assertGreaterEqual(cur.fetchone()[0], 9)

    def test_receipt_increments_stock(self):
        from wms import operations as ops
        from wms import repository as repo
        # Ensure a RECEIVE location exists.
        receive_zone = repo.get_zone_by_code(self.conn, "RECEIVE")
        locs = repo.list_locations(self.conn, zone_code="RECEIVE")
        if not locs:
            repo.create_location(
                self.conn, zone_id=receive_zone.id, code="RCV-01", name_ru="Приёмка 1"
            )
        pk = self._pk(product_name="Тест-Брюки-1")
        result = ops.receive_from_production(pk, 10, employee_id=1, request_key="test:receipt:1")
        self.assertTrue(result.ok)
        stock = repo.find_stock(self.conn, pk)
        self.assertIsNotNone(stock)
        self.assertEqual(stock.quantity, 10)

    def test_idempotent_receipt(self):
        from wms import operations as ops
        pk = self._pk(product_name="Тест-Брюки-2")
        r1 = ops.receive_from_production(pk, 5, request_key="test:idem:1")
        r2 = ops.receive_from_production(pk, 5, request_key="test:idem:1")
        self.assertTrue(r1.ok)
        self.assertTrue(r2.skipped_duplicate)

    def test_transfer_insufficient_stock(self):
        from wms import operations as ops
        from wms import repository as repo
        # Create two locations.
        storage = repo.get_zone_by_code(self.conn, "STORAGE")
        for code in ("ST-A-01", "ST-A-02"):
            if not repo.get_location_by_code(self.conn, code):
                repo.create_location(self.conn, zone_id=storage.id, code=code)
        self.conn.commit()
        pk = self._pk(product_name="Тест-Брюки-3")
        result = ops.transfer(
            pk, 100, from_location_code="ST-A-01", to_location_code="ST-A-02",
            request_key="test:transfer:fail",
        )
        self.assertFalse(result.ok)
        self.assertIn("Недостаточно", result.reason)

    def test_negative_adjustment_is_guarded_and_never_inserts_negative_row(self):
        from wms import repository as repo

        receive = repo.list_locations(self.conn, zone_code="RECEIVE")[0]
        pk = self._pk(product_name="Тест-Защита-Отрицательного-Остатка")
        repo.upsert_stock(self.conn, pk, delta=5, location_id=receive.id)
        self.assertEqual(
            repo.find_stock(self.conn, pk, location_id=receive.id).quantity,
            5,
        )
        repo.upsert_stock(self.conn, pk, delta=-3, location_id=receive.id)
        self.assertEqual(
            repo.find_stock(self.conn, pk, location_id=receive.id).quantity,
            2,
        )
        with self.assertRaises(ValueError):
            repo.upsert_stock(self.conn, pk, delta=-3, location_id=receive.id)

    def test_partial_putaway_and_transfer_keep_separate_location_balances(self):
        from wms import operations as ops
        from wms import repository as repo

        receive_zone = repo.get_zone_by_code(self.conn, "RECEIVE")
        receive_locations = repo.list_locations(self.conn, zone_code="RECEIVE")
        if receive_locations:
            receive = receive_locations[0]
        else:
            receive = repo.create_location(
                self.conn, zone_id=receive_zone.id, code="RCV-PARTIAL"
            )
        storage = repo.get_zone_by_code(self.conn, "STORAGE")
        locations = []
        for code in ("ST-PARTIAL-A", "ST-PARTIAL-B"):
            location = repo.get_location_by_code(self.conn, code)
            if location is None:
                location = repo.create_location(self.conn, zone_id=storage.id, code=code)
            locations.append(location)
        self.conn.commit()

        pk = self._pk(product_name="Тест-Частичное-Перемещение")
        self.assertTrue(
            ops.receive_from_production(pk, 10, request_key="test:partial:receive").ok
        )
        self.assertTrue(
            ops.putaway(
                pk,
                4,
                to_location_code=locations[0].code,
                request_key="test:partial:putaway",
            ).ok
        )
        self.assertEqual(repo.find_stock(self.conn, pk, location_id=receive.id).quantity, 6)
        self.assertEqual(repo.find_stock(self.conn, pk, location_id=locations[0].id).quantity, 4)

        self.assertTrue(
            ops.transfer(
                pk,
                2,
                from_location_code=locations[0].code,
                to_location_code=locations[1].code,
                request_key="test:partial:transfer",
            ).ok
        )
        self.assertEqual(repo.find_stock(self.conn, pk, location_id=locations[0].id).quantity, 2)
        self.assertEqual(repo.find_stock(self.conn, pk, location_id=locations[1].id).quantity, 2)

    def test_direct_putaway_is_rejected_without_receipt(self):
        from wms import operations as ops
        from wms import repository as repo

        storage = repo.get_zone_by_code(self.conn, "STORAGE")
        location = repo.get_location_by_code(self.conn, "ST-DIRECT-PUTAWAY")
        if location is None:
            location = repo.create_location(
                self.conn, zone_id=storage.id, code="ST-DIRECT-PUTAWAY"
            )
        self.conn.commit()
        product = self._pk(product_name="Тест-Прямое-Размещение")

        result = ops.putaway(
            product, 6, to_location_code=location.code, request_key="test:direct:putaway"
        )

        self.assertFalse(result.ok)
        self.assertIn("зоне приёмки доступно 0", result.reason)
        self.assertIsNone(repo.find_stock(self.conn, product, location_id=location.id))

    def test_material_receipt_is_not_placed_in_receive_or_address_cell(self):
        from wms import operations as ops
        from wms import repository as repo

        material = self._pk(
            item_type="material",
            product_name="Тест-Дублерин",
            product_size="—",
            product_color="Черный",
            stage_name="Материал",
        )
        result = ops.receive_material(
            material, 2, unit="рул", request_key="test:material:direct-store"
        )
        self.assertTrue(result.ok)
        stock = repo.find_stock(self.conn, material, unit="рул", location_id=None)
        self.assertIsNotNone(stock)
        self.assertEqual(stock.quantity, 2)

    def test_pick_decrements_only_scanned_location_and_is_idempotent(self):
        from wms import operations as ops
        from wms import repository as repo

        storage = repo.get_zone_by_code(self.conn, "STORAGE")
        location = repo.get_location_by_code(self.conn, "ST-PICK-A")
        if location is None:
            location = repo.create_location(self.conn, zone_id=storage.id, code="ST-PICK-A")
        self.conn.commit()

        pk = self._pk(product_name="Тест-Подбор-Из-Ячейки")
        repo.upsert_stock(self.conn, pk, delta=7, location_id=location.id)
        self.conn.commit()

        first = ops.pick(
            pk,
            3,
            from_location_code=location.code,
            request_key="test:pick:one",
        )
        repeated = ops.pick(
            pk,
            3,
            from_location_code=location.code,
            request_key="test:pick:one",
        )
        self.assertTrue(first.ok)
        self.assertTrue(repeated.skipped_duplicate)
        self.assertEqual(repo.find_stock(self.conn, pk, location_id=location.id).quantity, 4)

        too_many = ops.pick(
            pk,
            5,
            from_location_code=location.code,
            request_key="test:pick:too-many",
        )
        self.assertFalse(too_many.ok)
        self.assertIn("доступно только 4", too_many.reason)

    def test_scrap_changes_state(self):
        from wms import operations as ops
        from wms import repository as repo
        pk = self._pk(product_name="Тест-Брюки-4")
        ops.receive_from_production(pk, 8, request_key="test:scrap:rcv")
        result = ops.scrap(pk, 3, reason="брак шва", request_key="test:scrap:1")
        self.assertTrue(result.ok)
        sellable = repo.find_stock(self.conn, pk, item_state="SELLABLE")
        scrapped = repo.find_stock(self.conn, pk, item_state="SCRAPPED")
        self.assertEqual(sellable.quantity, 5)
        self.assertEqual(scrapped.quantity, 3)


if __name__ == "__main__":
    unittest.main()
