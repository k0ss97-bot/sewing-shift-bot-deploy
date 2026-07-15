import sqlite3
import tempfile
import unittest
from datetime import date
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()
