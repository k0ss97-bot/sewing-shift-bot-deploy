import hashlib
import json
import os
import shutil
import sqlite3
import uuid
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

    db_paths = [
        os.path.join(db_dir, DB_FILE_NAME)
        for db_dir in DB_DIR_CANDIDATES
        if db_dir and os.path.isdir(db_dir)
    ]

    configured_dir = os.getenv("DB_DIR", "").strip()
    if configured_dir:
        configured_path = os.path.join(configured_dir, DB_FILE_NAME)
        if has_business_data(configured_path):
            return configured_path
        if has_business_data(DB_FILE_NAME):
            os.makedirs(configured_dir, exist_ok=True)
            shutil.copy2(DB_FILE_NAME, configured_path)
        return configured_path

    for db_path in db_paths:
        if has_business_data(db_path):
            return db_path

    if has_business_data(DB_FILE_NAME):
        return DB_FILE_NAME

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
    "priority",
    "due_date",
    "parent_batch_id",
    "source_cutting_batch_id",
    "trace_code",
    "route_version",
    "route_snapshot",
    "work_state",
    "blocked_reason",
    "paused_at",
    "last_activity_at",
    "handover_count",
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
    "priority",
    "due_date",
    "assigned_employee_id",
    "assigned_at",
    "trace_code",
    "route_version",
    "route_snapshot",
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


