import sqlite3
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo


DB_NAME = "bot.db"
LOCAL_TZ = ZoneInfo("Asia/Yekaterinburg")


def local_now():
    return datetime.now(LOCAL_TZ).replace(tzinfo=None)


def local_today():
    return local_now().date()


CUTTING_PRODUCTS = [
    "Брюки со стрелками детские",
    "Брюки со стрелками подростковые",
    "Брюки-клёш со стрелками для девочек",
    "Брюки-джоггеры",
    "Брюки-ползунки",
    "Легинсы",
    "Шорты",
    "Футболки",
    "Свитшоты",
    "Кардиган",
    "Кардиган детский и подростковый",
    "Бомбер",
    "Жакет для девочек",
    "Юбка-шорты",
]


CUTTING_OPERATIONS = [
    "Нанесение контуров лекал на ткань",
    "Формирование настила",
    "Раскрой",
    "Формирование готового кроя",
]


PACKING_PRODUCTS = CUTTING_PRODUCTS
PACKING_OPERATIONS = [
    "Упаковка",
]


PRODUCTION_OPERATIONS = [
    ("Упаковщик", "Подготовка", "Нарезка резинок"),
    ("Упаковщик", "Брюки со стрелками детские", "Заутюживание стрелок"),
    ("Упаковщик", "Брюки со стрелками детские", "ВТО стрелок"),
    ("Упаковщик", "Брюки со стрелками подростковые", "Заутюживание стрелок и проклейка флизелином входа в карман"),
    ("Упаковщик", "Брюки со стрелками подростковые", "ВТО стрелок"),
    ("Упаковщик", "Брюки-клёш со стрелками для девочек", "Заутюживание стрелок"),
    ("Упаковщик", "Брюки-клёш со стрелками для девочек", "ВТО стрелок"),
    ("Упаковщик", "Кардиган", "Проклеивание планок флизелином"),
    ("Упаковщик", "Кардиган", "ВТО и разметка"),
    ("Упаковщик", "Кардиган детский и подростковый", "Проклеивание планок флизелином"),
    ("Упаковщик", "Кардиган детский и подростковый", "ВТО и разметка"),
    ("Упаковщик", "Бомбер", "Проклеивание планок флизелином"),
    ("Упаковщик", "Бомбер", "ВТО и разметка"),
    ("Упаковщик", "Бомбер", "Установка кнопок"),
    ("Упаковщик", "Жакет для девочек", "Проклеивание планок флизелином"),
    ("Упаковщик", "Жакет для девочек", "Выворачивание и ВТО клапана"),
    ("Упаковщик", "Жакет для девочек", "ВТО и разметка под клапан, петли, пуговицы"),
    ("Швея", "Подготовка", "Сшивание резинок в кольцо"),
    ("Швея", "Брюки со стрелками детские", "Отстрочка стрелок"),
    ("Швея", "Брюки со стрелками детские", "Сборка брюк на оверлоке"),
    ("Швея", "Брюки со стрелками детские", "Притачивание резинки к поясу"),
    ("Швея", "Брюки со стрелками детские", "Отстрачивание пояса"),
    ("Швея", "Брюки со стрелками детские", "Формирование низа брюк"),
    ("Швея", "Брюки со стрелками подростковые", "Подготовка кармана на оверлоке"),
    ("Швея", "Брюки со стрелками подростковые", "Отстрочка стрелок"),
    ("Швея", "Брюки со стрелками подростковые", "Формирование кармана"),
    ("Швея", "Брюки со стрелками подростковые", "Сборка брюк на оверлоке"),
    ("Швея", "Брюки со стрелками подростковые", "Стачивание пояса в кольцо"),
    ("Швея", "Брюки со стрелками подростковые", "Пришивание пояса к брюкам"),
    ("Швея", "Брюки со стрелками подростковые", "Формирование низа брюк и закрепки на поясе"),
    ("Швея", "Брюки-клёш со стрелками для девочек", "Отстрочка стрелок"),
    ("Швея", "Брюки-клёш со стрелками для девочек", "Сборка брюк на оверлоке"),
    ("Швея", "Брюки-клёш со стрелками для девочек", "Притачивание резинки к поясу"),
    ("Швея", "Брюки-клёш со стрелками для девочек", "Отстрачивание пояса"),
    ("Швея", "Брюки-клёш со стрелками для девочек", "Подшивание низа брюк"),
    ("Швея", "Брюки-джоггеры", "Сборка брюк на оверлоке с притачиванием резинок на манжеты"),
    ("Швея", "Брюки-джоггеры", "Притачивание резинки к поясу"),
    ("Швея", "Брюки-джоггеры", "Отстрачивание пояса и манжет"),
    ("Швея", "Брюки-ползунки", "Сборка брюк на оверлоке с притачиванием манжет"),
    ("Швея", "Брюки-ползунки", "Притачивание резинки к поясу"),
    ("Швея", "Брюки-ползунки", "Отстрачивание пояса"),
    ("Швея", "Легинсы", "Сборка на оверлоке"),
    ("Швея", "Легинсы", "Притачивание резинки к поясу"),
    ("Швея", "Легинсы", "Отстрачивание пояса"),
    ("Швея", "Легинсы", "Подшивание низа"),
    ("Швея", "Шорты", "Сборка шорт на оверлоке"),
    ("Швея", "Шорты", "Притачивание резинки к поясу"),
    ("Швея", "Шорты", "Отстрачивание пояса"),
    ("Швея", "Шорты", "Подшивание низа"),
    ("Швея", "Футболки", "Стачивание горловин в кольцо"),
    ("Швея", "Футболки", "Сборка футболки на оверлоке"),
    ("Швея", "Футболки", "Притачивание горловин к футболке"),
    ("Швея", "Футболки", "Подшивание рукавов и низа футболки"),
    ("Швея", "Свитшоты", "Стачивание горловин, манжет и поясов в кольцо"),
    ("Швея", "Свитшоты", "Сборка свитшота на оверлоке с притачиванием пояса и манжет"),
    ("Швея", "Свитшоты", "Притачивание горловин к свитшоту"),
    ("Швея", "Кардиган", "Сборка кардигана с манжетами и поясом"),
    ("Швея", "Кардиган", "Сборка и притачивание воротника"),
    ("Швея", "Кардиган", "Выметывание петель"),
    ("Швея", "Кардиган", "Пришивание пуговиц"),
    ("Швея", "Кардиган детский и подростковый", "Сборка кардигана с манжетами и поясом"),
    ("Швея", "Кардиган детский и подростковый", "Сборка и притачивание воротника"),
    ("Швея", "Кардиган детский и подростковый", "Выметывание петель"),
    ("Швея", "Кардиган детский и подростковый", "Пришивание пуговиц"),
    ("Швея", "Бомбер", "Стачивание манжет в кольцо и подготовка пояса"),
    ("Швея", "Бомбер", "Сборка бомбера с манжетами, поясом и воротником"),
    ("Швея", "Жакет для девочек", "Сборка жакета с обтачками"),
    ("Швея", "Жакет для девочек", "Подшивание рукавов"),
    ("Швея", "Жакет для девочек", "Формирование клапана"),
    ("Швея", "Жакет для девочек", "Подшивание жакета и настрачивание клапанов, закрепки обтачки"),
    ("Швея", "Жакет для девочек", "Выметывание петель"),
    ("Швея", "Жакет для девочек", "Пришивание пуговиц"),
    ("Швея", "Юбка-шорты", "Сборка шорт на оверлоке"),
    ("Швея", "Юбка-шорты", "Сборка юбки на оверлоке"),
    ("Швея", "Юбка-шорты", "Подшивание шорт"),
    ("Швея", "Юбка-шорты", "Подшивание юбки"),
    ("Швея", "Юбка-шорты", "Притачивание резинки к поясу"),
    ("Швея", "Юбка-шорты", "Отстрачивание пояса"),
]


