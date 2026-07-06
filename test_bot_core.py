import importlib
import os
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent


class IsolatedDatabaseTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.old_db_dir = os.environ.get("DB_DIR")
        self.old_cwd = os.getcwd()
        os.environ["DB_DIR"] = self.temp_dir.name
        os.chdir(self.temp_dir.name)

        for module_name in ["database", "catalog"]:
            sys.modules.pop(module_name, None)

        sys.path.insert(0, str(PROJECT_DIR))
        self.database = importlib.import_module("database")
        self.database.init_db()

    def tearDown(self):
        if self.old_db_dir is None:
            os.environ.pop("DB_DIR", None)
        else:
            os.environ["DB_DIR"] = self.old_db_dir

        if str(PROJECT_DIR) in sys.path:
            sys.path.remove(str(PROJECT_DIR))

        os.chdir(self.old_cwd)
        for module_name in ["database", "catalog"]:
            sys.modules.pop(module_name, None)

        self.temp_dir.cleanup()

    def test_database_uses_isolated_path_and_indexes(self):
        self.assertEqual(Path(self.database.DB_NAME).parent, Path(self.temp_dir.name))
        self.assertEqual(self.database.get_backup_dir(), str(Path(self.temp_dir.name) / "backups"))

        conn = sqlite3.connect(self.database.DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type = 'index' AND name LIKE 'idx_%'"
        )
        indexes = {row[0] for row in cursor.fetchall()}
        conn.close()

        self.assertIn("idx_shifts_employee_date", indexes)
        self.assertIn("idx_operations_navigation", indexes)
        self.assertIn("idx_cutting_batches_product_status", indexes)

    def test_catalog_seed_contains_expected_operations(self):
        operations = self.database.get_active_operations(position="Упаковщик", folder="Нарезание резинки")
        operation_names = {operation[2] for operation in operations}

        self.assertIn("Ползунки — резинка 25 мм", operation_names)
        self.assertIn("Шорты — резинка 25 мм", operation_names)
        self.assertIn("80 (43 см)", self.database.get_preparation_operation_sizes("Шорты — резинка 25 мм"))

    def test_cutting_batch_flow_multiplies_sizes_by_layers(self):
        batch_id = self._create_layout_done_batch()

        self.assertTrue(
            self.database.update_cutting_batch_progress(
                batch_id,
                self.shift_id,
                self.employee_id,
                self.operation_id,
                100,
            )
        )

        rows = self.database.get_cutting_batch_result_rows(batch_id)

        self.assertEqual(
            rows,
            [
                ("80", "Бежевый", 20),
                ("80", "Синий", 10),
                ("86", "Бежевый", 30),
                ("86", "Синий", 15),
            ],
        )

    def test_admin_can_update_and_rollback_cutting_batch(self):
        batch_id = self._create_layout_done_batch()

        progress_result = self.database.admin_update_cutting_batch_progress(batch_id, 50)
        self.assertEqual(progress_result["new_status"], "cutting_in_progress")
        self.assertEqual(progress_result["new_progress"], 50)

        rollback_to_layout = self.database.rollback_cutting_batch(batch_id, "layout_done")
        self.assertEqual(rollback_to_layout["new_status"], "layout_done")

        conn = sqlite3.connect(self.database.DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT status, cutting_progress FROM cutting_batches WHERE id = ?", (batch_id,))
        self.assertEqual(cursor.fetchone(), ("layout_done", 0))
        conn.close()

        rollback_to_contours = self.database.rollback_cutting_batch(batch_id, "contours_done")
        self.assertEqual(rollback_to_contours["new_status"], "contours_done")

        conn = sqlite3.connect(self.database.DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM cutting_batch_colors WHERE batch_id = ?", (batch_id,))
        self.assertEqual(cursor.fetchone()[0], 0)
        cursor.execute("SELECT status, layout_date, cutting_progress FROM cutting_batches WHERE id = ?", (batch_id,))
        self.assertEqual(cursor.fetchone(), ("contours_done", None, 0))
        conn.close()

    def _create_layout_done_batch(self):
        self.database.create_employee(1001, "Тест Раскройщик", "Раскройщик")
        employee = self.database.get_employee_by_telegram_id(1001)
        self.employee_id = employee[0]
        self.database.update_employee_status(self.employee_id, "active")
        shift = self.database.create_shift(self.employee_id)
        self.shift_id = shift["id"]

        contour_operation = self.database.get_active_operations(
            position="Раскройщик",
            folder="Брюки-ползунки",
        )[0]
        self.operation_id = contour_operation[0]

        batch_id = self.database.create_cutting_contour_batch(
            "Брюки-ползунки",
            self.shift_id,
            self.employee_id,
            self.operation_id,
            {"80": 2, "86": 3},
        )

        self.assertTrue(
            self.database.add_cutting_layout(
                batch_id,
                self.shift_id,
                self.employee_id,
                self.operation_id,
                {"Синий": 5, "Бежевый": 10},
            )
        )

        return batch_id


if __name__ == "__main__":
    unittest.main()
