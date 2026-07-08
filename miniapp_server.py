import hashlib
import hmac
import io
import json
import logging
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qsl, quote, urlparse

from database import (
    add_fabric_receipt,
    add_edit_log,
    add_feedback_entry,
    add_operation,
    add_shift_operation,
    admin_close_shift,
    cancel_production_task,
    cancel_route_batch,
    close_shift,
    complete_route_batch_step,
    create_cutting_contour_batch_for_task,
    create_production_task,
    create_route_batch,
    create_shift,
    delete_shift_by_id,
    ensure_admin_employee,
    get_active_operations,
    get_active_production_tasks,
    get_active_production_tasks_for_contours,
    get_active_route_batches,
    get_all_product_colors,
    get_all_employees,
    get_all_operations,
    get_employee_by_telegram_id,
    get_employee_period_operation_totals,
    get_employee_period_summary,
    get_employee_shifts_by_period,
    get_employees_by_status,
    get_feedback_entries,
    get_feedback_entries_by_shift,
    get_fabric_stock_rows,
    get_open_shifts,
    get_open_shift_for_today,
    get_pending_employees,
    get_period_employee_summary,
    get_period_operation_rows,
    get_period_shift_details,
    get_product_colors,
    get_product_sizes,
    get_recent_shifts,
    get_route_batch_by_id,
    get_production_task_by_id,
    get_shift_for_today,
    get_shift_report,
    get_today_shifts,
    hide_operation,
    local_today,
    restore_operation,
    update_employee_position,
    update_employee_status,
    update_operation_field,
)
from catalog import format_color_label
from miniapp_auth import parse_auth_token
from route_maps import CUTTING_ROUTE, PRODUCT_ROUTE_MAPS


AUTH_MAX_AGE_SECONDS = 7 * 24 * 60 * 60
ROUTES_MINIAPP_ENABLED = False
CUTTING_CONTOUR_OPERATION = "Нанесение контуров лекал на ткань"


def get_admin_ids():
    admin_ids = []
    raw_admin_ids = os.getenv("ADMIN_IDS", "").replace("ADMIN_IDS=", "")

    for raw_admin_id in raw_admin_ids.split(","):
        raw_admin_id = raw_admin_id.strip()

        if not raw_admin_id:
            continue

        try:
            admin_ids.append(int(raw_admin_id))
        except ValueError:
            logging.warning("Invalid ADMIN_IDS item ignored: %s", raw_admin_id)

    return admin_ids


def is_admin(telegram_id: int):
    return telegram_id in get_admin_ids()


def get_employee_for_access(telegram_id: int):
    if is_admin(telegram_id):
        return ensure_admin_employee(telegram_id)

    return get_employee_by_telegram_id(telegram_id)


def format_minutes(total_minutes: int | None):
    if total_minutes is None:
        return ""

    hours = total_minutes // 60
    minutes = total_minutes % 60
    return f"{hours}:{minutes:02d}"


