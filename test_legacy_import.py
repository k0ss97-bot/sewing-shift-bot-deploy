import sqlite3
import tempfile
import unittest
from datetime import date
from pathlib import Path

import database
from scripts.import_legacy_bot_data import import_legacy_data


SCHEMA = """
CREATE TABLE employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    position TEXT,
    role TEXT NOT NULL DEFAULT 'employee',
    status TEXT NOT NULL DEFAULT 'pending',
    registered_at TEXT NOT NULL
);
CREATE TABLE operations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    number INTEGER UNIQUE NOT NULL,
    name TEXT NOT NULL,
    position TEXT,
    operation_group TEXT,
    folder TEXT,
    sort_order INTEGER,
    unit TEXT NOT NULL DEFAULT 'шт',
    is_active INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE shifts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    shift_date TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT,
    total_minutes INTEGER,
    status TEXT NOT NULL DEFAULT 'open',
    edit_until TEXT,
    created_at TEXT NOT NULL,
    closed_at TEXT,
    FOREIGN KEY (employee_id) REFERENCES employees (id)
);
CREATE TABLE shift_operations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    shift_id INTEGER NOT NULL,
    employee_id INTEGER NOT NULL,
    operation_id INTEGER NOT NULL,
    product_size TEXT NOT NULL DEFAULT '',
    product_color TEXT NOT NULL DEFAULT '',
    quantity INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(shift_id, operation_id, product_size, product_color),
    FOREIGN KEY (shift_id) REFERENCES shifts (id),
    FOREIGN KEY (employee_id) REFERENCES employees (id),
    FOREIGN KEY (operation_id) REFERENCES operations (id)
);
CREATE UNIQUE INDEX idx_shifts_one_open ON shifts (employee_id) WHERE status = 'open';
"""


