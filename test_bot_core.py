import importlib
import io
import os
import sqlite3
import sys
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent


class IsolatedDatabaseTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.old_db_dir = os.environ.get("DB_DIR")
        self.old_admin_ids = os.environ.get("ADMIN_IDS")
        self.old_cwd = os.getcwd()
        os.environ["DB_DIR"] = self.temp_dir.name
        os.chdir(self.temp_dir.name)

        for module_name in ["database", "catalog", "route_maps", "miniapp_server"]:
            sys.modules.pop(module_name, None)

        sys.path.insert(0, str(PROJECT_DIR))
        self.database = importlib.import_module("database")
        self.database.init_db()

    def tearDown(self):
        if self.old_db_dir is None:
            os.environ.pop("DB_DIR", None)
        else:
            os.environ["DB_DIR"] = self.old_db_dir

        if self.old_admin_ids is None:
            os.environ.pop("ADMIN_IDS", None)
        else:
            os.environ["ADMIN_IDS"] = self.old_admin_ids

        if str(PROJECT_DIR) in sys.path:
            sys.path.remove(str(PROJECT_DIR))

        os.chdir(self.old_cwd)
        for module_name in ["database", "catalog", "route_maps", "miniapp_server"]:
            sys.modules.pop(module_name, None)

        self.temp_dir.cleanup()

    def route_step_index(self, product_name: str, operation_name: str, position: str | None = None):
        route_maps = importlib.import_module("route_maps")

        for index, route_step in enumerate(route_maps.PRODUCT_ROUTE_MAPS[product_name]):
            if route_step["operation"] == operation_name and (position is None or route_step["position"] == position):
                return index

        self.fail(f"Route step not found: {product_name} / {operation_name}")

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
        self.assertIn("idx_feedback_entries_date", indexes)
        self.assertIn("idx_feedback_entries_employee_date", indexes)
        self.assertIn("idx_route_batches_status_step", indexes)
        self.assertIn("idx_route_batch_history_batch", indexes)
        self.assertIn("idx_route_batch_inputs_batch", indexes)
        self.assertIn("idx_route_batch_inputs_stock", indexes)
        self.assertIn("idx_cutting_batches_task", indexes)
        self.assertIn("idx_cutting_batch_matrix_batch", indexes)
        self.assertIn("idx_fabric_stock_color", indexes)
        self.assertIn("idx_production_tasks_status", indexes)
        self.assertIn("idx_production_task_items_task", indexes)
        self.assertIn("idx_production_task_fabric_rolls_task", indexes)
        self.assertIn("idx_warehouse_stock_type_position", indexes)
        self.assertIn("idx_warehouse_stock_product", indexes)

    def test_catalog_seed_contains_expected_operations(self):
        operations = self.database.get_active_operations(position="Упаковщик", folder="Нарезание резинки")
        operation_names = {operation[2] for operation in operations}

        self.assertIn("Ползунки — резинка 25 мм", operation_names)
        self.assertIn("Шорты — резинка 25 мм", operation_names)
        self.assertIn("80 (43 см)", self.database.get_preparation_operation_sizes("Шорты — резинка 25 мм"))

        dublerin_operations = self.database.get_active_operations(
            position="Упаковщик",
            folder="Нарезание дублерина",
        )
        self.assertIn("Кардиганы — дублерин 25 мм", {operation[2] for operation in dublerin_operations})
        self.assertEqual(
            self.database.get_preparation_operation_sizes("Кардиганы — дублерин 25 мм"),
            [
                "92 (100 см)",
                "98 (100 см)",
                "104 (100 см)",
                "110 (100 см)",
                "116 (100 см)",
                "122 (100 см)",
                "134 (100 см)",
                "140 (100 см)",
                "146 (100 см)",
                "152 (100 см)",
                "158 (100 см)",
                "164 (100 см)",
            ],
        )
        self.assertEqual(
            self.database.get_preparation_operation_colors("Кардиганы — дублерин 25 мм"),
            ["Черный", "Белый"],
        )

        for operation_name in ["Установка петель", "Установка пуговиц"]:
            preparation_operations = self.database.get_active_operations(
                position="Упаковщик",
                folder=operation_name,
            )
            self.assertEqual([operation[2] for operation in preparation_operations], [operation_name])
            self.assertTrue(self.database.is_preparation_operation_folder(operation_name))
            self.assertEqual(
                self.database.get_preparation_operation_sizes(operation_name),
                ["92", "98", "104", "110", "116", "122", "134", "140", "146", "152", "158", "164"],
            )
            self.assertEqual(
                self.database.get_preparation_operation_colors(operation_name),
                ["Голубой", "Бежевый", "Капучино", "Темно-синий", "Брауни", "Светло-серый", "Черный"],
            )

    def test_route_maps_cover_catalog_products_and_operations(self):
        catalog = importlib.import_module("catalog")
        route_maps = importlib.import_module("route_maps")
        known_operations = {
            *catalog.CUTTING_OPERATIONS,
            *catalog.PACKING_OPERATIONS,
            *(operation[2] for operation in catalog.PRODUCTION_OPERATIONS),
        }

        self.assertEqual(set(route_maps.PRODUCT_ROUTE_MAPS), set(catalog.CUTTING_PRODUCTS))

        for product_name, steps in route_maps.PRODUCT_ROUTE_MAPS.items():
            self.assertGreater(len(steps), 0, product_name)

            for route_step in steps:
                self.assertIn(route_step["operation"], known_operations, product_name)
                self.assertIn(route_step["position"], {"Раскройщик", "Упаковщик", "Швея"}, product_name)
                self.assertTrue(route_step["status_after"], product_name)

    def test_route_batch_flow_advances_and_writes_history(self):
        route_maps = importlib.import_module("route_maps")
        self.database.create_employee(4004, "Тест Маршрут", "Раскройщик")
        employee = self.database.get_employee_by_telegram_id(4004)
        employee_id = employee[0]
        self.database.update_employee_status(employee_id, "active")

        batch = self.database.create_route_batch(
            "Шорты",
            "110",
            "Голубой",
            12,
            employee_id,
        )
        first_step = route_maps.PRODUCT_ROUTE_MAPS["Шорты"][0]

        self.assertIsNotNone(batch)
        self.assertEqual(batch["route_step_index"], 0)
        self.assertEqual(batch["status"], "active")

        updated = self.database.complete_route_batch_step(
            batch["id"],
            employee_id,
            first_step["operation"],
            first_step["position"],
            1,
            "active",
        )

        self.assertEqual(updated["route_step_index"], 1)
        self.assertEqual(updated["status"], "active")

        conn = sqlite3.connect(self.database.DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT operation_name, position, quantity FROM route_batch_history WHERE batch_id = ?",
            (batch["id"],),
        )
        self.assertEqual(cursor.fetchone(), (first_step["operation"], first_step["position"], 12))
        conn.close()

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

    def test_cutting_progress_is_atomic_idempotent_and_backfilled(self):
        batch_id = self._create_layout_done_batch()
        cutting_operation = next(
            operation
            for operation in self.database.get_active_operations(
                position="Раскройщик",
                folder="Брюки-ползунки",
            )
            if operation[2] == "Раскрой"
        )
        cutting_operation_id = cutting_operation[0]

        self.assertEqual(cutting_operation[3], "%")
        self.assertTrue(
            self.database.update_cutting_batch_progress(
                batch_id,
                self.shift_id,
                self.employee_id,
                cutting_operation_id,
                100,
            )
        )
        self.assertTrue(
            self.database.update_cutting_batch_progress(
                batch_id,
                self.shift_id,
                self.employee_id,
                cutting_operation_id,
                100,
            )
        )
        self.assertIn(
            ("Брюки-ползунки: Раскрой", "готовность", "без цвета", 100, "%"),
            self.database.get_shift_report(self.shift_id),
        )

        conn = sqlite3.connect(self.database.DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            """
            DELETE FROM shift_operations
            WHERE shift_id = ?
              AND operation_id = ?
              AND product_size = 'готовность'
              AND product_color = 'без цвета'
            """,
            (self.shift_id, cutting_operation_id),
        )
        conn.commit()
        conn.close()

        self.database.init_db()
        self.assertIn(
            ("Брюки-ползунки: Раскрой", "готовность", "без цвета", 100, "%"),
            self.database.get_shift_report(self.shift_id),
        )

    def test_cutting_batch_at_75_percent_stays_visible_for_cutter(self):
        miniapp_server = importlib.import_module("miniapp_server")
        batch_id = self._create_layout_done_batch()

        self.assertTrue(
            self.database.update_cutting_batch_progress(
                batch_id,
                self.shift_id,
                self.employee_id,
                self.operation_id,
                75,
            )
        )

        state = miniapp_server.get_production_state_for_telegram(1001)
        cutting_tasks = [
            task
            for task in state["cutting_tasks"]
            if task["id"] == batch_id and task["stage"] == "cutting"
        ]

        self.assertEqual(len(cutting_tasks), 1)
        self.assertEqual(cutting_tasks[0]["progress"], 75)
        self.assertEqual(cutting_tasks[0]["status_text"], "готовность 75%")

    def test_incomplete_cutting_survives_closed_shift_and_can_be_reopened_once(self):
        batch_id = self._create_layout_done_batch()
        shift_date = "2026-01-01"
        self.database.close_shift(self.shift_id)

        self.assertEqual(
            [row[0] for row in self.database.get_cutting_batches_for_cutting("Брюки-ползунки")],
            [batch_id],
        )

        conn = sqlite3.connect(self.database.DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE shifts SET shift_date = ? WHERE id = ?",
            (shift_date, self.shift_id),
        )
        restored = self.database.restore_incomplete_cutting_shift(
            cursor,
            repair_key="test_restore_incomplete_cutting",
            batch_id=batch_id,
            shift_id=self.shift_id,
            expected_shift_date=shift_date,
        )
        restored_again = self.database.restore_incomplete_cutting_shift(
            cursor,
            repair_key="test_restore_incomplete_cutting",
            batch_id=batch_id,
            shift_id=self.shift_id,
            expected_shift_date=shift_date,
        )
        conn.commit()
        cursor.execute(
            "SELECT status, end_time, total_minutes, closed_at FROM shifts WHERE id = ?",
            (self.shift_id,),
        )
        shift = cursor.fetchone()
        conn.close()

        self.assertTrue(restored)
        self.assertFalse(restored_again)
        self.assertEqual(shift, ("open", None, None, None))
        self.assertEqual(
            self.database.get_open_shift_for_today(self.employee_id)[0],
            self.shift_id,
        )

    def test_production_task_creates_matrix_cutting_batch(self):
        task = self.database.create_production_task(
            "Шорты",
            ["80", "92"],
            ["Бежевый", "Синий"],
            None,
        )
        self.assertIsNotNone(task)

        batch_id = self.database.create_cutting_contour_batch_for_task(
            task["id"],
            "Шорты",
            1,
            1,
            1,
            {
                ("80", "Бежевый"): 2,
                ("92", "Бежевый"): 3,
                ("80", "Синий"): 4,
                ("92", "Синий"): 0,
            },
        )

        self.assertIsNotNone(batch_id)
        self.assertEqual(self.database.get_production_task_by_id(task["id"])["status"], "contours_done")
        self.assertEqual(
            self.database.get_cutting_batch_task_options(batch_id),
            (["80", "92"], ["Бежевый", "Синий"]),
        )
        self.assertEqual(len(self.database.get_cutting_batches_for_layout("Шорты")[0]), 7)

        self.assertTrue(
            self.database.add_cutting_layout(
                batch_id,
                1,
                1,
                1,
                {"Бежевый": 3, "Синий": 2},
            )
        )
        self.assertEqual(self.database.get_production_task_by_id(task["id"])["status"], "in_cutting")
        preparation_batches = self.database.get_active_route_batches()
        elastic_step_index = self.route_step_index("Шорты", "Шорты — резинка 25 мм", "Упаковщик")
        self.assertEqual({batch["route_step_index"] for batch in preparation_batches}, {elastic_step_index})
        self.assertEqual(
            sorted((batch["product_size"], batch["product_color"], batch["quantity"]) for batch in preparation_batches),
            [
                ("80 (43 см)", "Черный", 14),
                ("92 (45 см)", "Черный", 9),
            ],
        )

        self.assertTrue(self.database.update_cutting_batch_progress(batch_id, 1, 1, 1, 100))
        self.assertEqual(
            self.database.get_cutting_batch_result_rows(batch_id),
            [
                ("80", "Бежевый", 6),
                ("80", "Синий", 8),
                ("92", "Бежевый", 9),
            ],
        )

        self.assertTrue(self.database.mark_cutting_batch_formed(batch_id, 1, 1, 1))
        self.assertEqual(self.database.get_production_task_by_id(task["id"])["status"], "formed")

        conn = sqlite3.connect(self.database.DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT product_size, product_color, contour_quantity, formed_quantity
            FROM production_task_items
            WHERE task_id = ?
            ORDER BY product_color, CAST(product_size AS INTEGER)
            """,
            (task["id"],),
        )
        self.assertEqual(
            cursor.fetchall(),
            [
                ("80", "Бежевый", 2, 6),
                ("92", "Бежевый", 3, 9),
                ("80", "Синий", 4, 8),
                ("92", "Синий", 0, 0),
            ],
        )
        conn.close()
        warehouse_rows = self.database.get_warehouse_stock_rows()
        self.assertEqual(
            {
                (row["product_size"], row["product_color"], row["quantity"], row["stage_name"], row["ready_for_position"])
                for row in warehouse_rows
            },
            {
                ("80", "Бежевый", 6, "Раскроенные", "Швея"),
                ("92", "Бежевый", 9, "Раскроенные", "Швея"),
                ("80", "Синий", 8, "Раскроенные", "Швея"),
            },
        )
        conn = sqlite3.connect(self.database.DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT product_size, product_color, quantity, movement_type, source_type, source_id
            FROM warehouse_stock_movements
            ORDER BY product_color, CAST(product_size AS INTEGER)
            """
        )
        self.assertEqual(
            cursor.fetchall(),
            [
                ("80", "Бежевый", 6, "receipt", "cutting_batch", batch_id),
                ("92", "Бежевый", 9, "receipt", "cutting_batch", batch_id),
                ("80", "Синий", 8, "receipt", "cutting_batch", batch_id),
            ],
        )
        conn.close()

    def test_layout_creates_dublerin_and_dubling_preparation_tasks(self):
        task = self.database.create_production_task(
            "Жакет для девочек",
            ["98"],
            ["Черный"],
            None,
        )
        batch_id = self.database.create_cutting_contour_batch_for_task(
            task["id"],
            "Жакет для девочек",
            1,
            1,
            1,
            {("98", "Черный"): 5},
        )

        self.assertTrue(
            self.database.add_cutting_layout(
                batch_id,
                1,
                1,
                1,
                {"Черный": 2},
            )
        )

        dublerin_index = self.route_step_index("Жакет для девочек", "Жакеты — дублерин 80 мм", "Упаковщик")
        dubling_index = self.route_step_index("Жакет для девочек", "Жакет для девочек — Дублирование", "Упаковщик")
        preparation_batches = self.database.get_active_route_batches()

        self.assertEqual(
            sorted((batch["route_step_index"], batch["product_size"], batch["product_color"], batch["quantity"]) for batch in preparation_batches),
            [
                (dublerin_index, "98 (28,5 см)", "Черный", 10),
                (dubling_index, "98", "Черный", 10),
            ],
        )

    def test_miniapp_production_creates_task_and_submits_contours(self):
        os.environ["ADMIN_IDS"] = "9001"
        miniapp_server = importlib.import_module("miniapp_server")

        self.database.create_employee(9002, "Тест Раскройщик Миниапп", "Раскройщик")
        cutter = self.database.get_employee_by_telegram_id(9002)
        cutter_id = cutter[0]
        self.database.update_employee_status(cutter_id, "active")
        shift = self.database.create_shift(cutter_id)

        fabric_result = miniapp_server.add_fabric_receipt_for_telegram(
            9001,
            {
                "material_name": "Ткань",
                "product_color": "Бежевый",
                "quantity": "12",
            },
        )
        self.assertTrue(fabric_result["ok"], fabric_result)
        self.assertEqual(len(fabric_result["production"]["fabric_stock"]), 1)

        task_result = miniapp_server.create_production_task_for_telegram(
            9001,
            {
                "product_name": "Шорты",
                "sizes": ["80", "92"],
                "colors": ["Бежевый"],
                "fabric_rolls": {"Бежевый": "2"},
                "attachment": {
                    "file_name": "layout.pdf",
                    "mime_type": "",
                    "content_base64": "ZmlsZQ==",
                },
            },
        )
        self.assertTrue(task_result["ok"], task_result)
        self.assertEqual(task_result["production"]["fabric_stock"][0]["quantity"], 10)

        task_id = self.database.get_active_production_tasks()[0][0]
        cutter_state = miniapp_server.get_production_state_for_telegram(9002)
        self.assertTrue(cutter_state["can_contours"])
        self.assertEqual(cutter_state["contour_tasks"][0]["id"], task_id)
        self.assertEqual(cutter_state["contour_tasks"][0]["attachment"]["mime_type"], "application/pdf")
        self.assertEqual(cutter_state["contour_tasks"][0]["fabric_rolls"][0]["rolls"], 2)

        contour_result = miniapp_server.submit_production_contours_for_telegram(
            9002,
            {
                "task_id": task_id,
                "quantities": {
                    "80|Бежевый": "4",
                    "92|Бежевый": "6",
                },
            },
        )
        self.assertTrue(contour_result["ok"], contour_result)
        self.assertEqual(self.database.get_production_task_by_id(task_id)["status"], "contours_done")
        self.assertEqual(len(self.database.get_shift_report(shift["id"])), 2)

    def test_miniapp_admin_creates_order_tasks(self):
        os.environ["ADMIN_IDS"] = "9001"
        miniapp_server = importlib.import_module("miniapp_server")
        self.database.add_fabric_receipt("Ткань", "Бежевый", 8, None)
        self.database.add_fabric_receipt("Ткань", "Фуксия", 12, None)

        cutting_result = miniapp_server.create_order_task_for_telegram(
            9001,
            {
                "product_name": "Шорты",
                "task_type": "cutting",
                "material_name": "Ткань",
                "sizes": ["80", "92"],
                "colors": ["Бежевый", "Фуксия"],
                "fabric_rolls": {"Бежевый": "1", "Фуксия": "2"},
                "attachment": {
                    "file_name": "cutting.xlsx",
                    "mime_type": "application/octet-stream",
                    "content_base64": "ZmlsZQ==",
                },
            },
        )

        self.assertTrue(cutting_result["ok"], cutting_result)
        self.assertEqual(len(self.database.get_active_production_tasks()), 1)
        self.assertEqual(set(self.database.get_production_task_options(1)[1]), {"Бежевый", "Фуксия"})
        self.assertEqual(
            {(row["product_color"], row["unit"]): row["quantity"] for row in cutting_result["production"]["fabric_stock"]},
            {("Бежевый", "рул"): 7, ("Фуксия", "рул"): 10},
        )
        self.assertEqual(
            {(row["product_color"], row["rolls"]) for row in cutting_result["production"]["tasks"][0]["fabric_rolls"]},
            {("Бежевый", 1), ("Фуксия", 2)},
        )
        self.assertEqual(
            cutting_result["production"]["tasks"][0]["attachment"]["mime_type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        stock_items = []

        for product_size in ["86", "92"]:
            for product_color in ["Бежевый", "Голубой"]:
                stock_row = self.database.add_warehouse_stock(
                    "semifinished",
                    "Легинсы",
                    product_size,
                    product_color,
                    "Раскроенные",
                    "Швея",
                    10,
                    None,
                )
                stock_items.append({"stock_id": stock_row["id"], "quantity": "7"})

        sewing_step_index = self.route_step_index("Легинсы", "Сборка на оверлоке", "Швея")
        route_result = miniapp_server.create_order_task_for_telegram(
            9001,
            {
                "product_name": "Легинсы",
                "task_type": "route",
                "route_step_index": sewing_step_index,
                "stock_items": stock_items,
            },
        )

        self.assertTrue(route_result["ok"], route_result)
        batches = self.database.get_active_route_batches()
        self.assertEqual(len(batches), 4)
        self.assertEqual({batch["quantity"] for batch in batches}, {7})
        self.assertEqual({batch["route_step_index"] for batch in batches}, {sewing_step_index})
        self.assertEqual({row["quantity"] for row in self.database.get_warehouse_stock_rows()}, {3})
        self.assertIn("Сборка на оверлоке", {task["operation"] for task in route_result["routes"]["tasks"]})

    def test_elastic_preparation_completion_creates_sewing_task(self):
        miniapp_server = importlib.import_module("miniapp_server")
        self.database.create_employee(9003, "Тест Упаковщик", "Упаковщик")
        self.database.create_employee(9004, "Тест Швея", "Швея")
        packer = self.database.get_employee_by_telegram_id(9003)
        seamstress = self.database.get_employee_by_telegram_id(9004)
        self.database.update_employee_status(packer[0], "active")
        self.database.update_employee_status(seamstress[0], "active")
        elastic_step_index = self.route_step_index("Шорты", "Шорты — резинка 25 мм", "Упаковщик")

        batch = self.database.create_route_batch(
            "Шорты",
            "80 (43 см)",
            "Черный",
            14,
            packer[0],
            route_step_index=elastic_step_index,
        )
        result = miniapp_server.complete_route_task_for_telegram(9003, batch["id"])

        self.assertTrue(result["ok"], result)
        self.assertIn("Следующее задание создано", result["message"])
        active_batches = self.database.get_active_route_batches()
        self.assertEqual(len(active_batches), 1)

        sewing_batch = active_batches[0]
        sewing_step = miniapp_server.get_route_step("Шорты", sewing_batch["route_step_index"])
        self.assertEqual(sewing_step["operation"], "Сшивание резинок в кольцо")
        self.assertEqual(sewing_batch["quantity"], 14)
        self.assertIsNotNone(sewing_batch["source_stock_id"])
        self.assertEqual(self.database.get_warehouse_stock_by_id(sewing_batch["source_stock_id"])["quantity"], 0)

        seamstress_tasks = miniapp_server.get_route_tasks_for_telegram(9004)
        self.assertTrue(seamstress_tasks["ok"], seamstress_tasks)
        self.assertEqual(seamstress_tasks["tasks"][0]["category"], "Подготовка")

    def test_employee_starts_and_completes_route_task_with_defects(self):
        miniapp_server = importlib.import_module("miniapp_server")
        self.database.create_employee(9013, "Тест Упаковщик", "Упаковщик")
        packer = self.database.get_employee_by_telegram_id(9013)
        self.database.update_employee_status(packer[0], "active")
        elastic_step_index = self.route_step_index("Шорты", "Шорты — резинка 25 мм", "Упаковщик")
        batch = self.database.create_route_batch(
            "Шорты",
            "80 (43 см)",
            "Черный",
            10,
            None,
            route_step_index=elastic_step_index,
        )

        free_tasks = miniapp_server.get_route_tasks_for_telegram(9013)
        self.assertTrue(free_tasks["ok"], free_tasks)
        self.assertEqual(free_tasks["tasks"][0]["status_text"], "Свободно")
        self.assertTrue(free_tasks["tasks"][0]["can_take"])

        started = miniapp_server.start_route_task_for_telegram(9013, batch["id"])
        self.assertTrue(started["ok"], started)
        started_task = started["tasks"][0]
        self.assertEqual(started_task["status_text"], "В работе")
        self.assertEqual(started_task["assigned_employee_name"], "Тест Упаковщик")
        self.assertTrue(started_task["can_complete"])

        completed = miniapp_server.complete_route_task_for_telegram(
            9013,
            batch["id"],
            {"good_quantity": 9, "defect_quantity": 1},
        )
        self.assertTrue(completed["ok"], completed)
        completed_batch = self.database.get_route_batch_by_id(batch["id"])
        self.assertEqual(completed_batch["status"], "done")
        self.assertEqual(completed_batch["assigned_employee_id"], packer[0])
        self.assertEqual(completed_batch["good_quantity"], 9)
        self.assertEqual(completed_batch["defect_quantity"], 1)
        self.assertEqual(completed["completed_tasks"][0]["status_text"], "Завершено")
        self.assertEqual(completed["completed_tasks"][0]["good_quantity"], 9)
        self.assertEqual(completed["completed_tasks"][0]["defect_quantity"], 1)

    def test_open_shift_survives_midnight_and_remains_current(self):
        miniapp_server = importlib.import_module("miniapp_server")
        self.database.create_employee(9040, "Тест Ночная Смена", "Швея")
        employee = self.database.get_employee_by_telegram_id(9040)
        self.database.update_employee_status(employee[0], "active")
        shift = self.database.create_shift(employee[0])
        yesterday = (self.database.local_today() - timedelta(days=1)).isoformat()

        conn = sqlite3.connect(self.database.DB_NAME)
        conn.execute("UPDATE shifts SET shift_date = ? WHERE id = ?", (yesterday, shift["id"]))
        conn.commit()
        conn.close()

        open_shift = self.database.get_open_shift_for_today(employee[0])
        self.assertEqual(open_shift[0], shift["id"])
        self.assertEqual(open_shift[2], yesterday)

        reopened = miniapp_server.open_shift_for_telegram(9040)
        self.assertTrue(reopened["ok"], reopened)
        self.assertEqual(reopened["message"], "Смена уже открыта.")
        self.assertEqual(reopened["shift"]["id"], shift["id"])

        report = miniapp_server.get_current_report_for_telegram(9040)
        self.assertEqual(report["shift"]["id"], shift["id"])

        conn = sqlite3.connect(self.database.DB_NAME)
        self.assertEqual(conn.execute("SELECT COUNT(*) FROM shifts WHERE employee_id = ?", (employee[0],)).fetchone()[0], 1)
        conn.close()

    def test_miniapp_excel_export_contains_detailed_production_sheets(self):
        os.environ["ADMIN_IDS"] = "9001"
        miniapp_server = importlib.import_module("miniapp_server")
        self.database.create_employee(9041, "Тест Выгрузка", "Упаковщик")
        employee = self.database.get_employee_by_telegram_id(9041)
        self.database.update_employee_status(employee[0], "active")
        self.database.create_shift(employee[0])
        self.database.add_fabric_receipt("Ткань", "Черный", 3, None, "Тестовая приёмка")
        stock = self.database.add_warehouse_stock(
            "semifinished", "Шорты", "80", "Черный", "Раскроенные", "Упаковщик", 10, None,
        )
        step_index = self.route_step_index("Шорты", "Шорты — резинка 25 мм", "Упаковщик")
        batch = self.database.create_route_batch_with_inputs(
            "Шорты", "80", "Черный", 10, None, step_index,
            [{"stock_id": stock["id"], "quantity": 10, "input_role": "main"}],
        )
        self.assertIsNotNone(batch)
        self.assertTrue(miniapp_server.start_route_task_for_telegram(9041, batch["id"])["ok"])
        completed = miniapp_server.complete_route_task_for_telegram(
            9041, batch["id"], {"good_quantity": 9, "defect_quantity": 1},
        )
        self.assertTrue(completed["ok"], completed)

        today = self.database.local_today().isoformat()
        export = miniapp_server.export_admin_report_for_telegram(
            9001, {"report_type": "period", "start_date": today, "end_date": today},
        )
        self.assertTrue(export["ok"], export)

        from openpyxl import load_workbook
        workbook = load_workbook(io.BytesIO(export["content"]), data_only=False)
        expected_sheets = {
            "Сводка", "Смены по дням", "Операции", "Раскрой", "Пошив", "Упаковка",
            "Задания раскроя", "Маршрутные задания", "Входы заданий", "Брак",
            "Движения склада", "Движения материалов", "Остатки склада", "Остатки материалов",
        }
        self.assertTrue(expected_sheets.issubset(set(workbook.sheetnames)))

        route_sheet = workbook["Маршрутные задания"]
        route_values = list(route_sheet.values)
        self.assertEqual(route_values[1][9:14], (10, 9, 1, 90, 10))
        self.assertEqual(route_values[1][15], "Тест Выгрузка")
        defect_values = list(workbook["Брак"].values)
        self.assertEqual(defect_values[1][8], 1)
        self.assertEqual(defect_values[1][9], "Нет данных")
        self.assertGreaterEqual(workbook["Движения склада"].max_row, 3)
        self.assertGreaterEqual(workbook["Движения материалов"].max_row, 2)

    def test_miniapp_full_production_cycle_is_strictly_sequential(self):
        os.environ["ADMIN_IDS"] = "9001"
        miniapp_server = importlib.import_module("miniapp_server")
        route_maps = importlib.import_module("route_maps")

        employees = {
            "Раскройщик": (9002, "Тест Раскройщик Цикл"),
            "Швея": (9003, "Тест Швея Цикл"),
            "Упаковщик": (9004, "Тест Упаковщик Цикл"),
        }
        employee_rows = {}

        for position, (telegram_id, full_name) in employees.items():
            self.database.create_employee(telegram_id, full_name, position)
            employee = self.database.get_employee_by_telegram_id(telegram_id)
            self.database.update_employee_status(employee[0], "active")
            employee_rows[position] = employee

        self.database.create_shift(employee_rows["Раскройщик"][0])

        receipt = miniapp_server.add_fabric_receipt_for_telegram(
            9001,
            {"material_name": "Ткань", "product_color": "Бежевый", "quantity": "3"},
        )
        self.assertTrue(receipt["ok"], receipt)

        cutting_task = miniapp_server.create_order_task_for_telegram(
            9001,
            {
                "product_name": "Легинсы",
                "task_type": "cutting",
                "material_name": "Ткань",
                "sizes": ["86"],
                "colors": ["Бежевый"],
                "fabric_rolls": {"Бежевый": "1"},
            },
        )
        self.assertTrue(cutting_task["ok"], cutting_task)
        self.assertEqual(cutting_task["production"]["fabric_stock"][0]["quantity"], 2)
        task_id = self.database.get_active_production_tasks()[0][0]

        blocked_layout = miniapp_server.submit_cutting_stage_for_telegram(
            9002,
            {"stage": "layout", "batch_id": task_id, "color_layers": {"Бежевый": "2"}},
        )
        self.assertFalse(blocked_layout["ok"], blocked_layout)

        contours = miniapp_server.submit_cutting_stage_for_telegram(
            9002,
            {"stage": "contours", "task_id": task_id, "quantities": {"86|Бежевый": "5"}},
        )
        self.assertTrue(contours["ok"], contours)
        batch_id = self.database.get_cutting_batches_for_layout("Легинсы")[0][0]

        blocked_cutting = miniapp_server.submit_cutting_stage_for_telegram(
            9002,
            {"stage": "cutting", "batch_id": batch_id, "progress": "100"},
        )
        self.assertFalse(blocked_cutting["ok"], blocked_cutting)

        layout = miniapp_server.submit_cutting_stage_for_telegram(
            9002,
            {"stage": "layout", "batch_id": batch_id, "color_layers": {"Бежевый": "2"}},
        )
        self.assertTrue(layout["ok"], layout)

        partial_cutting = miniapp_server.submit_cutting_stage_for_telegram(
            9002,
            {"stage": "cutting", "batch_id": batch_id, "progress": "50"},
        )
        self.assertTrue(partial_cutting["ok"], partial_cutting)
        blocked_formation = miniapp_server.submit_cutting_stage_for_telegram(
            9002,
            {"stage": "formation", "batch_id": batch_id},
        )
        self.assertFalse(blocked_formation["ok"], blocked_formation)

        completed_cutting = miniapp_server.submit_cutting_stage_for_telegram(
            9002,
            {"stage": "cutting", "batch_id": batch_id, "progress": "100"},
        )
        self.assertTrue(completed_cutting["ok"], completed_cutting)
        formation = miniapp_server.submit_cutting_stage_for_telegram(
            9002,
            {"stage": "formation", "batch_id": batch_id},
        )
        self.assertTrue(formation["ok"], formation)

        stock = next(row for row in self.database.get_warehouse_stock_rows() if row["quantity"] > 0)
        self.assertEqual(
            (stock["item_type"], stock["stage_name"], stock["ready_for_position"], stock["quantity"]),
            ("semifinished", "Раскроенные", "Швея", 10),
        )

        route_steps = route_maps.PRODUCT_ROUTE_MAPS["Легинсы"]
        first_step_index = len(route_maps.CUTTING_ROUTE)
        skipped = miniapp_server.create_order_task_for_telegram(
            9001,
            {
                "product_name": "Легинсы",
                "task_type": "route",
                "route_step_index": first_step_index + 1,
                "stock_items": [{"stock_id": stock["id"], "quantity": "10"}],
            },
        )
        self.assertFalse(skipped["ok"], skipped)
        self.assertEqual(self.database.get_warehouse_stock_by_id(stock["id"])["quantity"], 10)

        position_telegram_ids = {position: data[0] for position, data in employees.items()}

        for step_index in range(first_step_index, len(route_steps)):
            positive_stock = [row for row in self.database.get_warehouse_stock_rows() if row["quantity"] > 0]
            self.assertEqual(len(positive_stock), 1, (step_index, positive_stock))
            source_stock = positive_stock[0]

            if step_index + 1 < len(route_steps) and route_steps[step_index + 1]["position"] == route_steps[step_index]["position"]:
                skipped = miniapp_server.create_order_task_for_telegram(
                    9001,
                    {
                        "product_name": "Легинсы",
                        "task_type": "route",
                        "route_step_index": step_index + 1,
                        "stock_items": [{"stock_id": source_stock["id"], "quantity": "10"}],
                    },
                )
                self.assertFalse(skipped["ok"], (step_index, skipped))

            created = miniapp_server.create_order_task_for_telegram(
                9001,
                {
                    "product_name": "Легинсы",
                    "task_type": "route",
                    "route_step_index": step_index,
                    "stock_items": [{"stock_id": source_stock["id"], "quantity": "10"}],
                },
            )
            self.assertTrue(created["ok"], (step_index, created))
            active_batch = self.database.get_active_route_batches()[0]
            telegram_id = position_telegram_ids[route_steps[step_index]["position"]]
            started = miniapp_server.start_route_task_for_telegram(telegram_id, active_batch["id"])
            self.assertTrue(started["ok"], (step_index, started))
            completed = miniapp_server.complete_route_task_for_telegram(
                telegram_id,
                active_batch["id"],
                {"good_quantity": 10, "defect_quantity": 0},
            )
            self.assertTrue(completed["ok"], (step_index, completed))

        final_stock = [row for row in self.database.get_warehouse_stock_rows() if row["quantity"] > 0]
        self.assertEqual(len(final_stock), 1)
        self.assertEqual(
            (
                final_stock[0]["item_type"],
                final_stock[0]["stage_name"],
                final_stock[0]["ready_for_position"],
                final_stock[0]["quantity"],
            ),
            ("finished", "На складе", "Склад", 10),
        )
        self.assertEqual(self.database.get_active_route_batches(), [])

    def test_miniapp_route_task_combines_main_and_component_inputs(self):
        os.environ["ADMIN_IDS"] = "9001"
        miniapp_server = importlib.import_module("miniapp_server")
        self.database.create_employee(9014, "Тест Швея Компоненты", "Швея")
        seamstress = self.database.get_employee_by_telegram_id(9014)
        self.database.update_employee_status(seamstress[0], "active")

        main_stock = self.database.add_warehouse_stock(
            "semifinished",
            "Шорты",
            "80",
            "Бежевый",
            "Раскроенные",
            "Швея",
            10,
            None,
        )
        second_main_stock = self.database.add_warehouse_stock(
            "semifinished",
            "Шорты",
            "86",
            "Голубой",
            "Раскроенные",
            "Швея",
            15,
            None,
        )
        elastic_stock = self.database.add_warehouse_stock(
            "semifinished",
            "Шорты",
            "80, 86 (43 см)",
            "Черный",
            "Резинка сшита в кольцо",
            "Швея",
            25,
            None,
        )
        assembly_step_index = self.route_step_index("Шорты", "Сборка шорт на оверлоке", "Швея")

        missing_component = miniapp_server.create_order_task_for_telegram(
            9001,
            {
                "product_name": "Шорты",
                "task_type": "route",
                "route_step_index": assembly_step_index,
                "stock_items": [{"stock_id": main_stock["id"], "quantity": "10"}],
            },
        )
        self.assertFalse(missing_component["ok"], missing_component)
        self.assertEqual(self.database.get_warehouse_stock_by_id(main_stock["id"])["quantity"], 10)
        self.assertEqual(self.database.get_active_route_batches(), [])

        created = miniapp_server.create_order_task_for_telegram(
            9001,
            {
                "product_name": "Шорты",
                "task_type": "route",
                "route_step_index": assembly_step_index,
                "stock_items": [
                    {"stock_id": main_stock["id"], "quantity": "10"},
                    {"stock_id": second_main_stock["id"], "quantity": "15"},
                    {"stock_id": elastic_stock["id"], "quantity": "25"},
                ],
            },
        )
        self.assertTrue(created["ok"], created)
        batches = self.database.get_active_route_batches()
        self.assertEqual(len(batches), 2)
        inputs = [
            input_row
            for batch in batches
            for input_row in self.database.get_route_batch_inputs(batch["id"])
        ]
        self.assertEqual(
            {(row["input_role"], row["stage_name"], row["quantity"]) for row in inputs},
            {
                ("main", "Раскроенные", 10),
                ("main", "Раскроенные", 15),
                ("component", "Резинка сшита в кольцо", 10),
                ("component", "Резинка сшита в кольцо", 15),
            },
        )
        self.assertEqual(self.database.get_warehouse_stock_by_id(main_stock["id"])["quantity"], 0)
        self.assertEqual(self.database.get_warehouse_stock_by_id(second_main_stock["id"])["quantity"], 0)
        self.assertEqual(self.database.get_warehouse_stock_by_id(elastic_stock["id"])["quantity"], 0)

        employee_tasks = miniapp_server.get_route_tasks_for_telegram(9014)
        self.assertTrue(employee_tasks["ok"], employee_tasks)
        self.assertEqual(len(employee_tasks["tasks"]), 2)
        self.assertTrue(all(len(task["inputs"]) == 2 for task in employee_tasks["tasks"]))

        for batch in batches:
            deleted = miniapp_server.delete_order_task_for_telegram(
                9001,
                {"task_kind": "route", "task_id": batch["id"]},
            )
            self.assertTrue(deleted["ok"], deleted)

        self.assertEqual(self.database.get_warehouse_stock_by_id(main_stock["id"])["quantity"], 10)
        self.assertEqual(self.database.get_warehouse_stock_by_id(second_main_stock["id"])["quantity"], 15)
        self.assertEqual(self.database.get_warehouse_stock_by_id(elastic_stock["id"])["quantity"], 25)

    def test_miniapp_admin_deletes_order_tasks(self):
        os.environ["ADMIN_IDS"] = "9001"
        miniapp_server = importlib.import_module("miniapp_server")
        self.database.add_fabric_receipt("Ткань", "Бежевый", 5, None)

        cutting_result = miniapp_server.create_order_task_for_telegram(
            9001,
            {
                "product_name": "Шорты",
                "task_type": "cutting",
                "material_name": "Ткань",
                "sizes": ["80"],
                "colors": ["Бежевый"],
                "fabric_rolls": {"Бежевый": "2"},
            },
        )
        self.assertTrue(cutting_result["ok"], cutting_result)
        self.assertEqual(cutting_result["production"]["fabric_stock"][0]["quantity"], 3)
        stock_row = self.database.add_warehouse_stock(
            "semifinished",
            "Легинсы",
            "86",
            "Бежевый",
            "Раскроенные",
            "Швея",
            5,
            None,
        )

        sewing_step_index = self.route_step_index("Легинсы", "Сборка на оверлоке", "Швея")
        route_result = miniapp_server.create_order_task_for_telegram(
            9001,
            {
                "product_name": "Легинсы",
                "task_type": "route",
                "route_step_index": sewing_step_index,
                "stock_items": [{"stock_id": stock_row["id"], "quantity": "3"}],
            },
        )
        self.assertTrue(route_result["ok"], route_result)

        production_id = self.database.get_active_production_tasks()[0][0]
        route_id = self.database.get_active_route_batches()[0]["id"]

        delete_production = miniapp_server.delete_order_task_for_telegram(
            9001,
            {"task_kind": "production", "task_id": production_id},
        )
        self.assertTrue(delete_production["ok"], delete_production)
        self.assertEqual(self.database.get_production_task_by_id(production_id)["status"], "cancelled")
        self.assertEqual(self.database.get_active_production_tasks(), [])
        self.assertEqual(self.database.get_fabric_stock_rows()[0][2], 5)

        delete_route = miniapp_server.delete_order_task_for_telegram(
            9001,
            {"task_kind": "route", "task_id": route_id},
        )
        self.assertTrue(delete_route["ok"], delete_route)
        self.assertEqual(self.database.get_route_batch_by_id(route_id)["status"], "cancelled")
        self.assertEqual(self.database.get_active_route_batches(), [])
        self.assertEqual(self.database.get_warehouse_stock_by_id(stock_row["id"])["quantity"], 5)

        conn = sqlite3.connect(self.database.DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT quantity, movement_type, source_type, source_id
            FROM warehouse_stock_movements
            WHERE stock_id = ?
            ORDER BY id
            """,
            (stock_row["id"],),
        )
        self.assertEqual(
            cursor.fetchall(),
            [
                (5, "receipt", "", None),
                (-3, "issue", "route_batch", route_id),
                (3, "receipt", "cancelled_task", route_id),
            ],
        )
        conn.close()

    def test_zero_quantity_is_not_saved_or_reported(self):
        self.database.create_employee(2002, "Тест Швея", "Швея")
        employee = self.database.get_employee_by_telegram_id(2002)
        employee_id = employee[0]
        self.database.update_employee_status(employee_id, "active")
        shift = self.database.create_shift(employee_id)

        operation = self.database.get_active_operations(
            position="Швея",
            folder="Брюки-джоггеры",
        )[0]
        operation_id = operation[0]

        self.assertFalse(
            self.database.add_shift_operation(
                shift["id"],
                employee_id,
                operation_id,
                "86",
                "Капучино",
                0,
            )
        )
        self.assertEqual(self.database.get_shift_report(shift["id"]), [])
        self.assertEqual(self.database.get_shift_operation_choices(shift["id"]), [])

        self.assertTrue(
            self.database.add_shift_operation(
                shift["id"],
                employee_id,
                operation_id,
                "86",
                "Капучино",
                5,
            )
        )
        self.assertEqual(len(self.database.get_shift_report(shift["id"])), 1)

        self.assertFalse(
            self.database.set_shift_operation_quantity(
                shift["id"],
                employee_id,
                operation_id,
                "86",
                "Капучино",
                0,
            )
        )
        self.assertEqual(self.database.get_shift_report(shift["id"]), [])
        self.assertEqual(self.database.get_shift_operation_choices(shift["id"]), [])

    def test_feedback_entries_are_saved_and_listed(self):
        self.database.create_employee(3003, "Тест Сотрудник", "Упаковщик")
        employee = self.database.get_employee_by_telegram_id(3003)
        employee_id = employee[0]
        self.database.update_employee_status(employee_id, "active")
        shift = self.database.create_shift(employee_id)

        today = self.database.local_today().isoformat()
        feedback_id = self.database.add_feedback_entry(
            employee_id,
            shift["id"],
            "Производство",
            "Заканчивается резинка 25 мм",
        )

        self.assertIsNotNone(feedback_id)
        self.assertIsNone(self.database.add_feedback_entry(employee_id, shift["id"], "Бытовое", "   "))

        period_rows = self.database.get_feedback_entries(today, today)
        shift_rows = self.database.get_feedback_entries_by_shift(shift["id"])
        employee_rows = self.database.get_feedback_entries(today, today, employee_id=employee_id)
        status = self.database.get_database_status()

        self.assertEqual(period_rows, shift_rows)
        self.assertEqual(period_rows, employee_rows)
        self.assertEqual(len(period_rows), 1)
        self.assertEqual(period_rows[0][2], "Тест Сотрудник")
        self.assertEqual(period_rows[0][4], "Производство")
        self.assertEqual(period_rows[0][5], "Заканчивается резинка 25 мм")
        self.assertEqual(period_rows[0][6], shift["id"])
        self.assertEqual(status["feedback_entries"], 1)

    def test_admins_are_excluded_from_employee_reports(self):
        self.database.create_employee(5001, "Тест Рабочий", "Швея")
        employee = self.database.get_employee_by_telegram_id(5001)
        employee_id = employee[0]
        self.database.update_employee_status(employee_id, "active")
        admin = self.database.ensure_admin_employee(9001)
        admin_id = admin[0]

        employee_shift = self.database.create_shift(employee_id)
        admin_shift = self.database.create_shift(admin_id)
        today = self.database.local_today().isoformat()

        open_shift_names = {row[1] for row in self.database.get_open_shifts()}
        self.assertIn("Тест Рабочий", open_shift_names)
        self.assertNotIn(admin[2], open_shift_names)

        operation = self.database.get_active_operations(
            position="Швея",
            folder="Брюки-джоггеры",
        )[0]
        operation_id = operation[0]

        self.database.add_shift_operation(employee_shift["id"], employee_id, operation_id, "86", "Капучино", 5)
        self.database.add_shift_operation(admin_shift["id"], admin_id, operation_id, "86", "Капучино", 99)
        self.database.add_feedback_entry(employee_id, employee_shift["id"], "Производство", "Рабочее сообщение")
        self.database.add_feedback_entry(admin_id, admin_shift["id"], "Производство", "Админское сообщение")
        self.database.close_shift(employee_shift["id"])
        self.database.close_shift(admin_shift["id"])

        self.assertEqual([row[1] for row in self.database.get_all_employees()], ["Тест Рабочий"])
        self.assertEqual([row[1] for row in self.database.get_employees_by_status("active")], ["Тест Рабочий"])
        self.assertEqual([row[1] for row in self.database.get_period_employee_summary(today, today)], ["Тест Рабочий"])
        self.assertEqual([row[1] for row in self.database.get_period_shift_details(today, today)], ["Тест Рабочий"])
        self.assertEqual({row[1] for row in self.database.get_period_operation_rows(today, today)}, {"Тест Рабочий"})
        self.assertEqual([row[2] for row in self.database.get_feedback_entries(today, today)], ["Тест Рабочий"])
        self.assertEqual([row[1] for row in self.database.get_recent_shifts(10)], ["Тест Рабочий"])
        self.assertIsNone(self.database.get_employee_period_summary(admin_id, today, today))
        self.assertEqual(self.database.get_employee_period_operation_totals(admin_id, today, today), [])

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