def parse_telegram_init_data(init_data: str, bot_token: str):
    if not init_data or not bot_token:
        return None

    parsed_items = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = parsed_items.pop("hash", "")

    if not received_hash:
        return None

    data_check_string = "\n".join(
        f"{key}={value}" for key, value in sorted(parsed_items.items())
    )
    secret_key = hmac.new(
        b"WebAppData",
        bot_token.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(calculated_hash, received_hash):
        return None

    try:
        auth_date = int(parsed_items.get("auth_date", "0"))
    except ValueError:
        return None

    if auth_date <= 0 or time.time() - auth_date > AUTH_MAX_AGE_SECONDS:
        return None

    try:
        return json.loads(parsed_items.get("user", "{}"))
    except json.JSONDecodeError:
        return None


def authenticate_payload(payload: dict, bot_token: str, debug: bool):
    if debug and payload.get("telegram_id"):
        try:
            return {"id": int(payload["telegram_id"])}
        except (TypeError, ValueError):
            return None

    telegram_user = parse_telegram_init_data(payload.get("initData", ""), bot_token)

    if telegram_user:
        return telegram_user

    return parse_auth_token(payload.get("authToken", ""), bot_token)


def shift_to_dict(shift):
    if not shift:
        return None

    return {
        "id": shift[0],
        "date": shift[2],
        "start_time": shift[3],
        "end_time": shift[4],
        "status": shift[5],
    }


def employee_to_dict(employee):
    if not employee:
        return None

    return {
        "id": employee[0],
        "telegram_id": employee[1],
        "full_name": employee[2],
        "position": employee[3],
        "role": employee[4],
        "status": employee[5],
    }


def get_shift_state(telegram_id: int, message: str = ""):
    employee = get_employee_for_access(telegram_id)

    if employee is None:
        return {
            "ok": False,
            "code": "not_registered",
            "message": (
                "Вы не зарегистрированы или ваша запись не перенесена в новую базу. "
                f"Ваш Telegram ID: {telegram_id}. Вернитесь в бот и нажмите /start."
            ),
            "employee": None,
            "shift": None,
        }

    employee_data = employee_to_dict(employee)

    if employee[5] != "active":
        return {
            "ok": False,
            "code": employee[5],
            "message": "Профиль ещё не активен. Дождитесь подтверждения администратора.",
            "employee": employee_data,
            "shift": None,
        }

    open_shift = get_open_shift_for_today(employee[0])
    today_shift = open_shift or get_shift_for_today(employee[0])
    shift_data = shift_to_dict(today_shift)

    if today_shift and today_shift[5] == "closed":
        shift_data["total_minutes_text"] = ""

    return {
        "ok": True,
        "code": "ok",
        "message": message,
        "employee": employee_data,
        "shift": shift_data,
        "has_open_shift": open_shift is not None,
    }


def open_shift_for_telegram(telegram_id: int):
    employee = get_employee_for_access(telegram_id)

    if employee is None or employee[5] != "active":
        return get_shift_state(telegram_id)

    open_shift = get_open_shift_for_today(employee[0])

    if open_shift is not None:
        return get_shift_state(telegram_id, "Смена уже открыта.")

    today_shift = get_shift_for_today(employee[0])

    if today_shift is not None and today_shift[5] == "closed":
        return get_shift_state(telegram_id, "Сегодня смена уже закрыта.")

    shift = create_shift(employee[0])
    add_edit_log(
        telegram_id,
        "employee",
        "Открыл смену из миниаппа",
        "shift",
        shift["id"],
        f"Дата: {shift['shift_date']}, начало: {shift['start_time']}",
    )
    return get_shift_state(telegram_id, "Смена открыта.")


def close_shift_for_telegram(telegram_id: int):
    employee = get_employee_for_access(telegram_id)

    if employee is None or employee[5] != "active":
        return get_shift_state(telegram_id)

    open_shift = get_open_shift_for_today(employee[0])

    if open_shift is None:
        return get_shift_state(telegram_id, "У вас нет открытой смены.")

    result = close_shift(open_shift[0])

    if result is None:
        return get_shift_state(telegram_id, "Не удалось закрыть смену.")

    add_edit_log(
        telegram_id,
        "employee",
        "Закрыл смену из миниаппа",
        "shift",
        open_shift[0],
        f"Окончание: {result['end_time']}, отработано: {format_minutes(result['total_minutes'])}",
    )

    response = get_shift_state(
        telegram_id,
        f"Смена закрыта. Отработано: {format_minutes(result['total_minutes'])}.",
    )

    if response.get("shift"):
        response["shift"]["total_minutes"] = result["total_minutes"]
        response["shift"]["total_minutes_text"] = format_minutes(result["total_minutes"])

    return response


def operation_row_to_dict(row):
    operation_name, product_size, product_color, quantity, unit = row

    return {
        "operation_name": operation_name,
        "product_size": product_size,
        "product_color": format_color_label(product_color),
        "quantity": quantity,
        "unit": unit,
    }


def feedback_row_to_dict(row):
    feedback_date, feedback_time, full_name, position, category, message, shift_id = row

    return {
        "date": feedback_date,
        "time": feedback_time,
        "employee": full_name,
        "position": position,
        "category": category,
        "message": message,
        "shift_id": shift_id,
    }


def get_current_report_for_telegram(telegram_id: int):
    employee = get_employee_for_access(telegram_id)

    if employee is None or employee[5] != "active":
        return {
            "ok": False,
            "message": "Нет активного профиля.",
            "shift": None,
            "operations": [],
            "feedback": [],
        }

    shift = get_shift_for_today(employee[0])

    if shift is None:
        return {
            "ok": True,
            "message": "За сегодня отчёта пока нет.",
            "shift": None,
            "operations": [],
            "feedback": [],
        }

    return {
        "ok": True,
        "message": "",
        "shift": shift_to_dict(shift),
        "operations": [operation_row_to_dict(row) for row in get_shift_report(shift[0])],
        "feedback": [feedback_row_to_dict(row) for row in get_feedback_entries_by_shift(shift[0])],
    }


def submit_feedback_for_telegram(telegram_id: int, category: str, message: str):
    category = category.strip()
    message = message.strip()

    if category not in {"Производство", "Бытовое"}:
        return {"ok": False, "message": "Выберите раздел обратной связи."}

    if not message:
        return {"ok": False, "message": "Введите сообщение."}

    employee = get_employee_for_access(telegram_id)

    if employee is None or employee[5] != "active":
        return {"ok": False, "message": "Нет активного профиля."}

    shift = get_open_shift_for_today(employee[0]) or get_shift_for_today(employee[0])
    shift_id = shift[0] if shift else None
    feedback_id = add_feedback_entry(employee[0], shift_id, category, message)

    if feedback_id is None:
        return {"ok": False, "message": "Не удалось сохранить сообщение."}

    add_edit_log(
        telegram_id,
        "admin" if is_admin(telegram_id) else "employee",
        "Отправил обратную связь из миниаппа",
        "feedback",
        feedback_id,
        f"{category}: {message}",
    )

    return {
        "ok": True,
        "message": "Сообщение отправлено.",
        "report": get_current_report_for_telegram(telegram_id),
    }


def get_route_step(product_name: str, step_index: int):
    steps = PRODUCT_ROUTE_MAPS.get(product_name, [])

    if step_index < 0 or step_index >= len(steps):
        return None

    return steps[step_index]


def get_route_previous_status(batch: dict):
    if batch["status"] == "done":
        steps = PRODUCT_ROUTE_MAPS.get(batch["product_name"], [])
        return steps[-1]["status_after"] if steps else "Маршрут завершён"

    step_index = batch["route_step_index"]

    if step_index == 0:
        return "Партия создана"

    previous_step = get_route_step(batch["product_name"], step_index - 1)
    return previous_step["status_after"] if previous_step else "Партия в работе"


def route_batch_identity(batch: dict):
    return (
        f"{batch['product_name']} / "
        f"{batch['product_size']} / "
        f"{format_color_label(batch['product_color'])} / "
        f"{batch['quantity']} шт"
    )


def can_employee_work_route_step(employee, current_step: dict | None):
    return bool(employee and current_step and employee[3] == current_step["position"])


def route_map_to_dict(product_name: str):
    return {
        "product_name": product_name,
        "sizes": get_product_sizes(product_name),
        "colors": [format_color_label(color) for color in get_product_colors(product_name)],
        "raw_colors": get_product_colors(product_name),
        "steps": [
            {
                "number": index,
                "position": route_step["position"],
                "operation": route_step["operation"],
                "status_after": route_step["status_after"],
            }
            for index, route_step in enumerate(PRODUCT_ROUTE_MAPS[product_name], start=1)
        ],
    }


def route_task_to_dict(batch: dict, current_step: dict):
    return {
        "id": batch["id"],
        "identity": route_batch_identity(batch),
        "product_name": batch["product_name"],
        "product_size": batch["product_size"],
        "product_color": format_color_label(batch["product_color"]),
        "quantity": batch["quantity"],
        "current_status": get_route_previous_status(batch),
        "position": current_step["position"],
        "operation": current_step["operation"],
        "status_after": current_step["status_after"],
    }


def get_route_tasks_for_telegram(telegram_id: int):
    employee = get_employee_for_access(telegram_id)

    if employee is None or employee[5] != "active":
        return {"ok": False, "message": "Нет активного профиля.", "tasks": []}

    tasks = []

    for batch in get_active_route_batches():
        current_step = get_route_step(batch["product_name"], batch["route_step_index"])

        if current_step is None:
            continue

        if is_admin(telegram_id) or can_employee_work_route_step(employee, current_step):
            tasks.append(route_task_to_dict(batch, current_step))

    return {"ok": True, "tasks": tasks}


def create_route_batch_for_telegram(telegram_id: int, payload: dict):
    employee = get_employee_for_access(telegram_id)

    if employee is None or employee[5] != "active":
        return {"ok": False, "message": "Нет активного профиля."}

    product_name = (payload.get("product_name") or "").strip()
    product_size = (payload.get("product_size") or "").strip()
    product_color = (payload.get("product_color") or "").strip()

    try:
        quantity = int(payload.get("quantity") or 0)
    except (TypeError, ValueError):
        quantity = 0

    if product_name not in PRODUCT_ROUTE_MAPS:
        return {"ok": False, "message": "Выберите изделие."}

    if quantity <= 0:
        return {"ok": False, "message": "Введите количество больше 0."}

    sizes = get_product_sizes(product_name)
    colors = get_product_colors(product_name)

    if sizes and product_size not in sizes:
        return {"ok": False, "message": "Выберите размер из списка."}

    if colors and product_color not in colors:
        return {"ok": False, "message": "Выберите цвет из списка."}

    batch = create_route_batch(
        product_name,
        product_size or "без размера",
        product_color or "без цвета",
        quantity,
        employee[0],
    )

    if batch is None:
        return {"ok": False, "message": "Не удалось создать партию."}

    current_step = get_route_step(batch["product_name"], batch["route_step_index"])
    add_edit_log(
        telegram_id,
        "admin" if is_admin(telegram_id) else "employee",
        "Создал маршрутную партию из миниаппа",
        "route_batch",
        batch["id"],
        route_batch_identity(batch),
    )

    return {
        "ok": True,
        "message": f"Партия #{batch['id']} создана.",
        "batch": route_task_to_dict(batch, current_step),
        "tasks": get_route_tasks_for_telegram(telegram_id)["tasks"],
    }


def complete_route_task_for_telegram(telegram_id: int, batch_id: int):
    employee = get_employee_for_access(telegram_id)

    if employee is None or employee[5] != "active":
        return {"ok": False, "message": "Нет активного профиля."}

    batch = get_route_batch_by_id(batch_id)

    if batch is None or batch["status"] != "active":
        return {"ok": False, "message": "Эта партия уже недоступна."}

    current_step = get_route_step(batch["product_name"], batch["route_step_index"])

    if not is_admin(telegram_id) and not can_employee_work_route_step(employee, current_step):
        return {"ok": False, "message": "Это задание сейчас доступно другой должности."}

    route_steps = PRODUCT_ROUTE_MAPS[batch["product_name"]]
    next_step_index = batch["route_step_index"] + 1
    new_status = "done" if next_step_index >= len(route_steps) else "active"
    updated_batch = complete_route_batch_step(
        batch["id"],
        employee[0],
        current_step["operation"],
        current_step["position"],
        next_step_index,
        new_status,
    )

    if updated_batch is None:
        return {"ok": False, "message": "Не удалось завершить этап."}

    add_edit_log(
        telegram_id,
        "admin" if is_admin(telegram_id) else "employee",
        "Завершил этап маршрута из миниаппа",
        "route_batch",
        batch["id"],
        f"{route_batch_identity(batch)}. Этап: {current_step['operation']}",
    )

    if updated_batch["status"] == "done":
        message = f"Этап завершён. Партия #{batch['id']} полностью прошла маршрут."
    else:
        next_step = get_route_step(updated_batch["product_name"], updated_batch["route_step_index"])
        message = f"Этап завершён. Следующий этап: {next_step['position']} — {next_step['operation']}."

    return {
        "ok": True,
        "message": message,
        "tasks": get_route_tasks_for_telegram(telegram_id)["tasks"],
    }


def get_route_catalog():
    return [route_map_to_dict(product_name) for product_name in PRODUCT_ROUTE_MAPS]


def sort_size_key(value: str):
    value_text = str(value)

    if value_text.isdigit():
        return (0, int(value_text))

    return (1, value_text)


def split_group_concat(value: str | None, *, sort_sizes: bool = False):
    items = [item for item in (value or "").split(",") if item]

    if sort_sizes:
        return sorted(items, key=sort_size_key)

    return sorted(items)


def format_number(value: float):
    if float(value).is_integer():
        return str(int(value))

    return str(value).rstrip("0").rstrip(".")


def parse_positive_float(value):
    try:
        parsed = float(str(value or "").replace(",", "."))
    except (TypeError, ValueError):
        return None

    if parsed <= 0:
        return None

    return parsed


def get_order_color_options():
    colors = []

    for color in get_all_product_colors():
        if color not in colors:
            colors.append(color)

    for _material_name, product_color, _quantity, _unit, _updated_at in get_fabric_stock_rows():
        if product_color not in colors:
            colors.append(product_color)

    return colors


def production_catalog_to_dict():
    return [
        {
            "product_name": product_name,
            "sizes": get_product_sizes(product_name),
            "colors": get_product_colors(product_name),
            "color_labels": [format_color_label(color) for color in get_product_colors(product_name)],
        }
        for product_name in PRODUCT_ROUTE_MAPS
    ]


def production_task_to_dict(row):
    task_id, product_name, status, created_at, sizes_text, colors_text = row
    colors = split_group_concat(colors_text)

    return {
        "id": task_id,
        "product_name": product_name,
        "status": status,
        "status_text": {
            "active": "ожидает контуров",
            "contours_done": "контуры нанесены",
            "in_cutting": "в раскрое",
            "formed": "готовый крой сформирован",
            "cancelled": "отменено",
        }.get(status, status),
        "created_at": created_at,
        "sizes": split_group_concat(sizes_text, sort_sizes=True),
        "colors": colors,
        "color_labels": [format_color_label(color) for color in colors],
    }


def fabric_stock_to_dict(row):
    material_name, product_color, quantity, unit, updated_at = row

    return {
        "material_name": material_name,
        "product_color": product_color,
        "product_color_label": format_color_label(product_color),
        "quantity": quantity,
        "quantity_text": format_number(quantity),
        "unit": unit,
        "updated_at": updated_at,
    }


def get_cutting_contour_operation(product_name: str):
    operations = get_active_operations("Раскройщик", product_name, "Раскрой изделий")

    for operation_id, _number, name, unit in operations:
        if name == CUTTING_CONTOUR_OPERATION:
            return {
                "id": operation_id,
                "name": f"{product_name}: {name}",
                "unit": unit,
            }

    return None


def get_production_state_for_telegram(telegram_id: int):
    employee = get_employee_for_access(telegram_id)
    is_admin_user = is_admin(telegram_id)
    can_work_contours = bool(employee and employee[5] == "active" and employee[3] == "Раскройщик")

    return {
        "catalog": production_catalog_to_dict(),
        "order_colors": get_order_color_options(),
        "order_color_labels": [format_color_label(color) for color in get_order_color_options()],
        "fabric_stock": [fabric_stock_to_dict(row) for row in get_fabric_stock_rows()] if is_admin_user else [],
        "tasks": [production_task_to_dict(row) for row in get_active_production_tasks()] if is_admin_user else [],
        "contour_tasks": [
            production_task_to_dict(row)
            for row in get_active_production_tasks_for_contours()
        ] if can_work_contours else [],
        "can_admin": is_admin_user,
        "can_contours": can_work_contours,
    }


def add_fabric_receipt_for_telegram(telegram_id: int, payload: dict):
    if not is_admin(telegram_id):
        return {"ok": False, "message": "Нет прав администратора."}

    material_name = (payload.get("material_name") or "").strip()
    product_color = (payload.get("product_color") or "").strip()
    quantity = parse_positive_float(payload.get("quantity"))

    if not material_name:
        return {"ok": False, "message": "Введите материал."}

    if not product_color:
        return {"ok": False, "message": "Выберите цвет."}

    if quantity is None:
        return {"ok": False, "message": "Введите количество больше 0."}

    employee = get_employee_for_access(telegram_id)
    row = add_fabric_receipt(
        material_name,
        product_color,
        quantity,
        employee[0] if employee else None,
    )

    if row is None:
        return {"ok": False, "message": "Не удалось сохранить приход ткани."}

    stock_id, stock_material, stock_color, total_quantity, unit, _updated_at = row
    add_edit_log(
        telegram_id,
        "admin",
        "Добавил приход ткани из миниаппа",
        "fabric_stock",
        stock_id,
        f"{stock_material}, {stock_color}: +{format_number(quantity)} {unit}, остаток {format_number(total_quantity)} {unit}",
    )

    return {
        "ok": True,
        "message": "Приход ткани сохранён.",
        "production": get_production_state_for_telegram(telegram_id),
    }


def create_production_task_for_telegram(telegram_id: int, payload: dict):
    if not is_admin(telegram_id):
        return {"ok": False, "message": "Нет прав администратора."}

    product_name = (payload.get("product_name") or "").strip()
    sizes = [str(size).strip() for size in payload.get("sizes", []) if str(size).strip()]
    colors = [str(color).strip() for color in payload.get("colors", []) if str(color).strip()]

    if product_name not in PRODUCT_ROUTE_MAPS:
        return {"ok": False, "message": "Выберите изделие."}

    allowed_sizes = set(get_product_sizes(product_name))
    allowed_colors = set(get_order_color_options())

    if not sizes or any(size not in allowed_sizes for size in sizes):
        return {"ok": False, "message": "Выберите размеры из списка."}

    if not colors or any(color not in allowed_colors for color in colors):
        return {"ok": False, "message": "Выберите цвета из списка."}

    employee = get_employee_for_access(telegram_id)
    task = create_production_task(
        product_name,
        sizes,
        colors,
        employee[0] if employee else None,
    )

    if task is None:
        return {"ok": False, "message": "Не удалось создать задание."}

    add_edit_log(
        telegram_id,
        "admin",
        "Создал производственное задание из миниаппа",
        "production_task",
        task["id"],
        f"{task['product_name']}; размеры: {', '.join(sizes)}; цвета: {', '.join(colors)}",
    )

    return {
        "ok": True,
        "message": f"Задание #{task['id']} создано.",
        "production": get_production_state_for_telegram(telegram_id),
    }


def create_order_task_for_telegram(telegram_id: int, payload: dict):
    if not is_admin(telegram_id):
        return {"ok": False, "message": "Нет прав администратора."}

    product_name = (payload.get("product_name") or "").strip()
    task_type = (payload.get("task_type") or "cutting").strip()
    material_name = (payload.get("material_name") or "").strip()
    sizes = [str(size).strip() for size in payload.get("sizes", []) if str(size).strip()]
    colors = [str(color).strip() for color in payload.get("colors", []) if str(color).strip()]

    if product_name not in PRODUCT_ROUTE_MAPS:
        return {"ok": False, "message": "Выберите изделие."}

    if task_type not in {"cutting", "route"}:
        return {"ok": False, "message": "Выберите тип задания."}

    allowed_sizes = set(get_product_sizes(product_name))
    allowed_colors = set(get_order_color_options())

    if not sizes or any(size not in allowed_sizes for size in sizes):
        return {"ok": False, "message": "Выберите размеры из списка."}

    if not colors or any(color not in allowed_colors for color in colors):
        return {"ok": False, "message": "Выберите цвета из списка."}

    employee = get_employee_for_access(telegram_id)
    employee_id = employee[0] if employee else None

    if task_type == "cutting":
        material_name = material_name or "Ткань"

        if material_name != "Ткань":
            return {"ok": False, "message": "Пока для раскроя доступен только материал: Ткань."}

        task = create_production_task(
            product_name,
            sizes,
            colors,
            employee_id,
            f"Материал: {material_name}",
        )

        if task is None:
            return {"ok": False, "message": "Не удалось создать задание на раскрой."}

        add_edit_log(
            telegram_id,
            "admin",
            "Создал задание на раскрой из миниаппа",
            "production_task",
            task["id"],
            f"{task['product_name']}; материал: {material_name}; размеры: {', '.join(sizes)}; цвета: {', '.join(colors)}",
        )

        return {
            "ok": True,
            "message": f"Задание на раскрой #{task['id']} создано.",
            "production": get_production_state_for_telegram(telegram_id),
            "routes": {
                "enabled": ROUTES_MINIAPP_ENABLED,
                "catalog": get_route_catalog(),
                "tasks": get_route_tasks_for_telegram(telegram_id).get("tasks", []),
            },
        }

    try:
        route_step_index = int(payload.get("route_step_index"))
    except (TypeError, ValueError):
        route_step_index = -1

    route_step = get_route_step(product_name, route_step_index)

    if route_step is None:
        return {"ok": False, "message": "Выберите операцию маршрута."}

    if route_step_index < len(CUTTING_ROUTE):
        return {"ok": False, "message": "Для раскроя используйте тип задания «Раскрой»."}

    try:
        quantity = int(payload.get("quantity") or 0)
    except (TypeError, ValueError):
        quantity = 0

    if quantity <= 0:
        return {"ok": False, "message": "Введите количество больше 0."}

    created_batches = []

    for product_size in sizes:
        for product_color in colors:
            batch = create_route_batch(
                product_name,
                product_size,
                product_color,
                quantity,
                employee_id,
                route_step_index=route_step_index,
            )

            if batch is not None:
                created_batches.append(batch)

    if not created_batches:
        return {"ok": False, "message": "Не удалось создать маршрутные задания."}

    add_edit_log(
        telegram_id,
        "admin",
        "Создал маршрутные задания из миниаппа",
        "route_batch",
        created_batches[0]["id"],
        (
            f"{product_name}; {route_step['position']} — {route_step['operation']}; "
            f"вход: полуфабрикат; размеры: {', '.join(sizes)}; цвета: {', '.join(colors)}; "
            f"количество на комбинацию: {quantity}; партий: {len(created_batches)}"
        ),
    )

    return {
        "ok": True,
        "message": f"Создано маршрутных заданий: {len(created_batches)}.",
        "production": get_production_state_for_telegram(telegram_id),
        "routes": {
            "enabled": ROUTES_MINIAPP_ENABLED,
            "catalog": get_route_catalog(),
            "tasks": get_route_tasks_for_telegram(telegram_id).get("tasks", []),
        },
    }


def delete_order_task_for_telegram(telegram_id: int, payload: dict):
    if not is_admin(telegram_id):
        return {"ok": False, "message": "Нет прав администратора."}

    task_kind = (payload.get("task_kind") or "").strip()

    try:
        task_id = int(payload.get("task_id") or 0)
    except (TypeError, ValueError):
        task_id = 0

    if task_id <= 0:
        return {"ok": False, "message": "Выберите задание."}

    if task_kind == "production":
        task = get_production_task_by_id(task_id)

        if task is None:
            return {"ok": False, "message": "Задание не найдено."}

        cancelled_task = cancel_production_task(task_id)

        if cancelled_task is None:
            return {"ok": False, "message": "Это задание уже нельзя удалить."}

        add_edit_log(
            telegram_id,
            "admin",
            "Удалил производственное задание из миниаппа",
            "production_task",
            task_id,
            f"{task['product_name']}; прежний статус: {task['status']}",
        )
        message = f"Задание #{task_id} удалено."
    elif task_kind == "route":
        batch = get_route_batch_by_id(task_id)

        if batch is None:
            return {"ok": False, "message": "Маршрутное задание не найдено."}

        cancelled_batch = cancel_route_batch(task_id)

        if cancelled_batch is None:
            return {"ok": False, "message": "Это маршрутное задание уже нельзя удалить."}

        add_edit_log(
            telegram_id,
            "admin",
            "Удалил маршрутное задание из миниаппа",
            "route_batch",
            task_id,
            route_batch_identity(batch),
        )
        message = f"Маршрутное задание #{task_id} удалено."
    else:
        return {"ok": False, "message": "Неизвестный тип задания."}

    return {
        "ok": True,
        "message": message,
        "production": get_production_state_for_telegram(telegram_id),
        "routes": {
            "enabled": ROUTES_MINIAPP_ENABLED,
            "catalog": get_route_catalog(),
            "tasks": get_route_tasks_for_telegram(telegram_id).get("tasks", []),
        },
    }


def submit_production_contours_for_telegram(telegram_id: int, payload: dict):
    employee = get_employee_for_access(telegram_id)

    if employee is None or employee[5] != "active":
        return {"ok": False, "message": "Нет активного профиля."}

    if employee[3] != "Раскройщик" and not is_admin(telegram_id):
        return {"ok": False, "message": "Задания на раскрой доступны раскройщику."}

    shift = get_open_shift_for_today(employee[0])

    if shift is None:
        return {"ok": False, "message": "Откройте смену перед выполнением задания."}

    try:
        task_id = int(payload.get("task_id") or 0)
    except (TypeError, ValueError):
        task_id = 0

    task_rows = [row for row in get_active_production_tasks_for_contours() if row[0] == task_id]

    if not task_rows:
        return {"ok": False, "message": "Задание уже недоступно."}

    task = production_task_to_dict(task_rows[0])
    operation = get_cutting_contour_operation(task["product_name"])

    if operation is None:
        return {"ok": False, "message": "Для изделия не найдена операция контуров."}

    raw_quantities = payload.get("quantities") or {}
    matrix_quantities = {}

    for color in task["colors"]:
        for product_size in task["sizes"]:
            key = f"{product_size}|{color}"
            try:
                quantity = int(raw_quantities.get(key) or 0)
            except (TypeError, ValueError):
                return {"ok": False, "message": "Количество должно быть целым числом."}

            if quantity < 0:
                return {"ok": False, "message": "Количество не может быть отрицательным."}

            matrix_quantities[(product_size, color)] = quantity

    positive_rows = [
        (product_size, color, quantity)
        for (product_size, color), quantity in matrix_quantities.items()
        if quantity > 0
    ]

    if not positive_rows:
        return {"ok": False, "message": "Укажите количество хотя бы в одной строке."}

    batch_id = create_cutting_contour_batch_for_task(
        task_id,
        task["product_name"],
        shift[0],
        employee[0],
        operation["id"],
        matrix_quantities,
    )

    if batch_id is None:
        return {"ok": False, "message": "Не удалось создать партию раскроя."}

    for product_size, color, quantity in positive_rows:
        add_shift_operation(
            shift[0],
            employee[0],
            operation["id"],
            product_size,
            color,
            quantity,
        )

    add_edit_log(
        telegram_id,
        "employee",
        "Выполнил контуры по производственному заданию из миниаппа",
        "production_task",
        task_id,
        f"Партия раскроя {batch_id}, строк добавлено: {len(positive_rows)}",
    )

    return {
        "ok": True,
        "message": f"Контуры сохранены. Партия раскроя #{batch_id}.",
        "production": get_production_state_for_telegram(telegram_id),
    }


ADMIN_MENU = [
    {
        "id": "requests",
        "title": "Заявки",
        "buttons": ["Заявки"],
    },
    {
        "id": "reports",
        "title": "Отчёты",
        "buttons": [
            "Отчёт за сегодня",
            "Отчёт за период",
            "Отчёт по сотруднику",
            "Править отчёт",
        ],
    },
    {
        "id": "shifts",
        "title": "Смены",
        "buttons": ["Открытые смены", "Последние смены", "Удалить смену"],
    },
    {
        "id": "employees",
        "title": "Сотрудники",
        "buttons": [
            "Список сотрудников",
            "Активные сотрудники",
            "Неактивные сотрудники",
            "Активировать сотрудника",
            "Отключить сотрудника",
            "Сменить должность",
        ],
    },
    {
        "id": "operations",
        "title": "Операции",
        "buttons": [
            "Список операций",
            "Добавить операцию",
            "Изменить операцию",
            "Скрыть операцию",
            "Вернуть операцию",
        ],
    },
]

POSITIONS = ["Швея", "Упаковщик", "Раскройщик", "Ремонт"]


def clean_date(value: str | None, fallback: str):
    value = (value or "").strip()

    if len(value) == 10 and value[4] == "-" and value[7] == "-":
        return value

    return fallback


def month_bounds():
    today = local_today()
    return today.replace(day=1).isoformat(), today.isoformat()


def quarter_bounds():
    today = local_today()
    quarter_start_month = ((today.month - 1) // 3) * 3 + 1
    return today.replace(month=quarter_start_month, day=1).isoformat(), today.isoformat()


def employee_admin_to_dict(employee):
    employee_id, full_name, position, telegram_id_value, employee_status = employee

    return {
        "id": employee_id,
        "full_name": full_name,
        "position": position or "-",
        "telegram_id": telegram_id_value,
        "status": employee_status,
    }


def pending_employee_to_dict(employee):
    employee_id, full_name, position, telegram_id_value, registered_at = employee

    return {
        "id": employee_id,
        "full_name": full_name,
        "position": position or "-",
        "telegram_id": telegram_id_value,
        "registered_at": registered_at,
    }


def open_shift_to_dict(shift):
    shift_id, full_name, shift_date, start_time = shift

    return {
        "id": shift_id,
        "employee": full_name,
        "date": shift_date,
        "start_time": start_time,
    }


def recent_shift_to_dict(shift):
    shift_id, full_name, shift_date, start_time, end_time, shift_status, operation_count = shift

    return {
        "id": shift_id,
        "employee": full_name,
        "date": shift_date,
        "start_time": start_time,
        "end_time": end_time,
        "status": shift_status,
        "operation_count": operation_count,
    }


def shift_detail_to_dict(row):
    if len(row) == 7:
        shift_id, full_name, shift_date, start_time, end_time, total_minutes, shift_status = row
    else:
        shift_id = None
        shift_date, full_name, start_time, end_time, total_minutes, shift_status = row

    return {
        "id": shift_id,
        "date": shift_date,
        "employee": full_name,
        "start_time": start_time,
        "end_time": end_time,
        "total_minutes": total_minutes,
        "total_time": format_minutes(total_minutes or 0),
        "status": shift_status,
    }


def employee_shift_to_dict(row):
    shift_id, shift_date, start_time, end_time, total_minutes, shift_status = row

    return {
        "id": shift_id,
        "date": shift_date,
        "start_time": start_time,
        "end_time": end_time,
        "total_minutes": total_minutes,
        "total_time": format_minutes(total_minutes or 0),
        "status": shift_status,
    }


def employee_summary_to_dict(row):
    employee_id, full_name, shift_count, total_minutes = row[:4]

    return {
        "employee_id": employee_id,
        "full_name": full_name,
        "shift_count": shift_count,
        "total_minutes": total_minutes,
        "total_time": format_minutes(total_minutes or 0),
    }


def operation_summary_to_dict(row):
    (
        shift_date,
        full_name,
        work_group,
        operation_name,
        product_size,
        product_color,
        total_quantity,
        unit,
    ) = row

    return {
        "date": shift_date,
        "employee": full_name,
        "group": work_group,
        "operation": operation_name,
        "size": product_size,
        "color": format_color_label(product_color),
        "quantity": total_quantity,
        "unit": unit,
    }


def minutes_to_excel_time(total_minutes):
    if total_minutes is None:
        return ""

    hours = total_minutes // 60
    minutes = total_minutes % 60
    return f"{hours}:{minutes:02d}"


def style_excel_sheet(sheet):
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    header_fill = PatternFill("solid", fgColor="F1E1D6")
    header_font = Font(bold=True)

    if sheet.max_row == 0:
        return

    for cell in sheet[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")

    for column_cells in sheet.columns:
        max_length = 0
        column_letter = get_column_letter(column_cells[0].column)

        for cell in column_cells:
            value = "" if cell.value is None else str(cell.value)
            max_length = max(max_length, len(value))

        sheet.column_dimensions[column_letter].width = min(max_length + 3, 45)

    sheet.freeze_panes = "A2"

    if not sheet.auto_filter.ref:
        sheet.auto_filter.ref = sheet.dimensions


def append_excel_total_row(sheet, label: str, value, label_column: int = 1, value_column: int = 2):
    from openpyxl.styles import Font, PatternFill

    row_number = sheet.max_row + 1
    sheet.cell(row=row_number, column=label_column, value=label)
    sheet.cell(row=row_number, column=value_column, value=value)

    for cell in sheet[row_number]:
        cell.font = Font(bold=True)
        cell.fill = PatternFill("solid", fgColor="EEF6EE")


def set_excel_filter_range(sheet, last_data_row: int | None = None):
    from openpyxl.utils import get_column_letter

    if sheet.max_row == 0 or sheet.max_column == 0:
        return

    end_row = last_data_row if last_data_row is not None else sheet.max_row
    end_column = get_column_letter(sheet.max_column)
    sheet.auto_filter.ref = f"A1:{end_column}{max(1, end_row)}"


def append_excel_filtered_total_row(sheet, label: str, label_column: int, value_column: int):
    from openpyxl.utils import get_column_letter

    last_data_row = sheet.max_row

    if last_data_row < 2:
        value = 0
    else:
        value_letter = get_column_letter(value_column)
        value = f"=SUBTOTAL(109,{value_letter}2:{value_letter}{last_data_row})"

    append_excel_total_row(sheet, label, value, label_column=label_column, value_column=value_column)
    set_excel_filter_range(sheet, last_data_row=last_data_row)


def append_excel_operation_rows(sheet, operation_rows):
    sheet.append(["Дата", "Сотрудник", "Группа", "Операция", "Размер", "Цвет", "Количество", "Ед."])

    for row in operation_rows:
        shift_date, full_name, work_group, operation_name, product_size, product_color, quantity, unit = row
        sheet.append([
            shift_date,
            full_name,
            work_group,
            operation_name,
            product_size,
            format_color_label(product_color),
            quantity,
            unit,
        ])

    append_excel_filtered_total_row(sheet, "Итого по фильтру", label_column=6, value_column=7)


def append_excel_feedback_rows(sheet, feedback_rows):
    sheet.append(["Дата", "Время", "Сотрудник", "Должность", "Раздел", "Сообщение", "ID смены"])

    for row in feedback_rows:
        feedback_date, feedback_time, full_name, position, category, message_text, shift_id = row
        sheet.append([
            feedback_date,
            feedback_time,
            full_name,
            position,
            category,
            message_text,
            shift_id or "",
        ])


def append_excel_shift_rows(sheet, shift_rows, employee_name: str | None = None):
    sheet.append(["Дата", "Сотрудник", "Пришёл", "Ушёл", "Отработано", "Статус"])

    for row in shift_rows:
        if employee_name is None:
            shift_date, full_name, start_time, end_time, total_minutes, status = row[-6:]
        else:
            _, shift_date, start_time, end_time, total_minutes, status = row
            full_name = employee_name

        status_text = "Закрыта" if status == "closed" else "Открыта"
        sheet.append([
            shift_date,
            full_name,
            start_time,
            end_time or "",
            minutes_to_excel_time(total_minutes),
            status_text,
        ])


def workbook_to_bytes(workbook):
    output = io.BytesIO()
    workbook.save(output)
    output.seek(0)
    return output.getvalue()


def create_period_excel_bytes(start_date: str, end_date: str):
    from openpyxl import Workbook

    employee_summary = get_period_employee_summary(start_date, end_date)
    operation_rows = get_period_operation_rows(start_date, end_date)
    shift_rows = get_period_shift_details(start_date, end_date)
    feedback_rows = get_feedback_entries(start_date, end_date)

    workbook = Workbook()

    summary_sheet = workbook.active
    summary_sheet.title = "Сводка"
    summary_sheet.append(["Сотрудник", "Смен", "Часы"])
    total_shifts = 0
    total_minutes = 0

    for employee_id, full_name, shift_count, employee_minutes in employee_summary:
        total_shifts += shift_count or 0
        total_minutes += employee_minutes or 0
        summary_sheet.append([full_name, shift_count, minutes_to_excel_time(employee_minutes)])

    append_excel_total_row(summary_sheet, "Итого", total_shifts, label_column=1, value_column=2)
    summary_sheet.cell(row=summary_sheet.max_row, column=3, value=minutes_to_excel_time(total_minutes))

    shifts_sheet = workbook.create_sheet("Смены по дням", 1)
    append_excel_shift_rows(shifts_sheet, shift_rows)

    operations_sheet = workbook.create_sheet("Операции")
    append_excel_operation_rows(operations_sheet, operation_rows)

    feedback_sheet = workbook.create_sheet("Обратная связь")
    append_excel_feedback_rows(feedback_sheet, feedback_rows)

    for sheet in workbook.worksheets:
        style_excel_sheet(sheet)

    return workbook_to_bytes(workbook)


def create_employee_excel_bytes(employee_id: int, start_date: str, end_date: str):
    from openpyxl import Workbook

    employee_summary = get_employee_period_summary(employee_id, start_date, end_date)

    if employee_summary is None:
        return None, None

    _, full_name, position, shift_count, total_minutes = employee_summary
    operations = get_employee_period_operation_totals(employee_id, start_date, end_date)
    shift_rows = get_employee_shifts_by_period(employee_id, start_date, end_date)
    feedback_rows = get_feedback_entries(start_date, end_date, employee_id=employee_id)

    workbook = Workbook()

    summary_sheet = workbook.active
    summary_sheet.title = "Итог"
    summary_sheet.append(["Показатель", "Значение"])
    summary_sheet.append(["Сотрудник", full_name])
    summary_sheet.append(["Должность", position or ""])
    summary_sheet.append(["Период", f"{start_date} — {end_date}"])
    summary_sheet.append(["Отработано смен", shift_count])
    summary_sheet.append(["Отработано часов", minutes_to_excel_time(total_minutes)])

    shifts_sheet = workbook.create_sheet("Смены по дням", 1)
    append_excel_shift_rows(shifts_sheet, shift_rows, employee_name=full_name)

    operations_sheet = workbook.create_sheet("Операции")
    operations_sheet.append(["Операция", "Количество", "Ед."])

    for operation_name, quantity, unit in operations:
        operations_sheet.append([operation_name, quantity, unit])

    append_excel_filtered_total_row(operations_sheet, "Итого по фильтру", label_column=1, value_column=2)

    feedback_sheet = workbook.create_sheet("Обратная связь")
    append_excel_feedback_rows(feedback_sheet, feedback_rows)

    for sheet in workbook.worksheets:
        style_excel_sheet(sheet)

    return workbook_to_bytes(workbook), full_name


def employee_operation_total_to_dict(row):
    operation_name, total_quantity, unit = row

    return {
        "operation": operation_name,
        "quantity": total_quantity,
        "unit": unit,
    }


def operation_admin_to_dict(row):
    operation_id, number, name, position, operation_group, folder, unit, is_active = row

    return {
        "id": operation_id,
        "number": number,
        "name": name,
        "position": position or "-",
        "group": operation_group or "-",
        "folder": folder or "-",
        "unit": unit or "шт",
        "active": bool(is_active),
    }


def quantity_as_float(value):
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def quantity_text(value):
    return format_number(quantity_as_float(value))


def get_admin_home_period_payload(
    period_id: str,
    title: str,
    start_date: str,
    end_date: str,
    employees: list[dict],
    open_shifts: list[dict],
):
    report = get_admin_report_payload("period", start_date, end_date)
    employee_by_name = {employee["full_name"]: employee for employee in employees}
    rows_by_name = {}

    def ensure_employee(full_name: str):
        employee = employee_by_name.get(full_name, {})
        if full_name not in rows_by_name:
            rows_by_name[full_name] = {
                "name": full_name,
                "position": employee.get("position") or "-",
                "plan": 0,
                "plan_text": "0",
                "fact": 0,
                "fact_text": "0",
                "shift_count": 0,
                "on_shift": False,
                "status": "",
                "operations": [],
            }
        return rows_by_name[full_name]

    for shift in report.get("shifts", []):
        employee = ensure_employee(shift.get("employee") or "Сотрудник")
        employee["shift_count"] += 1
        if shift.get("status") == "open":
            employee["on_shift"] = True
        employee["status"] = shift.get("status") or employee["status"]

    if period_id == "today":
        for shift in open_shifts:
            employee = ensure_employee(shift.get("employee") or "Сотрудник")
            employee["on_shift"] = True
            employee["status"] = "open"
            employee["start_time"] = shift.get("start_time") or ""
            employee["date"] = shift.get("date") or start_date

    fact_total = 0.0

    for operation in report.get("operations", []):
        employee = ensure_employee(operation.get("employee") or "Сотрудник")
        operation_quantity = quantity_as_float(operation.get("quantity"))
        fact_total += operation_quantity
        employee["fact"] += operation_quantity
        employee["operations"].append(
            {
                "operation": operation.get("operation") or "-",
                "stage": operation.get("group") or "-",
                "date": operation.get("date") or "",
                "size": operation.get("size") or "-",
                "color": operation.get("color") or "-",
                "quantity": operation_quantity,
                "quantity_text": quantity_text(operation_quantity),
                "unit": operation.get("unit") or "шт",
            }
        )

    for employee in rows_by_name.values():
        employee["fact_text"] = quantity_text(employee["fact"])
        employee["operations"].sort(key=lambda row: (row["date"], row["operation"], row["size"], row["color"]))

    employee_rows = sorted(
        rows_by_name.values(),
        key=lambda row: (not row["on_shift"], -row["fact"], row["name"]),
    )

    return {
        "id": period_id,
        "title": title,
        "start_date": start_date,
        "end_date": end_date,
        "plan": 0,
        "plan_text": "0",
        "fact": fact_total,
        "fact_text": quantity_text(fact_total),
        "defect_count": 0,
        "employees": employee_rows,
        "defects": [],
        "defect_fields": ["Изделие", "Этап", "Причина"],
    }


def get_admin_home_payload(employees: list[dict], open_shifts: list[dict]):
    today = local_today().isoformat()
    month_start, month_end = month_bounds()
    quarter_start, quarter_end = quarter_bounds()

    return {
        "periods": {
            "today": get_admin_home_period_payload(
                "today",
                "Сегодня",
                today,
                today,
                employees,
                open_shifts,
            ),
            "month": get_admin_home_period_payload(
                "month",
                "Текущий месяц",
                month_start,
                month_end,
                employees,
                open_shifts,
            ),
            "quarter": get_admin_home_period_payload(
                "quarter",
                "Текущий квартал",
                quarter_start,
                quarter_end,
                employees,
                open_shifts,
            ),
        }
    }


def get_admin_dashboard(telegram_id: int):
    if not is_admin(telegram_id):
        return {"ok": False, "message": "Нет прав администратора."}

    employees = get_all_employees()
    employee_rows = [employee_admin_to_dict(employee) for employee in employees]
    open_shift_rows = [open_shift_to_dict(shift) for shift in get_open_shifts()]
    month_start, today = month_bounds()

    return {
        "ok": True,
        "menu": ADMIN_MENU,
        "positions": POSITIONS,
        "period_defaults": {"start_date": month_start, "end_date": today},
        "employees": employee_rows,
        "active_employees": [
            employee_admin_to_dict(employee) for employee in get_employees_by_status("active")
        ],
        "inactive_employees": [
            employee_admin_to_dict(employee) for employee in get_employees_by_status("inactive")
        ],
        "pending_employees": [
            pending_employee_to_dict(employee) for employee in get_pending_employees()
        ],
        "open_shifts": open_shift_rows,
        "recent_shifts": [recent_shift_to_dict(shift) for shift in get_recent_shifts(20)],
        "operations": [
            operation_admin_to_dict(operation) for operation in get_all_operations()
        ],
        "reports": get_admin_report_payload("period", month_start, today),
        "home": get_admin_home_payload(employee_rows, open_shift_rows),
        "feedback": [
            feedback_row_to_dict(row)
            for row in get_feedback_entries(month_start, today)
        ],
    }


def get_admin_report_payload(
    report_type: str,
    start_date: str,
    end_date: str,
    employee_id: int | None = None,
):
    if report_type == "today":
        today = local_today().isoformat()
        return {
            "type": "today",
            "title": f"Отчёт за сегодня: {today}",
            "start_date": today,
            "end_date": today,
            "summary": [employee_summary_to_dict(row) for row in get_period_employee_summary(today, today)],
            "shifts": [shift_detail_to_dict(row) for row in get_today_shifts()],
            "operations": [operation_summary_to_dict(row) for row in get_period_operation_rows(today, today)],
        }

    if report_type == "employee" and employee_id:
        summary = get_employee_period_summary(employee_id, start_date, end_date)
        return {
            "type": "employee",
            "title": f"Отчёт по сотруднику: {start_date} — {end_date}",
            "start_date": start_date,
            "end_date": end_date,
            "employee_summary": (
                {
                    "employee_id": summary[0],
                    "full_name": summary[1],
                    "position": summary[2],
                    "shift_count": summary[3],
                    "total_minutes": summary[4],
                    "total_time": format_minutes(summary[4] or 0),
                }
                if summary
                else None
            ),
            "employee_shifts": [
                {
                    "id": row[0],
                    "date": row[1],
                    "start_time": row[2],
                    "end_time": row[3],
                    "total_minutes": row[4],
                    "total_time": format_minutes(row[4] or 0),
                    "status": row[5],
                }
                for row in get_employee_shifts_by_period(employee_id, start_date, end_date)
            ],
            "employee_operations": [
                employee_operation_total_to_dict(row)
                for row in get_employee_period_operation_totals(employee_id, start_date, end_date)
            ],
        }

    title = f"Отчёт за период: {start_date} — {end_date}"
    summary_rows = get_period_employee_summary(start_date, end_date)
    operation_rows = get_period_operation_rows(start_date, end_date)
    shift_rows = get_period_shift_details(start_date, end_date)

    return {
        "type": "period",
        "title": title,
        "start_date": start_date,
        "end_date": end_date,
        "summary": [employee_summary_to_dict(row) for row in summary_rows],
        "shifts": [shift_detail_to_dict(row) for row in shift_rows],
        "operations": [operation_summary_to_dict(row) for row in operation_rows],
    }


def get_admin_report_for_telegram(telegram_id: int, payload: dict):
    if not is_admin(telegram_id):
        return {"ok": False, "message": "Нет прав администратора."}

    month_start, today = month_bounds()
    report_type = (payload.get("report_type") or "period").strip()
    start_date = clean_date(payload.get("start_date"), month_start)
    end_date = clean_date(payload.get("end_date"), today)

    try:
        employee_id = int(payload.get("employee_id") or 0)
    except (TypeError, ValueError):
        employee_id = 0

    return {
        "ok": True,
        "report": get_admin_report_payload(
            report_type,
            start_date,
            end_date,
            employee_id or None,
        ),
    }


def get_employee_history_for_telegram(telegram_id: int, payload: dict):
    month_start, today = month_bounds()
    start_date = clean_date(payload.get("start_date"), month_start)
    end_date = clean_date(payload.get("end_date"), today)
    employee = get_employee_for_access(telegram_id)

    if employee is None or employee[5] != "active":
        return {
            "ok": False,
            "message": "Нет активного профиля.",
            "start_date": start_date,
            "end_date": end_date,
            "summary": None,
            "shifts": [],
            "operations": [],
        }

    summary = get_employee_period_summary(employee[0], start_date, end_date)

    return {
        "ok": True,
        "message": "",
        "start_date": start_date,
        "end_date": end_date,
        "summary": (
            {
                "employee_id": summary[0],
                "full_name": summary[1],
                "position": summary[2],
                "shift_count": summary[3],
                "total_minutes": summary[4],
                "total_time": format_minutes(summary[4] or 0),
            }
            if summary
            else None
        ),
        "shifts": [
            employee_shift_to_dict(row)
            for row in get_employee_shifts_by_period(employee[0], start_date, end_date)
        ],
        "operations": [
            employee_operation_total_to_dict(row)
            for row in get_employee_period_operation_totals(employee[0], start_date, end_date)
        ],
    }


def get_admin_feedback_for_telegram(telegram_id: int, payload: dict):
    if not is_admin(telegram_id):
        return {"ok": False, "message": "Нет прав администратора.", "feedback": []}

    month_start, today = month_bounds()
    start_date = clean_date(payload.get("start_date"), month_start)
    end_date = clean_date(payload.get("end_date"), today)

    return {
        "ok": True,
        "start_date": start_date,
        "end_date": end_date,
        "feedback": [
            feedback_row_to_dict(row)
            for row in get_feedback_entries(start_date, end_date)
        ],
    }


def export_admin_report_for_telegram(telegram_id: int, payload: dict):
    if not is_admin(telegram_id):
        return {"ok": False, "message": "Нет прав администратора."}

    month_start, today = month_bounds()
    report_type = (payload.get("report_type") or "period").strip()
    start_date = clean_date(payload.get("start_date"), month_start)
    end_date = clean_date(payload.get("end_date"), today)

    try:
        employee_id = int(payload.get("employee_id") or 0)
    except (TypeError, ValueError):
        employee_id = 0

    if report_type == "today":
        start_date = today
        end_date = today
        content = create_period_excel_bytes(start_date, end_date)
        filename = f"report_today_{today}.xlsx"
    elif report_type == "employee":
        if employee_id <= 0:
            return {"ok": False, "message": "Выберите сотрудника для выгрузки."}

        content, employee_name = create_employee_excel_bytes(employee_id, start_date, end_date)

        if content is None:
            return {"ok": False, "message": "Сотрудник не найден."}

        safe_name = "".join(
            char if char.isalnum() or char in {"_", "-"} else "_"
            for char in employee_name
        ).strip("_")
        filename = f"employee_{employee_id}_{safe_name}_{start_date}_{end_date}.xlsx"
    else:
        content = create_period_excel_bytes(start_date, end_date)
        filename = f"report_{start_date}_{end_date}.xlsx"

    add_edit_log(
        telegram_id,
        "admin",
        "Выгрузил отчёт из миниаппа",
        "report",
        None,
        f"{report_type}: {start_date} — {end_date}",
    )

    return {
        "ok": True,
        "filename": filename,
        "content": content,
    }


def set_employee_status_for_admin(telegram_id: int, payload: dict):
    if not is_admin(telegram_id):
        return {"ok": False, "message": "Нет прав администратора."}

    try:
        employee_id = int(payload.get("employee_id") or 0)
    except (TypeError, ValueError):
        employee_id = 0

    status = (payload.get("status") or "").strip()

    if status not in {"active", "inactive", "pending"}:
        return {"ok": False, "message": "Некорректный статус."}

    employee = update_employee_status(employee_id, status)

    if employee is None:
        return {"ok": False, "message": "Сотрудник не найден."}

    add_edit_log(
        telegram_id,
        "admin",
        f"Изменил статус сотрудника на {status} из миниаппа",
        "employee",
        employee_id,
        employee[2],
    )
    dashboard = get_admin_dashboard(telegram_id)
    dashboard["message"] = "Статус сотрудника изменён."
    return dashboard


def set_employee_position_for_admin(telegram_id: int, payload: dict):
    if not is_admin(telegram_id):
        return {"ok": False, "message": "Нет прав администратора."}

    try:
        employee_id = int(payload.get("employee_id") or 0)
    except (TypeError, ValueError):
        employee_id = 0

    position = (payload.get("position") or "").strip()

    if position not in POSITIONS:
        return {"ok": False, "message": "Выберите должность из списка."}

    employee = update_employee_position(employee_id, position)

    if employee is None:
        return {"ok": False, "message": "Сотрудник не найден."}

    add_edit_log(
        telegram_id,
        "admin",
        f"Изменил должность на {position} из миниаппа",
        "employee",
        employee_id,
        employee[2],
    )
    dashboard = get_admin_dashboard(telegram_id)
    dashboard["message"] = "Должность сотрудника изменена."
    return dashboard


def close_shift_for_admin(telegram_id: int, payload: dict):
    if not is_admin(telegram_id):
        return {"ok": False, "message": "Нет прав администратора."}

    try:
        shift_id = int(payload.get("shift_id") or 0)
    except (TypeError, ValueError):
        shift_id = 0

    end_time = (payload.get("end_time") or "").strip()

    if not end_time:
        return {"ok": False, "message": "Укажите время закрытия в формате 18:00."}

    result = admin_close_shift(shift_id, end_time)

    if result is None:
        return {"ok": False, "message": "Открытая смена с таким ID не найдена."}

    if result == "bad_time":
        return {"ok": False, "message": "Время закрытия меньше времени начала."}

    add_edit_log(
        telegram_id,
        "admin",
        "Закрыл смену сотрудника из миниаппа",
        "shift",
        shift_id,
        f"Окончание: {result['end_time']}, отработано: {format_minutes(result['total_minutes'])}",
    )
    dashboard = get_admin_dashboard(telegram_id)
    dashboard["message"] = "Смена закрыта."
    return dashboard


def delete_shift_for_admin(telegram_id: int, payload: dict):
    if not is_admin(telegram_id):
        return {"ok": False, "message": "Нет прав администратора."}

    try:
        shift_id = int(payload.get("shift_id") or 0)
    except (TypeError, ValueError):
        shift_id = 0

    shift = delete_shift_by_id(shift_id)

    if shift is None:
        return {"ok": False, "message": "Смена не найдена."}

    add_edit_log(
        telegram_id,
        "admin",
        "Удалил смену из миниаппа",
        "shift",
        shift_id,
        f"{shift[1]} {shift[2]} {shift[3]}-{shift[4] or ''}",
    )
    dashboard = get_admin_dashboard(telegram_id)
    dashboard["message"] = "Смена удалена."
    return dashboard


def operation_action_for_admin(telegram_id: int, payload: dict):
    if not is_admin(telegram_id):
        return {"ok": False, "message": "Нет прав администратора."}

    action = (payload.get("action") or "").strip()

    try:
        number = int(payload.get("number") or 0)
    except (TypeError, ValueError):
        number = 0

    if action == "hide":
        operation = hide_operation(number)
        message = "Операция скрыта."
    elif action == "restore":
        operation = restore_operation(number)
        message = "Операция возвращена."
    elif action == "update":
        operation = update_operation_field(
            number,
            (payload.get("field") or "").strip(),
            (payload.get("value") or "").strip(),
        )
        message = "Операция изменена."
    elif action == "add":
        operation = add_operation(
            (payload.get("name") or "").strip(),
            (payload.get("position") or "").strip(),
            (payload.get("operation_group") or "").strip(),
            (payload.get("folder") or "").strip(),
        )
        message = "Операция добавлена."
    else:
        return {"ok": False, "message": "Неизвестное действие."}

    if operation is None:
        return {"ok": False, "message": "Операция не найдена или данные некорректны."}

    operation_log_id = number

    if not operation_log_id and isinstance(operation, dict):
        operation_log_id = operation.get("id")

    add_edit_log(
        telegram_id,
        "admin",
        message,
        "operation",
        operation_log_id,
        json.dumps(operation, ensure_ascii=False),
    )
    dashboard = get_admin_dashboard(telegram_id)
    dashboard["message"] = message
    return dashboard


def get_app_state(telegram_id: int, message: str = ""):
    shift_state = get_shift_state(telegram_id, message)
    employee = shift_state.get("employee")

    return {
        **shift_state,
        "is_admin": is_admin(telegram_id),
        "report": get_current_report_for_telegram(telegram_id),
        "history": get_employee_history_for_telegram(telegram_id, {}),
        "routes": {
            "enabled": ROUTES_MINIAPP_ENABLED,
            "catalog": get_route_catalog(),
            "tasks": get_route_tasks_for_telegram(telegram_id).get("tasks", []),
        },
        "production": get_production_state_for_telegram(telegram_id),
        "admin": get_admin_dashboard(telegram_id) if is_admin(telegram_id) else None,
        "features": {
            "can_work": bool(employee and employee.get("status") == "active"),
            "can_admin": is_admin(telegram_id),
            "routes_enabled": ROUTES_MINIAPP_ENABLED,
        },
    }


MINIAPP_HTML = """<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>Шагаем вместе</title>
  <script src="https://telegram.org/js/telegram-web-app.js"></script>
  <style>
    :root {
      color-scheme: light;
      --bg: #f4eee6;
      --text: #241b16;
      --muted: #7b6d62;
      --soft: rgba(255, 250, 243, .78);
      --line: rgba(78, 56, 42, .13);
      --accent: #c36f55;
      --accent-dark: #a95640;
      --sage: #8f9f7f;
      --sage-dark: #6f805f;
      --cream: #fffaf3;
      --danger: #bd6758;
      --good: #789265;
      --shadow: 0 26px 80px rgba(55, 39, 29, .18);
      --inset-shadow: inset 0 1px 0 rgba(255,255,255,.72);
      --font: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Inter, Arial, sans-serif;
    }

    * { box-sizing: border-box; }

    html, body {
      margin: 0;
      min-height: 100%;
      font-family: var(--font);
      color: var(--text);
      background:
        radial-gradient(circle at 8% 8%, rgba(195,111,85,.18), transparent 28%),
        radial-gradient(circle at 92% 4%, rgba(143,159,127,.22), transparent 30%),
        linear-gradient(135deg, #fff8ee 0%, #f4eee6 48%, #eadfd2 100%);
      overflow-x: hidden;
    }

    button, input, select, textarea {
      font: inherit;
    }

    button {
      cursor: pointer;
      -webkit-tap-highlight-color: transparent;
    }

    .app {
      min-height: 100vh;
      padding: 12px 12px 118px;
      background:
        radial-gradient(circle at 20% 0%, rgba(195,111,85,.12), transparent 33%),
        radial-gradient(circle at 90% 0%, rgba(143,159,127,.15), transparent 31%),
        var(--cream);
      position: relative;
      overflow: hidden;
    }

    .app::after {
      content: "";
      position: fixed;
      inset: 0;
      background-image: radial-gradient(circle, rgba(195,111,85,.10) 1px, transparent 1.7px);
      background-size: 22px 22px;
      opacity: .22;
      pointer-events: none;
    }

    .appbar {
      position: relative;
      z-index: 2;
      display: grid;
      grid-template-columns: 42px 1fr 42px;
      gap: 8px;
      align-items: center;
      padding: 4px 4px 12px;
    }

    .icon-btn {
      width: 40px;
      height: 40px;
      border: none;
      border-radius: 16px;
      background: rgba(255,255,255,.58);
      box-shadow: var(--inset-shadow);
      color: var(--muted);
      display: grid;
      place-items: center;
      font-size: 22px;
    }

    .icon-btn:hover {
      background: rgba(255,255,255,.78);
      color: var(--accent-dark);
    }

    .app-title {
      text-align: center;
      font-size: 16px;
      font-weight: 950;
      line-height: 1.05;
      letter-spacing: 0;
    }

    .app-title small {
      display: block;
      margin-top: 3px;
      color: var(--muted);
      font-size: 10px;
      font-weight: 850;
    }

    .body {
      position: relative;
      z-index: 2;
    }

    .tabs {
      display: grid;
      grid-template-columns: repeat(var(--tab-count, 3), minmax(0, 1fr));
      gap: 5px;
      padding: 5px;
      margin: 3px 0 16px;
      background: rgba(255,255,255,.52);
      border: 1px solid rgba(78,56,42,.11);
      border-radius: 17px;
    }

    .tabs[hidden] {
      display: none;
    }

    .tab {
      min-width: 0;
      min-height: 36px;
      border: none;
      background: transparent;
      color: var(--muted);
      border-radius: 13px;
      padding: 8px 4px;
      font-size: 10.5px;
      line-height: 1.05;
      font-weight: 900;
      overflow-wrap: anywhere;
      word-break: break-word;
    }

    .tab.active {
      color: white;
      background: var(--accent);
      box-shadow: 0 9px 18px rgba(195,111,85,.20);
    }

    .tab:hover:not(.active) {
      color: var(--accent-dark);
      background: rgba(195,111,85,.10);
    }

    .screen-head {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: flex-end;
      margin: 4px 0 14px;
    }

    .screen-head h2 {
      margin: 0;
      font-size: 25px;
      letter-spacing: 0;
      line-height: 1;
    }

    .screen-head p {
      margin: 6px 0 0;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.35;
    }

    .date {
      color: var(--muted);
      font-size: 11px;
      font-weight: 900;
      padding: 8px 10px;
      border-radius: 99px;
      background: rgba(255,255,255,.54);
      white-space: nowrap;
    }

    .card {
      border: 1px solid rgba(78,56,42,.11);
      background: rgba(255,250,244,.76);
      border-radius: 22px;
      box-shadow: 0 10px 24px rgba(80,55,36,.055), var(--inset-shadow);
    }

    .shift-card {
      padding: 14px;
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 12px;
    }

    .shift-card b {
      display: block;
      font-size: 15px;
      margin-bottom: 5px;
    }

    .shift-card span {
      color: var(--muted);
      font-size: 12px;
      line-height: 1.35;
    }

    .status-chip {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      color: var(--sage-dark);
      background: rgba(143,159,127,.16);
      border: 1px solid rgba(143,159,127,.18);
      border-radius: 99px;
      padding: 7px 9px;
      font-size: 10.5px;
      font-weight: 950;
      white-space: nowrap;
    }

    .status-chip.warn {
      color: var(--accent-dark);
      background: rgba(195,111,85,.12);
      border-color: rgba(195,111,85,.18);
    }

    .status-chip.gray {
      color: var(--muted);
      background: rgba(120,96,76,.10);
      border-color: rgba(120,96,76,.10);
    }

    .kpi-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
      margin: 12px 0;
    }

    .kpi {
      padding: 13px;
      min-height: 104px;
    }

    .kpi-top {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      color: var(--muted);
      font-size: 11px;
      font-weight: 900;
    }

    .kpi-ico {
      width: 34px;
      height: 34px;
      border-radius: 13px;
      background: rgba(195,111,85,.13);
      color: var(--accent-dark);
      display: grid;
      place-items: center;
      font-size: 16px;
    }

    .kpi.good .kpi-ico {
      background: rgba(143,159,127,.15);
      color: var(--sage-dark);
    }

    .kpi strong {
      display: block;
      margin-top: 12px;
      font-size: 26px;
      letter-spacing: 0;
    }

    .kpi strong small {
      font-size: 12px;
      letter-spacing: 0;
      color: var(--muted);
    }

    .kpi span {
      display: block;
      margin-top: 4px;
      color: var(--muted);
      font-size: 11px;
      line-height: 1.3;
    }

    .progress {
      height: 7px;
      border-radius: 99px;
      background: rgba(120,96,76,.12);
      overflow: hidden;
      margin-top: 10px;
    }

    .progress i {
      display: block;
      height: 100%;
      width: var(--w, 70%);
      border-radius: 99px;
      background: var(--accent);
    }

    .progress.sage i {
      background: var(--sage);
    }

    .section-title {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin: 17px 0 10px;
    }

    .section-title b {
      font-size: 15px;
      letter-spacing: 0;
    }

    .section-title button, .section-title span {
      border: none;
      background: transparent;
      color: var(--accent-dark);
      font-weight: 900;
      font-size: 11px;
    }

    .op-icon {
      width: 44px;
      height: 44px;
      border-radius: 16px;
      background: rgba(195,111,85,.13);
      display: grid;
      place-items: center;
      color: var(--accent-dark);
      flex: 0 0 auto;
    }

    .active-operation,
    .op-row,
    .order-head {
      display: grid;
      grid-template-columns: 44px minmax(0, 1fr) auto;
      gap: 10px;
      align-items: center;
      padding: 11px;
    }

    .active-operation b,
    .op-meta b,
    .order-head b {
      display: block;
      font-size: 13px;
      line-height: 1.18;
    }

    .active-operation span,
    .op-meta span,
    .order-head span,
    .item-meta {
      display: block;
      margin-top: 4px;
      color: var(--muted);
      font-size: 11px;
      line-height: 1.35;
    }

    .op-list {
      display: grid;
      gap: 10px;
    }

    .op-row.selected {
      border-color: rgba(195,111,85,.44);
      box-shadow: 0 12px 28px rgba(195,111,85,.12), var(--inset-shadow);
    }

    .op-num {
      text-align: right;
      font-size: 12px;
      color: var(--muted);
      font-weight: 900;
    }

    .op-num strong {
      display: block;
      color: var(--text);
      font-size: 15px;
      letter-spacing: 0;
    }

    .field-card {
      padding: 13px;
      margin-bottom: 10px;
    }

    .field-card label {
      display: block;
      color: var(--muted);
      font-size: 11px;
      font-weight: 900;
      margin-bottom: 9px;
    }

    .form-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 9px;
    }

    .field {
      min-width: 0;
    }

    .field.full {
      grid-column: 1 / -1;
    }

    .field input,
    .field select,
    .field textarea {
      width: 100%;
      min-height: 42px;
      border: 1px solid rgba(78,56,42,.13);
      border-radius: 15px;
      background: rgba(255,255,255,.56);
      color: var(--text);
      padding: 9px 10px;
      outline: none;
      font-size: 13px;
      font-weight: 850;
    }

    .field textarea {
      min-height: 108px;
      resize: vertical;
      line-height: 1.35;
    }

    .segment-row {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 6px;
      margin-bottom: 12px;
    }

    .segment-button {
      min-width: 0;
      min-height: 34px;
      border: none;
      border-radius: 13px;
      padding: 8px 5px;
      background: rgba(255,255,255,.56);
      color: var(--muted);
      font-size: 10.5px;
      line-height: 1.05;
      font-weight: 950;
      overflow-wrap: anywhere;
    }

    .segment-button.active {
      background: var(--accent);
      color: white;
    }

    .segment-button:hover:not(.active) {
      color: var(--accent-dark);
      background: rgba(195,111,85,.10);
    }

    .button-row {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 9px;
      margin-top: 11px;
    }

    .small-button {
      min-width: 0;
      border: none;
      border-radius: 15px;
      padding: 11px 10px;
      color: white;
      background: var(--accent);
      font-size: 12px;
      font-weight: 950;
      overflow-wrap: anywhere;
    }

    .small-button.secondary {
      color: var(--accent-dark);
      background: rgba(195,111,85,.12);
    }

    .small-button.danger {
      background: var(--danger);
    }

    .small-button:hover {
      filter: brightness(1.03);
      box-shadow: 0 10px 18px rgba(195,111,85,.15);
    }

    button,
    [data-go],
    [data-admin-home-period],
    [data-admin-home-view],
    [data-admin-home-employee],
    [data-admin-section],
    [data-admin-action],
    [data-order-action],
    [data-order-size],
    [data-order-color],
    [data-history-action],
    [data-feedback-action],
    [data-select-operation],
    [data-select-order] {
      cursor: pointer;
      user-select: none;
      -webkit-user-select: none;
      -webkit-tap-highlight-color: transparent;
    }

    .card[data-go],
    .card[data-order-action],
    .card[data-admin-home-view],
    .card[data-admin-home-employee],
    .card[data-select-operation],
    .card[data-select-order] {
      border-color: rgba(195,111,85,.24);
      box-shadow: 0 9px 22px rgba(95,67,48,.07);
      transition: transform .16s ease, border-color .16s ease, box-shadow .16s ease, background .16s ease;
    }

    .card[data-go]:hover,
    .card[data-order-action]:hover,
    .card[data-admin-home-view]:hover,
    .card[data-admin-home-employee]:hover,
    .card[data-select-operation]:hover,
    .card[data-select-order]:hover {
      transform: translateY(-1px);
      border-color: rgba(195,111,85,.52);
      background: rgba(255,255,255,.72);
      box-shadow: 0 14px 28px rgba(195,111,85,.16);
    }

    .card[data-go]:active,
    .card[data-order-action]:active,
    .card[data-admin-home-view]:active,
    .card[data-admin-home-employee]:active,
    .card[data-select-operation]:active,
    .card[data-select-order]:active {
      transform: translateY(0);
      box-shadow: 0 7px 16px rgba(195,111,85,.12);
    }

    .card[data-go] .status-chip.gray,
    .card[data-order-action] .status-chip.gray,
    .card[data-admin-home-view] .status-chip.gray,
    .card[data-admin-home-employee] .status-chip.gray,
    .card[data-select-operation] .status-chip.gray,
    .card[data-select-order] .status-chip.gray {
      color: var(--accent-dark);
      background: rgba(195,111,85,.13);
      border-color: rgba(195,111,85,.18);
    }

    .choice-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 8px;
    }

    .choice-chip {
      min-width: 0;
      min-height: 38px;
      border: 1px solid rgba(78,56,42,.13);
      border-radius: 14px;
      background: rgba(255,255,255,.54);
      color: var(--muted);
      padding: 9px 10px;
      font-size: 11px;
      font-weight: 900;
      line-height: 1.12;
      overflow-wrap: anywhere;
      transition: .16s ease;
    }

    .choice-chip.active,
    .choice-chip:hover {
      color: var(--accent-dark);
      border-color: rgba(195,111,85,.44);
      background: rgba(195,111,85,.12);
      box-shadow: 0 8px 18px rgba(195,111,85,.10);
    }

    .report-row {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 10px;
      align-items: center;
      padding: 12px 13px;
    }

    .report-row b {
      display: block;
      font-size: 13px;
      line-height: 1.22;
    }

    .report-row span {
      display: block;
      margin-top: 4px;
      color: var(--muted);
      font-size: 11px;
      line-height: 1.35;
    }

    .select-row {
      display: grid;
      grid-template-columns: 42px minmax(0, 1fr) auto;
      gap: 10px;
      align-items: center;
    }

    .select-row b {
      display: block;
      font-size: 13px;
    }

    .select-row span {
      display: block;
      margin-top: 4px;
      color: var(--muted);
      font-size: 11px;
    }

    .detail-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 8px;
      margin-top: 11px;
    }

    .detail-box {
      border-radius: 15px;
      background: rgba(255,255,255,.48);
      padding: 10px;
    }

    .detail-box span {
      display: block;
      color: var(--muted);
      font-size: 10px;
      font-weight: 900;
      text-transform: uppercase;
      letter-spacing: 0;
    }

    .detail-box strong {
      display: block;
      margin-top: 5px;
      font-size: 13px;
    }

    .order-card {
      padding: 12px;
    }

    .order-foot {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 10px;
      color: var(--muted);
      font-size: 11px;
      font-weight: 850;
    }

    .order-detail {
      padding: 14px;
      background: linear-gradient(135deg, rgba(195,111,85,.12), rgba(143,159,127,.10));
    }

    .chart-card {
      padding: 14px;
    }

    .chart-top {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 8px;
    }

    .chart-top b {
      display: block;
      font-size: 14px;
    }

    .chart-top strong {
      display: block;
      font-size: 27px;
      letter-spacing: 0;
      margin-top: 6px;
    }

    .chart-top small {
      color: var(--muted);
      font-size: 11px;
    }

    .ring {
      --p: 72;
      width: 68px;
      height: 68px;
      border-radius: 50%;
      background: conic-gradient(var(--accent) calc(var(--p)*1%), rgba(195,111,85,.13) 0);
      display: grid;
      place-items: center;
      position: relative;
      flex: 0 0 auto;
    }

    .ring::before {
      content: "";
      position: absolute;
      inset: 8px;
      border-radius: 50%;
      background: var(--cream);
      box-shadow: inset 0 1px 2px rgba(80,55,36,.08);
    }

    .ring strong {
      position: relative;
      z-index: 1;
      font-size: 15px;
      letter-spacing: 0;
    }

    .chart {
      width: 100%;
      height: 150px;
    }

    .mini-metrics {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 8px;
      margin-top: 10px;
    }

    .mini-metric {
      padding: 10px 8px;
      text-align: center;
    }

    .mini-metric .ring {
      width: 52px;
      height: 52px;
      margin: 0 auto 8px;
    }

    .mini-metric .ring::before {
      inset: 7px;
    }

    .mini-metric .ring strong {
      font-size: 12px;
    }

    .mini-metric b {
      display: block;
      font-size: 11px;
    }

    .mini-metric span {
      display: block;
      margin-top: 3px;
      color: var(--muted);
      font-size: 9.5px;
    }

    .empty {
      margin: 0;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.4;
      padding: 13px;
    }

    .toast {
      position: fixed;
      z-index: 50;
      left: 50%;
      bottom: 88px;
      transform: translate(-50%, 26px);
      opacity: 0;
      min-width: min(360px, calc(100% - 32px));
      border: 1px solid rgba(255,255,255,.42);
      border-radius: 20px;
      background: rgba(36,27,22,.88);
      color: white;
      padding: 14px 16px;
      box-shadow: 0 20px 60px rgba(0,0,0,.24);
      backdrop-filter: blur(20px);
      transition: .24s ease;
      pointer-events: none;
    }

    .toast.show {
      transform: translate(-50%, 0);
      opacity: 1;
    }

    .toast b {
      display: block;
      font-size: 13px;
      margin-bottom: 3px;
    }

    .toast span {
      color: rgba(255,255,255,.72);
      font-size: 12px;
    }

    .main-button {
      position: fixed;
      z-index: 6;
      left: 16px;
      right: 16px;
      bottom: 78px;
      border: none;
      border-radius: 18px;
      padding: 15px 16px;
      color: white;
      background: linear-gradient(135deg, var(--accent), #d27c5e);
      font-size: 15px;
      font-weight: 950;
      box-shadow: 0 18px 36px rgba(195,111,85,.30);
    }

    .main-button:disabled {
      opacity: .48;
      box-shadow: none;
    }

    .bottom-nav {
      position: fixed;
      z-index: 5;
      left: 0;
      right: 0;
      bottom: 0;
      padding: 9px 12px 12px;
      background: rgba(255,250,243,.88);
      border-top: 1px solid rgba(78,56,42,.11);
      backdrop-filter: blur(18px);
      display: grid;
      grid-template-columns: repeat(var(--nav-count, 5), minmax(0, 1fr));
      gap: 2px;
    }

    .nav-btn {
      min-width: 0;
      border: none;
      background: transparent;
      color: var(--muted);
      border-radius: 16px;
      padding: 8px 3px 6px;
      display: grid;
      gap: 4px;
      place-items: center;
      font-size: 10px;
      line-height: 1.05;
      font-weight: 850;
    }

    .nav-btn span:last-child {
      max-width: 100%;
      overflow-wrap: anywhere;
      word-break: break-word;
      text-align: center;
    }

    .nav-ico {
      width: 24px;
      height: 24px;
      border-radius: 10px;
      display: grid;
      place-items: center;
      font-size: 14px;
    }

    .nav-btn.active {
      color: var(--accent-dark);
    }

    .nav-btn.active .nav-ico {
      background: rgba(195,111,85,.12);
    }

    .nav-btn:hover {
      color: var(--accent-dark);
    }

    .nav-btn:hover .nav-ico {
      background: rgba(195,111,85,.10);
    }

    @media (min-width: 680px) {
      .app {
        width: min(430px, 100%);
        min-height: 880px;
        margin: 22px auto;
        border-radius: 38px;
        box-shadow: var(--shadow);
      }

      .main-button,
      .bottom-nav {
        left: 50%;
        width: min(430px, 100%);
        transform: translateX(-50%);
      }

      .toast {
        bottom: 104px;
      }
    }
  </style>
</head>
<body>
  <main class="app">
    <div class="appbar">
      <button class="icon-btn" id="backBtn" aria-label="Назад">‹</button>
      <div class="app-title">Шагаем вместе<small id="roleLabel">Загрузка</small></div>
      <button class="icon-btn" id="menuBtn" aria-label="Меню">⋯</button>
    </div>

    <div class="body">
      <div class="tabs" id="topTabs" hidden></div>
      <div id="mount"></div>
    </div>
  </main>

  <button class="main-button" id="mainButton">Загрузка</button>
  <nav class="bottom-nav" id="bottomNav" aria-label="Навигация миниаппа"></nav>
  <div class="toast" id="toast"><b></b><span></span></div>

  <script>
    const tg = window.Telegram && window.Telegram.WebApp;
    const urlParams = new URLSearchParams(window.location.search);
    const debugTelegramId = urlParams.get("debug_tg_id");
    const queryAuthToken = urlParams.get("auth");
    let storedAuthToken = "";

    try {
      if (queryAuthToken) {
        window.localStorage.setItem("miniapp_auth", queryAuthToken);
      }
      storedAuthToken = window.localStorage.getItem("miniapp_auth") || "";
    } catch (error) {
      storedAuthToken = "";
    }

    const authToken = queryAuthToken || storedAuthToken;
    const state = {
      initData: tg ? tg.initData : "",
      screen: "shift",
      selectedOperation: 0,
      selectedOrder: 0,
      orderMode: "list",
      orderProduct: "",
      orderTaskType: "cutting",
      orderRouteStep: "",
      orderMaterial: "Ткань",
      orderSizes: [],
      orderColors: [],
      orderQuantity: "1",
      adminSection: "reports",
      adminReportType: "period",
      adminStartDate: "",
      adminEndDate: "",
      adminEmployeeId: "",
      adminShiftEndTime: "",
      adminHomePeriod: "today",
      adminHomeView: "overview",
      adminHomeEmployee: "",
      userStartDate: "",
      userEndDate: "",
      data: null,
    };

    const mount = document.getElementById("mount");
    const mainButton = document.getElementById("mainButton");
    const topTabs = document.getElementById("topTabs");
    const bottomNav = document.getElementById("bottomNav");
    const toast = document.getElementById("toast");

    const baseNav = [
      { id: "shift", label: "Главная", icon: "⌂" },
      { id: "report", label: "Отчёт", icon: "＋" },
      { id: "analytics", label: "Аналитика", icon: "▥" },
      { id: "orders", label: "Заказы", icon: "▣" },
    ];

    if (tg) {
      tg.ready();
      tg.expand();
    }

    function escapeHtml(value) {
      return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }

    async function api(path, payload = {}) {
      const response = await fetch(path, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
          ...payload,
          initData: state.initData,
          authToken,
          telegram_id: debugTelegramId,
        }),
      });
      return await response.json();
    }

    function showToast(title, text) {
      toast.querySelector("b").textContent = title;
      toast.querySelector("span").textContent = text;
      toast.classList.add("show");
      clearTimeout(window.toastTimer);
      window.toastTimer = setTimeout(() => toast.classList.remove("show"), 2600);
    }

    function sewingIcon() {
      return `<svg viewBox="0 0 32 32" aria-hidden="true" width="25" height="25"><path d="M7 22h18v4H7z" fill="none" stroke="currentColor" stroke-width="2"/><path d="M10 22V8h9a5 5 0 0 1 5 5v2" fill="none" stroke="currentColor" stroke-width="2"/><path d="M6 14h5M19 15h8v7M13 8V5M22 15v-3M15 22v-5M13 17h4" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>`;
    }

    function itemEmpty(text) {
      return `<p class="empty">${escapeHtml(text)}</p>`;
    }

    function progressForTask(task) {
      if (!task) return 0;
      if (task.status === "formed") return 100;
      if (task.status === "in_cutting") return 70;
      if (task.status === "contours_done") return 40;
      return 12;
    }

    function getReportOperations() {
      return state.data && state.data.report && state.data.report.operations ? state.data.report.operations : [];
    }

    function getFeedbackRows() {
      return state.data && state.data.report && state.data.report.feedback ? state.data.report.feedback : [];
    }

    function getProduction() {
      return state.data && state.data.production ? state.data.production : {};
    }

    function getTasks() {
      return getProduction().tasks || [];
    }

    function getContourTasks() {
      return getProduction().contour_tasks || [];
    }

    function getRouteCatalog() {
      return state.data && state.data.routes && state.data.routes.catalog ? state.data.routes.catalog : [];
    }

    function getRouteTasks() {
      return state.data && state.data.routes && state.data.routes.tasks ? state.data.routes.tasks : [];
    }

    function getOrderColors() {
      const colors = getProduction().order_colors || [];
      if (colors.length) return colors;

      const fallbackColors = [];
      getRouteCatalog().forEach((product) => {
        (product.raw_colors || []).forEach((color) => {
          if (!fallbackColors.includes(color)) fallbackColors.push(color);
        });
      });
      return fallbackColors;
    }

    function routeProduct(productName) {
      return getRouteCatalog().find((item) => item.product_name === productName) || getRouteCatalog()[0] || null;
    }

    function routeOperations(product) {
      if (!product || !product.steps) return [];
      return product.steps
        .map((step, index) => ({...step, index}))
        .filter((step) => step.position !== "Раскройщик");
    }

    function shiftText() {
      const shift = state.data && state.data.shift;
      if (!shift) return "Смена не открыта";
      return shift.status === "open" ? "Смена открыта" : "Смена закрыта";
    }

    function navItems() {
      const items = [...baseNav];
      if (state.data && state.data.is_admin) {
        items.push({ id: "admin", label: "Админ", icon: "◎" });
      }
      return items;
    }

    function renderBottomNav() {
      const items = navItems();
      bottomNav.style.setProperty("--nav-count", items.length);
      bottomNav.innerHTML = items.map((item) => `
        <button class="nav-btn ${state.screen === item.id ? "active" : ""}" data-go="${item.id}">
          <span class="nav-ico">${item.icon}</span><span>${item.label}</span>
        </button>
      `).join("");
    }

    function renderTopTabs() {
      let tabs = [];

      if (state.screen === "shift" && state.data && state.data.is_admin) {
        tabs = [
          ["today", "Сегодня"],
          ["month", "Месяц"],
          ["quarter", "Квартал"],
        ].map(([id, label]) => ({
          id,
          label,
          attr: "data-admin-home-period",
          active: state.adminHomePeriod === id,
        }));
      }

      topTabs.hidden = tabs.length === 0;
      topTabs.style.setProperty("--tab-count", tabs.length || 1);
      topTabs.innerHTML = tabs.map((tab) => `
        <button class="tab ${tab.active ? "active" : ""}" ${tab.attr}="${tab.id}">${tab.label}</button>
      `).join("");
    }

    function roleLabel() {
      if (state.data && state.data.is_admin) return "Администратор";
      const employee = state.data && state.data.employee;
      if (!employee) return "Нет доступа";
      return employee.position || "Сотрудник";
    }

    function getAdmin() {
      return state.data && state.data.admin ? state.data.admin : null;
    }

    function getAdminReport() {
      const admin = getAdmin();
      return admin && admin.reports ? admin.reports : null;
    }

    function getHistory() {
      return state.data && state.data.history ? state.data.history : null;
    }

    function ensureUserDefaults() {
      const admin = getAdmin();
      const defaults = admin && admin.period_defaults ? admin.period_defaults : {};
      const history = getHistory();

      if (!state.userStartDate) {
        state.userStartDate = (history && history.start_date) || defaults.start_date || "";
      }
      if (!state.userEndDate) {
        state.userEndDate = (history && history.end_date) || defaults.end_date || "";
      }
    }

    function getHistoryPayload() {
      ensureUserDefaults();
      return {
        start_date: state.userStartDate,
        end_date: state.userEndDate,
      };
    }

    function ensureAdminDefaults() {
      const admin = getAdmin();
      const report = getAdminReport();
      const defaults = admin && admin.period_defaults ? admin.period_defaults : {};

      if (!state.adminStartDate) {
        state.adminStartDate = (report && report.start_date) || defaults.start_date || "";
      }
      if (!state.adminEndDate) {
        state.adminEndDate = (report && report.end_date) || defaults.end_date || "";
      }
      if (!state.adminEmployeeId && admin && admin.employees && admin.employees[0]) {
        state.adminEmployeeId = String(admin.employees[0].id);
      }
    }

    function syncHistoryForm() {
      const start = document.getElementById("userStartDate");
      const end = document.getElementById("userEndDate");

      if (start) state.userStartDate = start.value;
      if (end) state.userEndDate = end.value;
    }

    function getAdminReportPayload() {
      ensureAdminDefaults();
      return {
        report_type: state.adminReportType,
        start_date: state.adminStartDate,
        end_date: state.adminEndDate,
        employee_id: state.adminEmployeeId,
      };
    }

    function adminReportTotals(report) {
      if (!report) return { shifts: 0, minutes: 0, operations: 0, employees: 0 };

      if (report.type === "employee") {
        const summary = report.employee_summary || {};
        return {
          shifts: summary.shift_count || 0,
          minutes: summary.total_minutes || 0,
          operations: (report.employee_operations || []).length,
          employees: summary.full_name ? 1 : 0,
        };
      }

      const summaryRows = report.summary || [];
      return {
        shifts: summaryRows.reduce((sum, row) => sum + Number(row.shift_count || 0), 0),
        minutes: summaryRows.reduce((sum, row) => sum + Number(row.total_minutes || 0), 0),
        operations: (report.operations || []).length,
        employees: summaryRows.length,
      };
    }

    function minutesLabel(minutes) {
      const total = Number(minutes || 0);
      const hours = Math.floor(total / 60);
      const rest = total % 60;
      return `${hours}:${String(rest).padStart(2, "0")}`;
    }

    function syncAdminForm() {
      const type = document.getElementById("adminReportType");
      const start = document.getElementById("adminStartDate");
      const end = document.getElementById("adminEndDate");
      const employee = document.getElementById("adminEmployeeId");

      if (type) state.adminReportType = type.value;
      if (start) state.adminStartDate = start.value;
      if (end) state.adminEndDate = end.value;
      if (employee) state.adminEmployeeId = employee.value;
    }

    function replaceAdminDashboard(data, fallbackMessage) {
      if (!data.ok) {
        showToast("Админ", data.message || fallbackMessage || "Действие не выполнено.");
        mainButton.disabled = false;
        return;
      }

      state.data.admin = data;
      render();
      showToast("Админ", data.message || fallbackMessage || "Данные обновлены.");
    }

    function getAdminHomePeriod() {
      const admin = getAdmin() || {};
      const periods = admin.home && admin.home.periods ? admin.home.periods : {};
      return periods[state.adminHomePeriod] || periods.today || {
        id: state.adminHomePeriod,
        title: "Главная",
        start_date: "",
        end_date: "",
        plan_text: "0",
        fact_text: "0",
        defect_count: 0,
        employees: [],
        defects: [],
      };
    }

    function periodDateLabel(period) {
      if (!period) return "";
      if (!period.start_date || period.start_date === period.end_date) return period.start_date || "";
      return `${period.start_date} — ${period.end_date}`;
    }

    function homeEmployeeTitle(period) {
      if (period && period.id === "today") return "Сотрудники на смене";
      if (period && period.id === "quarter") return "Сотрудники за квартал";
      return "Сотрудники за месяц";
    }

    function renderPlanFactCards(entity) {
      return `
        <div class="kpi-grid">
          <div class="card kpi"><div class="kpi-top"><span>План</span><div class="kpi-ico">◎</div></div><strong>${escapeHtml(entity.plan_text || "0")}</strong><span>Плановое количество</span><div class="progress"><i style="--w:0%"></i></div></div>
          <div class="card kpi good"><div class="kpi-top"><span>Факт</span><div class="kpi-ico">✓</div></div><strong>${escapeHtml(entity.fact_text || "0")}</strong><span>Сделано по отчётам</span><div class="progress sage"><i style="--w:${Math.min(100, Number(entity.fact || 0))}%"></i></div></div>
        </div>
      `;
    }

    function renderAdminHomeOverview(period) {
      const employees = period.employees || [];
      const title = period.id === "today" ? "Текущая смена" : period.title;

      return `
        <div class="screen-head"><div><h2>${escapeHtml(title)}</h2><p>${escapeHtml(period.title)} · план/факт.</p></div><div class="date">${escapeHtml(periodDateLabel(period))}</div></div>
        <div class="card shift-card" data-admin-home-view="planfact">
          <div><b>План / факт</b><span>План ${escapeHtml(period.plan_text || "0")} · факт ${escapeHtml(period.fact_text || "0")}</span></div>
          <span class="status-chip">открыть</span>
        </div>
        <div class="op-list">
          <div class="card report-row" data-admin-home-view="employees"><div><b>${escapeHtml(homeEmployeeTitle(period))}</b><span>${escapeHtml(employees.length)} сотрудников · план/факт по каждому</span></div><span class="status-chip gray">›</span></div>
          <div class="card report-row" data-admin-home-view="defects"><div><b>Брак</b><span>${escapeHtml(period.defect_count || 0)} записей · изделие, этап, причина</span></div><span class="status-chip gray">›</span></div>
        </div>
      `;
    }

    function renderAdminHomePlanFact(period) {
      return `
        <div class="screen-head"><div><h2>План / факт</h2><p>${escapeHtml(period.title)}</p></div><div class="date">${escapeHtml(periodDateLabel(period))}</div></div>
        ${renderPlanFactCards(period)}
      `;
    }

    function renderAdminHomeEmployees(period) {
      const employees = period.employees || [];

      return `
        <div class="screen-head"><div><h2>${escapeHtml(homeEmployeeTitle(period))}</h2><p>${escapeHtml(period.title)} · сотрудник, должность, план/факт.</p></div><div class="date">${escapeHtml(employees.length)} чел</div></div>
        <div class="op-list">
          ${employees.length ? employees.map((employee, index) => `
            <div class="card report-row" data-admin-home-employee="${index}">
              <div><b>${escapeHtml(employee.name)}</b><span>${escapeHtml(employee.position)}${employee.on_shift ? ` · на смене${employee.start_time ? ` с ${escapeHtml(employee.start_time)}` : ""}` : ""}<br>План ${escapeHtml(employee.plan_text || "0")} · факт ${escapeHtml(employee.fact_text || "0")}</span></div>
              <span class="status-chip gray">›</span>
            </div>
          `).join("") : itemEmpty(period.id === "today" ? "Сотрудников на смене пока нет." : "За период сотрудников с отчётами пока нет.")}
        </div>
      `;
    }

    function renderAdminHomeEmployee(period) {
      const employees = period.employees || [];
      const employee = employees[Number(state.adminHomeEmployee)] || employees[0];

      if (!employee) {
        state.adminHomeView = "employees";
        return renderAdminHomeEmployees(period);
      }

      return `
        <div class="screen-head"><div><h2>${escapeHtml(employee.name)}</h2><p>${escapeHtml(employee.position)} · ${escapeHtml(period.title)}</p></div><div class="date">${escapeHtml(periodDateLabel(period))}</div></div>
        ${renderPlanFactCards(employee)}
        <div class="section-title"><b>Задания / факт</b><span>${(employee.operations || []).length}</span></div>
        <div class="op-list">
          ${(employee.operations || []).length ? employee.operations.map((operation) => `
            <div class="card report-row"><div><b>${escapeHtml(operation.operation)}</b><span>${escapeHtml(operation.stage)} · ${escapeHtml(operation.date || "")}<br>${escapeHtml(operation.size)} · ${escapeHtml(operation.color)}</span></div><span class="status-chip">${escapeHtml(operation.quantity_text)} ${escapeHtml(operation.unit)}</span></div>
          `).join("") : itemEmpty("Фактических операций за период пока нет.")}
        </div>
      `;
    }

    function renderAdminHomeDefects(period) {
      const defects = period.defects || [];

      mainButton.textContent = "Обновить главную";
      mainButton.disabled = false;

      return `
        <div class="screen-head"><div><h2>Брак</h2><p>${escapeHtml(period.title)} · изделие, этап, причина.</p></div><div class="date">${escapeHtml(defects.length)} записей</div></div>
        <div class="op-list">
          ${defects.length ? defects.map((defect) => `
            <div class="card report-row"><div><b>${escapeHtml(defect.product || "-")}</b><span>${escapeHtml(defect.stage || "-")}<br>${escapeHtml(defect.reason || "Причина не указана")}</span></div><span class="status-chip gray">${escapeHtml(defect.date || "")}</span></div>
          `).join("") : `
            <div class="card field-card">
              <div class="report-row"><div><b>Изделие</b><span>Этап<br>Причина</span></div><span class="status-chip gray">0</span></div>
            </div>
          `}
        </div>
      `;
    }

    function renderAdminHome() {
      const period = getAdminHomePeriod();

      mainButton.textContent = "Обновить главную";
      mainButton.disabled = false;

      if (state.adminHomeView === "planfact") {
        mount.innerHTML = renderAdminHomePlanFact(period);
        return;
      }
      if (state.adminHomeView === "employees") {
        mount.innerHTML = renderAdminHomeEmployees(period);
        return;
      }
      if (state.adminHomeView === "employee") {
        mount.innerHTML = renderAdminHomeEmployee(period);
        return;
      }
      if (state.adminHomeView === "defects") {
        mount.innerHTML = renderAdminHomeDefects(period);
        return;
      }

      mount.innerHTML = renderAdminHomeOverview(period);
    }

    async function loadHistory() {
      syncHistoryForm();
      mainButton.disabled = true;

      try {
        const data = await api("/api/report/history", getHistoryPayload());
        if (!data.ok) {
          showToast("История", data.message || "Не удалось загрузить историю.");
          mainButton.disabled = false;
          return;
        }
        state.data.history = data;
        render();
        showToast("История", "Данные обновлены.");
      } catch (error) {
        showToast("Ошибка", "Не удалось загрузить историю.");
        mainButton.disabled = false;
      }
    }

    async function sendFeedback() {
      const category = document.getElementById("feedbackCategory");
      const message = document.getElementById("feedbackMessage");
      mainButton.disabled = true;

      try {
        const data = await api("/api/feedback/send", {
          category: category ? category.value : "",
          message: message ? message.value : "",
        });
        if (!data.ok) {
          showToast("Связь", data.message || "Не удалось отправить сообщение.");
          mainButton.disabled = false;
          return;
        }
        state.data.report = data.report || state.data.report;
        if (message) message.value = "";
        render();
        showToast("Связь", data.message || "Сообщение отправлено.");
      } catch (error) {
        showToast("Ошибка", "Не удалось отправить сообщение.");
        mainButton.disabled = false;
      }
    }

    async function refreshAdminDashboard(message = "Данные обновлены.") {
      if (!state.data || !state.data.is_admin) return;
      mainButton.disabled = true;

      try {
        const data = await api("/api/admin/dashboard");
        replaceAdminDashboard(data, message);
      } catch (error) {
        showToast("Ошибка", "Не удалось обновить админ-раздел.");
        mainButton.disabled = false;
      }
    }

    async function adminEmployeeStatus(employeeId, status) {
      mainButton.disabled = true;

      try {
        const data = await api("/api/admin/employee/status", {
          employee_id: employeeId,
          status,
        });
        replaceAdminDashboard(data, "Статус сотрудника изменён.");
      } catch (error) {
        showToast("Ошибка", "Не удалось изменить статус.");
        mainButton.disabled = false;
      }
    }

    async function adminEmployeePosition(employeeId) {
      const select = document.getElementById(`employeePosition${employeeId}`);
      mainButton.disabled = true;

      try {
        const data = await api("/api/admin/employee/position", {
          employee_id: employeeId,
          position: select ? select.value : "",
        });
        replaceAdminDashboard(data, "Должность изменена.");
      } catch (error) {
        showToast("Ошибка", "Не удалось изменить должность.");
        mainButton.disabled = false;
      }
    }

    async function adminCloseShift(shiftId) {
      const endTime = document.getElementById("adminShiftEndTime");
      state.adminShiftEndTime = endTime ? endTime.value : state.adminShiftEndTime;
      mainButton.disabled = true;

      try {
        const data = await api("/api/admin/shift/close", {
          shift_id: shiftId,
          end_time: state.adminShiftEndTime,
        });
        replaceAdminDashboard(data, "Смена закрыта.");
      } catch (error) {
        showToast("Ошибка", "Не удалось закрыть смену.");
        mainButton.disabled = false;
      }
    }

    async function adminDeleteShift(shiftId) {
      if (!window.confirm("Удалить смену?")) return;
      mainButton.disabled = true;

      try {
        const data = await api("/api/admin/shift/delete", { shift_id: shiftId });
        replaceAdminDashboard(data, "Смена удалена.");
      } catch (error) {
        showToast("Ошибка", "Не удалось удалить смену.");
        mainButton.disabled = false;
      }
    }

    async function loadAdminFeedback() {
      ensureAdminDefaults();
      mainButton.disabled = true;

      try {
        const data = await api("/api/admin/feedback", {
          start_date: state.adminStartDate,
          end_date: state.adminEndDate,
        });
        if (!data.ok) {
          showToast("Связь", data.message || "Не удалось загрузить сообщения.");
          mainButton.disabled = false;
          return;
        }
        state.data.admin = {
          ...state.data.admin,
          feedback: data.feedback || [],
        };
        render();
        showToast("Связь", "Сообщения обновлены.");
      } catch (error) {
        showToast("Ошибка", "Не удалось загрузить сообщения.");
        mainButton.disabled = false;
      }
    }

    async function loadAdminReport() {
      if (!state.data || !state.data.is_admin) return;
      syncAdminForm();
      mainButton.disabled = true;

      try {
        const data = await api("/api/admin/report", getAdminReportPayload());
        if (!data.ok) {
          showToast("Отчёт", data.message || "Не удалось загрузить отчёт.");
          mainButton.disabled = false;
          return;
        }
        state.data.admin = {
          ...state.data.admin,
          reports: data.report,
        };
        render();
        showToast("Отчёт", "Данные обновлены.");
      } catch (error) {
        showToast("Ошибка", "Не удалось загрузить отчёт.");
        mainButton.disabled = false;
      }
    }

    async function exportAdminReport() {
      if (!state.data || !state.data.is_admin) return;
      syncAdminForm();
      mainButton.disabled = true;

      try {
        const response = await fetch("/api/admin/report/export", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({
            ...getAdminReportPayload(),
            initData: state.initData,
            authToken,
            telegram_id: debugTelegramId,
          }),
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          showToast("Выгрузка", errorData.message || "Не удалось выгрузить отчёт.");
          mainButton.disabled = false;
          return;
        }

        const blob = await response.blob();
        const disposition = response.headers.get("Content-Disposition") || "";
        const match = disposition.match(/filename\\*=UTF-8''([^;]+)/);
        const filename = match ? decodeURIComponent(match[1]) : "report.xlsx";
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        link.remove();
        URL.revokeObjectURL(url);
        showToast("Выгрузка", "Файл отчёта сформирован.");
      } catch (error) {
        showToast("Ошибка", "Не удалось выгрузить отчёт.");
      } finally {
        mainButton.disabled = false;
      }
    }

    function renderShift() {
      if (state.data && state.data.is_admin) {
        renderAdminHome();
        return;
      }

      const employee = state.data && state.data.employee;
      const shift = state.data && state.data.shift;
      const operations = getReportOperations();
      const tasks = getTasks();
      const contourTasks = getContourTasks();
      const fabricRows = getProduction().fabric_stock || [];
      const hasOpen = state.data && state.data.has_open_shift;

      mainButton.textContent = hasOpen ? "Закрыть смену" : "Открыть смену";
      mainButton.disabled = Boolean(shift && shift.status === "closed");

      mount.innerHTML = `
        <div class="screen-head"><div><h2>Сегодня</h2><p>${escapeHtml(employee ? employee.full_name : "Откройте приложение из Telegram")}</p></div><div class="date">${escapeHtml(shift ? shift.date : "сегодня")}</div></div>
        <div class="card shift-card"><div><b>${escapeHtml(shiftText())}</b><span>${escapeHtml(employee ? employee.position : "-")} · профиль ${escapeHtml(employee ? employee.status : "-")}<br>${escapeHtml(shift ? `${shift.start_time || "-"}-${shift.end_time || ""}` : "Начните смену, чтобы вести отчёт")}</span></div><span class="status-chip ${hasOpen ? "" : "gray"}">● ${hasOpen ? "в процессе" : "ожидает"}</span></div>
        <div class="kpi-grid">
          <div class="card kpi"><div class="kpi-top"><span>Отчёт</span><div class="kpi-ico">${sewingIcon()}</div></div><strong>${operations.length}<small> строк</small></strong><span>Операции текущей смены</span><div class="progress"><i style="--w:${Math.min(100, operations.length * 12)}%"></i></div></div>
          <div class="card kpi good"><div class="kpi-top"><span>Задания</span><div class="kpi-ico">✓</div></div><strong>${tasks.length}<small> акт.</small></strong><span>Производственные задания</span><div class="progress sage"><i style="--w:${Math.min(100, tasks.length * 18)}%"></i></div></div>
          <div class="card kpi"><div class="kpi-top"><span>Контуры</span><div class="kpi-ico">▣</div></div><strong>${contourTasks.length}<small> шт</small></strong><span>Доступно раскройщику</span></div>
          <div class="card kpi"><div class="kpi-top"><span>Ткань</span><div class="kpi-ico">▦</div></div><strong>${fabricRows.length}<small> поз.</small></strong><span>Остатки ткани</span></div>
        </div>
        <div class="section-title"><b>Активная операция</b><button data-go="report">отчёт</button></div>
        ${operations.length ? `
          <div class="card active-operation" data-go="report"><div class="op-icon">${sewingIcon()}</div><div><b>${escapeHtml(operations[0].operation_name)}</b><span>${escapeHtml(operations[0].product_size || "-")} · ${escapeHtml(operations[0].product_color || "-")}<br>${escapeHtml(operations[0].quantity)} ${escapeHtml(operations[0].unit)}</span></div><span class="status-chip">отчёт</span></div>
        ` : `<div class="card shift-card"><div><b>Операций пока нет</b><span>Когда появятся строки отчёта, они будут здесь.</span></div><span class="status-chip gray">пусто</span></div>`}
      `;
    }

    function renderOperations() {
      const operations = getReportOperations();
      const selected = operations[state.selectedOperation] || operations[0];
      mainButton.textContent = selected ? "Открыть отчёт" : "Обновить";
      mainButton.disabled = false;

      mount.innerHTML = `
        <div class="screen-head"><div><h2>Операции смены</h2><p>Строки текущего отчёта сотрудника.</p></div><div class="date">${operations.length} строк</div></div>
        <div class="op-list">
          ${operations.length ? operations.map((op, index) => `
            <div class="card op-row ${index === state.selectedOperation ? "selected" : ""}" data-select-operation="${index}">
              <div class="op-icon">${sewingIcon()}</div>
              <div class="op-meta"><b>${escapeHtml(op.operation_name)}</b><span>${escapeHtml(op.product_size || "-")} · ${escapeHtml(op.product_color || "-")}<br>${escapeHtml(op.quantity)} ${escapeHtml(op.unit)}</span><div class="progress ${Number(op.quantity || 0) > 0 ? "sage" : ""}"><i style="--w:${Math.min(100, Number(op.quantity || 0))}%"></i></div></div>
              <div class="op-num"><strong>${escapeHtml(op.quantity)}</strong>${escapeHtml(op.unit)}</div>
            </div>
          `).join("") : itemEmpty("Операций за текущую смену пока нет.")}
        </div>
      `;
    }

    function renderReport() {
      const operations = getReportOperations();
      const feedback = getFeedbackRows();
      const op = operations[state.selectedOperation] || operations[0];
      const history = getHistory();
      ensureUserDefaults();
      mainButton.textContent = "Обновить отчёт";
      mainButton.disabled = false;

      const historySummary = history && history.summary ? history.summary : null;
      const historyShifts = history && history.shifts ? history.shifts : [];
      const historyOperations = history && history.operations ? history.operations : [];

      mount.innerHTML = `
        <div class="screen-head"><div><h2>Отчёт по операции</h2><p>Просмотр данных текущей смены.</p></div><div class="date">${operations.length} строк</div></div>
        ${op ? `
          <div class="card field-card"><label>Операция</label><div class="select-row"><div class="op-icon">${sewingIcon()}</div><div><b>${escapeHtml(op.operation_name)}</b><span>${escapeHtml(op.product_size || "-")} · ${escapeHtml(op.product_color || "-")}</span></div><span>✓</span></div></div>
          <div class="card field-card"><label>Количество</label><div class="select-row"><div class="op-icon">✓</div><div><b>${escapeHtml(op.quantity)} ${escapeHtml(op.unit)}</b><span>Сохранено в сменном отчёте</span></div><span class="status-chip">принято</span></div></div>
        ` : `<div class="card field-card">${itemEmpty("В текущей смене пока нет строк отчёта.")}</div>`}
        <div class="section-title"><b>Обратная связь</b><span>${feedback.length}</span></div>
        <div class="op-list">
          ${feedback.length ? feedback.map((row) => `
            <div class="card field-card"><label>${escapeHtml(row.category)} · ${escapeHtml(row.date)}</label><div class="textarea">${escapeHtml(row.message)}</div></div>
          `).join("") : `<div class="card field-card">${itemEmpty("Сообщений за смену нет.")}</div>`}
        </div>
        <div class="card field-card">
          <label>Написать администратору</label>
          <div class="form-grid">
            <div class="field full"><label>Раздел</label><select id="feedbackCategory"><option value="Производство">Производство</option><option value="Бытовое">Бытовое</option></select></div>
            <div class="field full"><label>Сообщение</label><textarea id="feedbackMessage" placeholder="Напишите сообщение"></textarea></div>
          </div>
          <div class="button-row"><button class="small-button secondary" data-history-action="load">Обновить историю</button><button class="small-button" data-feedback-action="send">Отправить</button></div>
        </div>
        <div class="section-title"><b>Моя история</b><button data-history-action="load">показать</button></div>
        <div class="card field-card">
          <div class="form-grid">
            <div class="field"><label>Начало</label><input id="userStartDate" type="date" value="${escapeHtml(state.userStartDate)}"></div>
            <div class="field"><label>Окончание</label><input id="userEndDate" type="date" value="${escapeHtml(state.userEndDate)}"></div>
          </div>
          <div class="button-row"><button class="small-button secondary" data-history-action="load">Показать</button></div>
        </div>
        <div class="kpi-grid">
          <div class="card kpi"><div class="kpi-top"><span>Смены</span><div class="kpi-ico">◷</div></div><strong>${historySummary ? historySummary.shift_count : 0}<small> шт</small></strong><span>За выбранный период</span></div>
          <div class="card kpi good"><div class="kpi-top"><span>Часы</span><div class="kpi-ico">✓</div></div><strong>${escapeHtml(historySummary ? historySummary.total_time : "0:00")}</strong><span>Отработано суммарно</span></div>
        </div>
        <div class="section-title"><b>Смены за период</b><span>${historyShifts.length}</span></div>
        <div class="op-list">
          ${historyShifts.length ? historyShifts.slice(0, 8).map((shift) => `
            <div class="card report-row"><div><b>${escapeHtml(shift.date)}</b><span>${escapeHtml(shift.start_time || "-")} — ${escapeHtml(shift.end_time || "-")} · ${escapeHtml(shift.status)}</span></div><span class="status-chip gray">${escapeHtml(shift.total_time || "-")}</span></div>
          `).join("") : itemEmpty("За выбранный период смен пока нет.")}
        </div>
        <div class="section-title"><b>Операции за период</b><span>${historyOperations.length}</span></div>
        <div class="op-list">
          ${historyOperations.length ? historyOperations.slice(0, 10).map((operation) => `
            <div class="card report-row"><div><b>${escapeHtml(operation.operation)}</b><span>Итого по операции</span></div><span class="status-chip">${escapeHtml(operation.quantity)} ${escapeHtml(operation.unit)}</span></div>
          `).join("") : itemEmpty("Операций за выбранный период пока нет.")}
        </div>
      `;
    }

    function resetOrderDraft() {
      const firstProduct = getRouteCatalog()[0];
      state.orderMode = "create";
      state.orderProduct = firstProduct ? firstProduct.product_name : "";
      state.orderTaskType = "cutting";
      state.orderRouteStep = "";
      state.orderMaterial = "Ткань";
      state.orderSizes = [];
      state.orderColors = [];
      state.orderQuantity = "1";
    }

    function ensureOrderDraftDefaults() {
      const catalog = getRouteCatalog();
      if (!catalog.length) return null;

      let product = routeProduct(state.orderProduct);
      if (!product) {
        product = catalog[0];
        state.orderProduct = product.product_name;
      }

      const availableSizes = product.sizes || [];
      const availableColors = getOrderColors();
      state.orderSizes = state.orderSizes.filter((size) => availableSizes.includes(size));
      state.orderColors = state.orderColors.filter((color) => availableColors.includes(color));

      const operations = routeOperations(product);
      if (state.orderTaskType === "route" && !operations.some((operation) => String(operation.index) === String(state.orderRouteStep))) {
        state.orderRouteStep = operations[0] ? String(operations[0].index) : "";
      }

      return product;
    }

    function syncOrderDraft() {
      const product = document.getElementById("orderProduct");
      const taskType = document.getElementById("orderTaskType");
      const routeStep = document.getElementById("orderRouteStep");
      const material = document.getElementById("orderMaterial");
      const quantity = document.getElementById("orderQuantity");
      const previousProduct = state.orderProduct;

      if (product) state.orderProduct = product.value;
      if (taskType) state.orderTaskType = taskType.value;
      if (routeStep) state.orderRouteStep = routeStep.value;
      if (material) state.orderMaterial = material.value;
      if (quantity) state.orderQuantity = quantity.value;

      if (previousProduct && previousProduct !== state.orderProduct) {
        state.orderSizes = [];
        state.orderColors = [];
        state.orderRouteStep = "";
      }

      ensureOrderDraftDefaults();
    }

    function toggleOrderValue(kind, value) {
      const key = kind === "size" ? "orderSizes" : "orderColors";
      const values = state[key];
      state[key] = values.includes(value) ? values.filter((item) => item !== value) : [...values, value];
      render();
    }

    function renderChoiceChips(kind, values, selectedValues) {
      return `<div class="choice-grid">${values.map((value) => `
        <button class="choice-chip ${selectedValues.includes(value) ? "active" : ""}" data-order-${kind}="${escapeHtml(value)}">${escapeHtml(value)}</button>
      `).join("")}</div>`;
    }

    async function createOrderTask() {
      if (!state.data || !state.data.is_admin) return;
      syncOrderDraft();
      mainButton.disabled = true;

      try {
        const data = await api("/api/production/create-order-task", {
          product_name: state.orderProduct,
          task_type: state.orderTaskType,
          route_step_index: state.orderRouteStep,
          material_name: state.orderTaskType === "cutting" ? state.orderMaterial : "",
          sizes: state.orderSizes,
          colors: state.orderColors,
          quantity: state.orderQuantity,
        });

        if (!data.ok) {
          showToast("Задание", data.message || "Не удалось создать задание.");
          mainButton.disabled = false;
          return;
        }

        state.data.production = data.production || state.data.production;
        if (data.routes) state.data.routes = data.routes;
        state.orderMode = "list";
        render();
        showToast("Задание", data.message || "Задание создано.");
      } catch (error) {
        showToast("Ошибка", "Не удалось создать задание.");
        mainButton.disabled = false;
      }
    }

    async function deleteOrderTask() {
      if (!state.data || !state.data.is_admin) return;
      const productionTasks = getTasks().map((task) => ({...task, task_kind: "production"}));
      const routeRows = getRouteTasks().map((task) => ({...task, task_kind: "route"}));
      const current = [...productionTasks, ...routeRows][state.selectedOrder] || [...productionTasks, ...routeRows][0];

      if (!current) {
        showToast("Задание", "Выберите задание.");
        return;
      }

      const confirmed = window.confirm(`Удалить задание #${current.id}?`);
      if (!confirmed) return;

      mainButton.disabled = true;

      try {
        const data = await api("/api/production/delete-order-task", {
          task_kind: current.task_kind,
          task_id: current.id,
        });

        if (!data.ok) {
          showToast("Задание", data.message || "Не удалось удалить задание.");
          mainButton.disabled = false;
          return;
        }

        state.data.production = data.production || state.data.production;
        if (data.routes) state.data.routes = data.routes;
        state.selectedOrder = 0;
        render();
        showToast("Задание", data.message || "Задание удалено.");
      } catch (error) {
        showToast("Ошибка", "Не удалось удалить задание.");
        mainButton.disabled = false;
      }
    }

    function renderOrderCreate() {
      const product = ensureOrderDraftDefaults();
      const catalog = getRouteCatalog();
      const operations = routeOperations(product);
      const sizes = product ? product.sizes || [] : [];
      const colors = getOrderColors();
      const operationOptions = operations.map((operation) => `
        <option value="${operation.index}" ${String(operation.index) === String(state.orderRouteStep) ? "selected" : ""}>${escapeHtml(operation.position)} — ${escapeHtml(operation.operation)}</option>
      `).join("");

      mainButton.textContent = "Создать задание";
      mainButton.disabled = false;

      mount.innerHTML = `
        <div class="screen-head"><div><h2>Создать задание</h2><p>Массовое задание по размерам и цветам.</p></div><div class="date">админ</div></div>
        <div class="card field-card">
          <div class="form-grid">
            <div class="field full"><label>Изделие</label><select id="orderProduct">${catalog.map((item) => `<option value="${escapeHtml(item.product_name)}" ${item.product_name === state.orderProduct ? "selected" : ""}>${escapeHtml(item.product_name)}</option>`).join("")}</select></div>
            <div class="field full"><label>Тип задания</label><select id="orderTaskType"><option value="cutting" ${state.orderTaskType === "cutting" ? "selected" : ""}>Раскрой</option><option value="route" ${state.orderTaskType === "route" ? "selected" : ""}>Операция по маршруту</option></select></div>
            ${state.orderTaskType === "route" ? `<div class="field full"><label>Операция</label><select id="orderRouteStep">${operationOptions || `<option value="">Нет операций</option>`}</select></div>` : ""}
            ${state.orderTaskType === "cutting" ? `<div class="field full"><label>Материал</label><select id="orderMaterial"><option value="Ткань" selected>Ткань</option></select></div>` : `<div class="field full"><label>Вход</label><input value="Полуфабрикат" disabled></div>`}
            ${state.orderTaskType === "route" ? `<div class="field full"><label>Количество на каждую комбинацию</label><input id="orderQuantity" type="number" min="1" step="1" value="${escapeHtml(state.orderQuantity || "1")}"></div>` : ""}
          </div>
        </div>
        <div class="card field-card"><label>Размеры</label>${sizes.length ? renderChoiceChips("size", sizes, state.orderSizes) : itemEmpty("У изделия нет размеров.")}</div>
        <div class="card field-card"><label>${state.orderTaskType === "cutting" ? "Цвета ткани" : "Цвета изделия"}</label>${colors.length ? renderChoiceChips("color", colors, state.orderColors) : itemEmpty("У изделия нет цветов.")}</div>
        <div class="button-row"><button class="small-button secondary" data-order-action="cancel">К списку</button><button class="small-button" data-order-action="create">Создать</button></div>
      `;
    }

    function renderOrders() {
      if (state.data && state.data.is_admin && state.orderMode === "create") {
        renderOrderCreate();
        return;
      }

      const productionTasks = state.data && state.data.is_admin ? getTasks() : getContourTasks();
      const routeTasks = getRouteTasks();
      const tasks = productionTasks.map((task) => ({...task, task_kind: "production"}));
      const routeRows = routeTasks.map((task) => ({...task, task_kind: "route"}));
      const allTasks = [...tasks, ...routeRows];
      const current = allTasks[state.selectedOrder] || allTasks[0];
      mainButton.textContent = state.data && state.data.is_admin ? "Создать задание" : "Обновить статус";
      mainButton.disabled = false;

      mount.innerHTML = `
        <div class="screen-head"><div><h2>Заказы в работе</h2><p>${state.data && state.data.is_admin ? "Создание и контроль заданий." : "Доступные задания для вашей должности."}</p></div><div class="date">${allTasks.length} активных</div></div>
        ${state.data && state.data.is_admin ? `<div class="card shift-card" data-order-action="new"><div><b>Создать задание</b><span>Раскрой, пошив и другие операции по маршруту.</span></div><span class="status-chip">+</span></div>` : ""}
        <div class="op-list">
          ${allTasks.length ? `
          ${tasks.map((task, index) => `
            <div class="card order-card ${index === state.selectedOrder ? "selected" : ""}" data-select-order="${index}">
              <div class="order-head"><div class="op-icon">▣</div><div><b>Задание #${escapeHtml(task.id)}</b><span>${escapeHtml(task.product_name)}</span></div><span class="status-chip ${task.status === "active" ? "warn" : ""}">${escapeHtml(task.status_text || task.status)}</span></div>
              <div class="progress"><i style="--w:${progressForTask(task)}%"></i></div>
              <div class="order-foot"><span>${escapeHtml((task.sizes || []).join(", ") || "-")}</span><span>${progressForTask(task)}%</span></div>
            </div>
          `).join("")}
          ${routeRows.map((task, routeIndex) => {
            const index = tasks.length + routeIndex;
            return `
              <div class="card order-card ${index === state.selectedOrder ? "selected" : ""}" data-select-order="${index}">
                <div class="order-head"><div class="op-icon">▣</div><div><b>Маршрут #${escapeHtml(task.id)}</b><span>${escapeHtml(task.product_name)} · ${escapeHtml(task.position)}</span></div><span class="status-chip gray">${escapeHtml(task.operation)}</span></div>
                <div class="order-foot"><span>${escapeHtml(task.product_size)} · ${escapeHtml(task.product_color)}</span><span>${escapeHtml(task.quantity)} шт</span></div>
              </div>
            `;
          }).join("")}
          ` : itemEmpty("Активных заданий пока нет.")}
        </div>
        <div class="section-title"><b>Детали выбранного</b><span>${current ? progressForTask(current) : 0}%</span></div>
        ${current && current.task_kind === "production" ? `
          <div class="card order-detail"><div class="order-head"><div class="op-icon">${sewingIcon()}</div><div><b>Задание #${escapeHtml(current.id)}</b><span>${escapeHtml(current.product_name)}</span></div><span class="status-chip">${escapeHtml(current.status_text || current.status)}</span></div><div class="detail-grid"><div class="detail-box"><span>Размеры</span><strong>${escapeHtml((current.sizes || []).join(", ") || "-")}</strong></div><div class="detail-box"><span>Цвета</span><strong>${escapeHtml((current.color_labels || current.colors || []).join(", ") || "-")}</strong></div><div class="detail-box"><span>Статус</span><strong>${escapeHtml(current.status_text || current.status)}</strong></div><div class="detail-box"><span>Создано</span><strong>${escapeHtml((current.created_at || "").slice(0, 10) || "-")}</strong></div></div></div>
        ` : current ? `
          <div class="card order-detail"><div class="order-head"><div class="op-icon">${sewingIcon()}</div><div><b>Маршрут #${escapeHtml(current.id)}</b><span>${escapeHtml(current.product_name)}</span></div><span class="status-chip">${escapeHtml(current.position)}</span></div><div class="detail-grid"><div class="detail-box"><span>Операция</span><strong>${escapeHtml(current.operation)}</strong></div><div class="detail-box"><span>Размер</span><strong>${escapeHtml(current.product_size || "-")}</strong></div><div class="detail-box"><span>Цвет</span><strong>${escapeHtml(current.product_color || "-")}</strong></div><div class="detail-box"><span>Количество</span><strong>${escapeHtml(current.quantity || 0)} шт</strong></div></div></div>
        ` : `<div class="card order-detail">${itemEmpty("Детали появятся после создания задания.")}</div>`}
        ${state.data && state.data.is_admin && current ? `<div class="button-row"><button class="small-button danger" data-order-action="delete">Удалить задание</button></div>` : ""}
      `;
    }

    function renderAnalytics() {
      const operations = getReportOperations();
      const feedback = getFeedbackRows();
      const tasks = getTasks();
      const fabricRows = getProduction().fabric_stock || [];
      const formed = tasks.filter((task) => task.status === "formed").length;
      const inCutting = tasks.filter((task) => task.status === "in_cutting" || task.status === "contours_done").length;
      const active = tasks.filter((task) => task.status === "active").length;
      const total = Math.max(tasks.length, 1);
      const donePercent = Math.round(formed / total * 100);

      mainButton.textContent = "Открыть заказы";
      mainButton.disabled = false;

      mount.innerHTML = `
        <div class="screen-head"><div><h2>Статус производства</h2><p>Аналитика по текущим данным миниаппа.</p></div><div class="date">сейчас</div></div>
        <div class="card chart-card">
          <div class="chart-top"><div><b>Готовый крой</b><strong>${formed}<small> из ${tasks.length}</small></strong><small>сформированные задания</small></div><div class="ring" style="--p:${donePercent}"><strong>${donePercent}%</strong></div></div>
          <svg class="chart" viewBox="0 0 330 150" role="img" aria-label="График производства">
            <defs><linearGradient id="area" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#c36f55" stop-opacity=".28"/><stop offset="1" stop-color="#c36f55" stop-opacity="0"/></linearGradient></defs>
            <path d="M10 130H320" stroke="rgba(80,55,36,.16)"/><path d="M10 95H320" stroke="rgba(80,55,36,.12)"/><path d="M10 60H320" stroke="rgba(80,55,36,.12)"/><path d="M10 25H320" stroke="rgba(80,55,36,.12)"/>
            <path d="M12 126 C45 108,54 106,78 92 C103 78,110 85,132 70 C155 52,168 64,190 48 C215 32,232 54,258 42 C282 31,296 30,318 22 L318 136 L12 136 Z" fill="url(#area)"/>
            <path d="M12 126 C45 108,54 106,78 92 C103 78,110 85,132 70 C155 52,168 64,190 48 C215 32,232 54,258 42 C282 31,296 30,318 22" fill="none" stroke="#c36f55" stroke-width="4" stroke-linecap="round"/>
          </svg>
          <div class="mini-metrics">
            <div class="card mini-metric"><div class="ring" style="--p:${Math.round(operations.length / Math.max(operations.length, 1) * 100)}"><strong>${operations.length}</strong></div><b>Операции</b><span>в отчёте</span></div>
            <div class="card mini-metric"><div class="ring" style="--p:${Math.round(inCutting / total * 100)}"><strong>${inCutting}</strong></div><b>В раскрое</b><span>заданий</span></div>
            <div class="card mini-metric"><div class="ring" style="--p:${Math.round(active / total * 100)}"><strong>${active}</strong></div><b>Ожидают</b><span>контуры</span></div>
          </div>
        </div>
        <div class="section-title"><b>Показатели</b><button data-go="orders">все заказы</button></div>
        <div class="op-list">
          <div class="card shift-card"><div><b>Остатки ткани</b><span>${fabricRows.length} позиций</span></div><span class="status-chip gray">склад</span></div>
          <div class="card shift-card"><div><b>Обратная связь</b><span>${feedback.length} сообщений за смену</span></div><span class="status-chip gray">связь</span></div>
        </div>
      `;
    }

    function renderAdminTabs() {
      const sections = [
        ["reports", "Отчёты"],
        ["employees", "Сотрудники"],
        ["shifts", "Смены"],
        ["feedback", "Связь"],
      ];

      return `<div class="segment-row">${sections.map(([id, label]) => `
        <button class="segment-button ${state.adminSection === id ? "active" : ""}" data-admin-section="${id}">${label}</button>
      `).join("")}</div>`;
    }

    function renderAdminReports(admin) {
      ensureAdminDefaults();
      const report = getAdminReport();
      const totals = adminReportTotals(report);
      const employees = admin && admin.employees ? admin.employees : [];
      const employeeOptions = employees.map((employee) => `
        <option value="${escapeHtml(employee.id)}" ${String(employee.id) === String(state.adminEmployeeId) ? "selected" : ""}>${escapeHtml(employee.full_name)} · ${escapeHtml(employee.position)}</option>
      `).join("");
      const isEmployeeReport = state.adminReportType === "employee";
      const summaryHtml = report && report.type === "employee" ? `
        ${report.employee_summary ? `
          <div class="card report-row"><div><b>${escapeHtml(report.employee_summary.full_name)}</b><span>${escapeHtml(report.employee_summary.position)} · ${escapeHtml(report.employee_summary.shift_count)} смен · ${escapeHtml(report.employee_summary.total_time)}</span></div><span class="status-chip">сотрудник</span></div>
        ` : itemEmpty("По выбранному сотруднику нет данных.")}
      ` : `
        ${(report && report.summary && report.summary.length) ? report.summary.slice(0, 8).map((row) => `
          <div class="card report-row"><div><b>${escapeHtml(row.full_name)}</b><span>${escapeHtml(row.shift_count)} смен · ${escapeHtml(row.total_time)}</span></div><span class="status-chip gray">ID ${escapeHtml(row.employee_id)}</span></div>
        `).join("") : itemEmpty("За выбранный период закрытых смен пока нет.")}
      `;
      const shifts = report && report.type === "employee" ? (report.employee_shifts || []) : (report ? report.shifts || [] : []);
      const operations = report && report.type === "employee" ? (report.employee_operations || []) : (report ? report.operations || [] : []);
      const operationsHtml = operations.length ? operations.slice(0, 10).map((operation) => `
        <div class="card report-row"><div><b>${escapeHtml(operation.operation)}</b><span>${escapeHtml(operation.employee || "")}${operation.employee ? " · " : ""}${escapeHtml(operation.date || "")}${operation.group ? `<br>${escapeHtml(operation.group)} · ${escapeHtml(operation.size || "-")} · ${escapeHtml(operation.color || "-")}` : ""}</span></div><span class="status-chip">${escapeHtml(operation.quantity)} ${escapeHtml(operation.unit)}</span></div>
      `).join("") : itemEmpty("Операций за выбранный период пока нет.");

      mainButton.textContent = "Выгрузить отчёт";

      return `
        <div class="screen-head"><div><h2>Админ отчёты</h2><p>Сегодня, период или конкретный сотрудник.</p></div><div class="date">${escapeHtml(report ? `${report.start_date} — ${report.end_date}` : "период")}</div></div>
        ${renderAdminTabs()}
        <div class="card field-card">
          <div class="form-grid">
            <div class="field full"><label>Тип отчёта</label><select id="adminReportType"><option value="today" ${state.adminReportType === "today" ? "selected" : ""}>Сегодня</option><option value="period" ${state.adminReportType === "period" ? "selected" : ""}>Период</option><option value="employee" ${isEmployeeReport ? "selected" : ""}>Сотрудник</option></select></div>
            <div class="field"><label>Начало</label><input id="adminStartDate" type="date" value="${escapeHtml(state.adminStartDate)}"></div>
            <div class="field"><label>Окончание</label><input id="adminEndDate" type="date" value="${escapeHtml(state.adminEndDate)}"></div>
            <div class="field full"><label>Сотрудник</label><select id="adminEmployeeId" ${isEmployeeReport ? "" : "disabled"}>${employeeOptions || `<option value="">Нет сотрудников</option>`}</select></div>
          </div>
          <div class="button-row"><button class="small-button secondary" data-admin-action="load-report">Показать</button><button class="small-button" data-admin-action="export-report">Выгрузить</button></div>
        </div>
        <div class="kpi-grid">
          <div class="card kpi"><div class="kpi-top"><span>Смены</span><div class="kpi-ico">◷</div></div><strong>${totals.shifts}<small> шт</small></strong><span>Закрытые смены</span></div>
          <div class="card kpi good"><div class="kpi-top"><span>Часы</span><div class="kpi-ico">✓</div></div><strong>${escapeHtml(minutesLabel(totals.minutes))}</strong><span>Суммарно отработано</span></div>
          <div class="card kpi"><div class="kpi-top"><span>Операции</span><div class="kpi-ico">${sewingIcon()}</div></div><strong>${totals.operations}<small> строк</small></strong><span>Строки отчёта</span></div>
          <div class="card kpi"><div class="kpi-top"><span>Сотрудники</span><div class="kpi-ico">◎</div></div><strong>${totals.employees}<small> чел</small></strong><span>В выборке</span></div>
        </div>
        <div class="section-title"><b>${escapeHtml(report ? report.title : "Отчёт")}</b><button data-admin-action="export-report">выгрузить</button></div>
        <div class="op-list">${summaryHtml}</div>
        <div class="section-title"><b>Смены</b><span>${shifts.length}</span></div>
        <div class="op-list">
          ${shifts.length ? shifts.slice(0, 8).map((shift) => `
            <div class="card report-row"><div><b>${escapeHtml(shift.employee || "Сотрудник")}</b><span>${escapeHtml(shift.date)} · ${escapeHtml(shift.start_time || "-")} — ${escapeHtml(shift.end_time || "-")}</span></div><span class="status-chip gray">${escapeHtml(shift.total_time || "-")}</span></div>
          `).join("") : itemEmpty("Смен за выбранный период нет.")}
        </div>
        <div class="section-title"><b>Операции</b><span>${operations.length}</span></div>
        <div class="op-list">${operationsHtml}</div>
      `;
    }

    function renderAdminEmployees(admin) {
      const employees = admin && admin.employees ? admin.employees : [];
      const pending = admin && admin.pending_employees ? admin.pending_employees : [];
      const positions = admin && admin.positions ? admin.positions : [];
      mainButton.textContent = "Обновить сотрудников";

      const positionOptions = (employee) => positions.map((position) => `
        <option value="${escapeHtml(position)}" ${employee.position === position ? "selected" : ""}>${escapeHtml(position)}</option>
      `).join("");
      const employeeCards = employees.length ? employees.map((employee) => `
        <div class="card field-card">
          <label>ID ${escapeHtml(employee.id)} · ${escapeHtml(employee.status)}</label>
          <div class="report-row"><div><b>${escapeHtml(employee.full_name)}</b><span>${escapeHtml(employee.position)} · TG ${escapeHtml(employee.telegram_id || "-")}</span></div><span class="status-chip ${employee.status === "active" ? "" : "gray"}">${escapeHtml(employee.status)}</span></div>
          <div class="form-grid"><div class="field full"><select id="employeePosition${escapeHtml(employee.id)}">${positionOptions(employee)}</select></div></div>
          <div class="button-row"><button class="small-button secondary" data-admin-action="position" data-employee-id="${escapeHtml(employee.id)}">Должность</button><button class="small-button ${employee.status === "active" ? "danger" : ""}" data-admin-action="${employee.status === "active" ? "inactive" : "active"}" data-employee-id="${escapeHtml(employee.id)}">${employee.status === "active" ? "Отключить" : "Активировать"}</button></div>
        </div>
      `).join("") : itemEmpty("Сотрудников пока нет.");
      const pendingCards = pending.length ? pending.map((employee) => `
        <div class="card field-card">
          <label>Заявка · ${escapeHtml(employee.registered_at || "")}</label>
          <div class="report-row"><div><b>${escapeHtml(employee.full_name)}</b><span>${escapeHtml(employee.position)} · TG ${escapeHtml(employee.telegram_id || "-")}</span></div><span class="status-chip warn">pending</span></div>
          <div class="button-row"><button class="small-button secondary" data-admin-action="inactive" data-employee-id="${escapeHtml(employee.id)}">Отклонить</button><button class="small-button" data-admin-action="active" data-employee-id="${escapeHtml(employee.id)}">Активировать</button></div>
        </div>
      `).join("") : itemEmpty("Новых заявок нет.");

      return `
        <div class="screen-head"><div><h2>Сотрудники</h2><p>Заявки, статусы и должности.</p></div><div class="date">${employees.length} всего</div></div>
        ${renderAdminTabs()}
        <div class="kpi-grid">
          <div class="card kpi"><div class="kpi-top"><span>Заявки</span><div class="kpi-ico">◎</div></div><strong>${pending.length}<small> шт</small></strong><span>Ожидают решения</span></div>
          <div class="card kpi good"><div class="kpi-top"><span>Активные</span><div class="kpi-ico">✓</div></div><strong>${(admin.active_employees || []).length}<small> чел</small></strong><span>Могут работать</span></div>
        </div>
        <div class="section-title"><b>Заявки</b><span>${pending.length}</span></div>
        <div class="op-list">${pendingCards}</div>
        <div class="section-title"><b>Список сотрудников</b><button data-admin-action="refresh">обновить</button></div>
        <div class="op-list">${employeeCards}</div>
      `;
    }

    function renderAdminShifts(admin) {
      const openShifts = admin && admin.open_shifts ? admin.open_shifts : [];
      const recentShifts = admin && admin.recent_shifts ? admin.recent_shifts : [];
      mainButton.textContent = "Обновить смены";

      return `
        <div class="screen-head"><div><h2>Смены</h2><p>Открытые и последние смены сотрудников.</p></div><div class="date">${openShifts.length} открыто</div></div>
        ${renderAdminTabs()}
        <div class="card field-card">
          <div class="form-grid"><div class="field full"><label>Время закрытия</label><input id="adminShiftEndTime" type="time" value="${escapeHtml(state.adminShiftEndTime)}"></div></div>
        </div>
        <div class="section-title"><b>Открытые смены</b><span>${openShifts.length}</span></div>
        <div class="op-list">
          ${openShifts.length ? openShifts.map((shift) => `
            <div class="card field-card"><label>ID ${escapeHtml(shift.id)}</label><div class="report-row"><div><b>${escapeHtml(shift.employee)}</b><span>${escapeHtml(shift.date)} · начало ${escapeHtml(shift.start_time)}</span></div><span class="status-chip">open</span></div><div class="button-row"><button class="small-button secondary" data-admin-action="refresh">Обновить</button><button class="small-button" data-admin-action="close-shift" data-shift-id="${escapeHtml(shift.id)}">Закрыть</button></div></div>
          `).join("") : itemEmpty("Открытых смен сейчас нет.")}
        </div>
        <div class="section-title"><b>Последние смены</b><button data-admin-action="refresh">обновить</button></div>
        <div class="op-list">
          ${recentShifts.length ? recentShifts.map((shift) => `
            <div class="card field-card"><label>ID ${escapeHtml(shift.id)} · ${escapeHtml(shift.status)}</label><div class="report-row"><div><b>${escapeHtml(shift.employee)}</b><span>${escapeHtml(shift.date)} · ${escapeHtml(shift.start_time || "-")} — ${escapeHtml(shift.end_time || "-")}<br>Операций: ${escapeHtml(shift.operation_count || 0)}</span></div><span class="status-chip gray">${escapeHtml(shift.status)}</span></div><div class="button-row"><button class="small-button secondary" data-admin-action="refresh">Обновить</button><button class="small-button danger" data-admin-action="delete-shift" data-shift-id="${escapeHtml(shift.id)}">Удалить</button></div></div>
          `).join("") : itemEmpty("Последних смен пока нет.")}
        </div>
      `;
    }

    function renderAdminFeedback(admin) {
      ensureAdminDefaults();
      const feedback = admin && admin.feedback ? admin.feedback : [];
      mainButton.textContent = "Обновить связь";

      return `
        <div class="screen-head"><div><h2>Связь</h2><p>Сообщения сотрудников за выбранный период.</p></div><div class="date">${feedback.length} сообщений</div></div>
        ${renderAdminTabs()}
        <div class="card field-card">
          <div class="form-grid">
            <div class="field"><label>Начало</label><input id="adminStartDate" type="date" value="${escapeHtml(state.adminStartDate)}"></div>
            <div class="field"><label>Окончание</label><input id="adminEndDate" type="date" value="${escapeHtml(state.adminEndDate)}"></div>
          </div>
          <div class="button-row"><button class="small-button secondary" data-admin-action="refresh">Обновить всё</button><button class="small-button" data-admin-action="load-feedback">Показать связь</button></div>
        </div>
        <div class="op-list">
          ${feedback.length ? feedback.map((row) => `
            <div class="card report-row"><div><b>${escapeHtml(row.employee)} · ${escapeHtml(row.category)}</b><span>${escapeHtml(row.date)} ${escapeHtml(row.time || "")} · ${escapeHtml(row.position)}<br>${escapeHtml(row.message)}</span></div><span class="status-chip gray">${row.shift_id ? `#${escapeHtml(row.shift_id)}` : "-"}</span></div>
          `).join("") : itemEmpty("Сообщений за выбранный период нет.")}
        </div>
      `;
    }

    function renderAdmin() {
      if (!state.data || !state.data.is_admin) {
        mainButton.textContent = "Обновить";
        mainButton.disabled = false;
        mount.innerHTML = `
          <div class="screen-head"><div><h2>Админ</h2><p>Раздел доступен только администратору.</p></div></div>
          <div class="card field-card">${itemEmpty("Нет прав администратора.")}</div>
        `;
        return;
      }

      ensureAdminDefaults();
      const admin = getAdmin();
      mainButton.disabled = false;

      if (state.adminSection === "employees") {
        mount.innerHTML = renderAdminEmployees(admin);
        return;
      }
      if (state.adminSection === "shifts") {
        mount.innerHTML = renderAdminShifts(admin);
        return;
      }
      if (state.adminSection === "feedback") {
        mount.innerHTML = renderAdminFeedback(admin);
        return;
      }

      mount.innerHTML = renderAdminReports(admin);
    }

    function render() {
      if (!state.data) return;
      document.getElementById("roleLabel").textContent = roleLabel();
      renderBottomNav();
      renderTopTabs();
      if (state.screen === "shift") renderShift();
      if (state.screen === "operations") renderOperations();
      if (state.screen === "report") renderReport();
      if (state.screen === "analytics") renderAnalytics();
      if (state.screen === "orders") renderOrders();
      if (state.screen === "admin") renderAdmin();
      renderBottomNav();
      renderTopTabs();
    }

    function setScreen(screen) {
      state.screen = screen;
      render();
    }

    async function refreshState(message = "") {
      mainButton.disabled = true;
      try {
        const data = await api("/api/app/state", {message});
        state.data = data;
        if (message) showToast("Готово", message);
        render();
      } catch (error) {
        showToast("Ошибка", "Не удалось связаться с сервером.");
      }
    }

    async function shiftAction(action) {
      mainButton.disabled = true;
      const data = await api(`/api/shift/${action}`);
      state.data = data;
      render();
      showToast("Смена", data.message || "Данные обновлены.");
    }

    document.addEventListener("click", (event) => {
      const orderAction = event.target.closest("[data-order-action]");
      if (orderAction) {
        syncOrderDraft();
        if (orderAction.dataset.orderAction === "new") {
          resetOrderDraft();
          render();
        }
        if (orderAction.dataset.orderAction === "cancel") {
          state.orderMode = "list";
          render();
        }
        if (orderAction.dataset.orderAction === "create") {
          createOrderTask();
        }
        if (orderAction.dataset.orderAction === "delete") {
          deleteOrderTask();
        }
        return;
      }

      const orderSize = event.target.closest("[data-order-size]");
      if (orderSize) {
        syncOrderDraft();
        toggleOrderValue("size", orderSize.dataset.orderSize);
        return;
      }

      const orderColor = event.target.closest("[data-order-color]");
      if (orderColor) {
        syncOrderDraft();
        toggleOrderValue("color", orderColor.dataset.orderColor);
        return;
      }

      const adminHomePeriod = event.target.closest("[data-admin-home-period]");
      if (adminHomePeriod) {
        state.adminHomePeriod = adminHomePeriod.dataset.adminHomePeriod;
        state.adminHomeView = "overview";
        state.adminHomeEmployee = "";
        render();
        return;
      }

      const adminHomeView = event.target.closest("[data-admin-home-view]");
      if (adminHomeView) {
        state.adminHomeView = adminHomeView.dataset.adminHomeView;
        state.adminHomeEmployee = "";
        render();
        return;
      }

      const adminHomeEmployee = event.target.closest("[data-admin-home-employee]");
      if (adminHomeEmployee) {
        state.adminHomeEmployee = adminHomeEmployee.dataset.adminHomeEmployee;
        state.adminHomeView = "employee";
        render();
        return;
      }

      const go = event.target.closest("[data-go]");
      if (go) {
        setScreen(go.dataset.go);
        return;
      }

      const adminSection = event.target.closest("[data-admin-section]");
      if (adminSection) {
        state.adminSection = adminSection.dataset.adminSection;
        render();
        return;
      }

      const adminAction = event.target.closest("[data-admin-action]");
      if (adminAction) {
        syncAdminForm();
        if (adminAction.dataset.adminAction === "refresh") refreshAdminDashboard();
        if (adminAction.dataset.adminAction === "load-report") loadAdminReport();
        if (adminAction.dataset.adminAction === "export-report") exportAdminReport();
        if (adminAction.dataset.adminAction === "load-feedback") loadAdminFeedback();
        if (adminAction.dataset.adminAction === "active") adminEmployeeStatus(adminAction.dataset.employeeId, "active");
        if (adminAction.dataset.adminAction === "inactive") adminEmployeeStatus(adminAction.dataset.employeeId, "inactive");
        if (adminAction.dataset.adminAction === "position") adminEmployeePosition(adminAction.dataset.employeeId);
        if (adminAction.dataset.adminAction === "close-shift") adminCloseShift(adminAction.dataset.shiftId);
        if (adminAction.dataset.adminAction === "delete-shift") adminDeleteShift(adminAction.dataset.shiftId);
        return;
      }

      const historyAction = event.target.closest("[data-history-action]");
      if (historyAction) {
        loadHistory();
        return;
      }

      const feedbackAction = event.target.closest("[data-feedback-action]");
      if (feedbackAction) {
        sendFeedback();
        return;
      }

      const op = event.target.closest("[data-select-operation]");
      if (op) {
        state.selectedOperation = Number(op.dataset.selectOperation);
        setScreen("operations");
        return;
      }

      const order = event.target.closest("[data-select-order]");
      if (order) {
        state.selectedOrder = Number(order.dataset.selectOrder);
        setScreen("orders");
      }
    });

    mainButton.addEventListener("click", () => {
      if (!state.data) return;
      if (state.screen === "shift") {
        if (state.data.is_admin) {
          refreshAdminDashboard("Главная обновлена.");
          return;
        }
        if (state.data.shift && state.data.shift.status === "closed") return;
        shiftAction(state.data.has_open_shift ? "close" : "open");
        return;
      }
      if (state.screen === "operations") { setScreen("report"); return; }
      if (state.screen === "report") { refreshState("Отчёт обновлён."); return; }
      if (state.screen === "analytics") { setScreen("orders"); return; }
      if (state.screen === "orders" && state.data && state.data.is_admin) {
        if (state.orderMode === "create") { createOrderTask(); return; }
        resetOrderDraft();
        render();
        return;
      }
      if (state.screen === "orders") { refreshState("Статус обновлён."); return; }
      if (state.screen === "admin") {
        if (state.adminSection === "reports") { exportAdminReport(); return; }
        if (state.adminSection === "feedback") { loadAdminFeedback(); return; }
        refreshAdminDashboard();
      }
    });

    document.addEventListener("change", (event) => {
      if (event.target.closest("#orderProduct") || event.target.closest("#orderTaskType") || event.target.closest("#orderRouteStep") || event.target.closest("#orderMaterial") || event.target.closest("#orderQuantity")) {
        syncOrderDraft();
        render();
        return;
      }

      if (!event.target.closest("#adminReportType")) return;
      syncAdminForm();
      render();
    });

    document.getElementById("backBtn").addEventListener("click", () => {
      if (state.screen === "shift" && state.data && state.data.is_admin && state.adminHomeView !== "overview") {
        state.adminHomeView = state.adminHomeView === "employee" ? "employees" : "overview";
        state.adminHomeEmployee = "";
        render();
        return;
      }

      if (state.screen === "orders" && state.orderMode === "create") {
        state.orderMode = "list";
        render();
        return;
      }

      const flow = ["shift", "report", "analytics", "orders", "admin"];
      const index = flow.indexOf(state.screen);
      setScreen(flow[Math.max(0, index - 1)]);
    });

    document.getElementById("menuBtn").addEventListener("click", () => {
      if (state.data && state.data.is_admin) {
        setScreen("admin");
        return;
      }
      showToast("Меню", "Настройки профиля и уведомления подключим позже.");
    });

    refreshState();
  </script>
</body>
</html>
"""


def make_handler(bot_token: str, debug: bool):
    class MiniAppRequestHandler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def do_GET(self):
            path = urlparse(self.path).path

            if path in {"/", "/app"}:
                self.send_html(MINIAPP_HTML)
                return

            if path == "/health":
                self.send_json({"ok": True})
                return

            self.send_json({"ok": False, "message": "Not found"}, status=404)

        def do_POST(self):
            path = urlparse(self.path).path

            allowed_paths = {
                "/api/app/state",
                "/api/shift/status",
                "/api/shift/open",
                "/api/shift/close",
                "/api/report/history",
                "/api/feedback/send",
                "/api/production/fabric-receipt",
                "/api/production/create-task",
                "/api/production/create-order-task",
                "/api/production/delete-order-task",
                "/api/production/submit-contours",
                "/api/routes/create-batch",
                "/api/routes/complete",
                "/api/admin/dashboard",
                "/api/admin/report",
                "/api/admin/report/export",
                "/api/admin/feedback",
                "/api/admin/employee/status",
                "/api/admin/employee/position",
                "/api/admin/shift/close",
                "/api/admin/shift/delete",
                "/api/admin/operation",
            }

            if path not in allowed_paths:
                self.send_json({"ok": False, "message": "Not found"}, status=404)
                return

            payload = self.read_json_body()
            user = authenticate_payload(payload, bot_token, debug)

            if not user or not user.get("id"):
                self.send_json(
                    {
                        "ok": False,
                        "code": "unauthorized",
                        "message": "Откройте приложение из Telegram.",
                        "employee": None,
                        "shift": None,
                    },
                    status=401,
                )
                return

            telegram_id = int(user["id"])

            if path == "/api/admin/report/export":
                export_result = export_admin_report_for_telegram(telegram_id, payload)

                if not export_result.get("ok"):
                    self.send_json(export_result, status=400)
                    return

                self.send_file(export_result["content"], export_result["filename"])
                return

            if path == "/api/app/state":
                result = get_app_state(telegram_id, payload.get("message", ""))
            elif path == "/api/report/history":
                result = get_employee_history_for_telegram(telegram_id, payload)
            elif path == "/api/shift/open":
                action_result = open_shift_for_telegram(telegram_id)
                result = get_app_state(telegram_id, action_result.get("message", ""))
            elif path == "/api/shift/close":
                action_result = close_shift_for_telegram(telegram_id)
                result = get_app_state(telegram_id, action_result.get("message", ""))
            elif path == "/api/feedback/send":
                result = submit_feedback_for_telegram(
                    telegram_id,
                    payload.get("category", ""),
                    payload.get("message", ""),
                )
            elif path == "/api/production/fabric-receipt":
                result = add_fabric_receipt_for_telegram(telegram_id, payload)
            elif path == "/api/production/create-task":
                result = create_production_task_for_telegram(telegram_id, payload)
            elif path == "/api/production/create-order-task":
                result = create_order_task_for_telegram(telegram_id, payload)
            elif path == "/api/production/delete-order-task":
                result = delete_order_task_for_telegram(telegram_id, payload)
            elif path == "/api/production/submit-contours":
                result = submit_production_contours_for_telegram(telegram_id, payload)
            elif path == "/api/routes/create-batch":
                result = create_route_batch_for_telegram(telegram_id, payload)
            elif path == "/api/routes/complete":
                try:
                    batch_id = int(payload.get("batch_id") or 0)
                except (TypeError, ValueError):
                    batch_id = 0

                result = complete_route_task_for_telegram(telegram_id, batch_id)
            elif path == "/api/admin/dashboard":
                result = get_admin_dashboard(telegram_id)
            elif path == "/api/admin/report":
                result = get_admin_report_for_telegram(telegram_id, payload)
            elif path == "/api/admin/feedback":
                result = get_admin_feedback_for_telegram(telegram_id, payload)
            elif path == "/api/admin/employee/status":
                result = set_employee_status_for_admin(telegram_id, payload)
            elif path == "/api/admin/employee/position":
                result = set_employee_position_for_admin(telegram_id, payload)
            elif path == "/api/admin/shift/close":
                result = close_shift_for_admin(telegram_id, payload)
            elif path == "/api/admin/shift/delete":
                result = delete_shift_for_admin(telegram_id, payload)
            elif path == "/api/admin/operation":
                result = operation_action_for_admin(telegram_id, payload)
            else:
                result = get_app_state(telegram_id)

            self.send_json(result)

        def read_json_body(self):
            content_length = int(self.headers.get("Content-Length", "0") or "0")
            raw_body = self.rfile.read(content_length) if content_length else b"{}"

            try:
                return json.loads(raw_body.decode("utf-8"))
            except json.JSONDecodeError:
                return {}

        def send_html(self, html_text: str, status: int = 200):
            body = html_text.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def send_json(self, payload: dict, status: int = 200):
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def send_file(self, content: bytes, filename: str):
            safe_filename = quote(filename)
            self.send_response(200)
            self.send_header(
                "Content-Type",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            self.send_header("Content-Length", str(len(content)))
            self.send_header(
                "Content-Disposition",
                f"attachment; filename*=UTF-8''{safe_filename}",
            )
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(content)

        def log_message(self, format_string, *args):
            logging.info("Miniapp: " + format_string, *args)

    return MiniAppRequestHandler


class ReusableThreadingHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True


def start_miniapp_server(bot_token: str, host: str, port: int, debug: bool = False):
    if os.getenv("MINIAPP_ENABLED", "1") == "0":
        logging.info("Miniapp server disabled")
        return None

    try:
        server = ReusableThreadingHTTPServer(
            (host, port),
            make_handler(bot_token, debug),
        )
    except OSError:
        logging.exception("Miniapp server failed to bind on %s:%s", host, port)
        return None

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    logging.info("Miniapp server started on %s:%s", host, port)
    return server