class LegacyImportTest(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        root = Path(self.temporary_directory.name)
        self.source_path = root / "legacy.db"
        self.target_path = root / "target.db"

        source = sqlite3.connect(self.source_path)
        source.executescript(SCHEMA)
        source.execute(
            """
            INSERT INTO employees (telegram_id, full_name, position, role, status, registered_at)
            VALUES (111001, 'Тест Старый Сотрудник', 'Швея', 'employee', 'active', '2026-07-01T08:00:00')
            """
        )
        source.execute(
            """
            INSERT INTO operations (
                number, name, position, operation_group, folder, sort_order, unit, is_active
            ) VALUES (10, 'Старое название операции', 'Швея', 'Пошив', 'Тест', 10, 'шт', 1)
            """
        )
        source.execute(
            """
            INSERT INTO shifts (employee_id, shift_date, start_time, status, created_at)
            VALUES (1, '2026-07-02', '08:00', 'open', '2026-07-02T08:00:00')
            """
        )
        source.execute(
            """
            INSERT INTO shift_operations (
                shift_id, employee_id, operation_id, product_size, product_color,
                quantity, created_at, updated_at
            ) VALUES (1, 1, 1, '86', 'Бежевый', 7, '2026-07-02T09:00:00', '2026-07-02T10:30:00')
            """
        )
        source.commit()
        source.close()

        target = sqlite3.connect(self.target_path)
        target.executescript(SCHEMA)
        target.execute(
            """
            INSERT INTO employees (telegram_id, full_name, position, role, status, registered_at)
            VALUES (999001, 'Тест Администратор', 'Администратор', 'admin', 'active', '2026-07-01T08:00:00')
            """
        )
        target.execute(
            """
            INSERT INTO operations (
                number, name, position, operation_group, folder, sort_order, unit, is_active
            ) VALUES (10, 'Актуальное название операции', 'Швея', 'Пошив', 'Тест', 10, 'шт', 1)
            """
        )
        target.commit()
        target.close()

    def tearDown(self):
        self.temporary_directory.cleanup()

    def init_current_database(self, path: Path):
        original_path = database.DB_NAME
        try:
            database.DB_NAME = str(path)
            database.init_db()
        finally:
            database.DB_NAME = original_path

    def test_import_is_dry_by_default_idempotent_and_closes_stale_shifts(self):
        dry_run = import_legacy_data(
            self.source_path,
            self.target_path,
            today=date(2026, 7, 15),
        )
        self.assertEqual(dry_run.employees_added, 1)
        target = sqlite3.connect(self.target_path)
        self.assertEqual(target.execute("SELECT COUNT(*) FROM employees").fetchone()[0], 1)
        target.close()

        first = import_legacy_data(
            self.source_path,
            self.target_path,
            apply=True,
            today=date(2026, 7, 15),
        )
        second = import_legacy_data(
            self.source_path,
            self.target_path,
            apply=True,
            today=date(2026, 7, 15),
        )
        self.assertEqual(first.employees_added, 1)
        self.assertEqual(first.shifts_added, 1)
        self.assertEqual(first.operation_rows_added, 1)
        self.assertEqual(first.stale_shifts_closed, 1)
        self.assertEqual(second.employees_added, 0)
        self.assertEqual(second.shifts_added, 0)
        self.assertEqual(second.operation_rows_added, 0)

        target = sqlite3.connect(self.target_path)
        self.assertEqual(target.execute("SELECT COUNT(*) FROM employees").fetchone()[0], 2)
        self.assertEqual(target.execute("SELECT COUNT(*) FROM shifts").fetchone()[0], 1)
        self.assertEqual(target.execute("SELECT COUNT(*) FROM shift_operations").fetchone()[0], 1)
        shift = target.execute(
            "SELECT status, end_time, total_minutes FROM shifts"
        ).fetchone()
        operation = target.execute(
            """
            SELECT operations.name, shift_operations.quantity
            FROM shift_operations
            JOIN operations ON operations.id = shift_operations.operation_id
            """
        ).fetchone()
        target.close()
        self.assertEqual(shift, ("closed", "10:30", 150))
        self.assertEqual(operation, ("Актуальное название операции", 7))

    def test_full_import_preserves_target_and_adds_production_snapshot_once(self):
        root = Path(self.temporary_directory.name)
        source_path = root / "full-source.db"
        target_path = root / "full-target.db"
        self.init_current_database(source_path)
        self.init_current_database(target_path)

        source = sqlite3.connect(source_path)
        source.execute(
            """
            INSERT INTO employees (telegram_id, full_name, position, role, status, registered_at)
            VALUES (111002, 'Тест Работник Источника', 'Раскройщик', 'employee', 'active',
                    '2026-07-10T08:00:00')
            """
        )
        operation_id = source.execute(
            "SELECT id FROM operations WHERE number = 1"
        ).fetchone()[0]
        source.execute(
            """
            INSERT INTO shifts (
                employee_id, shift_date, start_time, end_time, total_minutes,
                status, created_at, closed_at
            ) VALUES (1, '2026-07-10', '08:00', '16:00', 480, 'closed',
                      '2026-07-10T08:00:00', '2026-07-10T16:00:00')
            """
        )
        source.execute(
            """
            INSERT INTO shift_operations (
                shift_id, employee_id, operation_id, product_size, product_color,
                quantity, created_at, updated_at
            ) VALUES (1, 1, ?, '92', 'Синий', 12,
                      '2026-07-10T09:00:00', '2026-07-10T09:30:00')
            """,
            (operation_id,),
        )
        source.execute(
            """
            INSERT INTO feedback_entries (
                employee_id, shift_id, category, message, feedback_date, created_at
            ) VALUES (1, 1, 'Тест', 'Тестовая запись', '2026-07-10',
                      '2026-07-10T15:00:00')
            """
        )
        source.execute(
            """
            INSERT INTO fabric_stock (
                material_name, product_color, quantity, unit, updated_at
            ) VALUES ('Футер', 'Синий', 4, 'рул', '2026-07-10T08:10:00')
            """
        )
        source.execute(
            """
            INSERT INTO fabric_stock_movements (
                material_name, product_color, quantity, unit, movement_type,
                comment, created_by_employee_id, created_at
            ) VALUES ('Футер', 'Синий', 4, 'рул', 'receipt', 'Тест', 1,
                      '2026-07-10T08:10:00')
            """
        )
        source.execute(
            """
            INSERT INTO production_tasks (
                product_name, status, created_by_employee_id, created_at, updated_at,
                note, priority
            ) VALUES ('Тестовое изделие', 'active', 1,
                      '2026-07-10T08:20:00', '2026-07-10T08:20:00', 'Тест', 'normal')
            """
        )
        source.execute(
            "INSERT INTO production_task_sizes (task_id, product_size) VALUES (1, '92')"
        )
        source.execute(
            "INSERT INTO production_task_colors (task_id, product_color) VALUES (1, 'Синий')"
        )
        source.execute(
            """
            INSERT INTO production_task_items (
                task_id, product_size, product_color, contour_quantity, formed_quantity
            ) VALUES (1, '92', 'Синий', 12, 12)
            """
        )
        source.execute(
            """
            INSERT INTO production_task_fabric_rolls (
                task_id, material_name, product_color, rolls
            ) VALUES (1, 'Футер', 'Синий', 1)
            """
        )
        source.execute(
            """
            INSERT INTO production_task_attachments (
                task_id, file_name, mime_type, content_base64, created_at
            ) VALUES (1, 'test.txt', 'text/plain', 'dGVzdA==', '2026-07-10T08:21:00')
            """
        )
        source.execute(
            """
            INSERT INTO cutting_batches (
                product_name, production_task_id, status,
                contour_shift_id, contour_operation_id, contour_employee_id,
                contour_date, cutting_progress, created_at, updated_at
            ) VALUES ('Тестовое изделие', 1, 'formed', 1, ?, 1,
                      '2026-07-10', 100, '2026-07-10T09:00:00', '2026-07-10T12:00:00')
            """,
            (operation_id,),
        )
        source.execute(
            "INSERT INTO cutting_batch_sizes (batch_id, product_size, quantity) VALUES (1, '92', 12)"
        )
        source.execute(
            "INSERT INTO cutting_batch_colors (batch_id, product_color, layers) VALUES (1, 'Синий', 1)"
        )
        source.execute(
            """
            INSERT INTO cutting_batch_matrix (
                batch_id, product_size, product_color, quantity
            ) VALUES (1, '92', 'Синий', 12)
            """
        )
        source.execute(
            """
            INSERT INTO warehouse_stock (
                item_type, product_name, product_size, product_color, stage_name,
                ready_for_position, quantity, unit, updated_at
            ) VALUES ('semifinished', 'Тестовое изделие', '92', 'Синий', 'Раскрой',
                      'Швея', 12, 'шт', '2026-07-10T12:00:00')
            """
        )
        source.execute(
            """
            INSERT INTO route_batches (
                product_name, product_size, product_color, quantity, route_step_index,
                status, created_by_employee_id, created_at, updated_at,
                source_stock_id, source_cutting_batch_id
            ) VALUES ('Тестовое изделие', '92', 'Синий', 12, 0, 'active', 1,
                      '2026-07-10T12:10:00', '2026-07-10T12:10:00', 1, 1)
            """
        )
        source.execute(
            """
            INSERT INTO route_batch_inputs (
                batch_id, stock_id, input_role, quantity, created_at
            ) VALUES (1, 1, 'main', 12, '2026-07-10T12:10:00')
            """
        )
        source.execute(
            """
            INSERT INTO route_batch_history (
                batch_id, step_index, operation_name, position, employee_id,
                quantity, completed_at
            ) VALUES (1, 0, 'Тестовая операция', 'Швея', 1, 12,
                      '2026-07-10T13:00:00')
            """
        )
        source.execute(
            """
            INSERT INTO route_batch_defects (
                batch_id, employee_id, operation_name, position, product_name,
                product_size, product_color, quantity, reason, disposition, created_at
            ) VALUES (1, 1, 'Тестовая операция', 'Швея', 'Тестовое изделие',
                      '92', 'Синий', 1, 'Тест', 'Списать', '2026-07-10T13:05:00')
            """
        )
        source.execute(
            """
            INSERT INTO warehouse_stock_movements (
                stock_id, item_type, product_name, product_size, product_color,
                stage_name, ready_for_position, quantity, unit, movement_type,
                source_type, source_id, created_by_employee_id, created_at
            ) VALUES (1, 'semifinished', 'Тестовое изделие', '92', 'Синий',
                      'Раскрой', 'Швея', 12, 'шт', 'receipt', 'cutting_batch', 1, 1,
                      '2026-07-10T12:00:00')
            """
        )
        source.execute(
            """
            INSERT INTO edit_logs (
                changed_by, role, action, entity_type, entity_id, details, changed_at
            ) VALUES (111002, 'employee', 'Тест', 'route_batch', 1, 'Тест',
                      '2026-07-10T13:10:00')
            """
        )
        source.commit()
        source.close()

        target = sqlite3.connect(target_path)
        target.execute(
            """
            INSERT INTO employees (telegram_id, full_name, position, role, status, registered_at)
            VALUES (999002, 'Тест Администратор Сайта', 'Администратор', 'admin', 'active',
                    '2026-07-10T07:00:00')
            """
        )
        target.commit()
        target.close()

        dry_run = import_legacy_data(
            source_path,
            target_path,
            include_business=True,
            today=date(2026, 7, 15),
        )
        self.assertEqual(dry_run.production_tasks_added, 1)
        target = sqlite3.connect(target_path)
        self.assertEqual(target.execute("SELECT COUNT(*) FROM employees").fetchone()[0], 1)
        target.close()

        first = import_legacy_data(
            source_path,
            target_path,
            apply=True,
            include_business=True,
            today=date(2026, 7, 15),
        )
        second = import_legacy_data(
            source_path,
            target_path,
            apply=True,
            include_business=True,
            today=date(2026, 7, 15),
        )
        self.assertEqual(first.business_snapshot_imported, 1)
        self.assertEqual(first.production_tasks_added, 1)
        self.assertEqual(first.cutting_batches_added, 1)
        self.assertEqual(first.route_batches_added, 1)
        self.assertEqual(first.warehouse_stocks_added, 1)
        self.assertEqual(second.business_snapshot_skipped, 1)
        self.assertEqual(second.production_tasks_added, 0)

        original_path = database.DB_NAME
        try:
            database.DB_NAME = str(target_path)
            database.init_db()
        finally:
            database.DB_NAME = original_path

        target = sqlite3.connect(target_path)
        counts = {
            table: target.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for table in (
                "employees",
                "shifts",
                "shift_operations",
                "feedback_entries",
                "fabric_stock",
                "production_tasks",
                "cutting_batches",
                "warehouse_stock",
                "route_batches",
                "route_batch_inputs",
                "route_batch_history",
                "route_batch_defects",
            )
        }
        fabric_lots = target.execute(
            "SELECT COALESCE(SUM(rolls_available), 0) FROM fabric_stock_lots"
        ).fetchone()[0]
        warehouse_lots = target.execute(
            "SELECT COALESCE(SUM(quantity_available), 0) FROM warehouse_stock_lots"
        ).fetchone()[0]
        target.close()
        self.assertEqual(counts["employees"], 2)
        for table in counts:
            if table != "employees":
                self.assertEqual(counts[table], 1, table)
        self.assertEqual(fabric_lots, 4)
        self.assertEqual(warehouse_lots, 12)


if __name__ == "__main__":
    unittest.main()
