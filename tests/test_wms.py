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
    classify_barcode,
    is_location_barcode,
    location_code_from_barcode,
    LOCATION_PREFIX,
    CONTAINER_PREFIX,
)
from wms.models import Location, OperationResult, ProductKey, WarehouseStock  # noqa: E402


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

    def test_prefixes(self):
        self.assertTrue("LOC:A-01".startswith(LOCATION_PREFIX))
        self.assertTrue("LPN:1".startswith(CONTAINER_PREFIX))


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