STARTER_OPERATION_NAMES = [
    "Пошив резинки",
    "Обработка горловины",
    "Стачивание бокового шва",
    "Упаковка",
    "ВТО",
    "Раскрой",
]


PRODUCT_OPTIONS = {
    "Раскрой": {
        "colors": ["бежевый", "голубой", "капучино", "кофейный", "светло-серый", "темно - синий", "черный", "Коричневый", "серый", "темно зеленый", "Карамель", "брауни", "Розовый", "Желтый", "синий", "темно - зеленый", "темно синий", "светло - сервый"],
        "sizes": ["86", "92", "98", "104", "110", "116", "122", "128", "134", "140", "146", "152", "158", "164"],
    },
    "Подготовка": {"colors": [], "sizes": []},
    "Брюки со стрелками детские": {
        "colors": ["бежевый", "голубой", "капучино", "кофейный", "светло-серый", "темно - синий", "черный"],
        "sizes": ["86", "92", "98", "104", "110", "116", "122", "128"],
    },
    "Брюки со стрелками подростковые": {
        "colors": ["светло-серый", "бежевый", "капучино", "черный", "темно - синий", "Коричневый", "Голубой", "серый"],
        "sizes": ["134", "140", "146", "152", "158", "164"],
    },
    "Брюки-клёш со стрелками для девочек": {
        "colors": ["темно - синий", "черный"],
        "sizes": ["98", "104", "110", "116", "122", "128"],
    },
    "Брюки-джоггеры": {
        "colors": ["темно - синий", "капучино", "темно зеленый", "Карамель"],
        "sizes": ["86", "92", "98", "104"],
    },
    "Брюки-ползунки": {
        "colors": ["серый", "брауни"],
        "sizes": ["110", "116", "122"],
    },
    "Легинсы": {
        "colors": ["Розовый", "Голубой", "Желтый", "Бежевый", "Карамель", "Капучино"],
        "sizes": ["86", "92", "98", "104", "110", "116"],
    },
    "Шорты": {"colors": [], "sizes": []},
    "Футболки": {
        "colors": ["Розовый", "Голубой", "Желтый", "Бежевый", "Карамель", "Капучино", "синий", "серый", "брауни"],
        "sizes": ["86", "92", "98", "104", "110", "116"],
    },
    "Свитшоты": {
        "colors": ["Карамель", "Капучино", "синий", "серый", "брауни", "темно - зеленый"],
        "sizes": ["86", "92", "98", "104", "110", "116", "122"],
    },
    "Кардиган": {
        "colors": ["голубой", "бежевый", "капучино", "темно синий", "брауни", "светло - сервый", "черный"],
        "sizes": ["92", "98", "104", "110", "116", "122"],
    },
    "Кардиган детский и подростковый": {
        "colors": ["голубой", "бежевый", "капучино", "темно синий", "брауни", "светло - сервый", "черный"],
        "sizes": ["134", "140", "146", "152", "158", "164"],
    },
    "Бомбер": {
        "colors": ["голубой", "бежевый", "светло - сервый", "темно синий", "черный"],
        "sizes": ["92", "98", "104", "110", "116", "122", "128"],
    },
    "Жакет для девочек": {
        "colors": ["темно синий", "черный"],
        "sizes": ["92", "98", "104", "110", "116", "122", "128", "134", "140", "146", "152", "158", "164"],
    },
    "Юбка-шорты": {
        "colors": ["темно синий", "черный"],
        "sizes": ["92", "98", "104", "110", "116", "122", "128", "134", "140", "146", "152", "158", "164"],
    },
}


def get_product_sizes(folder: str):
    return PRODUCT_OPTIONS.get(folder, {}).get("sizes", [])


def get_product_colors(folder: str):
    return PRODUCT_OPTIONS.get(folder, {}).get("colors", [])


def get_operation_group(position: str, folder: str, name: str | None = None):
    if position == "Раскройщик":
        return "Раскрой изделий"

    if position == "Упаковщик":
        if folder == "Подготовка":
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
        if item[0] == "Упаковщик" and item[1] == "Подготовка"
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
