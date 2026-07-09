import os
import shutil
import sqlite3
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo


DB_FILE_NAME = "bot.db"
DB_DIR_CANDIDATES = [
    os.getenv("DB_DIR", ""),
    os.getenv("SHARED_DIR", ""),
    "/app/shared",
    "/app/data",
    "data",
]


def resolve_database_path():
    def has_business_data(db_path: str):
        if not os.path.exists(db_path):
            return False

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM employees")
            employee_count = cursor.fetchone()[0]
            conn.close()
            return employee_count > 0
        except sqlite3.Error:
            return False

    root_db_has_data = has_business_data(DB_FILE_NAME)

    db_paths = [
        os.path.join(db_dir, DB_FILE_NAME)
        for db_dir in DB_DIR_CANDIDATES
        if db_dir and os.path.isdir(db_dir)
    ]

    if root_db_has_data:
        for db_path in db_paths:
            if not has_business_data(db_path):
                shutil.copy2(DB_FILE_NAME, db_path)

        return DB_FILE_NAME

    for db_path in db_paths:
        if has_business_data(db_path):
            return db_path

    if db_paths:
        target_path = db_paths[0]

        return target_path

    return DB_FILE_NAME


DB_NAME = resolve_database_path()
LOCAL_TZ = ZoneInfo("Asia/Yekaterinburg")
ROUTE_BATCH_COLUMNS = [
    "id",
    "product_name",
    "product_size",
    "product_color",
    "quantity",
    "route_step_index",
    "status",
    "created_by_employee_id",
    "created_at",
    "updated_at",
    "completed_at",
    "source_stock_id",
    "assigned_employee_id",
    "assigned_at",
    "good_quantity",
    "defect_quantity",
]
ROUTE_BATCH_SELECT = ", ".join(ROUTE_BATCH_COLUMNS)
PRODUCTION_TASK_COLUMNS = [
    "id",
    "product_name",
    "status",
    "created_by_employee_id",
    "created_at",
    "updated_at",
    "completed_at",
    "note",
]
WAREHOUSE_STOCK_COLUMNS = [
    "id",
    "item_type",
    "product_name",
    "product_size",
    "product_color",
    "stage_name",
    "ready_for_position",
    "quantity",
    "unit",
    "updated_at",
]
WAREHOUSE_STOCK_SELECT = ", ".join(WAREHOUSE_STOCK_COLUMNS)
MATERIAL_PREPARATION_FOLDERS = {"Нарезание резинки", "Нарезание дублерина"}
AUTO_PREPARATION_FOLDERS = {*MATERIAL_PREPARATION_FOLDERS, "Дублирование"}


def get_database_dir():
    return os.path.dirname(os.path.abspath(DB_NAME))


def get_backup_dir():
    return os.path.join(get_database_dir(), "backups")


def get_database_status():
    backup_dir = get_backup_dir()
    status = {
        "path": DB_NAME,
        "exists": os.path.exists(DB_NAME),
        "size": os.path.getsize(DB_NAME) if os.path.exists(DB_NAME) else 0,
        "backup_dir": backup_dir,
        "backup_count": len([name for name in os.listdir(backup_dir) if name.endswith(".db")]) if os.path.isdir(backup_dir) else 0,
        "employees": None,
        "shifts": None,
        "shift_operations": None,
        "operations": None,
        "feedback_entries": None,
    }

    if not status["exists"]:
        return status

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        for table in ["employees", "shifts", "shift_operations", "operations", "feedback_entries"]:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            status[table] = cursor.fetchone()[0]

        conn.close()
    except sqlite3.Error as error:
        status["error"] = str(error)

    return status


def local_now():
    return datetime.now(LOCAL_TZ).replace(tzinfo=None)


def local_today():
    return local_now().date()


def row_to_dict(columns, row):
    if row is None:
        return None

    return dict(zip(columns, row))


def route_batch_from_row(row):
    return row_to_dict(ROUTE_BATCH_COLUMNS, row)


def production_task_from_row(row):
    return row_to_dict(PRODUCTION_TASK_COLUMNS, row)


from catalog import (
    CUTTING_OPERATIONS,
    CUTTING_PRODUCTS,
    PACKING_OPERATIONS,
    PACKING_PRODUCTS,
    PREPARATION_MATERIAL_COLORS,
    PREPARATION_OPERATION_OPTIONS,
    PRODUCT_OPTIONS,
    PRODUCTION_OPERATIONS,
    SIMPLE_PREPARATION_OPERATIONS,
    STARTER_OPERATION_NAMES,
    format_color_label,
)


def get_product_sizes(folder: str):
    return PRODUCT_OPTIONS.get(folder, {}).get("sizes", [])


def get_product_colors(folder: str):
    return PRODUCT_OPTIONS.get(folder, {}).get("colors", [])


def get_all_product_colors():
    colors = []

    for options in PRODUCT_OPTIONS.values():
        for color in options.get("colors", []):
            if color not in colors:
                colors.append(color)

    return colors


def get_preparation_operation_sizes(operation_name: str):
    return PREPARATION_OPERATION_OPTIONS.get(operation_name, {}).get("sizes", [])


def get_preparation_operation_colors(operation_name: str):
    return PREPARATION_OPERATION_OPTIONS.get(operation_name, {}).get("colors", PREPARATION_MATERIAL_COLORS)


def get_preparation_material_colors():
    return PREPARATION_MATERIAL_COLORS


def is_preparation_operation_folder(folder: str):
    return folder in {"Нарезание резинки", "Нарезание дублерина", "Дублирование", *SIMPLE_PREPARATION_OPERATIONS}


def is_packing_product_folder(folder: str):
    return folder in PACKING_PRODUCTS


def get_operation_group(position: str, folder: str, name: str | None = None):
    if position == "Раскройщик":
        return "Раскрой изделий"

    if position == "Ремонт":
        return "ТО оборудования"

    if position == "Упаковщик":
        if folder == "Подготовка" or is_preparation_operation_folder(folder):
            return "Подготовка"

        if folder in {
            "Брюки со стрелками детские",
            "Брюки со стрелками подростковые",
            "Брюки-клёш со стрелками для девочек",
            "Брюки-джоггеры",
            "Брюки-ползунки",
            "Легинсы",
            "Шорты",
            "Юбка-шорты",
        }:
            return "Брюки / низ"

        if folder in {
            "Футболки",
            "Свитшоты",
        }:
            return "Верх"

        return "Кардиганы / жакеты"

    if folder == "Подготовка":
        return "Подготовка"

    if folder == "Техобслуживание швейной машинки":
        return "Техобслуживание"

    if folder == "ТО оборудования":
        return "ТО оборудования"

    if folder in {
        "Брюки со стрелками детские",
        "Брюки со стрелками подростковые",
        "Брюки-клёш со стрелками для девочек",
        "Брюки-джоггеры",
        "Брюки-ползунки",
        "Легинсы",
        "Шорты",
        "Юбка-шорты",
    }:
        return "Брюки / низ"

    if folder in {
        "Футболки",
        "Свитшоты",
    }:
        return "Верх"

    return "Кардиганы / жакеты"


