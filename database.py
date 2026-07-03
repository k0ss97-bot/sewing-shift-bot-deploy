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


def get_database_status():
    status = {
        "path": DB_NAME,
        "exists": os.path.exists(DB_NAME),
        "size": os.path.getsize(DB_NAME) if os.path.exists(DB_NAME) else 0,
        "employees": None,
        "shifts": None,
        "shift_operations": None,
        "operations": None,
    }

    if not status["exists"]:
        return status

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        for table in ["employees", "shifts", "shift_operations", "operations"]:
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
        CREATE TABLE IF NOT EXISTS cutting_batches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
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


def get_cutting_batches_for_layout(product_name: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            cutting_batches.id,
            cutting_batches.product_name,
            cutting_batches.contour_date,
            employees.full_name,
            GROUP_CONCAT(cutting_batch_sizes.product_size || ' - ' || cutting_batch_sizes.quantity, ', ') AS sizes_text
        FROM cutting_batches
        LEFT JOIN employees ON employees.id = cutting_batches.contour_employee_id
        LEFT JOIN cutting_batch_sizes ON cutting_batch_sizes.batch_id = cutting_batches.id
        WHERE cutting_batches.product_name = ?
          AND cutting_batches.status = 'contours_done'
        GROUP BY cutting_batches.id, cutting_batches.product_name, cutting_batches.contour_date, employees.full_name
        ORDER BY cutting_batches.contour_date ASC, cutting_batches.id ASC
        """,
        (product_name,)
    )

    rows = cursor.fetchall()
    conn.close()
    return rows


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
        ORDER BY
            CAST(cutting_batch_sizes.product_size AS INTEGER),
            cutting_batch_colors.product_color
        """,
        (batch_id, batch_id)
    )

    rows = cursor.fetchall()
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
    cursor.execute("DELETE FROM cutting_batches WHERE id = ?", (batch_id,))

    conn.commit()
    conn.close()
    return batch


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
        JOIN operations ON operations.id = shift_operations.operation_id
        WHERE shifts.employee_id = ?
          AND shifts.shift_date BETWEEN ? AND ?
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
        JOIN operations ON operations.id = shift_operations.operation_id
        WHERE shifts.employee_id = ?
          AND shifts.shift_date BETWEEN ? AND ?
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
        JOIN operations ON operations.id = shift_operations.operation_id
        WHERE shifts.employee_id = ?
          AND shifts.shift_date BETWEEN ? AND ?
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