def current_route_snapshot(product_name: str):
    from route_maps import PRODUCT_ROUTE_MAPS

    steps = PRODUCT_ROUTE_MAPS.get(product_name, [])
    return json.dumps(steps, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def route_version_for_snapshot(snapshot: str):
    return hashlib.sha256((snapshot or "[]").encode("utf-8")).hexdigest()[:12]


def route_steps_from_snapshot(snapshot: str, product_name: str = ""):
    try:
        steps = json.loads(snapshot or "[]")
    except (TypeError, ValueError, json.JSONDecodeError):
        steps = []

    if isinstance(steps, list) and steps:
        return steps

    if product_name:
        from route_maps import PRODUCT_ROUTE_MAPS

        return PRODUCT_ROUTE_MAPS.get(product_name, [])

    return []


def _trace_code(prefix: str, entity_id: int):
    return f"{prefix}-{int(entity_id):06d}"


def _record_production_event(
    cursor,
    event_type: str,
    *,
    batch_id: int | None = None,
    cutting_batch_id: int | None = None,
    production_task_id: int | None = None,
    actor_employee_id: int | None = None,
    shift_id: int | None = None,
    operation_name: str = "",
    position: str = "",
    quantity: int = 0,
    good_quantity: int = 0,
    defect_quantity: int = 0,
    reason: str = "",
    details: dict | None = None,
    request_key: str | None = None,
    created_at: str | None = None,
):
    cursor.execute(
        """
        INSERT OR IGNORE INTO production_trace_events (
            batch_id, cutting_batch_id, production_task_id, event_type,
            actor_employee_id, shift_id, operation_name, position,
            quantity, good_quantity, defect_quantity, reason, details_json,
            request_key, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            batch_id,
            cutting_batch_id,
            production_task_id,
            event_type,
            actor_employee_id,
            shift_id,
            operation_name.strip(),
            position.strip(),
            int(quantity or 0),
            int(good_quantity or 0),
            int(defect_quantity or 0),
            reason.strip(),
            json.dumps(details or {}, ensure_ascii=False, sort_keys=True),
            request_key,
            created_at or local_now().isoformat(),
        ),
    )
    return cursor.lastrowid if cursor.rowcount else None


def has_route_completion_request(batch_id: int, employee_id: int, request_id: str):
    request_id = str(request_id or "").strip()
    if not request_id:
        return False
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT 1
        FROM production_trace_events
        WHERE batch_id = ?
          AND actor_employee_id = ?
          AND request_key = ?
          AND event_type = 'operation_completed'
        """,
        (batch_id, employee_id, f"route-complete:{request_id}"),
    )
    exists = cursor.fetchone() is not None
    conn.close()
    return exists


def _create_fabric_lot(
    cursor,
    stock_id: int,
    quantity: int,
    employee_id: int | None,
    now_text: str,
    source_type: str = "receipt",
    source_id: int | None = None,
):
    if quantity <= 0:
        return None

    cursor.execute(
        """
        INSERT INTO fabric_stock_lots (
            stock_id, lot_code, source_type, source_id,
            rolls_received, rolls_available, created_by_employee_id,
            created_at, updated_at
        )
        VALUES (?, '', ?, ?, ?, ?, ?, ?, ?)
        """,
        (stock_id, source_type, source_id, quantity, quantity, employee_id, now_text, now_text),
    )
    lot_id = cursor.lastrowid
    cursor.execute(
        "UPDATE fabric_stock_lots SET lot_code = ? WHERE id = ?",
        (_trace_code("FAB", lot_id), lot_id),
    )
    return lot_id


def _allocate_fabric_lots(cursor, task_id: int, stock_id: int, rolls: int, now_text: str):
    remaining = int(rolls)
    cursor.execute(
        """
        SELECT id, rolls_available
        FROM fabric_stock_lots
        WHERE stock_id = ? AND rolls_available > 0
        ORDER BY created_at ASC, id ASC
        """,
        (stock_id,),
    )

    for lot_id, available in cursor.fetchall():
        if remaining <= 0:
            break
        allocated = min(remaining, int(available or 0))
        cursor.execute(
            """
            UPDATE fabric_stock_lots
            SET rolls_available = rolls_available - ?, updated_at = ?
            WHERE id = ? AND rolls_available >= ?
            """,
            (allocated, now_text, lot_id, allocated),
        )
        if cursor.rowcount != 1:
            raise ValueError("fabric lot changed")
        cursor.execute(
            """
            INSERT INTO production_task_fabric_lots (task_id, lot_id, rolls, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (task_id, lot_id, allocated, now_text),
        )
        remaining -= allocated

    if remaining:
        raise ValueError("fabric lots unavailable")


def _consume_fabric_lots(cursor, stock_id: int, quantity: int, now_text: str):
    remaining = int(quantity)
    cursor.execute(
        """
        SELECT id, rolls_available
        FROM fabric_stock_lots
        WHERE stock_id = ? AND rolls_available > 0
        ORDER BY created_at ASC, id ASC
        """,
        (stock_id,),
    )

    for lot_id, available in cursor.fetchall():
        if remaining <= 0:
            break
        consumed = min(remaining, int(available or 0))
        cursor.execute(
            """
            UPDATE fabric_stock_lots
            SET rolls_available = rolls_available - ?, updated_at = ?
            WHERE id = ? AND rolls_available >= ?
            """,
            (consumed, now_text, lot_id, consumed),
        )
        if cursor.rowcount != 1:
            raise ValueError("fabric lot changed")
        remaining -= consumed

    if remaining:
        raise ValueError("fabric lots unavailable")


def _create_warehouse_lot(
    cursor,
    stock_id: int,
    quantity: int,
    now_text: str,
    source_type: str = "",
    source_id: int | None = None,
):
    if quantity <= 0:
        return None

    cursor.execute(
        """
        INSERT INTO warehouse_stock_lots (
            stock_id, lot_code, source_type, source_id,
            quantity_received, quantity_available, created_at, updated_at
        )
        VALUES (?, '', ?, ?, ?, ?, ?, ?)
        """,
        (stock_id, source_type, source_id, quantity, quantity, now_text, now_text),
    )
    lot_id = cursor.lastrowid
    cursor.execute(
        "UPDATE warehouse_stock_lots SET lot_code = ? WHERE id = ?",
        (_trace_code("LOT", lot_id), lot_id),
    )
    return lot_id


def _allocate_warehouse_lots(
    cursor,
    batch_id: int,
    stock_id: int,
    input_role: str,
    quantity: int,
    now_text: str,
):
    remaining = int(quantity)
    cursor.execute(
        """
        SELECT id, quantity_available
        FROM warehouse_stock_lots
        WHERE stock_id = ? AND quantity_available > 0
        ORDER BY created_at ASC, id ASC
        """,
        (stock_id,),
    )

    for lot_id, available in cursor.fetchall():
        if remaining <= 0:
            break
        allocated = min(remaining, int(available or 0))
        cursor.execute(
            """
            UPDATE warehouse_stock_lots
            SET quantity_available = quantity_available - ?, updated_at = ?
            WHERE id = ? AND quantity_available >= ?
            """,
            (allocated, now_text, lot_id, allocated),
        )
        if cursor.rowcount != 1:
            raise ValueError("warehouse lot changed")
        cursor.execute(
            """
            INSERT INTO route_batch_input_lots (batch_id, lot_id, input_role, quantity, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (batch_id, lot_id, input_role, allocated, now_text),
        )
        remaining -= allocated

    if remaining:
        raise ValueError("warehouse lots unavailable")


def _consume_warehouse_lots(cursor, stock_id: int, quantity: int, now_text: str):
    remaining = int(quantity)
    cursor.execute(
        """
        SELECT id, quantity_available
        FROM warehouse_stock_lots
        WHERE stock_id = ? AND quantity_available > 0
        ORDER BY created_at ASC, id ASC
        """,
        (stock_id,),
    )
    for lot_id, available in cursor.fetchall():
        if remaining <= 0:
            break
        consumed = min(remaining, int(available or 0))
        cursor.execute(
            """
            UPDATE warehouse_stock_lots
            SET quantity_available = quantity_available - ?, updated_at = ?
            WHERE id = ? AND quantity_available >= ?
            """,
            (consumed, now_text, lot_id, consumed),
        )
        if cursor.rowcount != 1:
            raise ValueError("warehouse lot changed")
        remaining -= consumed

    if remaining:
        raise ValueError("warehouse lots unavailable")


def _initialize_route_batch_trace(
    cursor,
    batch_id: int,
    product_name: str,
    employee_id: int | None,
    now_text: str,
    *,
    source: str = "manual",
    route_snapshot: str = "",
    route_version: str = "",
):
    snapshot = route_snapshot or current_route_snapshot(product_name)
    version = route_version or route_version_for_snapshot(snapshot)
    trace_code = _trace_code("RB", batch_id)
    cursor.execute(
        """
        UPDATE route_batches
        SET trace_code = ?, route_version = ?, route_snapshot = ?,
            work_state = CASE WHEN status = 'done' THEN 'done' ELSE 'free' END,
            last_activity_at = ?
        WHERE id = ?
        """,
        (trace_code, version, snapshot, now_text, batch_id),
    )
    _record_production_event(
        cursor,
        "batch_created",
        batch_id=batch_id,
        actor_employee_id=employee_id,
        details={"source": source, "trace_code": trace_code, "route_version": version},
        request_key=f"route-batch:{batch_id}:created",
        created_at=now_text,
    )
    return trace_code


def _initialize_production_task_trace(
    cursor,
    task_id: int,
    product_name: str,
    employee_id: int | None,
    now_text: str,
):
    snapshot = current_route_snapshot(product_name)
    version = route_version_for_snapshot(snapshot)
    trace_code = _trace_code("CUT", task_id)
    cursor.execute(
        """
        UPDATE production_tasks
        SET trace_code = ?, route_version = ?, route_snapshot = ?
        WHERE id = ?
        """,
        (trace_code, version, snapshot, task_id),
    )
    _record_production_event(
        cursor,
        "task_created",
        production_task_id=task_id,
        actor_employee_id=employee_id,
        details={"trace_code": trace_code, "route_version": version},
        request_key=f"production-task:{task_id}:created",
        created_at=now_text,
    )
    return trace_code


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
    if folder in SIMPLE_PREPARATION_OPERATIONS:
        return True

    return any(
        options.get("folder") == folder
        for options in PREPARATION_OPERATION_OPTIONS.values()
    )


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
        unit = "%" if position == "Раскройщик" and name == "Раскрой" else "шт"

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
                SET unit = ?,
                    is_active = 1,
                    operation_group = ?,
                    sort_order = ?
                WHERE id = ?
                """,
                (unit, operation_group, sort_order, existing_operation[0]),
            )
            continue

        cursor.execute("SELECT COALESCE(MAX(number), 0) + 1 FROM operations")
        next_number = cursor.fetchone()[0]

        cursor.execute(
            """
            INSERT INTO operations (number, name, position, operation_group, folder, sort_order, unit, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1)
            """,
            (next_number, name, position, operation_group, folder, sort_order, unit),
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


def backfill_cutting_progress_reports(cursor):
    cursor.execute(
        """
        DELETE FROM shift_operations
        WHERE product_size = 'готовность'
          AND product_color = 'без цвета'
          AND EXISTS (
              SELECT 1
              FROM cutting_batches
              WHERE cutting_batches.cutting_shift_id = shift_operations.shift_id
                AND cutting_batches.cutting_operation_id = shift_operations.operation_id
          )
        """
    )
    cursor.execute(
        """
        INSERT INTO shift_operations (
            shift_id, employee_id, operation_id,
            product_size, product_color, quantity, created_at, updated_at
        )
        SELECT
            cutting_shift_id,
            cutting_employee_id,
            cutting_operation_id,
            'партия #' || id,
            'без цвета',
            cutting_progress,
            updated_at,
            updated_at
        FROM cutting_batches
        WHERE cutting_progress > 0
          AND cutting_shift_id IS NOT NULL
          AND cutting_employee_id IS NOT NULL
          AND cutting_operation_id IS NOT NULL
        ON CONFLICT(shift_id, operation_id, product_size, product_color)
        DO UPDATE SET
            employee_id = excluded.employee_id,
            quantity = excluded.quantity,
            updated_at = excluded.updated_at
        WHERE shift_operations.updated_at < excluded.updated_at
           OR shift_operations.quantity < excluded.quantity
        """
    )


def restore_incomplete_cutting_shift(
    cursor,
    repair_key: str,
    batch_id: int,
    shift_id: int,
    expected_shift_date: str,
):
    cursor.execute(
        "SELECT 1 FROM data_repairs WHERE repair_key = ?",
        (repair_key,),
    )

    if cursor.fetchone() is not None:
        return False

    cursor.execute(
        """
        SELECT cutting_batches.id
        FROM cutting_batches
        JOIN shifts ON shifts.id = ?
        WHERE cutting_batches.id = ?
          AND cutting_batches.layout_shift_id = shifts.id
          AND cutting_batches.layout_employee_id = shifts.employee_id
          AND cutting_batches.layout_date IS NOT NULL
          AND cutting_batches.cutting_progress < 100
          AND cutting_batches.status IN ('layout_done', 'cutting_in_progress')
          AND shifts.shift_date = ?
          AND shifts.status IN ('open', 'closed')
        """,
        (shift_id, batch_id, expected_shift_date),
    )

    if cursor.fetchone() is None:
        return False

    now_text = local_now().isoformat()
    cursor.execute(
        """
        UPDATE shifts
        SET end_time = NULL,
            total_minutes = NULL,
            status = 'open',
            edit_until = NULL,
            closed_at = NULL
        WHERE id = ?
        """,
        (shift_id,),
    )
    cursor.execute(
        """
        UPDATE cutting_batches
        SET status = CASE
                WHEN cutting_progress > 0 THEN 'cutting_in_progress'
                ELSE 'layout_done'
            END,
            formed_shift_id = NULL,
            formed_operation_id = NULL,
            formed_employee_id = NULL,
            formed_date = NULL,
            updated_at = ?
        WHERE id = ?
        """,
        (now_text, batch_id),
    )
    cursor.execute(
        """
        INSERT INTO data_repairs (repair_key, applied_at)
        VALUES (?, ?)
        """,
        (repair_key, now_text),
    )
    return True


def repair_legacy_uniqueness_conflicts(cursor):
    now = local_now()
    now_text = now.isoformat()

    cursor.execute(
        """
        SELECT employee_id
        FROM shifts
        WHERE status = 'open'
        GROUP BY employee_id
        HAVING COUNT(*) > 1
        """
    )
    duplicate_employee_ids = [row[0] for row in cursor.fetchall()]

    for employee_id in duplicate_employee_ids:
        cursor.execute(
            """
            SELECT id, shift_date, start_time, end_time, total_minutes
            FROM shifts
            WHERE employee_id = ? AND status = 'open'
            ORDER BY shift_date DESC, start_time DESC, id DESC
            """,
            (employee_id,),
        )
        shifts = cursor.fetchall()

        for shift_id, shift_date, start_time, end_time, total_minutes in shifts[1:]:
            repaired_end_time = end_time or start_time
            repaired_total_minutes = int(total_minutes or 0)
            cursor.execute(
                "SELECT MAX(updated_at) FROM shift_operations WHERE shift_id = ?",
                (shift_id,),
            )
            operation_timestamp = cursor.fetchone()[0]

            if operation_timestamp:
                try:
                    start_dt = datetime.strptime(f"{shift_date} {start_time}", "%Y-%m-%d %H:%M")
                    operation_dt = datetime.fromisoformat(operation_timestamp).replace(tzinfo=None)
                    elapsed = operation_dt - start_dt
                    if timedelta(0) <= elapsed <= timedelta(hours=24):
                        repaired_end_time = operation_dt.strftime("%H:%M")
                        repaired_total_minutes = int(elapsed.total_seconds() // 60)
                except (TypeError, ValueError):
                    pass

            cursor.execute(
                """
                UPDATE shifts
                SET end_time = ?,
                    total_minutes = ?,
                    status = 'closed',
                    edit_until = NULL,
                    closed_at = COALESCE(closed_at, ?)
                WHERE id = ? AND status = 'open'
                """,
                (repaired_end_time, repaired_total_minutes, now_text, shift_id),
            )
            cursor.execute(
                "INSERT OR IGNORE INTO data_repairs (repair_key, applied_at) VALUES (?, ?)",
                (f"deduplicate-open-shift-{shift_id}", now_text),
            )

    cursor.execute(
        """
        SELECT production_task_id
        FROM cutting_batches
        WHERE production_task_id IS NOT NULL AND status != 'cancelled'
        GROUP BY production_task_id
        HAVING COUNT(*) > 1
        """
    )
    duplicate_task_ids = [row[0] for row in cursor.fetchall()]
    status_priority = {
        "contours_done": 1,
        "layout_done": 2,
        "cutting_in_progress": 3,
        "cutting_done": 4,
        "formed": 5,
    }

    for task_id in duplicate_task_ids:
        cursor.execute(
            """
            SELECT id, status, updated_at
            FROM cutting_batches
            WHERE production_task_id = ? AND status != 'cancelled'
            """,
            (task_id,),
        )
        batches = cursor.fetchall()
        canonical = max(
            batches,
            key=lambda row: (status_priority.get(row[1], 0), row[2] or "", row[0]),
        )

        for batch_id, _status, _updated_at in batches:
            if batch_id == canonical[0]:
                continue
            cursor.execute(
                "UPDATE cutting_batches SET status = 'cancelled', updated_at = ? WHERE id = ?",
                (now_text, batch_id),
            )
            cursor.execute(
                """
                UPDATE route_batches
                SET status = 'cancelled', updated_at = ?, completed_at = COALESCE(completed_at, ?)
                WHERE source_cutting_batch_id = ? AND status = 'active'
                """,
                (now_text, now_text, batch_id),
            )
            cursor.execute(
                "INSERT OR IGNORE INTO data_repairs (repair_key, applied_at) VALUES (?, ?)",
                (f"deduplicate-cutting-batch-{batch_id}", now_text),
            )

    cursor.execute(
        """
        SELECT id
        FROM route_batch_history
        WHERE id NOT IN (
            SELECT MAX(id)
            FROM route_batch_history
            GROUP BY batch_id, step_index
        )
        """
    )
    duplicate_history_ids = [row[0] for row in cursor.fetchall()]

    for history_id in duplicate_history_ids:
        cursor.execute("DELETE FROM route_batch_history WHERE id = ?", (history_id,))
        cursor.execute(
            "INSERT OR IGNORE INTO data_repairs (repair_key, applied_at) VALUES (?, ?)",
            (f"deduplicate-route-history-{history_id}", now_text),
        )


def backfill_traceability(cursor):
    now_text = local_now().isoformat()

    cursor.execute("SELECT id, product_name, created_at FROM production_tasks")
    for task_id, product_name, created_at in cursor.fetchall():
        snapshot = current_route_snapshot(product_name)
        version = route_version_for_snapshot(snapshot)
        cursor.execute(
            """
            UPDATE production_tasks
            SET trace_code = COALESCE(NULLIF(trace_code, ''), ?),
                route_version = COALESCE(NULLIF(route_version, ''), ?),
                route_snapshot = COALESCE(NULLIF(route_snapshot, ''), ?)
            WHERE id = ?
            """,
            (_trace_code("CUT", task_id), version, snapshot, task_id),
        )
        _record_production_event(
            cursor,
            "task_created",
            production_task_id=task_id,
            details={"legacy_backfill": True, "product_name": product_name},
            request_key=f"production-task:{task_id}:created",
            created_at=created_at or now_text,
        )

    cursor.execute(
        """
        SELECT id, product_name, status, assigned_employee_id, created_at, updated_at
        FROM route_batches
        """
    )
    for batch_id, product_name, status, assigned_employee_id, created_at, updated_at in cursor.fetchall():
        snapshot = current_route_snapshot(product_name)
        version = route_version_for_snapshot(snapshot)
        work_state = "done" if status == "done" else "cancelled" if status == "cancelled" else "in_work" if assigned_employee_id else "free"
        cursor.execute(
            """
            UPDATE route_batches
            SET trace_code = COALESCE(NULLIF(trace_code, ''), ?),
                route_version = COALESCE(NULLIF(route_version, ''), ?),
                route_snapshot = COALESCE(NULLIF(route_snapshot, ''), ?),
                work_state = CASE
                    WHEN work_state IS NULL OR work_state = '' OR work_state = 'free' THEN ?
                    ELSE work_state
                END,
                last_activity_at = COALESCE(last_activity_at, updated_at, created_at, ?)
            WHERE id = ?
            """,
            (_trace_code("RB", batch_id), version, snapshot, work_state, now_text, batch_id),
        )
        _record_production_event(
            cursor,
            "batch_created",
            batch_id=batch_id,
            actor_employee_id=assigned_employee_id,
            details={"legacy_backfill": True, "product_name": product_name},
            request_key=f"route-batch:{batch_id}:created",
            created_at=created_at or now_text,
        )

    cursor.execute("SELECT id, quantity FROM fabric_stock WHERE quantity > 0")
    for stock_id, stock_quantity in cursor.fetchall():
        cursor.execute(
            "SELECT COALESCE(SUM(rolls_available), 0) FROM fabric_stock_lots WHERE stock_id = ?",
            (stock_id,),
        )
        tracked_quantity = int(cursor.fetchone()[0] or 0)
        missing_quantity = max(0, int(stock_quantity or 0) - tracked_quantity)
        if missing_quantity:
            _create_fabric_lot(
                cursor,
                stock_id,
                missing_quantity,
                None,
                now_text,
                source_type="legacy_balance",
            )

    cursor.execute("SELECT id, quantity FROM warehouse_stock WHERE quantity > 0")
    for stock_id, stock_quantity in cursor.fetchall():
        cursor.execute(
            "SELECT COALESCE(SUM(quantity_available), 0) FROM warehouse_stock_lots WHERE stock_id = ?",
            (stock_id,),
        )
        tracked_quantity = int(cursor.fetchone()[0] or 0)
        missing_quantity = max(0, int(stock_quantity or 0) - tracked_quantity)
        if missing_quantity:
            _create_warehouse_lot(
                cursor,
                stock_id,
                missing_quantity,
                now_text,
                source_type="legacy_balance",
            )


def init_db():
    conn = sqlite3.connect(DB_NAME, timeout=30)
    cursor = conn.cursor()
    cursor.execute("PRAGMA journal_mode = WAL")
    cursor.execute("PRAGMA synchronous = NORMAL")
    cursor.execute("PRAGMA busy_timeout = 30000")
    cursor.execute("PRAGMA foreign_keys = ON")

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
        CREATE TABLE IF NOT EXISTS data_repairs (
            repair_key TEXT PRIMARY KEY,
            applied_at TEXT NOT NULL
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
            unit TEXT NOT NULL DEFAULT 'рул',
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
            unit TEXT NOT NULL DEFAULT 'рул',
            movement_type TEXT NOT NULL,
            comment TEXT,
            created_by_employee_id INTEGER,
            created_at TEXT NOT NULL,
            FOREIGN KEY (created_by_employee_id) REFERENCES employees (id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fabric_stock_lots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stock_id INTEGER NOT NULL,
            lot_code TEXT NOT NULL UNIQUE,
            source_type TEXT,
            source_id INTEGER,
            rolls_received INTEGER NOT NULL,
            rolls_available INTEGER NOT NULL,
            created_by_employee_id INTEGER,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (stock_id) REFERENCES fabric_stock (id),
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
            comment TEXT,
            created_by_employee_id INTEGER,
            created_at TEXT NOT NULL,
            FOREIGN KEY (stock_id) REFERENCES warehouse_stock (id),
            FOREIGN KEY (created_by_employee_id) REFERENCES employees (id)
        )
    """)
    cursor.execute("PRAGMA table_info(warehouse_stock_movements)")
    warehouse_movement_columns = {row[1] for row in cursor.fetchall()}
    if "comment" not in warehouse_movement_columns:
        cursor.execute("ALTER TABLE warehouse_stock_movements ADD COLUMN comment TEXT")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS warehouse_stock_lots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stock_id INTEGER NOT NULL,
            lot_code TEXT NOT NULL UNIQUE,
            source_type TEXT,
            source_id INTEGER,
            quantity_received INTEGER NOT NULL,
            quantity_available INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (stock_id) REFERENCES warehouse_stock (id)
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
            assigned_employee_id INTEGER,
            assigned_at TEXT,
            FOREIGN KEY (created_by_employee_id) REFERENCES employees (id)
        )
    """)
    cursor.execute("PRAGMA table_info(production_tasks)")
    production_task_columns = {row[1] for row in cursor.fetchall()}
    if "assigned_employee_id" not in production_task_columns:
        cursor.execute("ALTER TABLE production_tasks ADD COLUMN assigned_employee_id INTEGER")
    if "assigned_at" not in production_task_columns:
        cursor.execute("ALTER TABLE production_tasks ADD COLUMN assigned_at TEXT")
    if "trace_code" not in production_task_columns:
        cursor.execute("ALTER TABLE production_tasks ADD COLUMN trace_code TEXT")
    if "route_version" not in production_task_columns:
        cursor.execute("ALTER TABLE production_tasks ADD COLUMN route_version TEXT")
    if "route_snapshot" not in production_task_columns:
        cursor.execute("ALTER TABLE production_tasks ADD COLUMN route_snapshot TEXT")

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
        CREATE TABLE IF NOT EXISTS production_task_fabric_rolls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            material_name TEXT NOT NULL,
            product_color TEXT NOT NULL,
            rolls INTEGER NOT NULL,
            UNIQUE(task_id, material_name, product_color),
            FOREIGN KEY (task_id) REFERENCES production_tasks (id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS production_task_fabric_lots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            lot_id INTEGER NOT NULL,
            rolls INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE(task_id, lot_id),
            FOREIGN KEY (task_id) REFERENCES production_tasks (id),
            FOREIGN KEY (lot_id) REFERENCES fabric_stock_lots (id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fabric_roll_defects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_key TEXT NOT NULL,
            task_id INTEGER NOT NULL,
            lot_id INTEGER NOT NULL,
            employee_id INTEGER,
            material_name TEXT NOT NULL,
            product_color TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            comment TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (task_id) REFERENCES production_tasks (id),
            FOREIGN KEY (lot_id) REFERENCES fabric_stock_lots (id),
            FOREIGN KEY (employee_id) REFERENCES employees (id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS production_task_attachments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL UNIQUE,
            file_name TEXT NOT NULL,
            mime_type TEXT NOT NULL,
            content_base64 TEXT NOT NULL,
            created_at TEXT NOT NULL,
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
    if "priority" not in route_batch_columns:
        cursor.execute("ALTER TABLE route_batches ADD COLUMN priority TEXT NOT NULL DEFAULT 'normal'")
    if "due_date" not in route_batch_columns:
        cursor.execute("ALTER TABLE route_batches ADD COLUMN due_date TEXT")
    if "parent_batch_id" not in route_batch_columns:
        cursor.execute("ALTER TABLE route_batches ADD COLUMN parent_batch_id INTEGER")
    if "source_cutting_batch_id" not in route_batch_columns:
        cursor.execute("ALTER TABLE route_batches ADD COLUMN source_cutting_batch_id INTEGER")
    if "trace_code" not in route_batch_columns:
        cursor.execute("ALTER TABLE route_batches ADD COLUMN trace_code TEXT")
    if "route_version" not in route_batch_columns:
        cursor.execute("ALTER TABLE route_batches ADD COLUMN route_version TEXT")
    if "route_snapshot" not in route_batch_columns:
        cursor.execute("ALTER TABLE route_batches ADD COLUMN route_snapshot TEXT")
    if "work_state" not in route_batch_columns:
        cursor.execute("ALTER TABLE route_batches ADD COLUMN work_state TEXT NOT NULL DEFAULT 'free'")
    if "blocked_reason" not in route_batch_columns:
        cursor.execute("ALTER TABLE route_batches ADD COLUMN blocked_reason TEXT")
    if "paused_at" not in route_batch_columns:
        cursor.execute("ALTER TABLE route_batches ADD COLUMN paused_at TEXT")
    if "last_activity_at" not in route_batch_columns:
        cursor.execute("ALTER TABLE route_batches ADD COLUMN last_activity_at TEXT")
    if "handover_count" not in route_batch_columns:
        cursor.execute("ALTER TABLE route_batches ADD COLUMN handover_count INTEGER NOT NULL DEFAULT 0")

    cursor.execute("PRAGMA table_info(production_tasks)")
    production_task_columns = [column[1] for column in cursor.fetchall()]

    if "priority" not in production_task_columns:
        cursor.execute("ALTER TABLE production_tasks ADD COLUMN priority TEXT NOT NULL DEFAULT 'normal'")
    if "due_date" not in production_task_columns:
        cursor.execute("ALTER TABLE production_tasks ADD COLUMN due_date TEXT")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS route_batch_inputs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_id INTEGER NOT NULL,
            stock_id INTEGER NOT NULL,
            input_role TEXT NOT NULL DEFAULT 'main',
            quantity INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE(batch_id, stock_id, input_role),
            FOREIGN KEY (batch_id) REFERENCES route_batches (id),
            FOREIGN KEY (stock_id) REFERENCES warehouse_stock (id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS route_batch_input_lots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_id INTEGER NOT NULL,
            lot_id INTEGER NOT NULL,
            input_role TEXT NOT NULL DEFAULT 'main',
            quantity INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE(batch_id, lot_id, input_role),
            FOREIGN KEY (batch_id) REFERENCES route_batches (id),
            FOREIGN KEY (lot_id) REFERENCES warehouse_stock_lots (id)
        )
    """)

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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS route_batch_defects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_id INTEGER NOT NULL,
            employee_id INTEGER,
            operation_name TEXT NOT NULL,
            position TEXT NOT NULL,
            product_name TEXT NOT NULL,
            product_size TEXT NOT NULL,
            product_color TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            reason TEXT NOT NULL,
            disposition TEXT NOT NULL,
            comment TEXT,
            rework_batch_id INTEGER,
            created_at TEXT NOT NULL,
            FOREIGN KEY (batch_id) REFERENCES route_batches (id),
            FOREIGN KEY (employee_id) REFERENCES employees (id),
            FOREIGN KEY (rework_batch_id) REFERENCES route_batches (id)
        )
    """)

    cursor.execute("PRAGMA table_info(route_batch_defects)")
    defect_columns = {row[1] for row in cursor.fetchall()}
    if "photo_name" not in defect_columns:
        cursor.execute("ALTER TABLE route_batch_defects ADD COLUMN photo_name TEXT")
    if "photo_mime_type" not in defect_columns:
        cursor.execute("ALTER TABLE route_batch_defects ADD COLUMN photo_mime_type TEXT")
    if "photo_base64" not in defect_columns:
        cursor.execute("ALTER TABLE route_batch_defects ADD COLUMN photo_base64 TEXT")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS route_batch_handoffs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_id INTEGER NOT NULL,
            from_employee_id INTEGER,
            to_employee_id INTEGER,
            reason TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (batch_id) REFERENCES route_batches (id),
            FOREIGN KEY (from_employee_id) REFERENCES employees (id),
            FOREIGN KEY (to_employee_id) REFERENCES employees (id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS production_trace_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_id INTEGER,
            cutting_batch_id INTEGER,
            production_task_id INTEGER,
            event_type TEXT NOT NULL,
            actor_employee_id INTEGER,
            shift_id INTEGER,
            operation_name TEXT,
            position TEXT,
            quantity INTEGER NOT NULL DEFAULT 0,
            good_quantity INTEGER NOT NULL DEFAULT 0,
            defect_quantity INTEGER NOT NULL DEFAULT 0,
            reason TEXT,
            details_json TEXT,
            request_key TEXT UNIQUE,
            created_at TEXT NOT NULL,
            FOREIGN KEY (batch_id) REFERENCES route_batches (id),
            FOREIGN KEY (cutting_batch_id) REFERENCES cutting_batches (id),
            FOREIGN KEY (production_task_id) REFERENCES production_tasks (id),
            FOREIGN KEY (actor_employee_id) REFERENCES employees (id),
            FOREIGN KEY (shift_id) REFERENCES shifts (id)
        )
    """)

    repair_legacy_uniqueness_conflicts(cursor)
    backfill_traceability(cursor)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_shifts_employee_date ON shifts (employee_id, shift_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_shifts_date_status ON shifts (shift_date, status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_employees_role_status ON employees (role, status)")
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_shifts_one_open ON shifts (employee_id) WHERE status = 'open'")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_shift_operations_shift ON shift_operations (shift_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_shift_operations_employee ON shift_operations (employee_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_operations_navigation ON operations (position, operation_group, folder, is_active)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cutting_batches_product_status ON cutting_batches (product_name, status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cutting_batches_task ON cutting_batches (production_task_id)")
    cursor.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_cutting_batches_active_task "
        "ON cutting_batches (production_task_id) "
        "WHERE production_task_id IS NOT NULL AND status != 'cancelled'"
    )
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cutting_batch_matrix_batch ON cutting_batch_matrix (batch_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_feedback_entries_date ON feedback_entries (feedback_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_feedback_entries_employee_date ON feedback_entries (employee_id, feedback_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_route_batches_status_step ON route_batches (status, route_step_index)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_route_batch_history_batch ON route_batch_history (batch_id)")
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_route_batch_history_step ON route_batch_history (batch_id, step_index)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_route_batch_inputs_batch ON route_batch_inputs (batch_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_route_batch_inputs_stock ON route_batch_inputs (stock_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_route_batch_input_lots_batch ON route_batch_input_lots (batch_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_route_batch_input_lots_lot ON route_batch_input_lots (lot_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_route_batch_defects_batch ON route_batch_defects (batch_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_route_batch_defects_date ON route_batch_defects (created_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_route_batches_due_date ON route_batches (status, due_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_route_batches_cutting_source ON route_batches (source_cutting_batch_id, status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_fabric_stock_color ON fabric_stock (product_color)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_production_tasks_status ON production_tasks (status, created_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_production_tasks_assignee ON production_tasks (assigned_employee_id, status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_production_task_items_task ON production_task_items (task_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_production_task_fabric_rolls_task ON production_task_fabric_rolls (task_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_production_task_fabric_lots_task ON production_task_fabric_lots (task_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_fabric_roll_defects_task ON fabric_roll_defects (task_id, created_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_fabric_roll_defects_lot ON fabric_roll_defects (lot_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_fabric_stock_lots_stock ON fabric_stock_lots (stock_id, rolls_available)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_warehouse_stock_type_position ON warehouse_stock (item_type, ready_for_position)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_warehouse_stock_product ON warehouse_stock (product_name, product_size, product_color)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_warehouse_stock_lots_stock ON warehouse_stock_lots (stock_id, quantity_available)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_trace_events_batch ON production_trace_events (batch_id, created_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_trace_events_cutting ON production_trace_events (cutting_batch_id, created_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_trace_events_task ON production_trace_events (production_task_id, created_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_route_batch_handoffs_batch ON route_batch_handoffs (batch_id, created_at)")
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_route_batches_trace_code ON route_batches (trace_code) WHERE trace_code IS NOT NULL")
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_production_tasks_trace_code ON production_tasks (trace_code) WHERE trace_code IS NOT NULL")

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
    backfill_cutting_progress_reports(cursor)

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

    if employee is not None and employee[4] == "admin" and employee[5] == "active" and employee[2] and employee[3]:
        conn.close()
        return employee

    try:
        cursor.execute("BEGIN IMMEDIATE")
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
                SET full_name = ?, position = ?, role = 'admin', status = 'active'
                WHERE telegram_id = ?
                """,
                (full_name, position, telegram_id),
            )
        conn.commit()
    except sqlite3.Error:
        conn.rollback()
        conn.close()
        return None

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


def get_all_user_accounts():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, full_name, position, telegram_id, status, role, registered_at
        FROM employees
        ORDER BY
            CASE role WHEN 'admin' THEN 0 ELSE 1 END,
            CASE status WHEN 'pending' THEN 0 WHEN 'active' THEN 1 ELSE 2 END,
            full_name COLLATE NOCASE,
            id
        """
    )

    accounts = cursor.fetchall()
    conn.close()
    return accounts


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


def update_employee_access_status(employee_id: int, status: str):
    if status not in {"active", "inactive", "pending", "rejected"}:
        return {"ok": False, "code": "invalid_status", "employee": None}

    conn = sqlite3.connect(DB_NAME, timeout=30)
    cursor = conn.cursor()

    try:
        cursor.execute("BEGIN IMMEDIATE")
        cursor.execute(
            """
            SELECT id, telegram_id, full_name, position, role, status
            FROM employees
            WHERE id = ?
            """,
            (employee_id,),
        )
        current = cursor.fetchone()
        if current is None:
            conn.rollback()
            return {"ok": False, "code": "not_found", "employee": None}

        if current[4] == "admin" and current[5] == "active" and status != "active":
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM employees
                WHERE role = 'admin' AND status = 'active' AND id != ?
                """,
                (employee_id,),
            )
            if int(cursor.fetchone()[0] or 0) == 0:
                conn.rollback()
                return {"ok": False, "code": "last_admin", "employee": current}

        cursor.execute(
            "UPDATE employees SET status = ? WHERE id = ?",
            (status, employee_id),
        )
        cursor.execute(
            """
            SELECT id, telegram_id, full_name, position, role, status
            FROM employees
            WHERE id = ?
            """,
            (employee_id,),
        )
        employee = cursor.fetchone()
        conn.commit()
        return {"ok": True, "code": "", "employee": employee}
    except sqlite3.Error:
        conn.rollback()
        raise
    finally:
        conn.close()


def update_employee_role(employee_id: int, role: str, position: str | None = None):
    if role not in {"admin", "employee"}:
        return {"ok": False, "code": "invalid_role", "employee": None}

    normalized_position = str(position or "").strip()
    if role == "employee" and not normalized_position:
        return {"ok": False, "code": "position_required", "employee": None}

    conn = sqlite3.connect(DB_NAME, timeout=30)
    cursor = conn.cursor()

    try:
        cursor.execute("BEGIN IMMEDIATE")
        cursor.execute(
            """
            SELECT id, telegram_id, full_name, position, role, status
            FROM employees
            WHERE id = ?
            """,
            (employee_id,),
        )
        current = cursor.fetchone()
        if current is None:
            conn.rollback()
            return {"ok": False, "code": "not_found", "employee": None}

        if current[4] == "admin" and current[5] == "active" and role != "admin":
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM employees
                WHERE role = 'admin' AND status = 'active' AND id != ?
                """,
                (employee_id,),
            )
            if int(cursor.fetchone()[0] or 0) == 0:
                conn.rollback()
                return {"ok": False, "code": "last_admin", "employee": current}

        if role == "admin":
            cursor.execute(
                """
                UPDATE employees
                SET role = 'admin', position = 'Администратор', status = 'active'
                WHERE id = ?
                """,
                (employee_id,),
            )
        else:
            cursor.execute(
                """
                UPDATE employees
                SET role = 'employee', position = ?, status = 'active'
                WHERE id = ?
                """,
                (normalized_position, employee_id),
            )

        cursor.execute(
            """
            SELECT id, telegram_id, full_name, position, role, status
            FROM employees
            WHERE id = ?
            """,
            (employee_id,),
        )
        employee = cursor.fetchone()
        conn.commit()
        return {"ok": True, "code": "", "employee": employee}
    except sqlite3.Error:
        conn.rollback()
        raise
    finally:
        conn.close()


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

    cursor.execute(
        """
        SELECT id, employee_id, shift_date, start_time, end_time, status
        FROM shifts
        WHERE employee_id = ?
          AND status = 'open'
        ORDER BY shift_date DESC, id DESC
        LIMIT 1
        """,
        (employee_id,)
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

    try:
        cursor.execute("BEGIN IMMEDIATE")
        cursor.execute(
            """
            SELECT id, employee_id, shift_date, start_time
            FROM shifts
            WHERE employee_id = ? AND status = 'open'
            ORDER BY id DESC
            LIMIT 1
            """,
            (employee_id,),
        )
        existing = cursor.fetchone()

        if existing is not None:
            conn.commit()
            conn.close()
            return {
                "id": existing[0],
                "employee_id": existing[1],
                "shift_date": existing[2],
                "start_time": existing[3],
                "status": "open",
            }

        cursor.execute(
            """
            INSERT INTO shifts (employee_id, shift_date, start_time, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (employee_id, shift_date, start_time, created_at),
        )
        shift_id = cursor.lastrowid
        conn.commit()
    except sqlite3.IntegrityError:
        conn.rollback()
        cursor.execute(
            """
            SELECT id, employee_id, shift_date, start_time
            FROM shifts
            WHERE employee_id = ? AND status = 'open'
            ORDER BY id DESC
            LIMIT 1
            """,
            (employee_id,),
        )
        existing = cursor.fetchone()
        conn.close()
        if existing is None:
            return None
        return {
            "id": existing[0],
            "employee_id": existing[1],
            "shift_date": existing[2],
            "start_time": existing[3],
            "status": "open",
        }
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
            quantity = shift_operations.quantity + excluded.quantity,
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
            work_state = 'cancelled',
            last_activity_at = ?,
            updated_at = ?,
            completed_at = ?
        WHERE id = ?
          AND status = 'active'
        """,
        (now, now, now, batch_id),
    )

    changed = cursor.rowcount > 0
    conn.commit()
    conn.close()

    return get_route_batch_by_id(batch_id) if changed else None


def cancel_route_batch_and_restore_inputs(batch_id: int, employee_id: int | None = None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    now = local_now().isoformat()

    try:
        cursor.execute("BEGIN IMMEDIATE")
        cursor.execute(
            f"SELECT {ROUTE_BATCH_SELECT} FROM route_batches WHERE id = ? AND status = 'active'",
            (batch_id,),
        )
        batch = route_batch_from_row(cursor.fetchone())
        if batch is None:
            raise ValueError("batch unavailable")

        cursor.execute(
            """
            UPDATE route_batches
            SET status = 'cancelled', work_state = 'cancelled',
                last_activity_at = ?, updated_at = ?, completed_at = ?
            WHERE id = ? AND status = 'active'
            """,
            (now, now, now, batch_id),
        )
        if cursor.rowcount != 1:
            raise ValueError("batch changed")

        cursor.execute(
            """
            SELECT
                route_batch_inputs.stock_id,
                route_batch_inputs.quantity,
                warehouse_stock.item_type,
                warehouse_stock.product_name,
                warehouse_stock.product_size,
                warehouse_stock.product_color,
                warehouse_stock.stage_name,
                warehouse_stock.ready_for_position,
                warehouse_stock.unit
            FROM route_batch_inputs
            JOIN warehouse_stock ON warehouse_stock.id = route_batch_inputs.stock_id
            WHERE route_batch_inputs.batch_id = ?
            """,
            (batch_id,),
        )
        input_rows = cursor.fetchall()
        cursor.execute(
            """
            SELECT route_batch_input_lots.lot_id, route_batch_input_lots.quantity
            FROM route_batch_input_lots
            WHERE route_batch_input_lots.batch_id = ?
            """,
            (batch_id,),
        )
        input_lot_rows = cursor.fetchall()

        if not input_rows and batch.get("source_stock_id"):
            cursor.execute(
                f"SELECT {WAREHOUSE_STOCK_SELECT} FROM warehouse_stock WHERE id = ?",
                (batch["source_stock_id"],),
            )
            stock = warehouse_stock_from_row(cursor.fetchone())
            if stock is not None:
                input_rows = [
                    (
                        stock["id"],
                        batch["quantity"],
                        stock["item_type"],
                        stock["product_name"],
                        stock["product_size"],
                        stock["product_color"],
                        stock["stage_name"],
                        stock["ready_for_position"],
                        stock["unit"],
                    )
                ]

        for stock_id, quantity, item_type, product_name, product_size, product_color, stage_name, ready_for_position, unit in input_rows:
            cursor.execute(
                "UPDATE warehouse_stock SET quantity = quantity + ?, updated_at = ? WHERE id = ?",
                (quantity, now, stock_id),
            )
            if cursor.rowcount != 1:
                raise ValueError("stock unavailable")
            cursor.execute(
                """
                INSERT INTO warehouse_stock_movements (
                    stock_id, item_type, product_name, product_size, product_color, stage_name,
                    ready_for_position, quantity, unit, movement_type, source_type, source_id,
                    created_by_employee_id, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'receipt', 'cancelled_task', ?, ?, ?)
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
                    unit,
                    batch_id,
                    employee_id,
                    now,
                ),
            )

        if input_lot_rows:
            for lot_id, quantity in input_lot_rows:
                cursor.execute(
                    """
                    UPDATE warehouse_stock_lots
                    SET quantity_available = quantity_available + ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (quantity, now, lot_id),
                )
                if cursor.rowcount != 1:
                    raise ValueError("lot unavailable")
        else:
            for stock_id, quantity, *_rest in input_rows:
                _create_warehouse_lot(
                    cursor,
                    stock_id,
                    quantity,
                    now,
                    source_type="cancelled_task",
                    source_id=batch_id,
                )

        _record_production_event(
            cursor,
            "task_cancelled",
            batch_id=batch_id,
            actor_employee_id=employee_id,
            quantity=batch["quantity"],
            details={"inputs_restored": len(input_rows)},
            request_key=f"route-batch:{batch_id}:cancelled",
            created_at=now,
        )

        conn.commit()
    except (sqlite3.Error, ValueError):
        conn.rollback()
        conn.close()
        return None

    conn.close()
    return get_route_batch_by_id(batch_id)


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
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    now = local_now().isoformat()

    try:
        cursor.execute("BEGIN IMMEDIATE")
        cursor.execute(
            """
            UPDATE route_batches
            SET assigned_employee_id = ?,
                assigned_at = COALESCE(assigned_at, ?),
                work_state = 'in_work',
                blocked_reason = NULL,
                paused_at = NULL,
                last_activity_at = ?,
                updated_at = ?
            WHERE id = ?
              AND status = 'active'
              AND (assigned_employee_id IS NULL OR assigned_employee_id = ?)
            """,
            (employee_id, now, now, now, batch_id, employee_id),
        )
        changed = cursor.rowcount > 0
        if changed:
            _record_production_event(
                cursor,
                "task_started",
                batch_id=batch_id,
                actor_employee_id=employee_id,
                request_key=f"route-batch:{batch_id}:first-start",
                created_at=now,
            )
        conn.commit()
    except sqlite3.Error:
        conn.rollback()
        conn.close()
        return None
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
    priority: str = "normal",
    due_date: str = "",
    parent_batch_id: int | None = None,
):
    if quantity <= 0:
        return None

    if status not in {"active", "done"}:
        return None

    if priority not in {"low", "normal", "high", "urgent"}:
        priority = "normal"

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
            source_stock_id,
            priority,
            due_date,
            parent_batch_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            priority,
            due_date or None,
            parent_batch_id,
        )
    )

    batch_id = cursor.lastrowid
    _initialize_route_batch_trace(cursor, batch_id, product_name, employee_id, now)
    conn.commit()
    conn.close()
    return get_route_batch_by_id(batch_id)


def create_route_batch_with_inputs(
    product_name: str,
    product_size: str,
    product_color: str,
    quantity: int,
    employee_id: int | None,
    route_step_index: int,
    input_items: list[dict],
    priority: str = "normal",
    due_date: str = "",
):
    if quantity <= 0 or not input_items:
        return None

    if priority not in {"low", "normal", "high", "urgent"}:
        priority = "normal"

    normalized_inputs = []
    stock_totals = {}

    for item in input_items:
        try:
            stock_id = int(item.get("stock_id") or 0)
            input_quantity = int(item.get("quantity") or 0)
        except (AttributeError, TypeError, ValueError):
            return None

        input_role = str(item.get("input_role") or "component").strip()

        if stock_id <= 0 or input_quantity <= 0 or input_role not in {"main", "component"}:
            return None

        normalized_inputs.append((stock_id, input_role, input_quantity))
        stock_totals[stock_id] = stock_totals.get(stock_id, 0) + input_quantity

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    now = local_now().isoformat()

    try:
        cursor.execute("BEGIN IMMEDIATE")
        stock_rows = {}

        for stock_id, total_quantity in stock_totals.items():
            cursor.execute(
                f"SELECT {WAREHOUSE_STOCK_SELECT} FROM warehouse_stock WHERE id = ?",
                (stock_id,),
            )
            stock = warehouse_stock_from_row(cursor.fetchone())

            if stock is None or stock["quantity"] < total_quantity:
                raise ValueError("insufficient stock")

            stock_rows[stock_id] = stock

        main_stock_id = next(
            (stock_id for stock_id, input_role, _input_quantity in normalized_inputs if input_role == "main"),
            normalized_inputs[0][0],
        )
        cursor.execute(
            """
            INSERT INTO route_batches (
                product_name, product_size, product_color, quantity,
                route_step_index, status, created_by_employee_id,
                created_at, updated_at, completed_at, source_stock_id,
                priority, due_date
            )
            VALUES (?, ?, ?, ?, ?, 'active', ?, ?, ?, NULL, ?, ?, ?)
            """,
            (
                product_name,
                product_size,
                product_color,
                quantity,
                route_step_index,
                employee_id,
                now,
                now,
                main_stock_id,
                priority,
                due_date or None,
            ),
        )
        batch_id = cursor.lastrowid
        _initialize_route_batch_trace(cursor, batch_id, product_name, employee_id, now, source="warehouse")

        for stock_id, input_role, input_quantity in normalized_inputs:
            stock = stock_rows[stock_id]
            cursor.execute(
                """
                UPDATE warehouse_stock
                SET quantity = quantity - ?, updated_at = ?
                WHERE id = ? AND quantity >= ?
                """,
                (input_quantity, now, stock_id, input_quantity),
            )

            if cursor.rowcount != 1:
                raise ValueError("stock changed")

            cursor.execute(
                """
                INSERT INTO warehouse_stock_movements (
                    stock_id, item_type, product_name, product_size, product_color, stage_name,
                    ready_for_position, quantity, unit, movement_type, source_type, source_id,
                    created_by_employee_id, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'issue', 'route_batch', ?, ?, ?)
                """,
                (
                    stock_id,
                    stock["item_type"],
                    stock["product_name"],
                    stock["product_size"],
                    stock["product_color"],
                    stock["stage_name"],
                    stock["ready_for_position"],
                    -input_quantity,
                    stock["unit"],
                    batch_id,
                    employee_id,
                    now,
                ),
            )
            cursor.execute(
                """
                INSERT INTO route_batch_inputs (
                    batch_id, stock_id, input_role, quantity, created_at
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (batch_id, stock_id, input_role, input_quantity, now),
            )
            _allocate_warehouse_lots(
                cursor,
                batch_id,
                stock_id,
                input_role,
                input_quantity,
                now,
            )

        _record_production_event(
            cursor,
            "inputs_reserved",
            batch_id=batch_id,
            actor_employee_id=employee_id,
            quantity=quantity,
            details={"inputs": len(normalized_inputs)},
            request_key=f"route-batch:{batch_id}:inputs-reserved",
            created_at=now,
        )

        conn.commit()
    except (sqlite3.Error, ValueError):
        conn.rollback()
        conn.close()
        return None

    conn.close()
    return get_route_batch_by_id(batch_id)


def create_route_batches_with_inputs(
    product_name: str,
    employee_id: int | None,
    route_step_index: int,
    batch_specs: list[dict],
    priority: str = "normal",
    due_date: str = "",
):
    if not batch_specs:
        return None

    if priority not in {"low", "normal", "high", "urgent"}:
        priority = "normal"

    normalized_specs = []
    stock_totals = {}

    for spec in batch_specs:
        try:
            quantity = int(spec.get("quantity") or 0)
        except (AttributeError, TypeError, ValueError):
            return None

        product_size = str(spec.get("product_size") or "").strip()
        product_color = str(spec.get("product_color") or "").strip()
        input_items = spec.get("input_items") or []

        if quantity <= 0 or not product_size or not product_color or not input_items:
            return None

        normalized_inputs = []
        for item in input_items:
            try:
                stock_id = int(item.get("stock_id") or 0)
                input_quantity = int(item.get("quantity") or 0)
            except (AttributeError, TypeError, ValueError):
                return None

            input_role = str(item.get("input_role") or "component").strip()
            if stock_id <= 0 or input_quantity <= 0 or input_role not in {"main", "component"}:
                return None

            normalized_inputs.append((stock_id, input_role, input_quantity))
            stock_totals[stock_id] = stock_totals.get(stock_id, 0) + input_quantity

        normalized_specs.append((product_size, product_color, quantity, normalized_inputs))

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    now = local_now().isoformat()
    batch_ids = []

    try:
        cursor.execute("BEGIN IMMEDIATE")
        stock_rows = {}
        for stock_id, total_quantity in stock_totals.items():
            cursor.execute(
                f"SELECT {WAREHOUSE_STOCK_SELECT} FROM warehouse_stock WHERE id = ?",
                (stock_id,),
            )
            stock = warehouse_stock_from_row(cursor.fetchone())
            if stock is None or stock["quantity"] < total_quantity:
                raise ValueError("insufficient stock")
            stock_rows[stock_id] = stock

        for product_size, product_color, quantity, normalized_inputs in normalized_specs:
            main_stock_id = next(
                (stock_id for stock_id, input_role, _quantity in normalized_inputs if input_role == "main"),
                normalized_inputs[0][0],
            )
            cursor.execute(
                """
                INSERT INTO route_batches (
                    product_name, product_size, product_color, quantity,
                    route_step_index, status, created_by_employee_id,
                    created_at, updated_at, completed_at, source_stock_id,
                    priority, due_date
                )
                VALUES (?, ?, ?, ?, ?, 'active', ?, ?, ?, NULL, ?, ?, ?)
                """,
                (
                    product_name,
                    product_size,
                    product_color,
                    quantity,
                    route_step_index,
                    employee_id,
                    now,
                    now,
                    main_stock_id,
                    priority,
                    due_date or None,
                ),
            )
            batch_id = cursor.lastrowid
            _initialize_route_batch_trace(cursor, batch_id, product_name, employee_id, now, source="warehouse_mass")
            batch_ids.append(batch_id)

            for stock_id, input_role, input_quantity in normalized_inputs:
                stock = stock_rows[stock_id]
                cursor.execute(
                    """
                    UPDATE warehouse_stock
                    SET quantity = quantity - ?, updated_at = ?
                    WHERE id = ? AND quantity >= ?
                    """,
                    (input_quantity, now, stock_id, input_quantity),
                )
                if cursor.rowcount != 1:
                    raise ValueError("stock changed")

                cursor.execute(
                    """
                    INSERT INTO warehouse_stock_movements (
                        stock_id, item_type, product_name, product_size, product_color, stage_name,
                        ready_for_position, quantity, unit, movement_type, source_type, source_id,
                        created_by_employee_id, created_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'issue', 'route_batch', ?, ?, ?)
                    """,
                    (
                        stock_id,
                        stock["item_type"],
                        stock["product_name"],
                        stock["product_size"],
                        stock["product_color"],
                        stock["stage_name"],
                        stock["ready_for_position"],
                        -input_quantity,
                        stock["unit"],
                        batch_id,
                        employee_id,
                        now,
                    ),
                )
                cursor.execute(
                    """
                    INSERT INTO route_batch_inputs (batch_id, stock_id, input_role, quantity, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (batch_id, stock_id, input_role, input_quantity, now),
                )
                _allocate_warehouse_lots(
                    cursor,
                    batch_id,
                    stock_id,
                    input_role,
                    input_quantity,
                    now,
                )

            _record_production_event(
                cursor,
                "inputs_reserved",
                batch_id=batch_id,
                actor_employee_id=employee_id,
                quantity=quantity,
                details={"inputs": len(normalized_inputs)},
                request_key=f"route-batch:{batch_id}:inputs-reserved",
                created_at=now,
            )

        conn.commit()
    except (sqlite3.Error, ValueError):
        conn.rollback()
        conn.close()
        return None

    conn.close()
    return [get_route_batch_by_id(batch_id) for batch_id in batch_ids]


def get_route_batch_inputs(batch_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            route_batch_inputs.id,
            route_batch_inputs.stock_id,
            route_batch_inputs.input_role,
            route_batch_inputs.quantity,
            warehouse_stock.item_type,
            warehouse_stock.product_name,
            warehouse_stock.product_size,
            warehouse_stock.product_color,
            warehouse_stock.stage_name,
            warehouse_stock.ready_for_position,
            warehouse_stock.unit
        FROM route_batch_inputs
        JOIN warehouse_stock ON warehouse_stock.id = route_batch_inputs.stock_id
        WHERE route_batch_inputs.batch_id = ?
        ORDER BY route_batch_inputs.input_role DESC, route_batch_inputs.id ASC
        """,
        (batch_id,),
    )
    rows = [
        {
            "id": row[0],
            "stock_id": row[1],
            "input_role": row[2],
            "quantity": row[3],
            "item_type": row[4],
            "product_name": row[5],
            "product_size": row[6],
            "product_color": row[7],
            "stage_name": row[8],
            "ready_for_position": row[9],
            "unit": row[10],
        }
        for row in cursor.fetchall()
    ]
    conn.close()
    return rows


def get_route_batch_input_lots(batch_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            route_batch_input_lots.id,
            route_batch_input_lots.input_role,
            route_batch_input_lots.quantity,
            warehouse_stock_lots.id,
            warehouse_stock_lots.lot_code,
            warehouse_stock_lots.source_type,
            warehouse_stock_lots.source_id,
            warehouse_stock.product_name,
            warehouse_stock.product_size,
            warehouse_stock.product_color,
            warehouse_stock.stage_name
        FROM route_batch_input_lots
        JOIN warehouse_stock_lots ON warehouse_stock_lots.id = route_batch_input_lots.lot_id
        JOIN warehouse_stock ON warehouse_stock.id = warehouse_stock_lots.stock_id
        WHERE route_batch_input_lots.batch_id = ?
        ORDER BY route_batch_input_lots.input_role DESC, route_batch_input_lots.id ASC
        """,
        (batch_id,),
    )
    rows = [
        {
            "id": row[0],
            "input_role": row[1],
            "quantity": row[2],
            "lot_id": row[3],
            "lot_code": row[4],
            "source_type": row[5] or "",
            "source_id": row[6],
            "product_name": row[7],
            "product_size": row[8],
            "product_color": row[9],
            "stage_name": row[10],
        }
        for row in cursor.fetchall()
    ]
    conn.close()
    return rows


def get_route_batch_by_trace_code(trace_code: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT {ROUTE_BATCH_SELECT} FROM route_batches WHERE trace_code = ?",
        (str(trace_code or "").strip().upper(),),
    )
    batch = route_batch_from_row(cursor.fetchone())
    conn.close()
    return batch


def set_route_batch_work_state(
    batch_id: int,
    employee_id: int | None,
    action: str,
    reason: str = "",
    *,
    force: bool = False,
):
    action = str(action or "").strip().lower()
    reason = str(reason or "").strip()
    if action not in {"pause", "block", "resume", "release"}:
        return None
    if action in {"block", "release"} and not reason:
        return None

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    now = local_now().isoformat()

    try:
        cursor.execute("BEGIN IMMEDIATE")
        cursor.execute(
            f"SELECT {ROUTE_BATCH_SELECT} FROM route_batches WHERE id = ? AND status = 'active'",
            (batch_id,),
        )
        batch = route_batch_from_row(cursor.fetchone())
        if batch is None:
            raise ValueError("batch unavailable")
        if not force and batch.get("assigned_employee_id") != employee_id:
            raise ValueError("not owner")

        if action == "pause":
            if not batch.get("assigned_employee_id"):
                raise ValueError("not assigned")
            values = ("paused", reason or "Перерыв", now, now, now, batch_id)
            cursor.execute(
                """
                UPDATE route_batches
                SET work_state = ?, blocked_reason = ?, paused_at = ?,
                    last_activity_at = ?, updated_at = ?
                WHERE id = ? AND status = 'active'
                """,
                values,
            )
            event_type = "task_paused"
        elif action == "block":
            if not batch.get("assigned_employee_id"):
                raise ValueError("not assigned")
            cursor.execute(
                """
                UPDATE route_batches
                SET work_state = 'blocked', blocked_reason = ?, paused_at = ?,
                    last_activity_at = ?, updated_at = ?
                WHERE id = ? AND status = 'active'
                """,
                (reason, now, now, now, batch_id),
            )
            event_type = "task_blocked"
        elif action == "resume":
            if not batch.get("assigned_employee_id"):
                raise ValueError("not assigned")
            cursor.execute(
                """
                UPDATE route_batches
                SET work_state = 'in_work', blocked_reason = NULL, paused_at = NULL,
                    last_activity_at = ?, updated_at = ?
                WHERE id = ? AND status = 'active'
                """,
                (now, now, batch_id),
            )
            event_type = "task_resumed"
        else:
            cursor.execute(
                """
                UPDATE route_batches
                SET assigned_employee_id = NULL, assigned_at = NULL,
                    work_state = 'free', blocked_reason = NULL, paused_at = NULL,
                    handover_count = handover_count + 1,
                    last_activity_at = ?, updated_at = ?
                WHERE id = ? AND status = 'active'
                """,
                (now, now, batch_id),
            )
            changed = cursor.rowcount
            cursor.execute(
                """
                INSERT INTO route_batch_handoffs (
                    batch_id, from_employee_id, to_employee_id, reason, created_at
                )
                VALUES (?, ?, NULL, ?, ?)
                """,
                (batch_id, batch.get("assigned_employee_id"), reason, now),
            )
            event_type = "task_released"

        if action != "release":
            changed = cursor.rowcount
        if changed != 1:
            raise ValueError("batch changed")
        _record_production_event(
            cursor,
            event_type,
            batch_id=batch_id,
            actor_employee_id=employee_id,
            reason=reason,
            details={"previous_state": batch.get("work_state") or ""},
            created_at=now,
        )
        conn.commit()
    except (sqlite3.Error, ValueError):
        conn.rollback()
        conn.close()
        return None

    conn.close()
    return get_route_batch_by_id(batch_id)


def get_route_batch_passport(batch_id: int):
    root = get_route_batch_by_id(batch_id)
    if root is None:
        return None

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    family_ids = {batch_id}
    cutting_ids = set()
    changed = True

    while changed:
        changed = False
        placeholders = ",".join("?" for _ in family_ids)
        cursor.execute(
            f"""
            SELECT id, parent_batch_id, source_cutting_batch_id
            FROM route_batches
            WHERE id IN ({placeholders}) OR parent_batch_id IN ({placeholders})
            """,
            (*family_ids, *family_ids),
        )
        for related_id, parent_id, cutting_id in cursor.fetchall():
            for candidate in (related_id, parent_id):
                if candidate and candidate not in family_ids:
                    family_ids.add(candidate)
                    changed = True
            if cutting_id:
                cutting_ids.add(cutting_id)

        placeholders = ",".join("?" for _ in family_ids)
        cursor.execute(
            f"""
            SELECT DISTINCT warehouse_stock_lots.source_id
            FROM route_batch_input_lots
            JOIN warehouse_stock_lots ON warehouse_stock_lots.id = route_batch_input_lots.lot_id
            WHERE route_batch_input_lots.batch_id IN ({placeholders})
              AND warehouse_stock_lots.source_type = 'route_batch'
              AND warehouse_stock_lots.source_id IS NOT NULL
            """,
            tuple(family_ids),
        )
        for (source_batch_id,) in cursor.fetchall():
            if source_batch_id not in family_ids:
                family_ids.add(source_batch_id)
                changed = True

        placeholders = ",".join("?" for _ in family_ids)
        cursor.execute(
            f"""
            SELECT DISTINCT warehouse_stock_lots.source_id
            FROM route_batch_input_lots
            JOIN warehouse_stock_lots ON warehouse_stock_lots.id = route_batch_input_lots.lot_id
            WHERE route_batch_input_lots.batch_id IN ({placeholders})
              AND warehouse_stock_lots.source_type = 'cutting_batch'
              AND warehouse_stock_lots.source_id IS NOT NULL
            """,
            tuple(family_ids),
        )
        cutting_ids.update(row[0] for row in cursor.fetchall() if row[0])

        if cutting_ids:
            cutting_placeholders = ",".join("?" for _ in cutting_ids)
            cursor.execute(
                f"SELECT id FROM route_batches WHERE source_cutting_batch_id IN ({cutting_placeholders})",
                tuple(cutting_ids),
            )
            for (sibling_batch_id,) in cursor.fetchall():
                if sibling_batch_id not in family_ids:
                    family_ids.add(sibling_batch_id)
                    changed = True

        placeholders = ",".join("?" for _ in family_ids)
        cursor.execute(
            f"""
            SELECT DISTINCT route_batch_input_lots.batch_id
            FROM route_batch_input_lots
            JOIN warehouse_stock_lots ON warehouse_stock_lots.id = route_batch_input_lots.lot_id
            WHERE warehouse_stock_lots.source_type = 'route_batch'
              AND warehouse_stock_lots.source_id IN ({placeholders})
            """,
            tuple(family_ids),
        )
        for (child_batch_id,) in cursor.fetchall():
            if child_batch_id not in family_ids:
                family_ids.add(child_batch_id)
                changed = True

    placeholders = ",".join("?" for _ in family_ids)
    cursor.execute(
        f"SELECT {ROUTE_BATCH_SELECT} FROM route_batches WHERE id IN ({placeholders}) ORDER BY created_at, id",
        tuple(family_ids),
    )
    batches = [route_batch_from_row(row) for row in cursor.fetchall()]
    for batch in batches:
        if batch.get("source_cutting_batch_id"):
            cutting_ids.add(batch["source_cutting_batch_id"])

    cutting_batches = []
    production_task_ids = set()
    if cutting_ids:
        cutting_placeholders = ",".join("?" for _ in cutting_ids)
        cursor.execute(
            f"""
            SELECT
                id, product_name, production_task_id, status,
                contour_employee_id, layout_employee_id, cutting_employee_id,
                cutting_progress, created_at, updated_at
            FROM cutting_batches
            WHERE id IN ({cutting_placeholders})
            ORDER BY created_at, id
            """,
            tuple(cutting_ids),
        )
        for row in cursor.fetchall():
            cutting_batches.append(
                {
                    "id": row[0],
                    "product_name": row[1],
                    "production_task_id": row[2],
                    "status": row[3],
                    "contour_employee_id": row[4],
                    "layout_employee_id": row[5],
                    "cutting_employee_id": row[6],
                    "cutting_progress": row[7],
                    "created_at": row[8],
                    "updated_at": row[9],
                }
            )
            if row[2]:
                production_task_ids.add(row[2])

    production_tasks = []
    fabric_lots = []
    if production_task_ids:
        task_placeholders = ",".join("?" for _ in production_task_ids)
        cursor.execute(
            f"""
            SELECT {', '.join(PRODUCTION_TASK_COLUMNS)}
            FROM production_tasks
            WHERE id IN ({task_placeholders})
            ORDER BY created_at, id
            """,
            tuple(production_task_ids),
        )
        production_tasks = [production_task_from_row(row) for row in cursor.fetchall()]
        cursor.execute(
            f"""
            SELECT
                production_task_fabric_lots.task_id,
                fabric_stock_lots.id,
                fabric_stock_lots.lot_code,
                production_task_fabric_lots.rolls,
                fabric_stock.material_name,
                fabric_stock.product_color
            FROM production_task_fabric_lots
            JOIN fabric_stock_lots
                ON fabric_stock_lots.id = production_task_fabric_lots.lot_id
            JOIN fabric_stock ON fabric_stock.id = fabric_stock_lots.stock_id
            WHERE production_task_fabric_lots.task_id IN ({task_placeholders})
            ORDER BY production_task_fabric_lots.task_id, fabric_stock_lots.id
            """,
            tuple(production_task_ids),
        )
        fabric_lots = [
            {
                "production_task_id": row[0],
                "lot_id": row[1],
                "lot_code": row[2],
                "rolls": row[3],
                "material_name": row[4],
                "product_color": row[5],
            }
            for row in cursor.fetchall()
        ]

    event_clauses = [f"batch_id IN ({placeholders})"]
    event_params = list(family_ids)
    if cutting_ids:
        cutting_placeholders = ",".join("?" for _ in cutting_ids)
        event_clauses.append(f"cutting_batch_id IN ({cutting_placeholders})")
        event_params.extend(cutting_ids)
    if production_task_ids:
        task_placeholders = ",".join("?" for _ in production_task_ids)
        event_clauses.append(f"production_task_id IN ({task_placeholders})")
        event_params.extend(production_task_ids)
    cursor.execute(
        f"""
        SELECT
            production_trace_events.id, production_trace_events.batch_id,
            production_trace_events.cutting_batch_id, production_trace_events.production_task_id,
            production_trace_events.event_type, production_trace_events.actor_employee_id,
            employees.full_name, production_trace_events.shift_id,
            production_trace_events.operation_name, production_trace_events.position,
            production_trace_events.quantity, production_trace_events.good_quantity,
            production_trace_events.defect_quantity, production_trace_events.reason,
            production_trace_events.details_json, production_trace_events.created_at
        FROM production_trace_events
        LEFT JOIN employees ON employees.id = production_trace_events.actor_employee_id
        WHERE {' OR '.join(event_clauses)}
        ORDER BY production_trace_events.created_at, production_trace_events.id
        """,
        tuple(event_params),
    )
    events = []
    for row in cursor.fetchall():
        try:
            details = json.loads(row[14] or "{}")
        except (TypeError, ValueError, json.JSONDecodeError):
            details = {}
        events.append(
            {
                "id": row[0],
                "batch_id": row[1],
                "cutting_batch_id": row[2],
                "production_task_id": row[3],
                "event_type": row[4],
                "actor_employee_id": row[5],
                "employee_name": row[6] or "",
                "shift_id": row[7],
                "operation_name": row[8] or "",
                "position": row[9] or "",
                "quantity": row[10],
                "good_quantity": row[11],
                "defect_quantity": row[12],
                "reason": row[13] or "",
                "details": details,
                "created_at": row[15],
            }
        )

    conn.close()
    return {
        "trace_code": root.get("trace_code") or _trace_code("RB", root["id"]),
        "route_version": root.get("route_version") or "",
        "focus_batch_id": batch_id,
        "batches": batches,
        "cutting_batches": cutting_batches,
        "production_tasks": production_tasks,
        "fabric_lots": fabric_lots,
        "events": events,
        "inputs": {str(item_id): get_route_batch_input_lots(item_id) for item_id in family_ids},
        "defects": {str(item_id): get_route_batch_defects(item_id) for item_id in family_ids},
    }


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


def complete_route_batch_step_atomic(
    batch_id: int,
    employee_id: int | None,
    expected_step_index: int,
    operation_name: str,
    position: str,
    next_step_index: int,
    good_quantity: int,
    defect_quantity: int,
    item_type: str,
    stage_name: str,
    ready_for_position: str,
    auto_create_next: bool = False,
    defect_reason: str = "",
    defect_disposition: str = "",
    defect_comment: str = "",
    defect_photo_name: str = "",
    defect_photo_mime_type: str = "",
    defect_photo_base64: str = "",
    shift_id: int | None = None,
    operation_id: int | None = None,
    request_id: str = "",
):
    if item_type not in {"semifinished", "finished"}:
        return None

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    now = local_now().isoformat()
    stock_id = None
    auto_batch_id = None
    rework_batch_id = None

    try:
        cursor.execute("BEGIN IMMEDIATE")
        explicit_request_key = f"route-complete:{request_id.strip()}" if request_id.strip() else ""
        request_key = explicit_request_key or f"route-batch:{batch_id}:step:{expected_step_index}:complete"
        if explicit_request_key:
            cursor.execute(
                "SELECT 1 FROM production_trace_events WHERE request_key = ?",
                (request_key,),
            )
            if cursor.fetchone() is not None:
                conn.commit()
                conn.close()
                return {
                    "batch": get_route_batch_by_id(batch_id),
                    "stock": None,
                    "auto_batch": None,
                    "rework_batch": None,
                    "replayed": True,
                }
        cursor.execute(
            f"SELECT {ROUTE_BATCH_SELECT} FROM route_batches WHERE id = ?",
            (batch_id,),
        )
        batch = route_batch_from_row(cursor.fetchone())

        if batch is None or batch["status"] != "active" or batch["route_step_index"] != expected_step_index:
            raise ValueError("batch already completed")
        if batch.get("assigned_employee_id") != employee_id or shift_id is None:
            raise ValueError("batch is not assigned in an open shift")
        if (batch.get("work_state") or "in_work") != "in_work":
            raise ValueError("batch is paused or blocked")
        if good_quantity < 0 or defect_quantity < 0 or good_quantity + defect_quantity != batch["quantity"]:
            raise ValueError("invalid quantities")

        cursor.execute(
            """
            INSERT INTO route_batch_history (
                batch_id, step_index, operation_name, position,
                employee_id, quantity, completed_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (batch_id, expected_step_index, operation_name, position, employee_id, good_quantity, now),
        )
        cursor.execute(
            """
            UPDATE route_batches
            SET route_step_index = ?, status = 'done',
                good_quantity = ?, defect_quantity = ?,
                work_state = 'done', blocked_reason = NULL, paused_at = NULL,
                last_activity_at = ?, updated_at = ?, completed_at = ?
            WHERE id = ? AND status = 'active' AND route_step_index = ?
              AND assigned_employee_id = ?
            """,
            (
                next_step_index,
                good_quantity,
                defect_quantity,
                now,
                now,
                now,
                batch_id,
                expected_step_index,
                employee_id,
            ),
        )
        if cursor.rowcount != 1:
            raise ValueError("batch changed")

        if good_quantity > 0:
            cursor.execute(
                """
                INSERT INTO warehouse_stock (
                    item_type, product_name, product_size, product_color, stage_name,
                    ready_for_position, quantity, unit, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, 'шт', ?)
                ON CONFLICT(item_type, product_name, product_size, product_color, stage_name, ready_for_position, unit)
                DO UPDATE SET quantity = quantity + excluded.quantity, updated_at = excluded.updated_at
                """,
                (
                    item_type,
                    batch["product_name"],
                    batch["product_size"],
                    batch["product_color"],
                    stage_name,
                    ready_for_position,
                    good_quantity,
                    now,
                ),
            )
            cursor.execute(
                """
                SELECT id FROM warehouse_stock
                WHERE item_type = ? AND product_name = ? AND product_size = ?
                  AND product_color = ? AND stage_name = ?
                  AND ready_for_position = ? AND unit = 'шт'
                """,
                (
                    item_type,
                    batch["product_name"],
                    batch["product_size"],
                    batch["product_color"],
                    stage_name,
                    ready_for_position,
                ),
            )
            stock_id = cursor.fetchone()[0]
            cursor.execute(
                """
                INSERT INTO warehouse_stock_movements (
                    stock_id, item_type, product_name, product_size, product_color, stage_name,
                    ready_for_position, quantity, unit, movement_type, source_type, source_id,
                    created_by_employee_id, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'шт', 'receipt', 'route_batch', ?, ?, ?)
                """,
                (
                    stock_id,
                    item_type,
                    batch["product_name"],
                    batch["product_size"],
                    batch["product_color"],
                    stage_name,
                    ready_for_position,
                    good_quantity,
                    batch_id,
                    employee_id,
                    now,
                ),
            )
            output_lot_id = _create_warehouse_lot(
                cursor,
                stock_id,
                good_quantity,
                now,
                source_type="route_batch",
                source_id=batch_id,
            )

            if auto_create_next:
                cursor.execute(
                    """
                    INSERT INTO route_batches (
                        product_name, product_size, product_color, quantity,
                        route_step_index, status, created_by_employee_id,
                        created_at, updated_at, completed_at, source_stock_id,
                        priority, due_date, parent_batch_id
                    )
                    VALUES (?, ?, ?, ?, ?, 'active', ?, ?, ?, NULL, ?, ?, ?, ?)
                    """,
                    (
                        batch["product_name"],
                        batch["product_size"],
                        batch["product_color"],
                        good_quantity,
                        next_step_index,
                        employee_id,
                        now,
                        now,
                        stock_id,
                        batch.get("priority") or "normal",
                        batch.get("due_date"),
                        batch_id,
                    ),
                )
                auto_batch_id = cursor.lastrowid
                _initialize_route_batch_trace(
                    cursor,
                    auto_batch_id,
                    batch["product_name"],
                    employee_id,
                    now,
                    source="automatic_next",
                    route_snapshot=batch.get("route_snapshot") or "",
                    route_version=batch.get("route_version") or "",
                )
                cursor.execute(
                    """
                    UPDATE warehouse_stock
                    SET quantity = quantity - ?, updated_at = ?
                    WHERE id = ? AND quantity >= ?
                    """,
                    (good_quantity, now, stock_id, good_quantity),
                )
                if cursor.rowcount != 1:
                    raise ValueError("new stock unavailable")
                cursor.execute(
                    """
                    INSERT INTO warehouse_stock_movements (
                        stock_id, item_type, product_name, product_size, product_color, stage_name,
                        ready_for_position, quantity, unit, movement_type, source_type, source_id,
                        created_by_employee_id, created_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'шт', 'issue', 'route_batch', ?, ?, ?)
                    """,
                    (
                        stock_id,
                        item_type,
                        batch["product_name"],
                        batch["product_size"],
                        batch["product_color"],
                        stage_name,
                        ready_for_position,
                        -good_quantity,
                        auto_batch_id,
                        employee_id,
                        now,
                    ),
                )
                cursor.execute(
                    """
                    INSERT INTO route_batch_inputs (batch_id, stock_id, input_role, quantity, created_at)
                    VALUES (?, ?, 'main', ?, ?)
                    """,
                    (auto_batch_id, stock_id, good_quantity, now),
                )
                cursor.execute(
                    """
                    UPDATE warehouse_stock_lots
                    SET quantity_available = quantity_available - ?, updated_at = ?
                    WHERE id = ? AND quantity_available >= ?
                    """,
                    (good_quantity, now, output_lot_id, good_quantity),
                )
                if cursor.rowcount != 1:
                    raise ValueError("output lot changed")
                cursor.execute(
                    """
                    INSERT INTO route_batch_input_lots (batch_id, lot_id, input_role, quantity, created_at)
                    VALUES (?, ?, 'main', ?, ?)
                    """,
                    (auto_batch_id, output_lot_id, good_quantity, now),
                )
                _record_production_event(
                    cursor,
                    "inputs_reserved",
                    batch_id=auto_batch_id,
                    actor_employee_id=employee_id,
                    quantity=good_quantity,
                    details={"automatic": True, "parent_batch_id": batch_id},
                    request_key=f"route-batch:{auto_batch_id}:inputs-reserved",
                    created_at=now,
                )

        if defect_quantity > 0 and defect_disposition == "На переделку":
            cursor.execute(
                """
                INSERT INTO route_batches (
                    product_name, product_size, product_color, quantity,
                    route_step_index, status, created_by_employee_id,
                    created_at, updated_at, completed_at, source_stock_id,
                    priority, due_date, parent_batch_id
                )
                VALUES (?, ?, ?, ?, ?, 'active', ?, ?, ?, NULL, NULL, 'urgent', ?, ?)
                """,
                (
                    batch["product_name"],
                    batch["product_size"],
                    batch["product_color"],
                    defect_quantity,
                    expected_step_index,
                    employee_id,
                    now,
                    now,
                    batch.get("due_date"),
                    batch_id,
                ),
            )
            rework_batch_id = cursor.lastrowid
            _initialize_route_batch_trace(
                cursor,
                rework_batch_id,
                batch["product_name"],
                employee_id,
                now,
                source="rework",
                route_snapshot=batch.get("route_snapshot") or "",
                route_version=batch.get("route_version") or "",
            )

        if defect_quantity > 0:
            if not defect_reason.strip() or not defect_disposition.strip():
                raise ValueError("defect details required")
            cursor.execute(
                """
                INSERT INTO route_batch_defects (
                    batch_id, employee_id, operation_name, position, product_name,
                    product_size, product_color, quantity, reason, disposition,
                    comment, rework_batch_id, created_at,
                    photo_name, photo_mime_type, photo_base64
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    batch_id,
                    employee_id,
                    operation_name,
                    position,
                    batch["product_name"],
                    batch["product_size"],
                    batch["product_color"],
                    defect_quantity,
                    defect_reason.strip(),
                    defect_disposition.strip(),
                    defect_comment.strip(),
                    rework_batch_id,
                    now,
                    defect_photo_name.strip(),
                    defect_photo_mime_type.strip(),
                    defect_photo_base64.strip(),
                ),
            )

        _record_production_event(
            cursor,
            "operation_completed",
            batch_id=batch_id,
            actor_employee_id=employee_id,
            shift_id=shift_id,
            operation_name=operation_name,
            position=position,
            quantity=batch["quantity"],
            good_quantity=good_quantity,
            defect_quantity=defect_quantity,
            reason=defect_reason if defect_quantity else "",
            details={
                "stage_name": stage_name,
                "next_step_index": next_step_index,
                "output_stock_id": stock_id,
                "auto_batch_id": auto_batch_id,
                "rework_batch_id": rework_batch_id,
            },
            request_key=request_key,
            created_at=now,
        )

        if shift_id and operation_id and good_quantity > 0:
            cursor.execute(
                """
                INSERT INTO shift_operations (
                    shift_id, employee_id, operation_id,
                    product_size, product_color, quantity, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(shift_id, operation_id, product_size, product_color)
                DO UPDATE SET quantity = quantity + excluded.quantity, updated_at = excluded.updated_at
                """,
                (
                    shift_id,
                    employee_id,
                    operation_id,
                    batch["product_size"],
                    batch["product_color"],
                    good_quantity,
                    now,
                    now,
                ),
            )

        conn.commit()
    except (sqlite3.Error, ValueError):
        conn.rollback()
        conn.close()
        return None

    conn.close()
    return {
        "batch": get_route_batch_by_id(batch_id),
        "stock": get_warehouse_stock_by_id(stock_id) if stock_id else None,
        "auto_batch": get_route_batch_by_id(auto_batch_id) if auto_batch_id else None,
        "rework_batch": get_route_batch_by_id(rework_batch_id) if rework_batch_id else None,
        "replayed": False,
    }


def add_route_batch_defect(
    batch_id: int,
    employee_id: int | None,
    operation_name: str,
    position: str,
    quantity: int,
    reason: str,
    disposition: str,
    comment: str = "",
    rework_batch_id: int | None = None,
):
    batch = get_route_batch_by_id(batch_id)

    if batch is None or quantity <= 0 or not reason.strip() or not disposition.strip():
        return None

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO route_batch_defects (
            batch_id, employee_id, operation_name, position, product_name,
            product_size, product_color, quantity, reason, disposition,
            comment, rework_batch_id, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            batch_id,
            employee_id,
            operation_name,
            position,
            batch["product_name"],
            batch["product_size"],
            batch["product_color"],
            quantity,
            reason.strip(),
            disposition.strip(),
            comment.strip(),
            rework_batch_id,
            local_now().isoformat(),
        ),
    )
    defect_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return defect_id


def get_route_batch_defect_rows(start_date: str, end_date: str, employee_id: int | None = None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            route_batch_defects.id,
            route_batch_defects.batch_id,
            route_batch_defects.created_at,
            route_batch_defects.product_name,
            route_batch_defects.product_size,
            route_batch_defects.product_color,
            route_batch_defects.operation_name,
            route_batch_defects.position,
            route_batch_defects.quantity,
            route_batch_defects.reason,
            route_batch_defects.disposition,
            route_batch_defects.comment,
            route_batch_defects.rework_batch_id,
            employees.id,
            employees.full_name
        FROM route_batch_defects
        LEFT JOIN employees ON employees.id = route_batch_defects.employee_id
        WHERE date(route_batch_defects.created_at) BETWEEN ? AND ?
          AND (? IS NULL OR route_batch_defects.employee_id = ?)
        ORDER BY route_batch_defects.created_at DESC, route_batch_defects.id DESC
        """,
        (start_date, end_date, employee_id, employee_id),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_route_batch_defects(batch_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            id, quantity, reason, disposition, comment, rework_batch_id, created_at,
            CASE WHEN COALESCE(photo_base64, '') != '' THEN 1 ELSE 0 END
        FROM route_batch_defects
        WHERE batch_id = ?
        ORDER BY id ASC
        """,
        (batch_id,),
    )
    rows = [
        {
            "id": row[0],
            "quantity": row[1],
            "reason": row[2],
            "disposition": row[3],
            "comment": row[4] or "",
            "rework_batch_id": row[5],
            "created_at": row[6],
            "has_photo": bool(row[7]),
        }
        for row in cursor.fetchall()
    ]
    conn.close()
    return rows


def get_route_batch_defect_photo(defect_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT batch_id, photo_name, photo_mime_type, photo_base64
        FROM route_batch_defects
        WHERE id = ? AND COALESCE(photo_base64, '') != ''
        """,
        (defect_id,),
    )
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return None
    return {
        "batch_id": row[0],
        "file_name": row[1] or f"defect-{defect_id}.jpg",
        "mime_type": row[2] or "image/jpeg",
        "content_base64": row[3],
    }


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

    _record_production_event(
        cursor,
        "cutting_contours_done",
        cutting_batch_id=batch_id,
        actor_employee_id=employee_id,
        shift_id=shift_id,
        operation_name="Нанесение контуров лекал на ткань",
        quantity=sum(int(value or 0) for value in size_quantities.values()),
        request_key=f"cutting-batch:{batch_id}:contours",
        created_at=now_text,
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
    now = local_now()
    now_text = now.isoformat()
    try:
        cursor.execute("BEGIN IMMEDIATE")
        cursor.execute(
            """
            UPDATE production_tasks
            SET status = 'contours_done', updated_at = ?
            WHERE id = ? AND product_name = ? AND status = 'active'
            """,
            (now_text, task_id, product_name),
        )
        if cursor.rowcount != 1:
            raise ValueError("task already claimed")

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
        for product_size, product_color in positive_matrix:
            size_totals[product_size] = size_totals.get(product_size, 0) + positive_matrix[(product_size, product_color)]

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
            WHERE task_id = ? AND product_size = ? AND product_color = ?
            """,
            [
                (quantity, task_id, product_size, product_color)
                for (product_size, product_color), quantity in positive_matrix.items()
            ],
        )
        cursor.executemany(
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
            [
                (shift_id, employee_id, operation_id, product_size, product_color, quantity, now_text, now_text)
                for (product_size, product_color), quantity in positive_matrix.items()
            ],
        )
        _record_production_event(
            cursor,
            "cutting_contours_done",
            cutting_batch_id=batch_id,
            production_task_id=task_id,
            actor_employee_id=employee_id,
            shift_id=shift_id,
            operation_name="Нанесение контуров лекал на ткань",
            quantity=sum(positive_matrix.values()),
            details={"matrix_rows": len(positive_matrix)},
            request_key=f"cutting-batch:{batch_id}:contours",
            created_at=now_text,
        )
        conn.commit()
    except (sqlite3.Error, ValueError):
        conn.rollback()
        conn.close()
        return None

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


def get_active_cutting_batch_product_names():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT DISTINCT product_name
        FROM cutting_batches
        WHERE status IN ('contours_done', 'layout_done', 'cutting_in_progress', 'cutting_done')
        ORDER BY product_name ASC
        """
    )
    rows = [row[0] for row in cursor.fetchall()]
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

    cursor.execute(
        """
        SELECT
            cutting_batches.product_name,
            production_tasks.route_snapshot,
            production_tasks.route_version
        FROM cutting_batches
        LEFT JOIN production_tasks
            ON production_tasks.id = cutting_batches.production_task_id
        WHERE cutting_batches.id = ?
        """,
        (batch_id,),
    )
    batch_row = cursor.fetchone()
    product_name = batch_row[0] if batch_row else ""
    route_snapshot = batch_row[1] if batch_row and batch_row[1] else current_route_snapshot(product_name)
    route_version = batch_row[2] if batch_row and batch_row[2] else route_version_for_snapshot(route_snapshot)
    route_steps = route_steps_from_snapshot(route_snapshot, product_name)

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
                source_stock_id,
                source_cutting_batch_id
            )
            VALUES (?, ?, ?, ?, ?, 'active', ?, ?, ?, NULL, NULL, ?)
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
                batch_id,
            ),
        )
        route_batch_id = cursor.lastrowid
        _initialize_route_batch_trace(
            cursor,
            route_batch_id,
            product_name,
            employee_id,
            now_text,
            source="automatic_preparation",
            route_snapshot=route_snapshot,
            route_version=route_version,
        )
        created_ids.append(route_batch_id)

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

    cursor.execute(
        "SELECT DISTINCT product_size FROM cutting_batch_matrix WHERE batch_id = ?",
        (batch_id,),
    )
    product_sizes = [row[0] for row in cursor.fetchall()]
    if not product_sizes:
        cursor.execute(
            "SELECT product_size FROM cutting_batch_sizes WHERE batch_id = ?",
            (batch_id,),
        )
        product_sizes = [row[0] for row in cursor.fetchall()]

    cursor.executemany(
        """
        INSERT INTO shift_operations (
            shift_id, employee_id, operation_id,
            product_size, product_color, quantity, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(shift_id, operation_id, product_size, product_color)
        DO UPDATE SET
            employee_id = excluded.employee_id,
            quantity = shift_operations.quantity + excluded.quantity,
            updated_at = excluded.updated_at
        """,
        [
            (shift_id, employee_id, operation_id, product_size, product_color, layers, now_text, now_text)
            for product_color, layers in color_layers.items()
            for product_size in product_sizes
        ],
    )

    preparation_batch_ids = _create_preparation_route_batches_for_layout(cursor, batch_id, employee_id, now_text)

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

    _record_production_event(
        cursor,
        "cutting_layout_done",
        cutting_batch_id=batch_id,
        production_task_id=task_row[0] if task_row else None,
        actor_employee_id=employee_id,
        shift_id=shift_id,
        operation_name="Формирование настила",
        quantity=sum(int(value or 0) for value in color_layers.values()),
        details={"color_layers": color_layers, "preparation_batch_ids": preparation_batch_ids},
        request_key=f"cutting-batch:{batch_id}:layout",
        created_at=now_text,
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
            cutting_batches.production_task_id,
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
            cutting_batches.cutting_progress,
            cutting_batches.production_task_id
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
          AND cutting_progress <= ?
        """,
        (status, shift_id, operation_id, employee_id, progress, now_text, batch_id, progress)
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
    else:
        cursor.execute(
            """
            SELECT 1
            FROM cutting_batches
            WHERE id = ?
              AND status = ?
              AND cutting_shift_id = ?
              AND cutting_operation_id = ?
              AND cutting_employee_id = ?
              AND cutting_progress = ?
            """,
            (batch_id, status, shift_id, operation_id, employee_id, progress),
        )
        changed = cursor.fetchone() is not None

    if changed:
        cursor.execute(
            """
            INSERT INTO shift_operations (
                shift_id, employee_id, operation_id,
                product_size, product_color, quantity, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, 'без цвета', ?, ?, ?)
            ON CONFLICT(shift_id, operation_id, product_size, product_color)
            DO UPDATE SET
                employee_id = excluded.employee_id,
                quantity = excluded.quantity,
                updated_at = excluded.updated_at
            """,
            (shift_id, employee_id, operation_id, f"партия #{batch_id}", progress, now_text, now_text),
        )
        cursor.execute("SELECT production_task_id FROM cutting_batches WHERE id = ?", (batch_id,))
        trace_task_row = cursor.fetchone()
        _record_production_event(
            cursor,
            "cutting_progress",
            cutting_batch_id=batch_id,
            production_task_id=trace_task_row[0] if trace_task_row else None,
            actor_employee_id=employee_id,
            shift_id=shift_id,
            operation_name="Раскрой",
            quantity=progress,
            details={"progress": progress},
            request_key=f"cutting-batch:{batch_id}:progress:{progress}",
            created_at=now_text,
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
            cutting_progress,
            production_task_id
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


def get_cutting_batch_owner(batch_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            production_task_id,
            COALESCE(cutting_employee_id, layout_employee_id, contour_employee_id),
            COALESCE(updated_at, layout_date, contour_date)
        FROM cutting_batches
        WHERE id = ?
        """,
        (batch_id,),
    )
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return None
    return {
        "production_task_id": row[0],
        "employee_id": row[1],
        "assigned_at": row[2] or "",
    }


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

                cursor.execute(
                    """
                    INSERT INTO shift_operations (
                        shift_id, employee_id, operation_id,
                        product_size, product_color, quantity, created_at, updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(shift_id, operation_id, product_size, product_color)
                    DO UPDATE SET
                        employee_id = excluded.employee_id,
                        quantity = shift_operations.quantity + excluded.quantity,
                        updated_at = excluded.updated_at
                    """,
                    (shift_id, employee_id, operation_id, product_size, product_color, quantity, now_text, now_text),
                )

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
                _create_warehouse_lot(
                    cursor,
                    stock_id,
                    quantity,
                    now_stock_text,
                    source_type="cutting_batch",
                    source_id=batch_id,
                )
                _record_production_event(
                    cursor,
                    "cutting_output_received",
                    cutting_batch_id=batch_id,
                    production_task_id=task_id,
                    actor_employee_id=employee_id,
                    shift_id=shift_id,
                    operation_name="Формирование кроя",
                    quantity=quantity,
                    details={
                        "stock_id": stock_id,
                        "product_name": batch_product_name,
                        "product_size": product_size,
                        "product_color": product_color,
                    },
                    request_key=f"cutting-batch:{batch_id}:output:{stock_id}",
                    created_at=now_stock_text,
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

            _record_production_event(
                cursor,
                "cutting_formed",
                cutting_batch_id=batch_id,
                production_task_id=task_id,
                actor_employee_id=employee_id,
                shift_id=shift_id,
                operation_name="Формирование кроя",
                quantity=sum(int(row[2] or 0) for row in result_rows),
                request_key=f"cutting-batch:{batch_id}:formed",
                created_at=now_text,
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

    if batch[2] != "contours_done":
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

    if old_status == "formed":
        conn.close()
        return None

    if target_status == "contours_done":
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM route_batches
            WHERE source_cutting_batch_id = ?
              AND status NOT IN ('active', 'cancelled')
            """,
            (batch_id,),
        )
        if cursor.fetchone()[0] > 0:
            conn.close()
            return None
        cursor.execute(
            """
            UPDATE route_batches
            SET status = 'cancelled', updated_at = ?, completed_at = ?
            WHERE source_cutting_batch_id = ? AND status = 'active'
            """,
            (now_text, now_text, batch_id),
        )
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
    unit: str = "рул",
    comment: str = "",
):
    material_name = material_name.strip()
    product_color = product_color.strip()
    unit = unit.strip() or "рул"

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
        SELECT id FROM fabric_stock
        WHERE material_name = ? AND product_color = ? AND unit = ?
        """,
        (material_name, product_color, unit),
    )
    stock_id = cursor.fetchone()[0]

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
    movement_id = cursor.lastrowid
    _create_fabric_lot(
        cursor,
        stock_id,
        int(quantity),
        employee_id,
        now,
        source_type="fabric_receipt",
        source_id=movement_id,
    )
    _record_production_event(
        cursor,
        "material_received",
        actor_employee_id=employee_id,
        quantity=int(quantity),
        details={
            "material_name": material_name,
            "product_color": product_color,
            "unit": unit,
            "fabric_movement_id": movement_id,
        },
        request_key=f"fabric-receipt:{movement_id}",
        created_at=now,
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


def get_fabric_stock_rows_with_ids():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, material_name, product_color, quantity, unit, updated_at
        FROM fabric_stock
        WHERE quantity > 0
        ORDER BY material_name ASC, product_color ASC
        """
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_fabric_stock_by_id(stock_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, material_name, product_color, quantity, unit, updated_at
        FROM fabric_stock
        WHERE id = ?
        """,
        (stock_id,),
    )
    row = cursor.fetchone()
    conn.close()
    return row


def adjust_fabric_stock(
    stock_id: int,
    new_quantity: int,
    employee_id: int | None,
    reason: str,
):
    reason = reason.strip()
    if stock_id <= 0 or new_quantity < 0 or not reason:
        return None

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("BEGIN IMMEDIATE")
        cursor.execute(
            """
            SELECT id, material_name, product_color, quantity, unit, updated_at
            FROM fabric_stock
            WHERE id = ?
            """,
            (stock_id,),
        )
        stock = cursor.fetchone()
        if stock is None:
            raise ValueError("stock unavailable")

        old_quantity = int(stock[3] or 0)
        delta = int(new_quantity) - old_quantity
        if delta == 0:
            raise ValueError("quantity unchanged")

        now = local_now().isoformat()
        if delta < 0:
            _consume_fabric_lots(cursor, stock_id, -delta, now)

        cursor.execute(
            "UPDATE fabric_stock SET quantity = ?, updated_at = ? WHERE id = ? AND quantity = ?",
            (new_quantity, now, stock_id, stock[3]),
        )
        if cursor.rowcount != 1:
            raise ValueError("stock changed")

        cursor.execute(
            """
            INSERT INTO fabric_stock_movements (
                material_name, product_color, quantity, unit, movement_type, comment,
                created_by_employee_id, created_at
            )
            VALUES (?, ?, ?, ?, 'adjustment', ?, ?, ?)
            """,
            (stock[1], stock[2], delta, stock[4], reason, employee_id, now),
        )
        movement_id = cursor.lastrowid

        if delta > 0:
            _create_fabric_lot(
                cursor,
                stock_id,
                delta,
                employee_id,
                now,
                source_type="manual_adjustment",
                source_id=movement_id,
            )

        _record_production_event(
            cursor,
            "material_stock_adjusted",
            actor_employee_id=employee_id,
            quantity=delta,
            reason=reason,
            details={
                "stock_id": stock_id,
                "material_name": stock[1],
                "product_color": stock[2],
                "old_quantity": old_quantity,
                "new_quantity": int(new_quantity),
            },
            request_key=f"fabric-adjustment:{movement_id}",
            created_at=now,
        )
        conn.commit()
    except (sqlite3.Error, ValueError):
        conn.rollback()
        conn.close()
        return None

    conn.close()
    return get_fabric_stock_by_id(stock_id)


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
    movement_id = cursor.lastrowid
    _create_warehouse_lot(
        cursor,
        stock_id,
        quantity,
        now,
        source_type=source_type or "manual_receipt",
        source_id=source_id or movement_id,
    )
    _record_production_event(
        cursor,
        "stock_received",
        batch_id=source_id if source_type == "route_batch" else None,
        cutting_batch_id=source_id if source_type == "cutting_batch" else None,
        actor_employee_id=employee_id,
        quantity=quantity,
        details={"stock_id": stock_id, "stage_name": stage_name},
        request_key=f"warehouse-receipt:{movement_id}",
        created_at=now,
    )

    conn.commit()
    conn.close()
    return get_warehouse_stock_by_id(stock_id)


def consume_warehouse_stock(stock_id: int, quantity: int, employee_id: int | None, source_type: str = "", source_id: int | None = None):
    if quantity <= 0:
        return None

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        cursor.execute("BEGIN IMMEDIATE")
        cursor.execute(
            f"SELECT {WAREHOUSE_STOCK_SELECT} FROM warehouse_stock WHERE id = ?",
            (stock_id,),
        )
        stock = warehouse_stock_from_row(cursor.fetchone())
        if stock is None or stock["quantity"] < quantity:
            raise ValueError("insufficient stock")

        now = local_now().isoformat()
        new_quantity = stock["quantity"] - quantity
        cursor.execute(
            """
            UPDATE warehouse_stock
            SET quantity = ?, updated_at = ?
            WHERE id = ? AND quantity >= ?
            """,
            (new_quantity, now, stock_id, quantity),
        )
        if cursor.rowcount != 1:
            raise ValueError("stock changed")
        _consume_warehouse_lots(cursor, stock_id, quantity, now)

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
    except (sqlite3.Error, ValueError):
        conn.rollback()
        conn.close()
        return None

    conn.close()
    return {**stock, "quantity": new_quantity}


def adjust_warehouse_stock(
    stock_id: int,
    new_quantity: int,
    employee_id: int | None,
    reason: str,
):
    reason = reason.strip()
    if stock_id <= 0 or new_quantity < 0 or not reason:
        return None

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("BEGIN IMMEDIATE")
        cursor.execute(
            f"SELECT {WAREHOUSE_STOCK_SELECT} FROM warehouse_stock WHERE id = ?",
            (stock_id,),
        )
        stock = warehouse_stock_from_row(cursor.fetchone())
        if stock is None:
            raise ValueError("stock unavailable")

        old_quantity = int(stock["quantity"] or 0)
        delta = int(new_quantity) - old_quantity
        if delta == 0:
            raise ValueError("quantity unchanged")

        now = local_now().isoformat()
        if delta < 0:
            _consume_warehouse_lots(cursor, stock_id, -delta, now)

        cursor.execute(
            "UPDATE warehouse_stock SET quantity = ?, updated_at = ? WHERE id = ? AND quantity = ?",
            (new_quantity, now, stock_id, old_quantity),
        )
        if cursor.rowcount != 1:
            raise ValueError("stock changed")

        cursor.execute(
            """
            INSERT INTO warehouse_stock_movements (
                stock_id, item_type, product_name, product_size, product_color, stage_name,
                ready_for_position, quantity, unit, movement_type, source_type, source_id,
                comment, created_by_employee_id, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'adjustment', 'manual_adjustment', NULL, ?, ?, ?)
            """,
            (
                stock_id,
                stock["item_type"],
                stock["product_name"],
                stock["product_size"],
                stock["product_color"],
                stock["stage_name"],
                stock["ready_for_position"],
                delta,
                stock["unit"],
                reason,
                employee_id,
                now,
            ),
        )
        movement_id = cursor.lastrowid

        if delta > 0:
            _create_warehouse_lot(
                cursor,
                stock_id,
                delta,
                now,
                source_type="manual_adjustment",
                source_id=movement_id,
            )

        _record_production_event(
            cursor,
            "warehouse_stock_adjusted",
            actor_employee_id=employee_id,
            quantity=delta,
            reason=reason,
            details={
                "stock_id": stock_id,
                "old_quantity": old_quantity,
                "new_quantity": int(new_quantity),
                "stage_name": stock["stage_name"],
            },
            request_key=f"warehouse-adjustment:{movement_id}",
            created_at=now,
        )
        conn.commit()
    except (sqlite3.Error, ValueError):
        conn.rollback()
        conn.close()
        return None

    conn.close()
    return get_warehouse_stock_by_id(stock_id)


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
    fabric_rolls: dict[str, int] | None = None,
    material_name: str = "Ткань",
    attachment: dict | None = None,
    priority: str = "normal",
    due_date: str = "",
):
    product_name = product_name.strip()
    sizes = [str(size).strip() for size in sizes if str(size).strip()]
    colors = [str(color).strip() for color in colors if str(color).strip()]
    material_name = material_name.strip() or "Ткань"
    fabric_rolls = fabric_rolls or {}

    if priority not in {"low", "normal", "high", "urgent"}:
        priority = "normal"

    if not product_name or not sizes or not colors:
        return None

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    now = local_now().isoformat()
    task_id = None

    try:
        cursor.execute("BEGIN IMMEDIATE")
        fabric_stock_ids = {}

        if fabric_rolls:
            for product_color in colors:
                rolls = int(fabric_rolls.get(product_color) or 0)
                if rolls <= 0:
                    raise ValueError("fabric rolls required")

                cursor.execute(
                    """
                    SELECT id, quantity
                    FROM fabric_stock
                    WHERE material_name = ?
                      AND product_color = ?
                      AND unit = 'рул'
                    """,
                    (material_name, product_color),
                )
                row = cursor.fetchone()
                if row is None or int(row[1] or 0) < rolls:
                    raise ValueError("fabric unavailable")
                fabric_stock_ids[product_color] = row[0]

        cursor.execute(
            """
            INSERT INTO production_tasks (
                product_name, status, created_by_employee_id, created_at, updated_at, note,
                priority, due_date
            )
            VALUES (?, 'active', ?, ?, ?, ?, ?, ?)
            """,
            (product_name, employee_id, now, now, note.strip(), priority, due_date or None),
        )
        task_id = cursor.lastrowid
        _initialize_production_task_trace(cursor, task_id, product_name, employee_id, now)

        cursor.executemany(
            "INSERT INTO production_task_sizes (task_id, product_size) VALUES (?, ?)",
            [(task_id, product_size) for product_size in sizes],
        )
        cursor.executemany(
            "INSERT INTO production_task_colors (task_id, product_color) VALUES (?, ?)",
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

        for product_color in colors:
            rolls = int(fabric_rolls.get(product_color) or 0)
            if rolls <= 0:
                continue

            stock_id = fabric_stock_ids[product_color]
            cursor.execute(
                """
                UPDATE fabric_stock
                SET quantity = quantity - ?, updated_at = ?
                WHERE id = ? AND quantity >= ?
                """,
                (rolls, now, stock_id, rolls),
            )
            if cursor.rowcount != 1:
                raise ValueError("fabric changed")

            cursor.execute(
                """
                INSERT INTO fabric_stock_movements (
                    material_name, product_color, quantity, unit, movement_type, comment,
                    created_by_employee_id, created_at
                )
                VALUES (?, ?, ?, 'рул', 'issue', ?, ?, ?)
                """,
                (
                    material_name,
                    product_color,
                    -rolls,
                    f"Задание на раскрой #{task_id}: {product_name}",
                    employee_id,
                    now,
                ),
            )
            cursor.execute(
                """
                INSERT INTO production_task_fabric_rolls (task_id, material_name, product_color, rolls)
                VALUES (?, ?, ?, ?)
                """,
                (task_id, material_name, product_color, rolls),
            )
            _allocate_fabric_lots(cursor, task_id, stock_id, rolls, now)
            _record_production_event(
                cursor,
                "materials_reserved",
                production_task_id=task_id,
                actor_employee_id=employee_id,
                quantity=rolls,
                details={
                    "stock_id": stock_id,
                    "material_name": material_name,
                    "product_color": product_color,
                    "unit": "рул",
                },
                request_key=f"production-task:{task_id}:fabric:{product_color}",
                created_at=now,
            )

        if attachment:
            file_name = str(attachment.get("file_name") or "").strip()
            mime_type = str(attachment.get("mime_type") or "").strip()
            content_base64 = str(attachment.get("content_base64") or "").strip()
            if file_name and mime_type and content_base64:
                cursor.execute(
                    """
                    INSERT INTO production_task_attachments (
                        task_id, file_name, mime_type, content_base64, created_at
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (task_id, file_name, mime_type, content_base64, now),
                )

        conn.commit()
    except (sqlite3.Error, ValueError, TypeError):
        conn.rollback()
        conn.close()
        return None

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
            note,
            priority,
            due_date,
            assigned_employee_id,
            assigned_at,
            trace_code,
            route_version,
            route_snapshot
        FROM production_tasks
        WHERE id = ?
        """,
        (task_id,),
    )

    task = production_task_from_row(cursor.fetchone())
    conn.close()
    return task


def assign_production_task(task_id: int, employee_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    now = local_now().isoformat()

    try:
        cursor.execute("BEGIN IMMEDIATE")
        cursor.execute(
            """
            UPDATE production_tasks
            SET assigned_employee_id = ?,
                assigned_at = COALESCE(assigned_at, ?),
                updated_at = ?
            WHERE id = ?
              AND status IN ('active', 'contours_done', 'in_cutting')
              AND (assigned_employee_id IS NULL OR assigned_employee_id = ?)
            """,
            (employee_id, now, now, task_id, employee_id),
        )
        changed = cursor.rowcount > 0
        if changed:
            _record_production_event(
                cursor,
                "task_started",
                production_task_id=task_id,
                actor_employee_id=employee_id,
                request_key=f"production-task:{task_id}:assigned:{employee_id}",
                created_at=now,
            )
        conn.commit()
    except sqlite3.Error:
        conn.rollback()
        conn.close()
        return None

    conn.close()
    return get_production_task_by_id(task_id) if changed else None


def get_production_task_fabric_rolls(task_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT material_name, product_color, rolls
        FROM production_task_fabric_rolls
        WHERE task_id = ?
        ORDER BY product_color ASC
        """,
        (task_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_production_task_fabric_defects(task_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            event_key,
            material_name,
            product_color,
            SUM(quantity) AS quantity,
            comment,
            MIN(created_at) AS created_at,
            employee_id
        FROM fabric_roll_defects
        WHERE task_id = ?
        GROUP BY event_key, material_name, product_color, comment, employee_id
        ORDER BY created_at ASC, event_key ASC
        """,
        (task_id,),
    )
    rows = [
        {
            "event_key": row[0],
            "material_name": row[1],
            "product_color": row[2],
            "quantity": int(row[3] or 0),
            "comment": row[4] or "",
            "created_at": row[5] or "",
            "employee_id": row[6],
        }
        for row in cursor.fetchall()
    ]
    conn.close()
    return rows


def reject_production_task_fabric_rolls(
    task_id: int,
    employee_id: int,
    product_color: str,
    quantity: int,
    comment: str,
):
    product_color = product_color.strip()
    comment = comment.strip()
    if task_id <= 0 or employee_id <= 0 or quantity <= 0 or not product_color or not comment:
        return None

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("BEGIN IMMEDIATE")
        cursor.execute(
            """
            SELECT product_name, status, assigned_employee_id
            FROM production_tasks
            WHERE id = ?
            """,
            (task_id,),
        )
        task = cursor.fetchone()
        if task is None or task[1] not in {"active", "contours_done", "in_cutting"}:
            raise ValueError("task unavailable")
        if int(task[2] or 0) != employee_id:
            raise ValueError("task belongs to another employee")

        cursor.execute(
            """
            SELECT
                production_task_fabric_lots.lot_id,
                production_task_fabric_lots.rolls,
                fabric_stock.material_name,
                fabric_stock.product_color,
                COALESCE((
                    SELECT SUM(fabric_roll_defects.quantity)
                    FROM fabric_roll_defects
                    WHERE fabric_roll_defects.task_id = production_task_fabric_lots.task_id
                      AND fabric_roll_defects.lot_id = production_task_fabric_lots.lot_id
                ), 0) AS rejected_rolls
            FROM production_task_fabric_lots
            JOIN fabric_stock_lots ON fabric_stock_lots.id = production_task_fabric_lots.lot_id
            JOIN fabric_stock ON fabric_stock.id = fabric_stock_lots.stock_id
            WHERE production_task_fabric_lots.task_id = ?
              AND fabric_stock.product_color = ?
            ORDER BY fabric_stock_lots.created_at ASC, fabric_stock_lots.id ASC
            """,
            (task_id, product_color),
        )
        lot_rows = cursor.fetchall()
        available = sum(max(0, int(row[1] or 0) - int(row[4] or 0)) for row in lot_rows)
        if quantity > available:
            raise ValueError("not enough assigned rolls")

        remaining = int(quantity)
        event_key = uuid.uuid4().hex
        now = local_now().isoformat()
        material_name = "Ткань"

        for lot_id, assigned_rolls, row_material_name, row_color, rejected_rolls in lot_rows:
            if remaining <= 0:
                break
            lot_available = max(0, int(assigned_rolls or 0) - int(rejected_rolls or 0))
            rejected = min(remaining, lot_available)
            if rejected <= 0:
                continue
            material_name = row_material_name
            cursor.execute(
                """
                INSERT INTO fabric_roll_defects (
                    event_key, task_id, lot_id, employee_id, material_name,
                    product_color, quantity, comment, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event_key,
                    task_id,
                    lot_id,
                    employee_id,
                    row_material_name,
                    row_color,
                    rejected,
                    comment,
                    now,
                ),
            )
            remaining -= rejected

        if remaining:
            raise ValueError("assigned rolls changed")

        _record_production_event(
            cursor,
            "fabric_rolls_rejected",
            production_task_id=task_id,
            actor_employee_id=employee_id,
            quantity=quantity,
            defect_quantity=quantity,
            reason=comment,
            details={
                "material_name": material_name,
                "product_color": product_color,
                "event_key": event_key,
            },
            request_key=f"fabric-defect:{event_key}",
            created_at=now,
        )
        conn.commit()
    except (sqlite3.Error, ValueError):
        conn.rollback()
        conn.close()
        return None

    conn.close()
    return {
        "event_key": event_key,
        "task_id": task_id,
        "material_name": material_name,
        "product_color": product_color,
        "quantity": int(quantity),
        "comment": comment,
        "created_at": now,
    }


def get_production_task_attachment(task_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT file_name, mime_type, content_base64
        FROM production_task_attachments
        WHERE task_id = ?
        """,
        (task_id,),
    )
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    return {
        "file_name": row[0],
        "mime_type": row[1],
        "content_base64": row[2],
    }


def cancel_production_task(task_id: int, employee_id: int | None = None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    now = local_now().isoformat()
    try:
        cursor.execute("BEGIN IMMEDIATE")
        cursor.execute(
            """
            SELECT product_name
            FROM production_tasks
            WHERE id = ? AND status = 'active'
            """,
            (task_id,),
        )
        task_row = cursor.fetchone()

        if task_row is None:
            conn.rollback()
            conn.close()
            return None

        cursor.execute(
            "SELECT 1 FROM cutting_batches WHERE production_task_id = ? AND status != 'cancelled' LIMIT 1",
            (task_id,),
        )
        if cursor.fetchone() is not None:
            conn.rollback()
            conn.close()
            return None

        cursor.execute(
            """
            UPDATE production_tasks
            SET status = 'cancelled',
                updated_at = ?,
                completed_at = ?
            WHERE id = ? AND status = 'active'
            """,
            (now, now, task_id),
        )
        if cursor.rowcount != 1:
            conn.rollback()
            conn.close()
            return None

        cursor.execute(
            """
            SELECT
                production_task_fabric_rolls.material_name,
                production_task_fabric_rolls.product_color,
                MAX(production_task_fabric_rolls.rolls) - COALESCE(SUM(fabric_roll_defects.quantity), 0)
                    AS restorable_rolls,
                COALESCE(SUM(fabric_roll_defects.quantity), 0) AS rejected_rolls
            FROM production_task_fabric_rolls
            LEFT JOIN fabric_roll_defects
                ON fabric_roll_defects.task_id = production_task_fabric_rolls.task_id
               AND fabric_roll_defects.material_name = production_task_fabric_rolls.material_name
               AND fabric_roll_defects.product_color = production_task_fabric_rolls.product_color
            WHERE production_task_fabric_rolls.task_id = ?
            GROUP BY
                production_task_fabric_rolls.material_name,
                production_task_fabric_rolls.product_color
            """,
            (task_id,),
        )
        roll_rows = cursor.fetchall()

        cursor.execute(
            """
            SELECT
                production_task_fabric_lots.lot_id,
                production_task_fabric_lots.rolls - COALESCE(SUM(fabric_roll_defects.quantity), 0)
                    AS restorable_rolls,
                fabric_stock_lots.stock_id
            FROM production_task_fabric_lots
            JOIN fabric_stock_lots
                ON fabric_stock_lots.id = production_task_fabric_lots.lot_id
            LEFT JOIN fabric_roll_defects
                ON fabric_roll_defects.task_id = production_task_fabric_lots.task_id
               AND fabric_roll_defects.lot_id = production_task_fabric_lots.lot_id
            WHERE production_task_fabric_lots.task_id = ?
            GROUP BY
                production_task_fabric_lots.lot_id,
                production_task_fabric_lots.rolls,
                fabric_stock_lots.stock_id
            """,
            (task_id,),
        )
        restored_stock_ids = set()
        for lot_id, rolls, stock_id in cursor.fetchall():
            if int(rolls or 0) <= 0:
                continue
            cursor.execute(
                """
                UPDATE fabric_stock_lots
                SET rolls_available = rolls_available + ?, updated_at = ?
                WHERE id = ?
                """,
                (rolls, now, lot_id),
            )
            restored_stock_ids.add(stock_id)

        for material_name, product_color, rolls, _rejected_rolls in roll_rows:
            rolls = int(rolls or 0)
            if rolls <= 0:
                continue
            cursor.execute(
                """
                INSERT INTO fabric_stock (material_name, product_color, quantity, unit, updated_at)
                VALUES (?, ?, ?, 'рул', ?)
                ON CONFLICT(material_name, product_color, unit)
                DO UPDATE SET
                    quantity = quantity + excluded.quantity,
                    updated_at = excluded.updated_at
                """,
                (material_name, product_color, rolls, now),
            )
            cursor.execute(
                """
                SELECT id FROM fabric_stock
                WHERE material_name = ? AND product_color = ? AND unit = 'рул'
                """,
                (material_name, product_color),
            )
            stock_id = cursor.fetchone()[0]
            cursor.execute(
                """
                INSERT INTO fabric_stock_movements (
                    material_name, product_color, quantity, unit, movement_type, comment,
                    created_by_employee_id, created_at
                )
                VALUES (?, ?, ?, 'рул', 'receipt', ?, ?, ?)
                """,
                (
                    material_name,
                    product_color,
                    rolls,
                    f"Возврат рулонов после отмены задания на раскрой #{task_id}: {task_row[0]}",
                    employee_id,
                    now,
                ),
            )
            if stock_id not in restored_stock_ids:
                _create_fabric_lot(
                    cursor,
                    stock_id,
                    rolls,
                    employee_id,
                    now,
                    source_type="task_cancellation",
                    source_id=task_id,
                )

        _record_production_event(
            cursor,
            "task_cancelled",
            production_task_id=task_id,
            actor_employee_id=employee_id,
            details={
                "returned_rolls": sum(int(row[2] or 0) for row in roll_rows),
                "rejected_rolls": sum(int(row[3] or 0) for row in roll_rows),
            },
            request_key=f"production-task:{task_id}:cancelled",
            created_at=now,
        )
        conn.commit()
    except sqlite3.Error:
        conn.rollback()
        conn.close()
        return None

    conn.close()
    return get_production_task_by_id(task_id)


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
            COALESCE(GROUP_CONCAT(DISTINCT production_task_colors.product_color), '') AS colors_text,
            production_tasks.priority,
            production_tasks.due_date,
            production_tasks.assigned_employee_id,
            production_tasks.assigned_at
        FROM production_tasks
        LEFT JOIN production_task_sizes ON production_task_sizes.task_id = production_tasks.id
        LEFT JOIN production_task_colors ON production_task_colors.task_id = production_tasks.id
        WHERE production_tasks.status IN ('active', 'contours_done', 'in_cutting')
        GROUP BY
            production_tasks.id,
            production_tasks.product_name,
            production_tasks.status,
            production_tasks.created_at,
            production_tasks.priority,
            production_tasks.due_date,
            production_tasks.assigned_employee_id,
            production_tasks.assigned_at
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
    cursor.execute("BEGIN IMMEDIATE")

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
          AND status = 'open'
        """,
        (end_time, total_minutes, edit_until, closed_at, shift_id)
    )

    if cursor.rowcount != 1:
        conn.rollback()
        conn.close()
        return None

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
    cursor.execute("BEGIN IMMEDIATE")

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM cutting_batches
        WHERE contour_shift_id = ? OR layout_shift_id = ?
           OR cutting_shift_id = ? OR formed_shift_id = ?
        """,
        (shift_id, shift_id, shift_id, shift_id),
    )
    if cursor.fetchone()[0] > 0:
        conn.rollback()
        conn.close()
        return None

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
        conn.rollback()
        conn.close()
        return None

    try:
        cursor.execute("UPDATE feedback_entries SET shift_id = NULL WHERE shift_id = ?", (shift_id,))
        cursor.execute("DELETE FROM shift_operations WHERE shift_id = ?", (shift_id,))
        cursor.execute("DELETE FROM shifts WHERE id = ?", (shift_id,))
        conn.commit()
    except sqlite3.Error:
        conn.rollback()
        conn.close()
        return None
    conn.close()
    return shift


def admin_close_shift(shift_id: int, end_time: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("BEGIN IMMEDIATE")

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
        end_dt += timedelta(days=1)

    if end_dt > local_now() + timedelta(minutes=5) or end_dt - start_dt > timedelta(hours=24):
        conn.rollback()
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
          AND status = 'open'
        """,
        (end_time, total_minutes, edit_until, closed_at, shift_id)
    )

    if cursor.rowcount != 1:
        conn.rollback()
        conn.close()
        return None

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


def get_period_route_batch_rows(start_date: str, end_date: str, employee_id: int | None = None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            route_batches.id,
            route_batches.product_name,
            route_batches.product_size,
            route_batches.product_color,
            route_batches.quantity,
            route_batches.route_step_index,
            route_batches.status,
            route_batches.created_at,
            route_batches.updated_at,
            route_batches.completed_at,
            route_batches.assigned_at,
            employees.id,
            employees.full_name,
            employees.position,
            route_batches.good_quantity,
            route_batches.defect_quantity,
            route_batches.priority,
            route_batches.due_date,
            route_batches.parent_batch_id
        FROM route_batches
        LEFT JOIN employees ON employees.id = route_batches.assigned_employee_id
        WHERE (
            date(route_batches.created_at) BETWEEN ? AND ?
            OR date(route_batches.completed_at) BETWEEN ? AND ?
        )
          AND (? IS NULL OR route_batches.assigned_employee_id = ?)
        ORDER BY route_batches.created_at ASC, route_batches.id ASC
        """,
        (start_date, end_date, start_date, end_date, employee_id, employee_id),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_period_employee_production_performance(start_date: str, end_date: str):
    totals = {}

    def add_rows(rows):
        for employee_id, full_name, position, plan, fact in rows:
            if employee_id is None:
                continue
            employee = totals.setdefault(
                employee_id,
                {
                    "full_name": full_name or "Сотрудник",
                    "position": position or "-",
                    "plan": 0,
                    "fact": 0,
                },
            )
            employee["plan"] += int(plan or 0)
            employee["fact"] += int(fact or 0)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            route_batch_history.employee_id,
            employees.full_name,
            employees.position,
            SUM(route_batches.quantity),
            SUM(route_batch_history.quantity)
        FROM route_batch_history
        JOIN route_batches ON route_batches.id = route_batch_history.batch_id
        JOIN employees ON employees.id = route_batch_history.employee_id
        WHERE date(route_batch_history.completed_at) BETWEEN ? AND ?
          AND employees.role != 'admin'
        GROUP BY route_batch_history.employee_id, employees.full_name, employees.position
        """,
        (start_date, end_date),
    )
    add_rows(cursor.fetchall())

    cursor.execute(
        """
        SELECT
            route_batches.assigned_employee_id,
            employees.full_name,
            employees.position,
            SUM(route_batches.quantity),
            0
        FROM route_batches
        JOIN employees ON employees.id = route_batches.assigned_employee_id
        WHERE route_batches.status = 'active'
          AND date(COALESCE(route_batches.assigned_at, route_batches.created_at)) BETWEEN ? AND ?
          AND employees.role != 'admin'
        GROUP BY route_batches.assigned_employee_id, employees.full_name, employees.position
        """,
        (start_date, end_date),
    )
    add_rows(cursor.fetchall())

    cursor.execute(
        """
        WITH task_totals AS (
            SELECT
                task_id,
                SUM(
                    CASE
                        WHEN formed_quantity > contour_quantity THEN formed_quantity
                        ELSE contour_quantity
                    END
                ) AS plan_quantity,
                SUM(formed_quantity) AS formed_quantity
            FROM production_task_items
            GROUP BY task_id
        ),
        matrix_totals AS (
            SELECT batch_id, SUM(quantity) AS quantity
            FROM cutting_batch_matrix
            GROUP BY batch_id
        ),
        size_totals AS (
            SELECT batch_id, SUM(quantity) AS quantity
            FROM cutting_batch_sizes
            GROUP BY batch_id
        ),
        batch_totals AS (
            SELECT
                cutting_batches.id,
                COALESCE(task_totals.plan_quantity, matrix_totals.quantity, size_totals.quantity, 0)
                    AS plan_quantity,
                COALESCE(task_totals.formed_quantity, matrix_totals.quantity, 0)
                    AS formed_quantity
            FROM cutting_batches
            LEFT JOIN task_totals ON task_totals.task_id = cutting_batches.production_task_id
            LEFT JOIN matrix_totals ON matrix_totals.batch_id = cutting_batches.id
            LEFT JOIN size_totals ON size_totals.batch_id = cutting_batches.id
            WHERE cutting_batches.status != 'cancelled'
        ),
        cutting_stages AS (
            SELECT
                cutting_batches.contour_employee_id AS employee_id,
                cutting_batches.contour_shift_id AS shift_id,
                cutting_batches.contour_date AS fallback_date,
                batch_totals.plan_quantity AS plan_quantity,
                batch_totals.plan_quantity AS fact_quantity
            FROM cutting_batches
            JOIN batch_totals ON batch_totals.id = cutting_batches.id
            WHERE cutting_batches.contour_employee_id IS NOT NULL

            UNION ALL

            SELECT
                cutting_batches.layout_employee_id,
                cutting_batches.layout_shift_id,
                cutting_batches.layout_date,
                batch_totals.plan_quantity,
                batch_totals.plan_quantity
            FROM cutting_batches
            JOIN batch_totals ON batch_totals.id = cutting_batches.id
            WHERE cutting_batches.layout_employee_id IS NOT NULL

            UNION ALL

            SELECT
                cutting_batches.cutting_employee_id,
                cutting_batches.cutting_shift_id,
                date(cutting_batches.updated_at),
                batch_totals.plan_quantity,
                ROUND(batch_totals.plan_quantity * cutting_batches.cutting_progress / 100.0)
            FROM cutting_batches
            JOIN batch_totals ON batch_totals.id = cutting_batches.id
            WHERE cutting_batches.cutting_employee_id IS NOT NULL

            UNION ALL

            SELECT
                cutting_batches.formed_employee_id,
                cutting_batches.formed_shift_id,
                cutting_batches.formed_date,
                batch_totals.plan_quantity,
                batch_totals.formed_quantity
            FROM cutting_batches
            JOIN batch_totals ON batch_totals.id = cutting_batches.id
            WHERE cutting_batches.formed_employee_id IS NOT NULL
        )
        SELECT
            cutting_stages.employee_id,
            employees.full_name,
            employees.position,
            SUM(cutting_stages.plan_quantity),
            SUM(cutting_stages.fact_quantity)
        FROM cutting_stages
        LEFT JOIN shifts ON shifts.id = cutting_stages.shift_id
        JOIN employees ON employees.id = cutting_stages.employee_id
        WHERE COALESCE(shifts.shift_date, date(cutting_stages.fallback_date)) BETWEEN ? AND ?
          AND employees.role != 'admin'
        GROUP BY cutting_stages.employee_id, employees.full_name, employees.position
        """,
        (start_date, end_date),
    )
    add_rows(cursor.fetchall())

    conn.close()
    return [
        (
            employee_id,
            employee["full_name"],
            employee["position"],
            employee["plan"],
            employee["fact"],
        )
        for employee_id, employee in sorted(
            totals.items(),
            key=lambda item: (item[1]["full_name"], item[0]),
        )
    ]


def get_period_route_batch_input_rows(start_date: str, end_date: str, employee_id: int | None = None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            route_batch_inputs.batch_id,
            route_batch_inputs.input_role,
            route_batch_inputs.quantity,
            route_batch_inputs.stock_id,
            warehouse_stock.item_type,
            warehouse_stock.product_name,
            warehouse_stock.product_size,
            warehouse_stock.product_color,
            warehouse_stock.stage_name,
            warehouse_stock.ready_for_position,
            warehouse_stock.unit,
            route_batches.status,
            route_batches.created_at,
            employees.full_name
        FROM route_batch_inputs
        JOIN route_batches ON route_batches.id = route_batch_inputs.batch_id
        JOIN warehouse_stock ON warehouse_stock.id = route_batch_inputs.stock_id
        LEFT JOIN employees ON employees.id = route_batches.assigned_employee_id
        WHERE (
            date(route_batches.created_at) BETWEEN ? AND ?
            OR date(route_batches.completed_at) BETWEEN ? AND ?
        )
          AND (? IS NULL OR route_batches.assigned_employee_id = ?)
        ORDER BY route_batch_inputs.batch_id ASC, route_batch_inputs.id ASC
        """,
        (start_date, end_date, start_date, end_date, employee_id, employee_id),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_period_route_batch_input_lot_rows(start_date: str, end_date: str, employee_id: int | None = None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            route_batches.id,
            route_batches.trace_code,
            route_batch_input_lots.input_role,
            route_batch_input_lots.quantity,
            warehouse_stock_lots.id,
            warehouse_stock_lots.lot_code,
            warehouse_stock_lots.source_type,
            warehouse_stock_lots.source_id,
            warehouse_stock.item_type,
            warehouse_stock.product_name,
            warehouse_stock.product_size,
            warehouse_stock.product_color,
            warehouse_stock.stage_name,
            warehouse_stock.ready_for_position,
            route_batches.created_at,
            employees.full_name
        FROM route_batch_input_lots
        JOIN route_batches ON route_batches.id = route_batch_input_lots.batch_id
        JOIN warehouse_stock_lots ON warehouse_stock_lots.id = route_batch_input_lots.lot_id
        JOIN warehouse_stock ON warehouse_stock.id = warehouse_stock_lots.stock_id
        LEFT JOIN employees ON employees.id = route_batches.assigned_employee_id
        WHERE (
            date(route_batches.created_at) BETWEEN ? AND ?
            OR date(route_batches.completed_at) BETWEEN ? AND ?
        )
          AND (? IS NULL OR route_batches.assigned_employee_id = ?)
        ORDER BY route_batches.id, route_batch_input_lots.id
        """,
        (start_date, end_date, start_date, end_date, employee_id, employee_id),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_period_production_trace_event_rows(start_date: str, end_date: str, employee_id: int | None = None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            production_trace_events.id,
            production_trace_events.created_at,
            production_trace_events.event_type,
            production_trace_events.batch_id,
            route_batches.trace_code,
            production_trace_events.production_task_id,
            production_trace_events.cutting_batch_id,
            production_trace_events.actor_employee_id,
            employees.full_name,
            production_trace_events.shift_id,
            production_trace_events.operation_name,
            production_trace_events.position,
            production_trace_events.quantity,
            production_trace_events.good_quantity,
            production_trace_events.defect_quantity,
            production_trace_events.reason,
            production_trace_events.details_json
        FROM production_trace_events
        LEFT JOIN route_batches ON route_batches.id = production_trace_events.batch_id
        LEFT JOIN employees ON employees.id = production_trace_events.actor_employee_id
        WHERE date(production_trace_events.created_at) BETWEEN ? AND ?
          AND (
              ? IS NULL
              OR production_trace_events.actor_employee_id = ?
              OR route_batches.assigned_employee_id = ?
          )
        ORDER BY production_trace_events.created_at, production_trace_events.id
        """,
        (start_date, end_date, employee_id, employee_id, employee_id),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_period_production_task_item_rows(start_date: str, end_date: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            production_tasks.id,
            production_tasks.product_name,
            production_tasks.status,
            production_tasks.created_at,
            production_tasks.completed_at,
            production_task_items.product_size,
            production_task_items.product_color,
            production_task_items.contour_quantity,
            production_task_items.formed_quantity,
            production_tasks.priority,
            production_tasks.due_date
        FROM production_tasks
        JOIN production_task_items ON production_task_items.task_id = production_tasks.id
        WHERE (
            date(production_tasks.created_at) BETWEEN ? AND ?
            OR date(production_tasks.completed_at) BETWEEN ? AND ?
        )
        ORDER BY production_tasks.created_at ASC, production_tasks.id ASC,
                 CAST(production_task_items.product_size AS INTEGER), production_task_items.product_color ASC
        """,
        (start_date, end_date, start_date, end_date),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_period_warehouse_movement_rows(start_date: str, end_date: str, employee_id: int | None = None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            warehouse_stock_movements.id,
            warehouse_stock_movements.stock_id,
            warehouse_stock_movements.created_at,
            warehouse_stock_movements.item_type,
            warehouse_stock_movements.product_name,
            warehouse_stock_movements.product_size,
            warehouse_stock_movements.product_color,
            warehouse_stock_movements.stage_name,
            warehouse_stock_movements.ready_for_position,
            warehouse_stock_movements.quantity,
            warehouse_stock_movements.unit,
            warehouse_stock_movements.movement_type,
            warehouse_stock_movements.source_type,
            warehouse_stock_movements.source_id,
            employees.full_name,
            warehouse_stock_movements.comment
        FROM warehouse_stock_movements
        LEFT JOIN employees ON employees.id = warehouse_stock_movements.created_by_employee_id
        WHERE date(warehouse_stock_movements.created_at) BETWEEN ? AND ?
          AND (? IS NULL OR warehouse_stock_movements.created_by_employee_id = ?)
        ORDER BY warehouse_stock_movements.created_at ASC, warehouse_stock_movements.id ASC
        """,
        (start_date, end_date, employee_id, employee_id),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_period_fabric_movement_rows(start_date: str, end_date: str, employee_id: int | None = None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            fabric_stock_movements.id,
            fabric_stock_movements.created_at,
            fabric_stock_movements.material_name,
            fabric_stock_movements.product_color,
            fabric_stock_movements.quantity,
            fabric_stock_movements.unit,
            fabric_stock_movements.movement_type,
            fabric_stock_movements.comment,
            employees.full_name
        FROM fabric_stock_movements
        LEFT JOIN employees ON employees.id = fabric_stock_movements.created_by_employee_id
        WHERE date(fabric_stock_movements.created_at) BETWEEN ? AND ?
          AND (? IS NULL OR fabric_stock_movements.created_by_employee_id = ?)
        ORDER BY fabric_stock_movements.created_at ASC, fabric_stock_movements.id ASC
        """,
        (start_date, end_date, employee_id, employee_id),
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