def seed_production_operations(cursor):
    cursor.execute(
        """
        UPDATE operations
        SET is_active = 0
        WHERE name IN (?, ?, ?, ?, ?, ?)
          AND (folder IS NULL OR folder IN ('Общие операции', 'Упаковка и ВТО', 'Раскрой'))
        """,
        STARTER_OPERATION_NAMES,
    )

    cursor.execute(
        """
        UPDATE operations
        SET is_active = 0
        WHERE position = 'Раскройщик'
          AND folder = 'Раскрой'
        """
    )

    cursor.execute(
        """
        UPDATE operations
        SET is_active = 0
        WHERE position = 'Упаковщик'
          AND folder = 'Подготовка'
        """
    )

    cursor.execute(
        """
        UPDATE operations
        SET name = 'Дублирование'
        WHERE position = 'Упаковщик'
          AND name LIKE 'Проклеивание планок%'
        """
    )

    material_word = "фли" + "зелином"
    cursor.execute(
        """
        UPDATE operations
        SET name = REPLACE(name, ?, '')
        WHERE position = 'Упаковщик'
          AND name LIKE ?
        """,
        (f" {material_word}", f"%{material_word}%"),
    )

    cursor.execute(
        """
        UPDATE operations
        SET name = 'ВТО пошитых стрелок'
        WHERE position = 'Упаковщик'
          AND name = 'ВТО стрелок'
        """
    )

    cursor.execute(
        """
        UPDATE operations
        SET is_active = 0
        WHERE position = 'Упаковщик'
          AND name = 'Дублирование'
          AND folder IN (
              'Кардиган',
              'Кардиган детский и подростковый',
              'Бомбер',
              'Жакет для девочек'
          )
        """
    )

    cursor.execute(
        """
        UPDATE operations
        SET is_active = 0
        WHERE position = 'Швея'
          AND folder = 'ТО оборудования'
        """
    )

    cutting_items = [
        ("Раскройщик", product, operation)
        for product in CUTTING_PRODUCTS
        for operation in CUTTING_OPERATIONS
    ]
    packing_items = [
        ("Упаковщик", product, operation)
        for product in PACKING_PRODUCTS
        for operation in PACKING_OPERATIONS
    ]
    packing_preparation_items = [
        item
        for item in PRODUCTION_OPERATIONS
        if item[0] == "Упаковщик" and get_operation_group(item[0], item[1], item[2]) == "Подготовка"
    ]
    remaining_production_items = [
        item
        for item in PRODUCTION_OPERATIONS
        if item not in packing_preparation_items
    ]
    seed_items = (
        cutting_items
        + packing_preparation_items
        + packing_items
        + remaining_production_items
    )

    for sort_order, (position, folder, name) in enumerate(seed_items, start=1):
        operation_group = get_operation_group(position, folder, name)

        cursor.execute(
            """
            SELECT id
            FROM operations
            WHERE name = ?
              AND position = ?
              AND folder = ?
            """,
            (name, position, folder),
        )

        existing_operation = cursor.fetchone()

        if existing_operation is not None:
            cursor.execute(
                """
                UPDATE operations
                SET unit = 'шт',
                    is_active = 1,
                    operation_group = ?,
                    sort_order = ?
                WHERE id = ?
                """,
                (operation_group, sort_order, existing_operation[0]),
            )
            continue

        cursor.execute("SELECT COALESCE(MAX(number), 0) + 1 FROM operations")
        next_number = cursor.fetchone()[0]

        cursor.execute(
            """
            INSERT INTO operations (number, name, position, operation_group, folder, sort_order, unit, is_active)
            VALUES (?, ?, ?, ?, ?, ?, 'шт', 1)
            """,
            (next_number, name, position, operation_group, folder, sort_order),
        )

    maintenance_items = [
        "замена игл",
        "замена ниток",
        "регулировка шва",
        "чистка швейной машинки",
    ]

    for offset, name in enumerate(maintenance_items, start=1):
        position = "Швея"
        folder = "Техобслуживание швейной машинки"
        operation_group = get_operation_group(position, folder, name)
        sort_order = len(seed_items) + offset

        cursor.execute(
            """
            SELECT id
            FROM operations
            WHERE name = ?
              AND position = ?
              AND folder = ?
            """,
            (name, position, folder),
        )

        existing_operation = cursor.fetchone()

        if existing_operation is not None:
            cursor.execute(
                """
                UPDATE operations
                SET unit = 'мин',
                    is_active = 1,
                    operation_group = ?,
                    sort_order = ?
                WHERE id = ?
                """,
                (operation_group, sort_order, existing_operation[0]),
            )
            continue

        cursor.execute("SELECT COALESCE(MAX(number), 0) + 1 FROM operations")
        next_number = cursor.fetchone()[0]

        cursor.execute(
            """
            INSERT INTO operations (number, name, position, operation_group, folder, sort_order, unit, is_active)
            VALUES (?, ?, ?, ?, ?, ?, 'мин', 1)
            """,
            (next_number, name, position, operation_group, folder, sort_order),
        )

    equipment_maintenance_items = [
        "Замена ножей",
        "Замена масла",
    ]

    for offset, name in enumerate(equipment_maintenance_items, start=1):
        position = "Ремонт"
        folder = "ТО оборудования"
        operation_group = get_operation_group(position, folder, name)
        sort_order = len(seed_items) + len(maintenance_items) + offset

        cursor.execute(
            """
            SELECT id
            FROM operations
            WHERE name = ?
              AND position = ?
              AND folder = ?
            """,
            (name, position, folder),
        )

        existing_operation = cursor.fetchone()

        if existing_operation is not None:
            cursor.execute(
                """
                UPDATE operations
                SET unit = 'шт',
                    is_active = 1,
                    operation_group = ?,
                    sort_order = ?
                WHERE id = ?
                """,
                (operation_group, sort_order, existing_operation[0]),
            )
            continue

        cursor.execute("SELECT COALESCE(MAX(number), 0) + 1 FROM operations")
        next_number = cursor.fetchone()[0]

        cursor.execute(
            """
            INSERT INTO operations (number, name, position, operation_group, folder, sort_order, unit, is_active)
            VALUES (?, ?, ?, ?, ?, ?, 'шт', 1)
            """,
            (next_number, name, position, operation_group, folder, sort_order),
        )


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            position TEXT,
            role TEXT NOT NULL DEFAULT 'employee',
            status TEXT NOT NULL DEFAULT 'pending',
            registered_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shifts (
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
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS operations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            number INTEGER UNIQUE NOT NULL,
            name TEXT NOT NULL,
            position TEXT,
            operation_group TEXT,
            folder TEXT,
            sort_order INTEGER,
            unit TEXT NOT NULL DEFAULT 'шт',
            is_active INTEGER NOT NULL DEFAULT 1
        )
    """)

    cursor.execute("PRAGMA table_info(operations)")
    operation_columns = [column[1] for column in cursor.fetchall()]

    if "position" not in operation_columns:
        cursor.execute("ALTER TABLE operations ADD COLUMN position TEXT")

    if "folder" not in operation_columns:
        cursor.execute("ALTER TABLE operations ADD COLUMN folder TEXT")

    if "operation_group" not in operation_columns:
        cursor.execute("ALTER TABLE operations ADD COLUMN operation_group TEXT")

    if "sort_order" not in operation_columns:
        cursor.execute("ALTER TABLE operations ADD COLUMN sort_order INTEGER")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shift_operations (
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
        )
    """)

    cursor.execute("PRAGMA table_info(shift_operations)")
    shift_operation_columns = [column[1] for column in cursor.fetchall()]

    if "product_size" not in shift_operation_columns or "product_color" not in shift_operation_columns:
        cursor.execute("ALTER TABLE shift_operations RENAME TO shift_operations_old")

        cursor.execute("""
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
            )
        """)

        cursor.execute("""
            INSERT INTO shift_operations (
                id, shift_id, employee_id, operation_id,
                product_size, product_color, quantity, created_at, updated_at
            )
            SELECT
                id, shift_id, employee_id, operation_id,
                '', '', quantity, created_at, updated_at
            FROM shift_operations_old
        """)

        cursor.execute("DROP TABLE shift_operations_old")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS edit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            changed_by INTEGER NOT NULL,
            role TEXT NOT NULL,
            action TEXT NOT NULL,
            entity_type TEXT NOT NULL,
            entity_id INTEGER,
            details TEXT,
            changed_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            shift_id INTEGER,
            category TEXT NOT NULL,
            message TEXT NOT NULL,
            feedback_date TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (employee_id) REFERENCES employees (id),
            FOREIGN KEY (shift_id) REFERENCES shifts (id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cutting_batches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            production_task_id INTEGER,
            status TEXT NOT NULL DEFAULT 'contours_done',
            contour_shift_id INTEGER,
            contour_operation_id INTEGER,
            contour_employee_id INTEGER,
            contour_date TEXT,
            layout_shift_id INTEGER,
            layout_operation_id INTEGER,
            layout_employee_id INTEGER,
            layout_date TEXT,
            cutting_shift_id INTEGER,
            cutting_operation_id INTEGER,
            cutting_employee_id INTEGER,
            cutting_progress INTEGER NOT NULL DEFAULT 0,
            formed_shift_id INTEGER,
            formed_operation_id INTEGER,
            formed_employee_id INTEGER,
            formed_date TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    cursor.execute("PRAGMA table_info(cutting_batches)")
    cutting_batch_columns = [column[1] for column in cursor.fetchall()]

    if "production_task_id" not in cutting_batch_columns:
        cursor.execute("ALTER TABLE cutting_batches ADD COLUMN production_task_id INTEGER")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cutting_batch_sizes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_id INTEGER NOT NULL,
            product_size TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            UNIQUE(batch_id, product_size),
            FOREIGN KEY (batch_id) REFERENCES cutting_batches (id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cutting_batch_colors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_id INTEGER NOT NULL,
            product_color TEXT NOT NULL,
            layers INTEGER NOT NULL,
            UNIQUE(batch_id, product_color),
            FOREIGN KEY (batch_id) REFERENCES cutting_batches (id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cutting_batch_matrix (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_id INTEGER NOT NULL,
            product_size TEXT NOT NULL,
            product_color TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            UNIQUE(batch_id, product_size, product_color),
            FOREIGN KEY (batch_id) REFERENCES cutting_batches (id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fabric_stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            material_name TEXT NOT NULL,
            product_color TEXT NOT NULL,
            quantity REAL NOT NULL DEFAULT 0,
            unit TEXT NOT NULL DEFAULT 'м',
            updated_at TEXT NOT NULL,
            UNIQUE(material_name, product_color, unit)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fabric_stock_movements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            material_name TEXT NOT NULL,
            product_color TEXT NOT NULL,
            quantity REAL NOT NULL,
            unit TEXT NOT NULL DEFAULT 'м',
            movement_type TEXT NOT NULL,
            comment TEXT,
            created_by_employee_id INTEGER,
            created_at TEXT NOT NULL,
            FOREIGN KEY (created_by_employee_id) REFERENCES employees (id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS warehouse_stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_type TEXT NOT NULL,
            product_name TEXT NOT NULL,
            product_size TEXT NOT NULL,
            product_color TEXT NOT NULL,
            stage_name TEXT NOT NULL,
            ready_for_position TEXT NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 0,
            unit TEXT NOT NULL DEFAULT 'шт',
            updated_at TEXT NOT NULL,
            UNIQUE(item_type, product_name, product_size, product_color, stage_name, ready_for_position, unit)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS warehouse_stock_movements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stock_id INTEGER,
            item_type TEXT NOT NULL,
            product_name TEXT NOT NULL,
            product_size TEXT NOT NULL,
            product_color TEXT NOT NULL,
            stage_name TEXT NOT NULL,
            ready_for_position TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit TEXT NOT NULL DEFAULT 'шт',
            movement_type TEXT NOT NULL,
            source_type TEXT,
            source_id INTEGER,
            created_by_employee_id INTEGER,
            created_at TEXT NOT NULL,
            FOREIGN KEY (stock_id) REFERENCES warehouse_stock (id),
            FOREIGN KEY (created_by_employee_id) REFERENCES employees (id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS production_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            created_by_employee_id INTEGER,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            completed_at TEXT,
            note TEXT,
            FOREIGN KEY (created_by_employee_id) REFERENCES employees (id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS production_task_sizes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            product_size TEXT NOT NULL,
            UNIQUE(task_id, product_size),
            FOREIGN KEY (task_id) REFERENCES production_tasks (id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS production_task_colors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            product_color TEXT NOT NULL,
            UNIQUE(task_id, product_color),
            FOREIGN KEY (task_id) REFERENCES production_tasks (id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS production_task_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            product_size TEXT NOT NULL,
            product_color TEXT NOT NULL,
            contour_quantity INTEGER NOT NULL DEFAULT 0,
            formed_quantity INTEGER NOT NULL DEFAULT 0,
            UNIQUE(task_id, product_size, product_color),
            FOREIGN KEY (task_id) REFERENCES production_tasks (id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS route_batches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            product_size TEXT NOT NULL,
            product_color TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            route_step_index INTEGER NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'active',
            created_by_employee_id INTEGER,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            completed_at TEXT,
            source_stock_id INTEGER,
            FOREIGN KEY (created_by_employee_id) REFERENCES employees (id)
        )
    """)

    cursor.execute("PRAGMA table_info(route_batches)")
    route_batch_columns = [column[1] for column in cursor.fetchall()]

    if "source_stock_id" not in route_batch_columns:
        cursor.execute("ALTER TABLE route_batches ADD COLUMN source_stock_id INTEGER")
    if "assigned_employee_id" not in route_batch_columns:
        cursor.execute("ALTER TABLE route_batches ADD COLUMN assigned_employee_id INTEGER")
    if "assigned_at" not in route_batch_columns:
        cursor.execute("ALTER TABLE route_batches ADD COLUMN assigned_at TEXT")
    if "good_quantity" not in route_batch_columns:
        cursor.execute("ALTER TABLE route_batches ADD COLUMN good_quantity INTEGER NOT NULL DEFAULT 0")
    if "defect_quantity" not in route_batch_columns:
        cursor.execute("ALTER TABLE route_batches ADD COLUMN defect_quantity INTEGER NOT NULL DEFAULT 0")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS route_batch_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_id INTEGER NOT NULL,
            step_index INTEGER NOT NULL,
            operation_name TEXT NOT NULL,
            position TEXT NOT NULL,
            employee_id INTEGER,
            quantity INTEGER NOT NULL,
            completed_at TEXT NOT NULL,
            FOREIGN KEY (batch_id) REFERENCES route_batches (id),
            FOREIGN KEY (employee_id) REFERENCES employees (id)
        )
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_shifts_employee_date ON shifts (employee_id, shift_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_shifts_date_status ON shifts (shift_date, status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_shift_operations_shift ON shift_operations (shift_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_shift_operations_employee ON shift_operations (employee_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_operations_navigation ON operations (position, operation_group, folder, is_active)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cutting_batches_product_status ON cutting_batches (product_name, status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cutting_batches_task ON cutting_batches (production_task_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cutting_batch_matrix_batch ON cutting_batch_matrix (batch_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_feedback_entries_date ON feedback_entries (feedback_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_feedback_entries_employee_date ON feedback_entries (employee_id, feedback_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_route_batches_status_step ON route_batches (status, route_step_index)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_route_batch_history_batch ON route_batch_history (batch_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_fabric_stock_color ON fabric_stock (product_color)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_production_tasks_status ON production_tasks (status, created_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_production_task_items_task ON production_task_items (task_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_warehouse_stock_type_position ON warehouse_stock (item_type, ready_for_position)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_warehouse_stock_product ON warehouse_stock (product_name, product_size, product_color)")

    cursor.execute("SELECT COUNT(*) FROM operations")
    count = cursor.fetchone()[0]

    if count == 0:
        cursor.executemany(
            """
            INSERT INTO operations (number, name, position, unit)
            VALUES (?, ?, ?, ?)
            """,
            [
                (1, "Пошив резинки", "Швея", "шт"),
                (2, "Обработка горловины", "Швея", "шт"),
                (3, "Стачивание бокового шва", "Швея", "шт"),
                (4, "Упаковка", "Упаковщик", "шт"),
                (5, "ВТО", "Упаковщик", "шт"),
                (6, "Раскрой", "Раскройщик", "шт"),
            ]
        )
    else:
        cursor.execute(
            """
            UPDATE operations
            SET position = CASE
                WHEN name LIKE '%Упаков%' THEN 'Упаковщик'
                WHEN name LIKE '%ВТО%' THEN 'Упаковщик'
                WHEN name LIKE '%Раскрой%' THEN 'Раскройщик'
                ELSE 'Швея'
            END
            WHERE position IS NULL
            """
        )

        cursor.execute(
            """
            UPDATE operations
            SET folder = CASE
                WHEN position = 'Раскройщик' THEN 'Раскрой'
                WHEN position = 'Упаковщик' THEN 'Упаковка и ВТО'
                ELSE 'Общие операции'
            END
            WHERE folder IS NULL OR folder = ''
            """
        )

        cursor.execute(
            """
            UPDATE operations
            SET operation_group = CASE
                WHEN position = 'Раскройщик' THEN 'Раскрой изделий'
                WHEN position = 'Упаковщик' AND folder = 'Подготовка' THEN 'Подготовка'
                WHEN position = 'Упаковщик' AND folder IN (
                    'Брюки со стрелками детские',
                    'Брюки со стрелками подростковые',
                    'Брюки-клёш со стрелками для девочек',
                    'Брюки-джоггеры',
                    'Брюки-ползунки',
                    'Легинсы',
                    'Шорты',
                    'Юбка-шорты'
                ) THEN 'Брюки / низ'
                WHEN position = 'Упаковщик' AND folder IN ('Футболки', 'Свитшоты') THEN 'Верх'
                WHEN position = 'Упаковщик' THEN 'Кардиганы / жакеты'
                WHEN folder = 'Подготовка' THEN 'Подготовка'
                WHEN folder IN (
                    'Брюки со стрелками детские',
                    'Брюки со стрелками подростковые',
                    'Брюки-клёш со стрелками для девочек',
                    'Брюки-джоггеры',
                    'Брюки-ползунки',
                    'Легинсы',
                    'Шорты',
                    'Юбка-шорты'
                ) THEN 'Брюки / низ'
                WHEN folder IN ('Футболки', 'Свитшоты') THEN 'Верх'
                ELSE 'Кардиганы / жакеты'
            END
            WHERE operation_group IS NULL OR operation_group = ''
            """
        )

        for default_name, default_position in [
            ("ВТО", "Упаковщик"),
        ]:
            cursor.execute(
                """
                SELECT id
                FROM operations
                WHERE name = ?
                """,
                (default_name,)
            )

            if cursor.fetchone() is None:
                cursor.execute("SELECT COALESCE(MAX(number), 0) + 1 FROM operations")
                next_number = cursor.fetchone()[0]

                cursor.execute(
                    """
                    INSERT INTO operations (number, name, position, operation_group, folder, sort_order, unit, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, 'шт', 1)
                    """,
                    (
                        next_number,
                        default_name,
                        default_position,
                        "Раскрой" if default_position == "Раскройщик" else "ВТО верха",
                        "Раскрой" if default_position == "Раскройщик" else "Упаковка и ВТО",
                        next_number,
                    )
                )

    seed_production_operations(cursor)

    conn.commit()
    conn.close()


def get_employee_by_telegram_id(telegram_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, telegram_id, full_name, position, role, status
        FROM employees
        WHERE telegram_id = ?
        """,
        (telegram_id,)
    )

    employee = cursor.fetchone()
    conn.close()
    return employee


def get_employee_by_id(employee_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, telegram_id, full_name, position, role, status
        FROM employees
        WHERE id = ?
        """,
        (employee_id,),
    )

    employee = cursor.fetchone()
    conn.close()
    return employee


def ensure_admin_employee(telegram_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, telegram_id, full_name, position, role, status
        FROM employees
        WHERE telegram_id = ?
        """,
        (telegram_id,),
    )

    employee = cursor.fetchone()

    if employee is None:
        cursor.execute(
            """
            INSERT INTO employees (telegram_id, full_name, position, role, status, registered_at)
            VALUES (?, ?, ?, 'admin', 'active', ?)
            """,
            (
                telegram_id,
                f"Администратор {telegram_id}",
                "Администратор",
                local_now().isoformat(),
            ),
        )
    else:
        full_name = employee[2] or f"Администратор {telegram_id}"
        position = employee[3] or "Администратор"

        cursor.execute(
            """
            UPDATE employees
            SET full_name = ?,
                position = ?,
                role = 'admin',
                status = 'active'
            WHERE telegram_id = ?
            """,
            (full_name, position, telegram_id),
        )

    conn.commit()

    cursor.execute(
        """
        SELECT id, telegram_id, full_name, position, role, status
        FROM employees
        WHERE telegram_id = ?
        """,
        (telegram_id,),
    )

    employee = cursor.fetchone()
    conn.close()
    return employee


def create_employee(telegram_id: int, full_name: str, position: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO employees (telegram_id, full_name, position, registered_at)
        VALUES (?, ?, ?, ?)
        """,
        (telegram_id, full_name, position, local_now().isoformat())
    )

    conn.commit()
    conn.close()


def get_pending_employees():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, full_name, position, telegram_id, registered_at
        FROM employees
        WHERE status = 'pending'
        ORDER BY registered_at ASC
        """
    )

    employees = cursor.fetchall()
    conn.close()
    return employees


def get_all_employees():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, full_name, position, telegram_id, status
        FROM employees
        WHERE role != 'admin'
        ORDER BY id ASC
        """
    )

    employees = cursor.fetchall()
    conn.close()
    return employees


def get_employees_by_status(status: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, full_name, position, telegram_id, status
        FROM employees
        WHERE status = ?
          AND role != 'admin'
        ORDER BY id ASC
        """,
        (status,)
    )

    employees = cursor.fetchall()
    conn.close()
    return employees


def update_employee_status(employee_id: int, status: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE employees
        SET status = ?
        WHERE id = ?
        """,
        (status, employee_id)
    )

    conn.commit()

    cursor.execute(
        """
        SELECT id, telegram_id, full_name, status
        FROM employees
        WHERE id = ?
        """,
        (employee_id,)
    )

    employee = cursor.fetchone()
    conn.close()
    return employee


def update_employee_position(employee_id: int, position: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE employees
        SET position = ?
        WHERE id = ?
        """,
        (position, employee_id)
    )

    conn.commit()

    cursor.execute(
        """
        SELECT id, telegram_id, full_name, position, status
        FROM employees
        WHERE id = ?
        """,
        (employee_id,)
    )

    employee = cursor.fetchone()
    conn.close()
    return employee


def get_shift_for_today(employee_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    today = local_today().isoformat()

    cursor.execute(
        """
        SELECT id, employee_id, shift_date, start_time, end_time, status
        FROM shifts
        WHERE employee_id = ?
          AND shift_date = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (employee_id, today)
    )

    shift = cursor.fetchone()
    conn.close()
    return shift


def get_employee_shifts_by_period(employee_id: int, start_date: str, end_date: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, shift_date, start_time, end_time, total_minutes, status
        FROM shifts
        WHERE employee_id = ?
          AND shift_date BETWEEN ? AND ?
        ORDER BY shift_date ASC, start_time ASC
        """,
        (employee_id, start_date, end_date)
    )

    shifts = cursor.fetchall()
    conn.close()
    return shifts


def add_feedback_entry(employee_id: int, shift_id: int | None, category: str, message: str):
    clean_message = message.strip()

    if not clean_message:
        return None

    now = local_now()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO feedback_entries (
            employee_id, shift_id, category, message, feedback_date, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (employee_id, shift_id, category, clean_message, now.date().isoformat(), now.isoformat())
    )

    feedback_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return feedback_id


def get_feedback_entries(start_date: str, end_date: str, employee_id: int | None = None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    params = [start_date, end_date]
    employee_filter = ""

    if employee_id is not None:
        employee_filter = "AND feedback_entries.employee_id = ?"
        params.append(employee_id)

    cursor.execute(
        f"""
        SELECT
            feedback_entries.feedback_date,
            substr(feedback_entries.created_at, 12, 5) AS feedback_time,
            employees.full_name,
            COALESCE(employees.position, ''),
            feedback_entries.category,
            feedback_entries.message,
            feedback_entries.shift_id
        FROM feedback_entries
        JOIN employees ON employees.id = feedback_entries.employee_id
        WHERE feedback_entries.feedback_date BETWEEN ? AND ?
          AND employees.role != 'admin'
          {employee_filter}
        ORDER BY feedback_entries.feedback_date ASC, feedback_entries.created_at ASC
        """,
        params
    )

    rows = cursor.fetchall()
    conn.close()
    return rows


def get_feedback_entries_by_shift(shift_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            feedback_entries.feedback_date,
            substr(feedback_entries.created_at, 12, 5) AS feedback_time,
            employees.full_name,
            COALESCE(employees.position, ''),
            feedback_entries.category,
            feedback_entries.message,
            feedback_entries.shift_id
        FROM feedback_entries
        JOIN employees ON employees.id = feedback_entries.employee_id
        WHERE feedback_entries.shift_id = ?
          AND employees.role != 'admin'
        ORDER BY feedback_entries.created_at ASC
        """,
        (shift_id,)
    )

    rows = cursor.fetchall()
    conn.close()
    return rows


def get_month_feedback_entries():
    month_start = local_today().replace(day=1).isoformat()
    today = local_today().isoformat()
    return get_feedback_entries(month_start, today)


def get_open_shift_for_today(employee_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    today = local_today().isoformat()

    cursor.execute(
        """
        SELECT id, employee_id, shift_date, start_time, end_time, status
        FROM shifts
        WHERE employee_id = ?
          AND shift_date = ?
          AND status = 'open'
        """,
        (employee_id, today)
    )

    shift = cursor.fetchone()
    conn.close()
    return shift


def get_editable_shift_for_today(employee_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    today = local_today().isoformat()

    cursor.execute(
        """
        SELECT id, employee_id, shift_date, start_time, end_time, status, edit_until
        FROM shifts
        WHERE employee_id = ?
          AND shift_date = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (employee_id, today)
    )

    shift = cursor.fetchone()
    conn.close()

    if shift is None:
        return None

    status = shift[5]
    edit_until = shift[6]

    if status == "open":
        return shift

    if status == "closed" and edit_until:
        try:
            if local_now() <= datetime.fromisoformat(edit_until):
                return shift
        except ValueError:
            return None

    return None


def create_shift(employee_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    now = local_now()
    shift_date = local_today().isoformat()
    start_time = now.strftime("%H:%M")
    created_at = now.isoformat()

    cursor.execute(
        """
        INSERT INTO shifts (employee_id, shift_date, start_time, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (employee_id, shift_date, start_time, created_at)
    )

    conn.commit()
    shift_id = cursor.lastrowid
    conn.close()

    return {
        "id": shift_id,
        "employee_id": employee_id,
        "shift_date": shift_date,
        "start_time": start_time,
        "status": "open",
    }


def get_active_operation_groups(position: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT operation_group
        FROM operations
        WHERE is_active = 1
          AND position = ?
        GROUP BY operation_group
        ORDER BY MIN(COALESCE(sort_order, number))
        """,
        (position,),
    )

    groups = [row[0] for row in cursor.fetchall() if row[0]]
    conn.close()
    return groups


def get_active_operation_folders(position: str, operation_group: str | None = None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    params = [position]
    group_filter = ""

    if operation_group:
        group_filter = "AND operation_group = ?"
        params.append(operation_group)

    cursor.execute(
        f"""
        SELECT folder
        FROM operations
        WHERE is_active = 1
          AND position = ?
          {group_filter}
        GROUP BY folder
        ORDER BY MIN(COALESCE(sort_order, number))
        """,
        params,
    )

    folders = [row[0] for row in cursor.fetchall() if row[0]]
    conn.close()
    return folders


def get_active_operations(position: str | None = None, folder: str | None = None, operation_group: str | None = None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if position:
        params = [position]
        folder_filter = ""
        group_filter = ""

        if operation_group:
            group_filter = "AND operation_group = ?"
            params.append(operation_group)

        if folder:
            folder_filter = "AND folder = ?"
            params.append(folder)

        cursor.execute(
            f"""
            SELECT id, number, name, unit
            FROM operations
            WHERE is_active = 1
              AND position = ?
              {group_filter}
              {folder_filter}
            ORDER BY COALESCE(sort_order, number), number
            """,
            params,
        )
    else:
        cursor.execute(
            """
            SELECT id, number, name, unit
            FROM operations
            WHERE is_active = 1
            ORDER BY COALESCE(sort_order, number), number
            """
        )

    operations = cursor.fetchall()
    conn.close()
    return operations


def get_all_operations():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, number, name, position, operation_group, folder, unit, is_active
        FROM operations
        ORDER BY position, operation_group, folder, COALESCE(sort_order, number), number
        """
    )

    operations = cursor.fetchall()
    conn.close()
    return operations


def get_operation_by_number(number: int, position: str | None = None, folder: str | None = None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if position:
        params = [number, position]
        folder_filter = ""

        if folder:
            folder_filter = "AND folder = ?"
            params.append(folder)

        cursor.execute(
            f"""
            SELECT id, number, name, unit
            FROM operations
            WHERE number = ? AND is_active = 1 AND position = ?
            {folder_filter}
            """,
            params,
        )
    else:
        cursor.execute(
            """
            SELECT id, number, name, unit
            FROM operations
            WHERE number = ?
            """,
            (number,)
        )

    operation = cursor.fetchone()
    conn.close()
    return operation


def add_operation(name: str, position: str, operation_group: str, folder: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT COALESCE(MAX(number), 0) + 1 FROM operations")
    next_number = cursor.fetchone()[0]
    cursor.execute("SELECT COALESCE(MAX(sort_order), 0) + 1 FROM operations")
    next_sort_order = cursor.fetchone()[0]

    cursor.execute(
        """
        INSERT INTO operations (number, name, position, operation_group, folder, sort_order, unit, is_active)
        VALUES (?, ?, ?, ?, ?, ?, 'шт', 1)
        """,
        (next_number, name, position, operation_group, folder, next_sort_order)
    )

    conn.commit()
    operation_id = cursor.lastrowid
    conn.close()

    return {
        "id": operation_id,
        "number": next_number,
        "name": name,
        "position": position,
        "operation_group": operation_group,
        "folder": folder,
    }


def hide_operation(number: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, number, name, position, operation_group, folder
        FROM operations
        WHERE number = ?
        """,
        (number,)
    )

    operation = cursor.fetchone()

    if operation is None:
        conn.close()
        return None

    cursor.execute(
        """
        UPDATE operations
        SET is_active = 0
        WHERE number = ?
        """,
        (number,)
    )

    conn.commit()
    conn.close()

    return operation


def restore_operation(number: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, number, name, position, operation_group, folder
        FROM operations
        WHERE number = ?
        """,
        (number,)
    )

    operation = cursor.fetchone()

    if operation is None:
        conn.close()
        return None

    cursor.execute(
        """
        UPDATE operations
        SET is_active = 1
        WHERE number = ?
        """,
        (number,)
    )

    conn.commit()
    conn.close()

    return operation


def update_operation_field(number: int, field: str, value: str):
    allowed_fields = {
        "name": "name",
        "position": "position",
        "operation_group": "operation_group",
        "folder": "folder",
    }

    if field not in allowed_fields:
        return None

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, number, name, position, operation_group, folder
        FROM operations
        WHERE number = ?
        """,
        (number,)
    )

    old_operation = cursor.fetchone()

    if old_operation is None:
        conn.close()
        return None

    cursor.execute(
        f"""
        UPDATE operations
        SET {allowed_fields[field]} = ?
        WHERE number = ?
        """,
        (value, number)
    )

    conn.commit()

    cursor.execute(
        """
        SELECT id, number, name, position, operation_group, folder
        FROM operations
        WHERE number = ?
        """,
        (number,)
    )

    new_operation = cursor.fetchone()
    conn.close()

    return {
        "old": old_operation,
        "new": new_operation,
        "field": field,
        "value": value,
    }


def add_shift_operation(
    shift_id: int,
    employee_id: int,
    operation_id: int,
    product_size: str,
    product_color: str,
    quantity: int,
):
    if quantity <= 0:
        return False

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    now = local_now().isoformat()

    cursor.execute(
        """
        INSERT INTO shift_operations (
            shift_id, employee_id, operation_id,
            product_size, product_color, quantity, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(shift_id, operation_id, product_size, product_color)
        DO UPDATE SET
            quantity = quantity + excluded.quantity,
            updated_at = excluded.updated_at
        """,
        (shift_id, employee_id, operation_id, product_size, product_color, quantity, now, now)
    )

    conn.commit()
    conn.close()
    return True


def set_shift_operation_quantity(
    shift_id: int,
    employee_id: int,
    operation_id: int,
    product_size: str,
    product_color: str,
    quantity: int,
):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    now = local_now().isoformat()

    if quantity <= 0:
        cursor.execute(
            """
            DELETE FROM shift_operations
            WHERE shift_id = ?
              AND operation_id = ?
              AND product_size = ?
              AND product_color = ?
            """,
            (shift_id, operation_id, product_size, product_color)
        )
        conn.commit()
        conn.close()
        return False

    cursor.execute(
        """
        INSERT INTO shift_operations (
            shift_id, employee_id, operation_id,
            product_size, product_color, quantity, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(shift_id, operation_id, product_size, product_color)
        DO UPDATE SET
            quantity = excluded.quantity,
            updated_at = excluded.updated_at
        """,
        (shift_id, employee_id, operation_id, product_size, product_color, quantity, now, now)
    )

    conn.commit()
    conn.close()
    return True


def get_route_batch_by_id(batch_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        f"""
        SELECT {ROUTE_BATCH_SELECT}
        FROM route_batches
        WHERE id = ?
        """,
        (batch_id,)
    )

    batch = route_batch_from_row(cursor.fetchone())
    conn.close()
    return batch


def cancel_route_batch(batch_id: int):
    batch = get_route_batch_by_id(batch_id)

    if batch is None or batch["status"] != "active":
        return None

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    now = local_now().isoformat()

    cursor.execute(
        """
        UPDATE route_batches
        SET status = 'cancelled',
            updated_at = ?,
            completed_at = ?
        WHERE id = ?
          AND status = 'active'
        """,
        (now, now, batch_id),
    )

    changed = cursor.rowcount > 0
    conn.commit()
    conn.close()

    return get_route_batch_by_id(batch_id) if changed else None


def get_active_route_batches():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        f"""
        SELECT {ROUTE_BATCH_SELECT}
        FROM route_batches
        WHERE status = 'active'
        ORDER BY created_at ASC, id ASC
        """
    )

    batches = [route_batch_from_row(row) for row in cursor.fetchall()]
    conn.close()
    return batches


def get_employee_route_batches(employee_id: int, status: str):
    if status not in {"active", "done"}:
        return []

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        f"""
        SELECT {ROUTE_BATCH_SELECT}
        FROM route_batches
        WHERE status = ?
          AND assigned_employee_id = ?
        ORDER BY updated_at DESC, id DESC
        """,
        (status, employee_id),
    )

    batches = [route_batch_from_row(row) for row in cursor.fetchall()]
    conn.close()
    return batches


def assign_route_batch(batch_id: int, employee_id: int):
    batch = get_route_batch_by_id(batch_id)

    if batch is None or batch["status"] != "active":
        return None

    if batch.get("assigned_employee_id") not in (None, employee_id):
        return None

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    now = local_now().isoformat()

    cursor.execute(
        """
        UPDATE route_batches
        SET assigned_employee_id = ?,
            assigned_at = COALESCE(assigned_at, ?),
            updated_at = ?
        WHERE id = ?
          AND status = 'active'
          AND (assigned_employee_id IS NULL OR assigned_employee_id = ?)
        """,
        (employee_id, now, now, batch_id, employee_id),
    )

    changed = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return get_route_batch_by_id(batch_id) if changed else None


def create_route_batch(
    product_name: str,
    product_size: str,
    product_color: str,
    quantity: int,
    employee_id: int | None,
    route_step_index: int = 0,
    status: str = "active",
    source_stock_id: int | None = None,
):
    if quantity <= 0:
        return None

    if status not in {"active", "done"}:
        return None

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    now = local_now().isoformat()
    completed_at = now if status == "done" else None

    cursor.execute(
        """
        INSERT INTO route_batches (
            product_name,
            product_size,
            product_color,
            quantity,
            route_step_index,
            status,
            created_by_employee_id,
            created_at,
            updated_at,
            completed_at,
            source_stock_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            product_name,
            product_size,
            product_color,
            quantity,
            route_step_index,
            status,
            employee_id,
            now,
            now,
            completed_at,
            source_stock_id,
        )
    )

    batch_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return get_route_batch_by_id(batch_id)


def complete_route_batch_step(
    batch_id: int,
    employee_id: int | None,
    operation_name: str,
    position: str,
    next_step_index: int,
    new_status: str,
    good_quantity: int | None = None,
    defect_quantity: int = 0,
):
    batch = get_route_batch_by_id(batch_id)

    if batch is None or batch["status"] != "active":
        return None

    if batch.get("assigned_employee_id") not in (None, employee_id):
        return None

    if good_quantity is None:
        good_quantity = batch["quantity"]

    if good_quantity < 0 or defect_quantity < 0 or good_quantity + defect_quantity > batch["quantity"]:
        return None

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    now = local_now().isoformat()
    completed_at = now if new_status == "done" else None

    cursor.execute(
        """
        INSERT INTO route_batch_history (
            batch_id,
            step_index,
            operation_name,
            position,
            employee_id,
            quantity,
            completed_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            batch_id,
            batch["route_step_index"],
            operation_name,
            position,
            employee_id,
            good_quantity,
            now,
        )
    )

    cursor.execute(
        """
        UPDATE route_batches
        SET route_step_index = ?,
            status = ?,
            assigned_employee_id = COALESCE(assigned_employee_id, ?),
            assigned_at = COALESCE(assigned_at, ?),
            good_quantity = ?,
            defect_quantity = ?,
            updated_at = ?,
            completed_at = ?
        WHERE id = ?
        """,
        (next_step_index, new_status, employee_id, now, good_quantity, defect_quantity, now, completed_at, batch_id)
    )

    conn.commit()
    conn.close()
    return get_route_batch_by_id(batch_id)


def get_shift_report(shift_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            CASE
                WHEN operations.folder IS NULL OR operations.folder = '' THEN operations.name
                ELSE operations.folder || ': ' || operations.name
            END AS operation_name,
            shift_operations.product_size,
            shift_operations.product_color,
            shift_operations.quantity,
            operations.unit
        FROM shift_operations
        JOIN operations ON operations.id = shift_operations.operation_id
        WHERE shift_operations.shift_id = ?
          AND shift_operations.quantity > 0
        ORDER BY COALESCE(operations.sort_order, operations.number), operations.number
        """,
        (shift_id,)
    )

    rows = cursor.fetchall()
    conn.close()
    return rows


def get_shift_operation_choices(shift_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            shift_operations.id,
            CASE
                WHEN operations.folder IS NULL OR operations.folder = '' THEN operations.name
                ELSE operations.folder || ': ' || operations.name
            END AS operation_name,
            shift_operations.product_size,
            shift_operations.product_color,
            shift_operations.quantity,
            operations.unit
        FROM shift_operations
        JOIN operations ON operations.id = shift_operations.operation_id
        WHERE shift_operations.shift_id = ?
          AND shift_operations.quantity > 0
        ORDER BY COALESCE(operations.sort_order, operations.number), operations.number
        """,
        (shift_id,)
    )

    rows = cursor.fetchall()
    conn.close()
    return rows


def update_shift_operation_quantity(shift_operation_id: int, quantity: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            shift_operations.id,
            shift_operations.shift_id,
            CASE
                WHEN operations.folder IS NULL OR operations.folder = '' THEN operations.name
                ELSE operations.folder || ': ' || operations.name
            END AS operation_name,
            shift_operations.product_size,
            shift_operations.product_color,
            shift_operations.quantity,
            operations.unit
        FROM shift_operations
        JOIN operations ON operations.id = shift_operations.operation_id
        WHERE shift_operations.id = ?
        """,
        (shift_operation_id,)
    )

    row = cursor.fetchone()

    if row is None:
        conn.close()
        return None

    _, shift_id, operation_name, product_size, product_color, old_quantity, unit = row

    cursor.execute(
        """
        UPDATE shift_operations
        SET quantity = ?,
            updated_at = ?
        WHERE id = ?
        """,
        (quantity, local_now().isoformat(), shift_operation_id)
    )

    conn.commit()
    conn.close()

    return {
        "shift_id": shift_id,
        "operation_name": operation_name,
        "product_size": product_size,
        "product_color": product_color,
        "old_quantity": old_quantity,
        "new_quantity": quantity,
        "unit": unit,
    }


def delete_shift_operation(shift_operation_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            shift_operations.id,
            shift_operations.shift_id,
            CASE
                WHEN operations.folder IS NULL OR operations.folder = '' THEN operations.name
                ELSE operations.folder || ': ' || operations.name
            END AS operation_name,
            shift_operations.product_size,
            shift_operations.product_color,
            shift_operations.quantity,
            operations.unit
        FROM shift_operations
        JOIN operations ON operations.id = shift_operations.operation_id
        WHERE shift_operations.id = ?
        """,
        (shift_operation_id,)
    )

    row = cursor.fetchone()

    if row is None:
        conn.close()
        return None

    _, shift_id, operation_name, product_size, product_color, quantity, unit = row

    cursor.execute(
        """
        DELETE FROM shift_operations
        WHERE id = ?
        """,
        (shift_operation_id,)
    )

    conn.commit()
    conn.close()

    return {
        "shift_id": shift_id,
        "operation_name": operation_name,
        "product_size": product_size,
        "product_color": product_color,
        "quantity": quantity,
        "unit": unit,
    }


def create_cutting_contour_batch(
    product_name: str,
    shift_id: int,
    employee_id: int,
    operation_id: int,
    size_quantities: dict[str, int],
):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    now = local_now()
    now_text = now.isoformat()

    cursor.execute(
        """
        INSERT INTO cutting_batches (
            product_name, status,
            contour_shift_id, contour_operation_id, contour_employee_id, contour_date,
            created_at, updated_at
        )
        VALUES (?, 'contours_done', ?, ?, ?, ?, ?, ?)
        """,
        (product_name, shift_id, operation_id, employee_id, now.date().isoformat(), now_text, now_text)
    )

    batch_id = cursor.lastrowid

    cursor.executemany(
        """
        INSERT INTO cutting_batch_sizes (batch_id, product_size, quantity)
        VALUES (?, ?, ?)
        """,
        [(batch_id, product_size, quantity) for product_size, quantity in size_quantities.items()]
    )

    conn.commit()
    conn.close()
    return batch_id


def create_cutting_contour_batch_for_task(
    task_id: int,
    product_name: str,
    shift_id: int,
    employee_id: int,
    operation_id: int,
    matrix_quantities: dict[tuple[str, str], int],
):
    positive_matrix = {
        (str(product_size), str(product_color)): quantity
        for (product_size, product_color), quantity in matrix_quantities.items()
        if quantity > 0
    }

    if not positive_matrix:
        return None

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id
        FROM production_tasks
        WHERE id = ?
          AND status = 'active'
        """,
        (task_id,),
    )

    if cursor.fetchone() is None:
        conn.close()
        return None

    now = local_now()
    now_text = now.isoformat()

    cursor.execute(
        """
        INSERT INTO cutting_batches (
            product_name, production_task_id, status,
            contour_shift_id, contour_operation_id, contour_employee_id, contour_date,
            created_at, updated_at
        )
        VALUES (?, ?, 'contours_done', ?, ?, ?, ?, ?, ?)
        """,
        (product_name, task_id, shift_id, operation_id, employee_id, now.date().isoformat(), now_text, now_text),
    )
    batch_id = cursor.lastrowid

    size_totals: dict[str, int] = {}
    for product_size, _product_color in positive_matrix:
        size_totals[product_size] = size_totals.get(product_size, 0) + positive_matrix[(product_size, _product_color)]

    cursor.executemany(
        """
        INSERT INTO cutting_batch_sizes (batch_id, product_size, quantity)
        VALUES (?, ?, ?)
        """,
        [(batch_id, product_size, quantity) for product_size, quantity in size_totals.items()],
    )

    cursor.executemany(
        """
        INSERT INTO cutting_batch_matrix (batch_id, product_size, product_color, quantity)
        VALUES (?, ?, ?, ?)
        """,
        [
            (batch_id, product_size, product_color, quantity)
            for (product_size, product_color), quantity in positive_matrix.items()
        ],
    )

    cursor.executemany(
        """
        UPDATE production_task_items
        SET contour_quantity = ?
        WHERE task_id = ?
          AND product_size = ?
          AND product_color = ?
        """,
        [
            (quantity, task_id, product_size, product_color)
            for (product_size, product_color), quantity in positive_matrix.items()
        ],
    )

    cursor.execute(
        """
        UPDATE production_tasks
        SET status = 'contours_done',
            updated_at = ?
        WHERE id = ?
        """,
        (now_text, task_id),
    )

    conn.commit()
    conn.close()
    return batch_id


def get_cutting_batches_for_layout(product_name: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            cutting_batches.id,
            cutting_batches.product_name,
            cutting_batches.contour_date,
            cutting_batches.production_task_id,
            employees.full_name,
            GROUP_CONCAT(DISTINCT cutting_batch_sizes.product_size || ' - ' || cutting_batch_sizes.quantity) AS sizes_text,
            GROUP_CONCAT(DISTINCT cutting_batch_matrix.product_color) AS colors_text
        FROM cutting_batches
        LEFT JOIN employees ON employees.id = cutting_batches.contour_employee_id
        LEFT JOIN cutting_batch_sizes ON cutting_batch_sizes.batch_id = cutting_batches.id
        LEFT JOIN cutting_batch_matrix ON cutting_batch_matrix.batch_id = cutting_batches.id
        WHERE cutting_batches.product_name = ?
          AND cutting_batches.status = 'contours_done'
        GROUP BY
            cutting_batches.id,
            cutting_batches.product_name,
            cutting_batches.contour_date,
            cutting_batches.production_task_id,
            employees.full_name
        ORDER BY cutting_batches.contour_date ASC, cutting_batches.id ASC
        """,
        (product_name,)
    )

    rows = cursor.fetchall()
    conn.close()
    return rows


def get_preparation_folder(operation_name: str):
    return PREPARATION_OPERATION_OPTIONS.get(operation_name, {}).get("folder", "")


def is_material_preparation_operation(operation_name: str):
    return get_preparation_folder(operation_name) in MATERIAL_PREPARATION_FOLDERS


def is_auto_preparation_operation(operation_name: str):
    return get_preparation_folder(operation_name) in AUTO_PREPARATION_FOLDERS


def is_elastic_preparation_operation(operation_name: str):
    return get_preparation_folder(operation_name) == "Нарезание резинки"


def should_skip_cut_output_step(route_step: dict):
    operation_name = route_step.get("operation", "")
    return is_material_preparation_operation(operation_name) or operation_name == "Сшивание резинок в кольцо"


def preparation_option_size_label(operation_name: str, product_size: str):
    product_size = str(product_size).strip()

    for label in PREPARATION_OPERATION_OPTIONS.get(operation_name, {}).get("sizes", []):
        if label == product_size or label.startswith(f"{product_size} "):
            return label

    return product_size


def preparation_group_label(operation_name: str, product_size: str):
    label = preparation_option_size_label(operation_name, product_size)

    if is_elastic_preparation_operation(operation_name) and "(" in label and ")" in label:
        return label[label.find("(") + 1:label.rfind(")")].strip()

    return label


def sort_product_size_values(values):
    def size_key(value):
        value_text = str(value)
        return (0, int(value_text)) if value_text.isdigit() else (1, value_text)

    return sorted(values, key=size_key)


def preparation_batch_size_label(operation_name: str, sizes, group_label: str):
    sorted_sizes = sort_product_size_values(sizes)
    size_text = ", ".join(sorted_sizes)

    if is_elastic_preparation_operation(operation_name):
        return f"{size_text} ({group_label})" if group_label and size_text else group_label or size_text

    if len(sorted_sizes) == 1:
        return preparation_option_size_label(operation_name, sorted_sizes[0])

    return f"{size_text} ({group_label})" if group_label else size_text


def preparation_material_color(operation_name: str, product_color: str):
    if is_elastic_preparation_operation(operation_name):
        return "Черный"

    return product_color


def _get_cutting_batch_result_rows(cursor, batch_id: int):
    cursor.execute("SELECT COUNT(*) FROM cutting_batch_matrix WHERE batch_id = ?", (batch_id,))
    has_matrix = cursor.fetchone()[0] > 0

    if has_matrix:
        cursor.execute(
            """
            SELECT
                cutting_batch_matrix.product_size,
                cutting_batch_matrix.product_color,
                cutting_batch_matrix.quantity * cutting_batch_colors.layers AS quantity
            FROM cutting_batch_matrix
            JOIN cutting_batch_colors
                ON cutting_batch_colors.batch_id = cutting_batch_matrix.batch_id
               AND cutting_batch_colors.product_color = cutting_batch_matrix.product_color
            WHERE cutting_batch_matrix.batch_id = ?
              AND cutting_batch_matrix.quantity > 0
              AND cutting_batch_colors.layers > 0
            ORDER BY
                CAST(cutting_batch_matrix.product_size AS INTEGER),
                cutting_batch_matrix.product_color
            """,
            (batch_id,),
        )

        return cursor.fetchall()

    cursor.execute(
        """
        SELECT
            cutting_batch_sizes.product_size,
            cutting_batch_colors.product_color,
            cutting_batch_sizes.quantity * cutting_batch_colors.layers AS quantity
        FROM cutting_batch_sizes
        CROSS JOIN cutting_batch_colors
        WHERE cutting_batch_sizes.batch_id = ?
          AND cutting_batch_colors.batch_id = ?
          AND cutting_batch_sizes.quantity > 0
          AND cutting_batch_colors.layers > 0
        ORDER BY
            CAST(cutting_batch_sizes.product_size AS INTEGER),
            cutting_batch_colors.product_color
        """,
        (batch_id, batch_id),
    )

    return cursor.fetchall()


def _create_preparation_route_batches_for_layout(cursor, batch_id: int, employee_id: int | None, now_text: str):
    from route_maps import CUTTING_ROUTE, PRODUCT_ROUTE_MAPS

    cursor.execute("SELECT product_name FROM cutting_batches WHERE id = ?", (batch_id,))
    batch_row = cursor.fetchone()
    product_name = batch_row[0] if batch_row else ""
    route_steps = PRODUCT_ROUTE_MAPS.get(product_name, [])

    if not product_name or not route_steps:
        return []

    result_rows = _get_cutting_batch_result_rows(cursor, batch_id)
    grouped_tasks = {}

    for step_index, route_step in enumerate(route_steps[len(CUTTING_ROUTE):], start=len(CUTTING_ROUTE)):
        operation_name = route_step["operation"]

        if not is_auto_preparation_operation(operation_name):
            continue

        for product_size, product_color, quantity in result_rows:
            if quantity <= 0:
                continue

            material_color = preparation_material_color(operation_name, product_color)
            size_label = preparation_option_size_label(operation_name, product_size)
            group_label = preparation_group_label(operation_name, product_size)
            group_size_key = group_label if is_elastic_preparation_operation(operation_name) else size_label
            group_key = (step_index, operation_name, material_color, group_size_key)
            group = grouped_tasks.setdefault(
                group_key,
                {
                    "route_step_index": step_index,
                    "operation_name": operation_name,
                    "product_color": material_color,
                    "group_label": group_label,
                    "sizes": set(),
                    "quantity": 0,
                },
            )
            group["sizes"].add(str(product_size))
            group["quantity"] += int(quantity)

    created_ids = []

    for group in grouped_tasks.values():
        product_size = preparation_batch_size_label(
            group["operation_name"],
            group["sizes"],
            group["group_label"],
        )
        cursor.execute(
            """
            INSERT INTO route_batches (
                product_name,
                product_size,
                product_color,
                quantity,
                route_step_index,
                status,
                created_by_employee_id,
                created_at,
                updated_at,
                completed_at,
                source_stock_id
            )
            VALUES (?, ?, ?, ?, ?, 'active', ?, ?, ?, NULL, NULL)
            """,
            (
                product_name,
                product_size,
                group["product_color"],
                group["quantity"],
                group["route_step_index"],
                employee_id,
                now_text,
                now_text,
            ),
        )
        created_ids.append(cursor.lastrowid)

    return created_ids


def add_cutting_layout(
    batch_id: int,
    shift_id: int,
    employee_id: int,
    operation_id: int,
    color_layers: dict[str, int],
):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    now = local_now()
    now_text = now.isoformat()

    cursor.execute(
        """
        UPDATE cutting_batches
        SET status = 'layout_done',
            layout_shift_id = ?,
            layout_operation_id = ?,
            layout_employee_id = ?,
            layout_date = ?,
            updated_at = ?
        WHERE id = ?
          AND status = 'contours_done'
        """,
        (shift_id, operation_id, employee_id, now.date().isoformat(), now_text, batch_id)
    )

    if cursor.rowcount == 0:
        conn.close()
        return False

    cursor.executemany(
        """
        INSERT INTO cutting_batch_colors (batch_id, product_color, layers)
        VALUES (?, ?, ?)
        ON CONFLICT(batch_id, product_color)
        DO UPDATE SET layers = excluded.layers
        """,
        [(batch_id, product_color, layers) for product_color, layers in color_layers.items()]
    )

    _create_preparation_route_batches_for_layout(cursor, batch_id, employee_id, now_text)

    cursor.execute("SELECT production_task_id FROM cutting_batches WHERE id = ?", (batch_id,))
    task_row = cursor.fetchone()

    if task_row and task_row[0] is not None:
        cursor.execute(
            """
            UPDATE production_tasks
            SET status = 'in_cutting',
                updated_at = ?
            WHERE id = ?
              AND status IN ('active', 'contours_done')
            """,
            (now_text, task_row[0]),
        )

    conn.commit()
    conn.close()
    return True


def get_cutting_batches_for_cutting(product_name: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            cutting_batches.id,
            cutting_batches.product_name,
            cutting_batches.contour_date,
            cutting_batches.layout_date,
            cutting_batches.cutting_progress,
            GROUP_CONCAT(DISTINCT cutting_batch_colors.product_color || ' - ' || cutting_batch_colors.layers || ' сл.') AS colors_text
        FROM cutting_batches
        LEFT JOIN cutting_batch_colors ON cutting_batch_colors.batch_id = cutting_batches.id
        WHERE cutting_batches.product_name = ?
          AND cutting_batches.status IN ('layout_done', 'cutting_in_progress')
        GROUP BY
            cutting_batches.id,
            cutting_batches.product_name,
            cutting_batches.contour_date,
            cutting_batches.layout_date,
            cutting_batches.cutting_progress
        ORDER BY cutting_batches.layout_date ASC, cutting_batches.id ASC
        """,
        (product_name,)
    )

    rows = cursor.fetchall()
    conn.close()
    return rows


def update_cutting_batch_progress(
    batch_id: int,
    shift_id: int,
    employee_id: int,
    operation_id: int,
    progress: int,
):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    now = local_now()
    now_text = now.isoformat()
    status = "cutting_done" if progress >= 100 else "cutting_in_progress"

    cursor.execute(
        """
        UPDATE cutting_batches
        SET status = ?,
            cutting_shift_id = ?,
            cutting_operation_id = ?,
            cutting_employee_id = ?,
            cutting_progress = ?,
            updated_at = ?
        WHERE id = ?
          AND status IN ('layout_done', 'cutting_in_progress')
        """,
        (status, shift_id, operation_id, employee_id, progress, now_text, batch_id)
    )

    changed = cursor.rowcount > 0

    if changed:
        cursor.execute("SELECT production_task_id FROM cutting_batches WHERE id = ?", (batch_id,))
        task_row = cursor.fetchone()

        if task_row and task_row[0] is not None:
            cursor.execute(
                """
                UPDATE production_tasks
                SET status = 'in_cutting',
                    updated_at = ?
                WHERE id = ?
                  AND status IN ('active', 'contours_done', 'in_cutting')
                """,
                (now_text, task_row[0]),
            )

    conn.commit()
    conn.close()
    return changed


def get_cutting_batches_for_formation(product_name: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            product_name,
            contour_date,
            layout_date,
            cutting_progress
        FROM cutting_batches
        WHERE product_name = ?
          AND status = 'cutting_done'
        ORDER BY layout_date ASC, id ASC
        """,
        (product_name,)
    )

    rows = cursor.fetchall()
    conn.close()
    return rows


def get_cutting_batch_result_rows(batch_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    rows = _get_cutting_batch_result_rows(cursor, batch_id)
    conn.close()
    return rows


def mark_cutting_batch_formed(batch_id: int, shift_id: int, employee_id: int, operation_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    now = local_now()
    now_text = now.isoformat()

    cursor.execute(
        """
        UPDATE cutting_batches
        SET status = 'formed',
            formed_shift_id = ?,
            formed_operation_id = ?,
            formed_employee_id = ?,
            formed_date = ?,
            updated_at = ?
        WHERE id = ?
          AND status = 'cutting_done'
        """,
        (shift_id, operation_id, employee_id, now.date().isoformat(), now_text, batch_id)
    )

    changed = cursor.rowcount > 0

    if changed:
        cursor.execute(
            """
            SELECT product_name, production_task_id
            FROM cutting_batches
            WHERE id = ?
            """,
            (batch_id,),
        )
        task_row = cursor.fetchone()
        batch_product_name = task_row[0] if task_row else ""
        task_id = task_row[1] if task_row else None

        if task_id is not None:
            cursor.execute("SELECT COUNT(*) FROM cutting_batch_matrix WHERE batch_id = ?", (batch_id,))
            has_matrix = cursor.fetchone()[0] > 0

            if has_matrix:
                cursor.execute(
                    """
                    SELECT
                        cutting_batch_matrix.product_size,
                        cutting_batch_matrix.product_color,
                        cutting_batch_matrix.quantity * cutting_batch_colors.layers AS quantity
                    FROM cutting_batch_matrix
                    JOIN cutting_batch_colors
                        ON cutting_batch_colors.batch_id = cutting_batch_matrix.batch_id
                       AND cutting_batch_colors.product_color = cutting_batch_matrix.product_color
                    WHERE cutting_batch_matrix.batch_id = ?
                    """,
                    (batch_id,),
                )
            else:
                cursor.execute(
                    """
                    SELECT
                        cutting_batch_sizes.product_size,
                        cutting_batch_colors.product_color,
                        cutting_batch_sizes.quantity * cutting_batch_colors.layers AS quantity
                    FROM cutting_batch_sizes
                    CROSS JOIN cutting_batch_colors
                    WHERE cutting_batch_sizes.batch_id = ?
                      AND cutting_batch_colors.batch_id = ?
                    """,
                    (batch_id, batch_id),
                )

            result_rows = cursor.fetchall()
            ready_for_position = get_first_production_position(batch_product_name)
            stage_name = "Раскроенные"

            cursor.executemany(
                """
                UPDATE production_task_items
                SET formed_quantity = ?
                WHERE task_id = ?
                  AND product_size = ?
                  AND product_color = ?
                """,
                [
                    (quantity, task_id, product_size, product_color)
                    for product_size, product_color, quantity in result_rows
                ],
            )

            for product_size, product_color, quantity in result_rows:
                if quantity <= 0:
                    continue

                now_stock_text = local_now().isoformat()
                cursor.execute(
                    """
                    INSERT INTO warehouse_stock (
                        item_type, product_name, product_size, product_color, stage_name,
                        ready_for_position, quantity, unit, updated_at
                    )
                    VALUES ('semifinished', ?, ?, ?, ?, ?, ?, 'шт', ?)
                    ON CONFLICT(item_type, product_name, product_size, product_color, stage_name, ready_for_position, unit)
                    DO UPDATE SET
                        quantity = quantity + excluded.quantity,
                        updated_at = excluded.updated_at
                    """,
                    (
                        batch_product_name,
                        product_size,
                        product_color,
                        stage_name,
                        ready_for_position,
                        quantity,
                        now_stock_text,
                    ),
                )
                cursor.execute(
                    """
                    SELECT id
                    FROM warehouse_stock
                    WHERE item_type = 'semifinished'
                      AND product_name = ?
                      AND product_size = ?
                      AND product_color = ?
                      AND stage_name = ?
                      AND ready_for_position = ?
                      AND unit = 'шт'
                    """,
                    (batch_product_name, product_size, product_color, stage_name, ready_for_position),
                )
                stock_id = cursor.fetchone()[0]
                cursor.execute(
                    """
                    INSERT INTO warehouse_stock_movements (
                        stock_id, item_type, product_name, product_size, product_color, stage_name,
                        ready_for_position, quantity, unit, movement_type, source_type, source_id,
                        created_by_employee_id, created_at
                    )
                    VALUES (?, 'semifinished', ?, ?, ?, ?, ?, ?, 'шт', 'receipt', 'cutting_batch', ?, ?, ?)
                    """,
                    (
                        stock_id,
                        batch_product_name,
                        product_size,
                        product_color,
                        stage_name,
                        ready_for_position,
                        quantity,
                        batch_id,
                        employee_id,
                        now_stock_text,
                    ),
                )

            cursor.execute(
                """
                UPDATE production_tasks
                SET status = 'formed',
                    updated_at = ?,
                    completed_at = ?
                WHERE id = ?
                """,
                (now_text, now_text, task_id),
            )

    conn.commit()
    conn.close()
    return changed


def get_admin_cutting_batches(limit: int = 50):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            cutting_batches.id,
            cutting_batches.product_name,
            cutting_batches.status,
            cutting_batches.contour_date,
            cutting_batches.layout_date,
            cutting_batches.cutting_progress,
            employees.full_name,
            GROUP_CONCAT(DISTINCT cutting_batch_sizes.product_size || ' - ' || cutting_batch_sizes.quantity) AS sizes_text,
            GROUP_CONCAT(DISTINCT cutting_batch_colors.product_color || ' - ' || cutting_batch_colors.layers || ' сл.') AS colors_text
        FROM cutting_batches
        LEFT JOIN employees ON employees.id = cutting_batches.contour_employee_id
        LEFT JOIN cutting_batch_sizes ON cutting_batch_sizes.batch_id = cutting_batches.id
        LEFT JOIN cutting_batch_colors ON cutting_batch_colors.batch_id = cutting_batches.id
        GROUP BY
            cutting_batches.id,
            cutting_batches.product_name,
            cutting_batches.status,
            cutting_batches.contour_date,
            cutting_batches.layout_date,
            cutting_batches.cutting_progress,
            employees.full_name
        ORDER BY cutting_batches.id DESC
        LIMIT ?
        """,
        (limit,)
    )

    rows = cursor.fetchall()
    conn.close()
    return rows


def delete_cutting_batch(batch_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            cutting_batches.id,
            cutting_batches.product_name,
            cutting_batches.status,
            cutting_batches.contour_date,
            employees.full_name
        FROM cutting_batches
        LEFT JOIN employees ON employees.id = cutting_batches.contour_employee_id
        WHERE cutting_batches.id = ?
        """,
        (batch_id,)
    )

    batch = cursor.fetchone()

    if batch is None:
        conn.close()
        return None

    cursor.execute("DELETE FROM cutting_batch_colors WHERE batch_id = ?", (batch_id,))
    cursor.execute("DELETE FROM cutting_batch_sizes WHERE batch_id = ?", (batch_id,))
    cursor.execute("DELETE FROM cutting_batch_matrix WHERE batch_id = ?", (batch_id,))
    cursor.execute("DELETE FROM cutting_batches WHERE id = ?", (batch_id,))

    conn.commit()
    conn.close()
    return batch


def rollback_cutting_batch(batch_id: int, target_status: str):
    if target_status not in {"contours_done", "layout_done", "cutting_done"}:
        return None

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, product_name, status, contour_date, layout_date, cutting_progress
        FROM cutting_batches
        WHERE id = ?
        """,
        (batch_id,)
    )
    batch = cursor.fetchone()

    if batch is None:
        conn.close()
        return None

    batch_id, product_name, old_status, contour_date, layout_date, cutting_progress = batch
    now_text = local_now().isoformat()

    if target_status == "contours_done":
        cursor.execute("DELETE FROM cutting_batch_colors WHERE batch_id = ?", (batch_id,))
        cursor.execute(
            """
            UPDATE cutting_batches
            SET status = 'contours_done',
                layout_shift_id = NULL,
                layout_operation_id = NULL,
                layout_employee_id = NULL,
                layout_date = NULL,
                cutting_shift_id = NULL,
                cutting_operation_id = NULL,
                cutting_employee_id = NULL,
                cutting_progress = 0,
                formed_shift_id = NULL,
                formed_operation_id = NULL,
                formed_employee_id = NULL,
                formed_date = NULL,
                updated_at = ?
            WHERE id = ?
            """,
            (now_text, batch_id)
        )
    elif target_status == "layout_done":
        if layout_date is None:
            conn.close()
            return None

        cursor.execute(
            """
            UPDATE cutting_batches
            SET status = 'layout_done',
                cutting_shift_id = NULL,
                cutting_operation_id = NULL,
                cutting_employee_id = NULL,
                cutting_progress = 0,
                formed_shift_id = NULL,
                formed_operation_id = NULL,
                formed_employee_id = NULL,
                formed_date = NULL,
                updated_at = ?
            WHERE id = ?
            """,
            (now_text, batch_id)
        )
    else:
        if layout_date is None:
            conn.close()
            return None

        cursor.execute(
            """
            UPDATE cutting_batches
            SET status = 'cutting_done',
                cutting_progress = 100,
                formed_shift_id = NULL,
                formed_operation_id = NULL,
                formed_employee_id = NULL,
                formed_date = NULL,
                updated_at = ?
            WHERE id = ?
            """,
            (now_text, batch_id)
        )

    conn.commit()
    conn.close()

    return {
        "id": batch_id,
        "product_name": product_name,
        "old_status": old_status,
        "new_status": target_status,
        "contour_date": contour_date,
        "layout_date": layout_date,
        "old_progress": cutting_progress,
    }


def admin_update_cutting_batch_progress(batch_id: int, progress: int):
    if progress not in {25, 50, 75, 100}:
        return None

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, product_name, status, layout_date, cutting_progress
        FROM cutting_batches
        WHERE id = ?
        """,
        (batch_id,)
    )
    batch = cursor.fetchone()

    if batch is None:
        conn.close()
        return None

    batch_id, product_name, old_status, layout_date, old_progress = batch

    if layout_date is None:
        conn.close()
        return None

    new_status = "cutting_done" if progress == 100 else "cutting_in_progress"

    cursor.execute(
        """
        UPDATE cutting_batches
        SET status = ?,
            cutting_progress = ?,
            formed_shift_id = NULL,
            formed_operation_id = NULL,
            formed_employee_id = NULL,
            formed_date = NULL,
            updated_at = ?
        WHERE id = ?
        """,
        (new_status, progress, local_now().isoformat(), batch_id)
    )

    conn.commit()
    conn.close()

    return {
        "id": batch_id,
        "product_name": product_name,
        "old_status": old_status,
        "new_status": new_status,
        "old_progress": old_progress,
        "new_progress": progress,
    }


def add_fabric_receipt(
    material_name: str,
    product_color: str,
    quantity: float,
    employee_id: int | None,
    unit: str = "м",
    comment: str = "",
):
    material_name = material_name.strip()
    product_color = product_color.strip()
    unit = unit.strip() or "м"

    if not material_name or not product_color or quantity <= 0:
        return None

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    now = local_now().isoformat()

    cursor.execute(
        """
        INSERT INTO fabric_stock (material_name, product_color, quantity, unit, updated_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(material_name, product_color, unit)
        DO UPDATE SET
            quantity = quantity + excluded.quantity,
            updated_at = excluded.updated_at
        """,
        (material_name, product_color, quantity, unit, now),
    )

    cursor.execute(
        """
        INSERT INTO fabric_stock_movements (
            material_name, product_color, quantity, unit, movement_type, comment,
            created_by_employee_id, created_at
        )
        VALUES (?, ?, ?, ?, 'receipt', ?, ?, ?)
        """,
        (material_name, product_color, quantity, unit, comment, employee_id, now),
    )

    conn.commit()

    cursor.execute(
        """
        SELECT id, material_name, product_color, quantity, unit, updated_at
        FROM fabric_stock
        WHERE material_name = ?
          AND product_color = ?
          AND unit = ?
        """,
        (material_name, product_color, unit),
    )
    row = cursor.fetchone()
    conn.close()
    return row


def get_fabric_stock_rows():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT material_name, product_color, quantity, unit, updated_at
        FROM fabric_stock
        WHERE quantity > 0
        ORDER BY material_name ASC, product_color ASC
        """
    )

    rows = cursor.fetchall()
    conn.close()
    return rows


def warehouse_stock_from_row(row):
    return row_to_dict(WAREHOUSE_STOCK_COLUMNS, row)


def get_next_route_position(product_name: str, route_step_index: int):
    from route_maps import PRODUCT_ROUTE_MAPS

    steps = PRODUCT_ROUTE_MAPS.get(product_name, [])
    next_index = route_step_index + 1

    if next_index < len(steps):
        return steps[next_index]["position"]

    return "Склад"


def get_first_production_position(product_name: str):
    from route_maps import CUTTING_ROUTE, PRODUCT_ROUTE_MAPS

    steps = PRODUCT_ROUTE_MAPS.get(product_name, [])

    for route_step in steps[len(CUTTING_ROUTE):]:
        if should_skip_cut_output_step(route_step):
            continue

        return route_step["position"]

    return "Склад"


def add_warehouse_stock(
    item_type: str,
    product_name: str,
    product_size: str,
    product_color: str,
    stage_name: str,
    ready_for_position: str,
    quantity: int,
    employee_id: int | None,
    source_type: str = "",
    source_id: int | None = None,
):
    item_type = item_type.strip()
    product_name = product_name.strip()
    product_size = str(product_size).strip()
    product_color = product_color.strip()
    stage_name = stage_name.strip()
    ready_for_position = ready_for_position.strip() or "Склад"

    if item_type not in {"semifinished", "finished"}:
        return None

    if not product_name or not product_size or not product_color or not stage_name or quantity <= 0:
        return None

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    now = local_now().isoformat()

    cursor.execute(
        """
        INSERT INTO warehouse_stock (
            item_type, product_name, product_size, product_color, stage_name,
            ready_for_position, quantity, unit, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, 'шт', ?)
        ON CONFLICT(item_type, product_name, product_size, product_color, stage_name, ready_for_position, unit)
        DO UPDATE SET
            quantity = quantity + excluded.quantity,
            updated_at = excluded.updated_at
        """,
        (item_type, product_name, product_size, product_color, stage_name, ready_for_position, quantity, now),
    )

    cursor.execute(
        """
        SELECT id
        FROM warehouse_stock
        WHERE item_type = ?
          AND product_name = ?
          AND product_size = ?
          AND product_color = ?
          AND stage_name = ?
          AND ready_for_position = ?
          AND unit = 'шт'
        """,
        (item_type, product_name, product_size, product_color, stage_name, ready_for_position),
    )
    stock_id = cursor.fetchone()[0]

    cursor.execute(
        """
        INSERT INTO warehouse_stock_movements (
            stock_id, item_type, product_name, product_size, product_color, stage_name,
            ready_for_position, quantity, unit, movement_type, source_type, source_id,
            created_by_employee_id, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'шт', 'receipt', ?, ?, ?, ?)
        """,
        (
            stock_id,
            item_type,
            product_name,
            product_size,
            product_color,
            stage_name,
            ready_for_position,
            quantity,
            source_type,
            source_id,
            employee_id,
            now,
        ),
    )

    conn.commit()
    conn.close()
    return get_warehouse_stock_by_id(stock_id)


def consume_warehouse_stock(stock_id: int, quantity: int, employee_id: int | None, source_type: str = "", source_id: int | None = None):
    if quantity <= 0:
        return None

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        f"""
        SELECT {WAREHOUSE_STOCK_SELECT}
        FROM warehouse_stock
        WHERE id = ?
        """,
        (stock_id,),
    )
    row = cursor.fetchone()
    stock = warehouse_stock_from_row(row)

    if stock is None or stock["quantity"] < quantity:
        conn.close()
        return None

    now = local_now().isoformat()
    new_quantity = stock["quantity"] - quantity

    cursor.execute(
        """
        UPDATE warehouse_stock
        SET quantity = ?,
            updated_at = ?
        WHERE id = ?
        """,
        (new_quantity, now, stock_id),
    )

    cursor.execute(
        """
        INSERT INTO warehouse_stock_movements (
            stock_id, item_type, product_name, product_size, product_color, stage_name,
            ready_for_position, quantity, unit, movement_type, source_type, source_id,
            created_by_employee_id, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'issue', ?, ?, ?, ?)
        """,
        (
            stock_id,
            stock["item_type"],
            stock["product_name"],
            stock["product_size"],
            stock["product_color"],
            stock["stage_name"],
            stock["ready_for_position"],
            -quantity,
            stock["unit"],
            source_type,
            source_id,
            employee_id,
            now,
        ),
    )

    conn.commit()
    conn.close()
    return {**stock, "quantity": new_quantity}


def get_warehouse_stock_by_id(stock_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        f"""
        SELECT {WAREHOUSE_STOCK_SELECT}
        FROM warehouse_stock
        WHERE id = ?
        """,
        (stock_id,),
    )
    row = warehouse_stock_from_row(cursor.fetchone())
    conn.close()
    return row


def get_warehouse_stock_rows():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        f"""
        SELECT {WAREHOUSE_STOCK_SELECT}
        FROM warehouse_stock
        WHERE quantity > 0
        ORDER BY
            item_type ASC,
            ready_for_position ASC,
            product_name ASC,
            CAST(product_size AS INTEGER),
            product_size ASC,
            product_color ASC
        """
    )
    rows = [warehouse_stock_from_row(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def create_production_task(
    product_name: str,
    sizes: list[str],
    colors: list[str],
    employee_id: int | None,
    note: str = "",
):
    product_name = product_name.strip()
    sizes = [str(size).strip() for size in sizes if str(size).strip()]
    colors = [str(color).strip() for color in colors if str(color).strip()]

    if not product_name or not sizes or not colors:
        return None

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    now = local_now().isoformat()

    cursor.execute(
        """
        INSERT INTO production_tasks (
            product_name, status, created_by_employee_id, created_at, updated_at, note
        )
        VALUES (?, 'active', ?, ?, ?, ?)
        """,
        (product_name, employee_id, now, now, note.strip()),
    )
    task_id = cursor.lastrowid

    cursor.executemany(
        """
        INSERT INTO production_task_sizes (task_id, product_size)
        VALUES (?, ?)
        """,
        [(task_id, product_size) for product_size in sizes],
    )
    cursor.executemany(
        """
        INSERT INTO production_task_colors (task_id, product_color)
        VALUES (?, ?)
        """,
        [(task_id, product_color) for product_color in colors],
    )
    cursor.executemany(
        """
        INSERT INTO production_task_items (task_id, product_size, product_color)
        VALUES (?, ?, ?)
        """,
        [
            (task_id, product_size, product_color)
            for product_color in colors
            for product_size in sizes
        ],
    )

    conn.commit()
    conn.close()
    return get_production_task_by_id(task_id)


def get_production_task_by_id(task_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            product_name,
            status,
            created_by_employee_id,
            created_at,
            updated_at,
            completed_at,
            note
        FROM production_tasks
        WHERE id = ?
        """,
        (task_id,),
    )

    task = production_task_from_row(cursor.fetchone())
    conn.close()
    return task


def cancel_production_task(task_id: int):
    task = get_production_task_by_id(task_id)

    if task is None or task["status"] not in {"active", "contours_done", "in_cutting"}:
        return None

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    now = local_now().isoformat()

    cursor.execute(
        """
        UPDATE production_tasks
        SET status = 'cancelled',
            updated_at = ?,
            completed_at = ?
        WHERE id = ?
          AND status IN ('active', 'contours_done', 'in_cutting')
        """,
        (now, now, task_id),
    )

    changed = cursor.rowcount > 0

    if changed:
        cursor.execute(
            """
            UPDATE cutting_batches
            SET status = 'cancelled',
                updated_at = ?
            WHERE production_task_id = ?
              AND status IN ('contours_done', 'layout_done', 'cutting_in_progress', 'cutting_done')
            """,
            (now, task_id),
        )

    conn.commit()
    conn.close()

    return get_production_task_by_id(task_id) if changed else None


def get_production_task_options(task_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT product_size
        FROM production_task_sizes
        WHERE task_id = ?
        ORDER BY CAST(product_size AS INTEGER), product_size
        """,
        (task_id,),
    )
    sizes = [row[0] for row in cursor.fetchall()]

    cursor.execute(
        """
        SELECT product_color
        FROM production_task_colors
        WHERE task_id = ?
        ORDER BY product_color
        """,
        (task_id,),
    )
    colors = [row[0] for row in cursor.fetchall()]

    conn.close()
    return sizes, colors


def get_active_production_tasks():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            production_tasks.id,
            production_tasks.product_name,
            production_tasks.status,
            production_tasks.created_at,
            COALESCE(GROUP_CONCAT(DISTINCT production_task_sizes.product_size), '') AS sizes_text,
            COALESCE(GROUP_CONCAT(DISTINCT production_task_colors.product_color), '') AS colors_text
        FROM production_tasks
        LEFT JOIN production_task_sizes ON production_task_sizes.task_id = production_tasks.id
        LEFT JOIN production_task_colors ON production_task_colors.task_id = production_tasks.id
        WHERE production_tasks.status IN ('active', 'contours_done', 'in_cutting')
        GROUP BY
            production_tasks.id,
            production_tasks.product_name,
            production_tasks.status,
            production_tasks.created_at
        ORDER BY production_tasks.created_at ASC, production_tasks.id ASC
        """
    )

    rows = cursor.fetchall()
    conn.close()
    return rows


def get_active_production_tasks_for_contours():
    return [row for row in get_active_production_tasks() if row[2] == "active"]


def get_cutting_batch_task_options(batch_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT production_task_id
        FROM cutting_batches
        WHERE id = ?
        """,
        (batch_id,),
    )
    row = cursor.fetchone()

    if row is None or row[0] is None:
        conn.close()
        return [], []

    task_id = row[0]

    cursor.execute(
        """
        SELECT product_size
        FROM production_task_sizes
        WHERE task_id = ?
        ORDER BY CAST(product_size AS INTEGER), product_size
        """,
        (task_id,),
    )
    sizes = [option[0] for option in cursor.fetchall()]

    cursor.execute(
        """
        SELECT product_color
        FROM production_task_colors
        WHERE task_id = ?
        ORDER BY product_color
        """,
        (task_id,),
    )
    colors = [option[0] for option in cursor.fetchall()]

    conn.close()
    return sizes, colors


def close_shift(shift_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    now = local_now()
    end_time = now.strftime("%H:%M")
    closed_at = now.isoformat()
    edit_until = (now + timedelta(hours=1)).isoformat()

    cursor.execute(
        """
        SELECT shift_date, start_time
        FROM shifts
        WHERE id = ? AND status = 'open'
        """,
        (shift_id,)
    )

    row = cursor.fetchone()

    if row is None:
        conn.close()
        return None

    shift_date, start_time = row
    start_dt = datetime.strptime(f"{shift_date} {start_time}", "%Y-%m-%d %H:%M")
    total_minutes = int((now - start_dt).total_seconds() // 60)

    cursor.execute(
        """
        UPDATE shifts
        SET end_time = ?,
            total_minutes = ?,
            status = 'closed',
            edit_until = ?,
            closed_at = ?
        WHERE id = ?
        """,
        (end_time, total_minutes, edit_until, closed_at, shift_id)
    )

    conn.commit()
    conn.close()

    return {
        "end_time": end_time,
        "total_minutes": total_minutes,
        "edit_until": edit_until,
    }


def get_open_shifts():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            shifts.id,
            employees.full_name,
            shifts.shift_date,
            shifts.start_time
        FROM shifts
        JOIN employees ON employees.id = shifts.employee_id
        WHERE shifts.status = 'open'
          AND employees.role != 'admin'
        ORDER BY shifts.shift_date ASC, shifts.start_time ASC
        """
    )

    shifts = cursor.fetchall()
    conn.close()
    return shifts


def get_recent_shifts(limit: int = 20):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            shifts.id,
            employees.full_name,
            shifts.shift_date,
            shifts.start_time,
            shifts.end_time,
            shifts.status,
            COALESCE(COUNT(shift_operations.id), 0) AS operation_count
        FROM shifts
        JOIN employees ON employees.id = shifts.employee_id
        LEFT JOIN shift_operations ON shift_operations.shift_id = shifts.id
        WHERE employees.role != 'admin'
        GROUP BY
            shifts.id,
            employees.full_name,
            shifts.shift_date,
            shifts.start_time,
            shifts.end_time,
            shifts.status
        ORDER BY shifts.shift_date DESC, shifts.start_time DESC, shifts.id DESC
        LIMIT ?
        """,
        (limit,)
    )

    shifts = cursor.fetchall()
    conn.close()
    return shifts


def get_employee_recent_shifts(employee_id: int, limit: int = 20):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            shifts.id,
            shifts.shift_date,
            shifts.start_time,
            shifts.end_time,
            shifts.status,
            COALESCE(COUNT(shift_operations.id), 0) AS operation_count
        FROM shifts
        LEFT JOIN shift_operations ON shift_operations.shift_id = shifts.id
        WHERE shifts.employee_id = ?
        GROUP BY
            shifts.id,
            shifts.shift_date,
            shifts.start_time,
            shifts.end_time,
            shifts.status
        ORDER BY shifts.shift_date DESC, shifts.start_time DESC, shifts.id DESC
        LIMIT ?
        """,
        (employee_id, limit)
    )

    shifts = cursor.fetchall()
    conn.close()
    return shifts


def delete_shift_by_id(shift_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            shifts.id,
            employees.full_name,
            shifts.shift_date,
            shifts.start_time,
            shifts.end_time,
            shifts.status
        FROM shifts
        JOIN employees ON employees.id = shifts.employee_id
        WHERE shifts.id = ?
        """,
        (shift_id,)
    )

    shift = cursor.fetchone()

    if shift is None:
        conn.close()
        return None

    cursor.execute("DELETE FROM shift_operations WHERE shift_id = ?", (shift_id,))
    cursor.execute("DELETE FROM shifts WHERE id = ?", (shift_id,))

    conn.commit()
    conn.close()
    return shift


def admin_close_shift(shift_id: int, end_time: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT shift_date, start_time
        FROM shifts
        WHERE id = ? AND status = 'open'
        """,
        (shift_id,)
    )

    row = cursor.fetchone()

    if row is None:
        conn.close()
        return None

    shift_date, start_time = row

    start_dt = datetime.strptime(f"{shift_date} {start_time}", "%Y-%m-%d %H:%M")
    end_dt = datetime.strptime(f"{shift_date} {end_time}", "%Y-%m-%d %H:%M")

    if end_dt < start_dt:
        conn.close()
        return "bad_time"

    now = local_now()
    closed_at = now.isoformat()
    edit_until = (now + timedelta(hours=1)).isoformat()
    total_minutes = int((end_dt - start_dt).total_seconds() // 60)

    cursor.execute(
        """
        UPDATE shifts
        SET end_time = ?,
            total_minutes = ?,
            status = 'closed',
            edit_until = ?,
            closed_at = ?
        WHERE id = ?
        """,
        (end_time, total_minutes, edit_until, closed_at, shift_id)
    )

    conn.commit()
    conn.close()

    return {
        "end_time": end_time,
        "total_minutes": total_minutes,
        "edit_until": edit_until,
    }


def get_today_shifts():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    today = local_today().isoformat()

    cursor.execute(
        """
        SELECT
            shifts.id,
            employees.full_name,
            shifts.shift_date,
            shifts.start_time,
            shifts.end_time,
            shifts.total_minutes,
            shifts.status
        FROM shifts
        JOIN employees ON employees.id = shifts.employee_id
        WHERE shifts.shift_date = ?
          AND employees.role != 'admin'
        ORDER BY shifts.start_time ASC
        """,
        (today,)
    )

    shifts = cursor.fetchall()
    conn.close()
    return shifts


def get_month_employee_summary():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    month_start = local_today().replace(day=1).isoformat()
    today = local_today().isoformat()

    cursor.execute(
        """
        SELECT
            employees.id,
            employees.full_name,
            COUNT(shifts.id) AS shift_count,
            COALESCE(SUM(shifts.total_minutes), 0) AS total_minutes
        FROM shifts
        JOIN employees ON employees.id = shifts.employee_id
        WHERE shifts.shift_date BETWEEN ? AND ?
          AND shifts.status = 'closed'
          AND employees.role != 'admin'
        GROUP BY employees.id, employees.full_name
        ORDER BY employees.full_name ASC
        """,
        (month_start, today)
    )

    rows = cursor.fetchall()
    conn.close()
    return rows


def get_period_employee_summary(start_date: str, end_date: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            employees.id,
            employees.full_name,
            COUNT(shifts.id) AS shift_count,
            COALESCE(SUM(shifts.total_minutes), 0) AS total_minutes
        FROM shifts
        JOIN employees ON employees.id = shifts.employee_id
        WHERE shifts.shift_date BETWEEN ? AND ?
          AND shifts.status = 'closed'
          AND employees.role != 'admin'
        GROUP BY employees.id, employees.full_name
        ORDER BY employees.full_name ASC
        """,
        (start_date, end_date)
    )

    rows = cursor.fetchall()
    conn.close()
    return rows


def get_employee_period_summary(employee_id: int, start_date: str, end_date: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            employees.id,
            employees.full_name,
            employees.position,
            COUNT(shifts.id) AS shift_count,
            COALESCE(SUM(shifts.total_minutes), 0) AS total_minutes
        FROM employees
        LEFT JOIN shifts ON shifts.employee_id = employees.id
            AND shifts.shift_date BETWEEN ? AND ?
            AND shifts.status = 'closed'
        WHERE employees.id = ?
          AND employees.role != 'admin'
        GROUP BY employees.id, employees.full_name, employees.position
        """,
        (start_date, end_date, employee_id)
    )

    row = cursor.fetchone()
    conn.close()
    return row


def get_employee_period_operation_totals(employee_id: int, start_date: str, end_date: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            CASE
                WHEN operations.folder IS NULL OR operations.folder = '' THEN operations.name
                ELSE operations.folder || ': ' || operations.name
            END AS operation_name,
            SUM(shift_operations.quantity) AS total_quantity,
            operations.unit
        FROM shift_operations
        JOIN shifts ON shifts.id = shift_operations.shift_id
        JOIN employees ON employees.id = shifts.employee_id
        JOIN operations ON operations.id = shift_operations.operation_id
        WHERE shifts.employee_id = ?
          AND employees.role != 'admin'
          AND shifts.shift_date BETWEEN ? AND ?
          AND shift_operations.quantity > 0
        GROUP BY
            operations.id,
            operations.folder,
            operations.name,
            operations.unit
        ORDER BY COALESCE(operations.sort_order, operations.number) ASC, operations.number ASC
        """,
        (employee_id, start_date, end_date)
    )

    rows = cursor.fetchall()
    conn.close()
    return rows


def get_month_operations_by_employee(employee_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    month_start = local_today().replace(day=1).isoformat()
    today = local_today().isoformat()

    cursor.execute(
        """
        SELECT
            CASE
                WHEN operations.folder IS NULL OR operations.folder = '' THEN operations.name
                ELSE operations.folder || ': ' || operations.name
            END AS operation_name,
            shift_operations.product_size,
            shift_operations.product_color,
            SUM(shift_operations.quantity) AS total_quantity,
            operations.unit
        FROM shift_operations
        JOIN shifts ON shifts.id = shift_operations.shift_id
        JOIN employees ON employees.id = shifts.employee_id
        JOIN operations ON operations.id = shift_operations.operation_id
        WHERE shifts.employee_id = ?
          AND employees.role != 'admin'
          AND shifts.shift_date BETWEEN ? AND ?
          AND shift_operations.quantity > 0
        GROUP BY
            operations.id,
            operations.folder,
            operations.name,
            shift_operations.product_size,
            shift_operations.product_color,
            operations.unit
        ORDER BY COALESCE(operations.sort_order, operations.number) ASC, operations.number ASC
        """,
        (employee_id, month_start, today)
    )

    rows = cursor.fetchall()
    conn.close()
    return rows


def get_period_operations_by_employee(employee_id: int, start_date: str, end_date: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            CASE
                WHEN operations.folder IS NULL OR operations.folder = '' THEN operations.name
                ELSE operations.folder || ': ' || operations.name
            END AS operation_name,
            shift_operations.product_size,
            shift_operations.product_color,
            SUM(shift_operations.quantity) AS total_quantity,
            operations.unit
        FROM shift_operations
        JOIN shifts ON shifts.id = shift_operations.shift_id
        JOIN employees ON employees.id = shifts.employee_id
        JOIN operations ON operations.id = shift_operations.operation_id
        WHERE shifts.employee_id = ?
          AND employees.role != 'admin'
          AND shifts.shift_date BETWEEN ? AND ?
          AND shift_operations.quantity > 0
        GROUP BY
            operations.id,
            operations.folder,
            operations.name,
            shift_operations.product_size,
            shift_operations.product_color,
            operations.unit
        ORDER BY COALESCE(operations.sort_order, operations.number) ASC, operations.number ASC
        """,
        (employee_id, start_date, end_date)
    )

    rows = cursor.fetchall()
    conn.close()
    return rows


def get_month_operation_rows():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    month_start = local_today().replace(day=1).isoformat()
    today = local_today().isoformat()

    cursor.execute(
        """
        SELECT
            shifts.shift_date,
            employees.full_name,
            CASE operations.position
                WHEN 'Швея' THEN 'Пошив'
                WHEN 'Упаковщик' THEN 'Упаковка'
                WHEN 'Раскройщик' THEN 'Раскрой'
                ELSE COALESCE(operations.position, '')
            END AS work_group,
            CASE
                WHEN operations.folder IS NULL OR operations.folder = '' THEN operations.name
                ELSE operations.folder || ': ' || operations.name
            END AS operation_name,
            shift_operations.product_size,
            shift_operations.product_color,
            SUM(shift_operations.quantity) AS total_quantity,
            operations.unit
        FROM shift_operations
        JOIN shifts ON shifts.id = shift_operations.shift_id
        JOIN employees ON employees.id = shifts.employee_id
        JOIN operations ON operations.id = shift_operations.operation_id
        WHERE shifts.shift_date BETWEEN ? AND ?
          AND shift_operations.quantity > 0
          AND employees.role != 'admin'
        GROUP BY
            shifts.shift_date,
            employees.id,
            employees.full_name,
            operations.position,
            operations.id,
            operations.folder,
            operations.name,
            shift_operations.product_size,
            shift_operations.product_color,
            operations.unit
        ORDER BY shifts.shift_date ASC, employees.full_name ASC, operations.number ASC
        """,
        (month_start, today)
    )

    rows = cursor.fetchall()
    conn.close()
    return rows


def get_period_operation_rows(start_date: str, end_date: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            shifts.shift_date,
            employees.full_name,
            CASE operations.position
                WHEN 'Швея' THEN 'Пошив'
                WHEN 'Упаковщик' THEN 'Упаковка'
                WHEN 'Раскройщик' THEN 'Раскрой'
                ELSE COALESCE(operations.position, '')
            END AS work_group,
            CASE
                WHEN operations.folder IS NULL OR operations.folder = '' THEN operations.name
                ELSE operations.folder || ': ' || operations.name
            END AS operation_name,
            shift_operations.product_size,
            shift_operations.product_color,
            SUM(shift_operations.quantity) AS total_quantity,
            operations.unit
        FROM shift_operations
        JOIN shifts ON shifts.id = shift_operations.shift_id
        JOIN employees ON employees.id = shifts.employee_id
        JOIN operations ON operations.id = shift_operations.operation_id
        WHERE shifts.shift_date BETWEEN ? AND ?
          AND shift_operations.quantity > 0
          AND employees.role != 'admin'
        GROUP BY
            shifts.shift_date,
            employees.id,
            employees.full_name,
            operations.position,
            operations.id,
            operations.folder,
            operations.name,
            shift_operations.product_size,
            shift_operations.product_color,
            operations.unit
        ORDER BY shifts.shift_date ASC, employees.full_name ASC, operations.number ASC
        """,
        (start_date, end_date)
    )

    rows = cursor.fetchall()
    conn.close()
    return rows


def get_month_shift_details():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    month_start = local_today().replace(day=1).isoformat()
    today = local_today().isoformat()

    cursor.execute(
        """
        SELECT
            shifts.shift_date,
            employees.full_name,
            shifts.start_time,
            shifts.end_time,
            shifts.total_minutes,
            shifts.status
        FROM shifts
        JOIN employees ON employees.id = shifts.employee_id
        WHERE shifts.shift_date BETWEEN ? AND ?
          AND employees.role != 'admin'
        ORDER BY shifts.shift_date ASC, employees.full_name ASC
        """,
        (month_start, today)
    )

    rows = cursor.fetchall()
    conn.close()
    return rows


def get_period_shift_details(start_date: str, end_date: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            shifts.shift_date,
            employees.full_name,
            shifts.start_time,
            shifts.end_time,
            shifts.total_minutes,
            shifts.status
        FROM shifts
        JOIN employees ON employees.id = shifts.employee_id
        WHERE shifts.shift_date BETWEEN ? AND ?
          AND employees.role != 'admin'
        ORDER BY shifts.shift_date ASC, employees.full_name ASC
        """,
        (start_date, end_date)
    )

    rows = cursor.fetchall()
    conn.close()
    return rows


def add_edit_log(changed_by: int, role: str, action: str, entity_type: str, entity_id: int | None, details: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO edit_logs (
            changed_by, role, action, entity_type, entity_id, details, changed_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            changed_by,
            role,
            action,
            entity_type,
            entity_id,
            details,
            local_now().isoformat(timespec="seconds"),
        )
    )

    conn.commit()
    conn.close()


def get_recent_edit_logs(limit: int = 20):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT changed_at, changed_by, role, action, entity_type, entity_id, details
        FROM edit_logs
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,)
    )

    rows = cursor.fetchall()
    conn.close()
    return rows
