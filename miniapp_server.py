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
    add_cutting_layout,
    add_warehouse_stock,
    admin_close_shift,
    assign_route_batch,
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
    get_cutting_batches_for_cutting,
    get_cutting_batches_for_formation,
    get_cutting_batches_for_layout,
    get_cutting_batch_result_rows,
    get_employee_by_telegram_id,
    get_employee_by_id,
    get_employee_route_batches,
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
    get_warehouse_stock_by_id,
    get_warehouse_stock_rows,
    get_today_shifts,
    hide_operation,
    local_today,
    mark_cutting_batch_formed,
    restore_operation,
    consume_warehouse_stock,
    set_shift_operation_quantity,
    update_cutting_batch_progress,
    update_employee_position,
    update_employee_status,
    update_operation_field,
)
from catalog import PREPARATION_OPERATION_OPTIONS, format_color_label
from miniapp_auth import parse_auth_token
from miniapp_assets import MINIAPP_HTML
from route_maps import CUTTING_ROUTE, PRODUCT_ROUTE_MAPS


AUTH_MAX_AGE_SECONDS = 7 * 24 * 60 * 60
ROUTES_MINIAPP_ENABLED = False
CUTTING_CONTOUR_OPERATION = "Нанесение контуров лекал на ткань"
CUTTING_LAYOUT_OPERATION = "Формирование настила"
CUTTING_CUT_OPERATION = "Раскрой"
CUTTING_FORM_OPERATION = "Формирование готового кроя"


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
        return steps[-1]["status_after"] if steps else "Процесс завершён"

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


def route_batch_assignee_to_dict(batch: dict):
    employee_id = batch.get("assigned_employee_id")

    if not employee_id:
        return None

    employee = get_employee_by_id(employee_id)

    if not employee:
        return {
            "id": employee_id,
            "full_name": "Сотрудник",
            "position": "",
        }

    return employee_to_dict(employee)


def can_employee_work_route_step(employee, current_step: dict | None):
    return bool(employee and current_step and employee[3] == current_step["position"])


def get_preparation_folder(operation_name: str):
    return PREPARATION_OPERATION_OPTIONS.get(operation_name, {}).get("folder", "")


def is_elastic_preparation_operation(operation_name: str):
    return get_preparation_folder(operation_name) == "Нарезание резинки"


def route_step_category(route_step: dict | None):
    if not route_step:
        return ""

    position = route_step.get("position", "")
    operation = route_step.get("operation", "")
    operation_lower = operation.lower()
    preparation_folder = get_preparation_folder(operation)

    if position == "Раскройщик":
        return "Раскрой"

    if position == "Упаковщик":
        if preparation_folder in {"Нарезание резинки", "Нарезание дублерина", "Дублирование"}:
            return "Подготовка"
        if "подготов" in operation_lower:
            return "Подготовка"
        if "упаков" in operation_lower or "склад" in operation_lower:
            return "Упаковка"
        if "вто" in operation_lower or "заутюж" in operation_lower or "проклей" in operation_lower:
            return "ВТО"
        return "Подготовка"

    if position == "Швея":
        if operation == "Сшивание резинок в кольцо":
            return "Подготовка"
        if "подготов" in operation_lower or "стачивание" in operation_lower:
            return "Подготовка"
        if "оверлок" in operation_lower or "сборка" in operation_lower:
            return "Оверлок"
        return "Прямострочка"

    return position


def should_auto_create_next_preparation_task(current_step: dict | None, next_step: dict | None):
    if not current_step or not next_step:
        return False

    return (
        is_elastic_preparation_operation(current_step.get("operation", ""))
        and next_step.get("position") == "Швея"
        and next_step.get("operation") == "Сшивание резинок в кольцо"
    )


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
                "category": route_step_category(route_step),
            }
            for index, route_step in enumerate(PRODUCT_ROUTE_MAPS[product_name], start=1)
        ],
    }


def route_task_to_dict(batch: dict, current_step: dict, viewer_employee=None):
    assignee = route_batch_assignee_to_dict(batch)
    viewer_employee_id = viewer_employee[0] if viewer_employee else None
    is_assigned_to_viewer = bool(viewer_employee_id and batch.get("assigned_employee_id") == viewer_employee_id)
    is_free = not batch.get("assigned_employee_id")
    is_done = batch.get("status") == "done"

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
        "category": route_step_category(current_step),
        "assigned_employee_id": batch.get("assigned_employee_id"),
        "assigned_employee": assignee,
        "assigned_employee_name": assignee["full_name"] if assignee else "",
        "assigned_at": batch.get("assigned_at") or "",
        "good_quantity": batch.get("good_quantity") or 0,
        "defect_quantity": batch.get("defect_quantity") or 0,
        "work_status": "done" if is_done else ("free" if is_free else "in_work"),
        "status_text": "Завершено" if is_done else ("Свободно" if is_free else "В работе"),
        "is_assigned_to_me": is_assigned_to_viewer,
        "can_take": is_free,
        "can_complete": is_assigned_to_viewer,
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
            tasks.append(route_task_to_dict(batch, current_step, employee))

    return {"ok": True, "tasks": tasks}


def get_completed_route_tasks_for_telegram(telegram_id: int):
    employee = get_employee_for_access(telegram_id)

    if employee is None or employee[5] != "active":
        return []

    tasks = []

    for batch in get_employee_route_batches(employee[0], "done"):
        step_index = max(0, batch["route_step_index"] - 1)
        completed_step = get_route_step(batch["product_name"], step_index)

        if completed_step is None:
            continue

        tasks.append(route_task_to_dict(batch, completed_step, employee))

    return tasks


def start_route_task_for_telegram(telegram_id: int, batch_id: int):
    employee = get_employee_for_access(telegram_id)

    if employee is None or employee[5] != "active":
        return {"ok": False, "message": "Нет активного профиля."}

    batch = get_route_batch_by_id(batch_id)

    if batch is None or batch["status"] != "active":
        return {"ok": False, "message": "Это задание уже недоступно."}

    current_step = get_route_step(batch["product_name"], batch["route_step_index"])

    if not can_employee_work_route_step(employee, current_step):
        return {"ok": False, "message": "Это задание доступно другой должности."}

    if batch.get("assigned_employee_id") and batch["assigned_employee_id"] != employee[0]:
        assignee = route_batch_assignee_to_dict(batch)
        assignee_name = assignee["full_name"] if assignee else "другого сотрудника"
        return {"ok": False, "message": f"Задание уже в работе у {assignee_name}."}

    assigned_batch = assign_route_batch(batch_id, employee[0])

    if assigned_batch is None:
        return {"ok": False, "message": "Не удалось взять задание в работу."}

    add_edit_log(
        telegram_id,
        "employee",
        "Взял задание в работу из миниаппа",
        "route_batch",
        batch_id,
        route_batch_identity(assigned_batch),
    )

    return {
        "ok": True,
        "message": "Задание взято в работу.",
        "tasks": get_route_tasks_for_telegram(telegram_id)["tasks"],
        "completed_tasks": get_completed_route_tasks_for_telegram(telegram_id),
    }


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
        "Создал задание по операции из миниаппа",
        "route_batch",
        batch["id"],
        route_batch_identity(batch),
    )

    return {
        "ok": True,
        "message": f"Задание #{batch['id']} создано.",
        "batch": route_task_to_dict(batch, current_step, employee),
        "tasks": get_route_tasks_for_telegram(telegram_id)["tasks"],
    }


def complete_route_task_for_telegram(telegram_id: int, batch_id: int, payload: dict | None = None):
    payload = payload or {}
    employee = get_employee_for_access(telegram_id)

    if employee is None or employee[5] != "active":
        return {"ok": False, "message": "Нет активного профиля."}

    batch = get_route_batch_by_id(batch_id)

    if batch is None or batch["status"] != "active":
        return {"ok": False, "message": "Эта партия уже недоступна."}

    current_step = get_route_step(batch["product_name"], batch["route_step_index"])

    if not is_admin(telegram_id) and not can_employee_work_route_step(employee, current_step):
        return {"ok": False, "message": "Это задание сейчас доступно другой должности."}

    if batch.get("assigned_employee_id") and batch["assigned_employee_id"] != employee[0]:
        assignee = route_batch_assignee_to_dict(batch)
        assignee_name = assignee["full_name"] if assignee else "другого сотрудника"
        return {"ok": False, "message": f"Задание в работе у {assignee_name}."}

    try:
        good_quantity = int(payload.get("good_quantity") if payload.get("good_quantity") not in (None, "") else batch["quantity"])
        defect_quantity = int(payload.get("defect_quantity") or 0)
    except (TypeError, ValueError):
        return {"ok": False, "message": "Количество годного и брака должно быть целым числом."}

    if good_quantity < 0 or defect_quantity < 0:
        return {"ok": False, "message": "Количество не может быть отрицательным."}

    if good_quantity + defect_quantity != batch["quantity"]:
        return {"ok": False, "message": "Распределите всё количество задания между годным и браком."}

    next_step_index = batch["route_step_index"] + 1
    updated_batch = complete_route_batch_step(
        batch["id"],
        employee[0],
        current_step["operation"],
        current_step["position"],
        next_step_index,
        "done",
        good_quantity,
        defect_quantity,
    )

    if updated_batch is None:
        return {"ok": False, "message": "Не удалось завершить этап."}

    next_step = get_route_step(updated_batch["product_name"], updated_batch["route_step_index"])
    item_type = "semifinished" if next_step else "finished"
    ready_for_position = next_step["position"] if next_step else "Склад"
    stage_name = current_step["status_after"]

    stock_row = None

    if good_quantity > 0:
        stock_row = add_warehouse_stock(
            item_type,
            batch["product_name"],
            batch["product_size"],
            batch["product_color"],
            stage_name,
            ready_for_position,
            good_quantity,
            employee[0],
            "route_batch",
            batch["id"],
        )
    auto_batch = None

    if stock_row and should_auto_create_next_preparation_task(current_step, next_step):
        auto_batch = create_route_batch(
            batch["product_name"],
            batch["product_size"],
            batch["product_color"],
            good_quantity,
            employee[0],
            route_step_index=updated_batch["route_step_index"],
            source_stock_id=stock_row["id"],
        )

        if auto_batch:
            consumed = consume_warehouse_stock(
                stock_row["id"],
                good_quantity,
                employee[0],
                "route_batch",
                auto_batch["id"],
            )

            if consumed is None:
                cancel_route_batch(auto_batch["id"])
                auto_batch = None

    add_edit_log(
        telegram_id,
        "admin" if is_admin(telegram_id) else "employee",
        "Завершил задание по операции из миниаппа",
        "route_batch",
        batch["id"],
        f"{route_batch_identity(batch)}. Этап: {current_step['operation']}",
    )

    if auto_batch:
        message = f"Этап завершён. Следующее задание создано для должности {next_step['position']}."
    elif next_step:
        message = f"Этап завершён. Результат на складе для должности {next_step['position']}."
    else:
        message = "Этап завершён. Готовая продукция принята на склад."

    return {
        "ok": True,
        "message": message,
        "tasks": get_route_tasks_for_telegram(telegram_id)["tasks"],
        "completed_tasks": get_completed_route_tasks_for_telegram(telegram_id),
        "production": get_production_state_for_telegram(telegram_id),
    }


def get_route_catalog():
    return [route_map_to_dict(product_name) for product_name in PRODUCT_ROUTE_MAPS]


def get_routes_payload(telegram_id: int):
    return {
        "enabled": ROUTES_MINIAPP_ENABLED,
        "catalog": get_route_catalog(),
        "tasks": get_route_tasks_for_telegram(telegram_id).get("tasks", []),
        "completed_tasks": get_completed_route_tasks_for_telegram(telegram_id),
    }


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
    catalog = []

    for product_name in PRODUCT_ROUTE_MAPS:
        colors = get_product_colors(product_name)
        catalog.append(
            {
                "product_name": product_name,
                "sizes": get_product_sizes(product_name),
                "colors": colors,
                "color_labels": [format_color_label(color) for color in colors],
            }
        )

    return catalog


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


def warehouse_stock_to_dict(row: dict):
    item_type_text = {
        "semifinished": "Полуфабрикаты",
        "finished": "Готовая продукция",
    }.get(row["item_type"], row["item_type"])

    return {
        **row,
        "item_type_text": item_type_text,
        "product_color_label": format_color_label(row["product_color"]),
        "quantity_text": format_number(row["quantity"]),
        "title": f"{row['product_name']} — {row['stage_name']}",
    }


def get_cutting_operation(product_name: str, operation_name: str):
    operations = get_active_operations("Раскройщик", product_name, "Раскрой изделий")

    for operation_id, _number, name, unit in operations:
        if name == operation_name:
            return {
                "id": operation_id,
                "name": f"{product_name}: {name}",
                "base_name": name,
                "unit": unit,
            }

    return None


def get_cutting_contour_operation(product_name: str):
    return get_cutting_operation(product_name, CUTTING_CONTOUR_OPERATION)


def cutting_stage_task_to_dict(stage: str, row):
    if stage == "contours":
        task = production_task_to_dict(row)
        return {
            **task,
            "task_kind": "cutting_stage",
            "category": "Раскрой",
            "stage": "contours",
            "stage_title": "Нанесение контуров лекал на ткань",
            "source_id": task["id"],
            "next_action": "Начать контуры",
        }

    if stage == "layout":
        batch_id, product_name, contour_date, production_task_id, employee_name, sizes_text, colors_text = row
        colors = split_group_concat(colors_text)
        return {
            "id": batch_id,
            "source_id": batch_id,
            "production_task_id": production_task_id,
            "task_kind": "cutting_stage",
            "category": "Раскрой",
            "stage": "layout",
            "stage_title": "Формирование настила",
            "next_action": "Сохранить настил",
            "product_name": product_name,
            "status": "contours_done",
            "status_text": "контуры нанесены",
            "created_at": contour_date,
            "employee": employee_name or "",
            "sizes_text": sizes_text or "",
            "colors": colors,
            "color_labels": [format_color_label(color) for color in colors],
        }

    if stage == "cutting":
        batch_id, product_name, contour_date, layout_date, progress, colors_text = row
        return {
            "id": batch_id,
            "source_id": batch_id,
            "task_kind": "cutting_stage",
            "category": "Раскрой",
            "stage": "cutting",
            "stage_title": "Раскрой",
            "next_action": "Обновить процент",
            "product_name": product_name,
            "status": "in_cutting" if progress else "layout_done",
            "status_text": f"готовность {progress or 0}%",
            "created_at": layout_date or contour_date,
            "progress": progress or 0,
            "colors_text": colors_text or "",
        }

    batch_id, product_name, contour_date, layout_date, progress = row
    return {
        "id": batch_id,
        "source_id": batch_id,
        "task_kind": "cutting_stage",
        "category": "Раскрой",
        "stage": "formation",
        "stage_title": "Формирование готового кроя",
        "next_action": "Принять крой на склад",
        "product_name": product_name,
        "status": "cutting_done",
        "status_text": "раскрой завершён",
        "created_at": layout_date or contour_date,
        "progress": progress or 100,
    }


def get_cutting_stage_tasks(employee):
    if not employee or employee[5] != "active" or employee[3] != "Раскройщик":
        return []

    tasks = [
        cutting_stage_task_to_dict("contours", row)
        for row in get_active_production_tasks_for_contours()
    ]

    for product_name in PRODUCT_ROUTE_MAPS:
        tasks.extend(cutting_stage_task_to_dict("layout", row) for row in get_cutting_batches_for_layout(product_name))
        tasks.extend(cutting_stage_task_to_dict("cutting", row) for row in get_cutting_batches_for_cutting(product_name))
        tasks.extend(cutting_stage_task_to_dict("formation", row) for row in get_cutting_batches_for_formation(product_name))

    return tasks


def get_production_state_for_telegram(telegram_id: int):
    employee = get_employee_for_access(telegram_id)
    is_admin_user = is_admin(telegram_id)
    can_work_contours = bool(employee and employee[5] == "active" and employee[3] == "Раскройщик")
    order_colors = get_order_color_options()
    warehouse_rows = [warehouse_stock_to_dict(row) for row in get_warehouse_stock_rows()]

    return {
        "catalog": production_catalog_to_dict(),
        "order_colors": order_colors,
        "order_color_labels": [format_color_label(color) for color in order_colors],
        "fabric_stock": [fabric_stock_to_dict(row) for row in get_fabric_stock_rows()] if is_admin_user else [],
        "warehouse_stock": warehouse_rows if is_admin_user else [],
        "tasks": [production_task_to_dict(row) for row in get_active_production_tasks()] if is_admin_user else [],
        "cutting_tasks": get_cutting_stage_tasks(employee),
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

    employee = get_employee_for_access(telegram_id)
    employee_id = employee[0] if employee else None

    if task_type == "cutting":
        allowed_sizes = set(get_product_sizes(product_name))
        allowed_colors = set(get_order_color_options())

        if not sizes or any(size not in allowed_sizes for size in sizes):
            return {"ok": False, "message": "Выберите размеры из списка."}

        if not colors or any(color not in allowed_colors for color in colors):
            return {"ok": False, "message": "Выберите цвета из списка."}

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
            "routes": get_routes_payload(telegram_id),
        }

    try:
        route_step_index = int(payload.get("route_step_index"))
    except (TypeError, ValueError):
        route_step_index = -1

    route_step = get_route_step(product_name, route_step_index)

    if route_step is None:
        return {"ok": False, "message": "Выберите операцию."}

    if route_step_index < len(CUTTING_ROUTE):
        return {"ok": False, "message": "Для раскроя используйте тип задания «Раскрой»."}

    raw_stock_items = payload.get("stock_items") or []

    if not raw_stock_items:
        return {"ok": False, "message": "Выберите полуфабрикат со склада."}

    created_batches = []
    consumed_rows = []

    for item in raw_stock_items:
        try:
            stock_id = int(item.get("stock_id") or 0)
            quantity = int(item.get("quantity") or 0)
        except (AttributeError, TypeError, ValueError):
            return {"ok": False, "message": "Количество по складу должно быть целым числом."}

        if quantity <= 0:
            continue

        stock_row = get_warehouse_stock_by_id(stock_id)

        if stock_row is None or stock_row["quantity"] <= 0:
            return {"ok": False, "message": "Один из полуфабрикатов уже недоступен."}

        if stock_row["item_type"] != "semifinished":
            return {"ok": False, "message": "Для задания выберите полуфабрикат."}

        if stock_row["product_name"] != product_name:
            return {"ok": False, "message": "Полуфабрикат не соответствует изделию."}

        if stock_row["ready_for_position"] != route_step["position"]:
            return {"ok": False, "message": f"Этот полуфабрикат не для должности {route_step['position']}."}

        if quantity > stock_row["quantity"]:
            return {"ok": False, "message": "Количество больше остатка на складе."}

        batch = create_route_batch(
            product_name,
            stock_row["product_size"],
            stock_row["product_color"],
            quantity,
            employee_id,
            route_step_index=route_step_index,
            source_stock_id=stock_id,
        )

        if batch is None:
            return {"ok": False, "message": "Не удалось создать одно из заданий."}

        consumed = consume_warehouse_stock(stock_id, quantity, employee_id, "route_batch", batch["id"])

        if consumed is None:
            cancel_route_batch(batch["id"])
            return {"ok": False, "message": "Не удалось списать полуфабрикат со склада."}

        consumed_rows.append(stock_row)
        created_batches.append(batch)

    if not created_batches:
        return {"ok": False, "message": "Введите количество хотя бы по одной строке склада."}

    add_edit_log(
        telegram_id,
        "admin",
        "Создал задания по операции из миниаппа",
        "route_batch",
        created_batches[0]["id"],
        (
            f"{product_name}; {route_step['position']} — {route_step['operation']}; "
            f"вход: полуфабрикат со склада; партий: {len(created_batches)}"
        ),
    )

    return {
        "ok": True,
        "message": f"Создано заданий: {len(created_batches)}.",
        "production": get_production_state_for_telegram(telegram_id),
        "routes": get_routes_payload(telegram_id),
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
            return {"ok": False, "message": "Задание не найдено."}

        cancelled_batch = cancel_route_batch(task_id)

        if cancelled_batch is None:
            return {"ok": False, "message": "Это задание уже нельзя удалить."}

        if batch.get("source_stock_id"):
            source_stock = get_warehouse_stock_by_id(batch["source_stock_id"])

            if source_stock is not None:
                add_warehouse_stock(
                    source_stock["item_type"],
                    source_stock["product_name"],
                    source_stock["product_size"],
                    source_stock["product_color"],
                    source_stock["stage_name"],
                    source_stock["ready_for_position"],
                    batch["quantity"],
                    employee[0] if (employee := get_employee_for_access(telegram_id)) else None,
                    "cancelled_task",
                    batch["id"],
                )

        add_edit_log(
            telegram_id,
            "admin",
            "Удалил задание по операции из миниаппа",
            "route_batch",
            task_id,
            route_batch_identity(batch),
        )
        message = f"Задание #{task_id} удалено."
    else:
        return {"ok": False, "message": "Неизвестный тип задания."}

    return {
        "ok": True,
        "message": message,
        "production": get_production_state_for_telegram(telegram_id),
        "routes": get_routes_payload(telegram_id),
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


def parse_cutting_sizes_text(value: str):
    sizes = []

    for item in (value or "").split(","):
        size = item.split(" - ", 1)[0].strip()

        if size:
            sizes.append(size)

    return sizes


def submit_cutting_stage_for_telegram(telegram_id: int, payload: dict):
    employee = get_employee_for_access(telegram_id)

    if employee is None or employee[5] != "active":
        return {"ok": False, "message": "Нет активного профиля."}

    if employee[3] != "Раскройщик" and not is_admin(telegram_id):
        return {"ok": False, "message": "Этапы раскроя доступны раскройщику."}

    shift = get_open_shift_for_today(employee[0])

    if shift is None:
        return {"ok": False, "message": "Откройте смену перед выполнением задания."}

    stage = (payload.get("stage") or "").strip()

    if stage == "contours":
        return submit_production_contours_for_telegram(telegram_id, payload)

    try:
        batch_id = int(payload.get("batch_id") or 0)
    except (TypeError, ValueError):
        batch_id = 0

    if batch_id <= 0:
        return {"ok": False, "message": "Выберите задание."}

    if stage == "layout":
        batch_row = None

        for product_name in PRODUCT_ROUTE_MAPS:
            for row in get_cutting_batches_for_layout(product_name):
                if row[0] == batch_id:
                    batch_row = row
                    break
            if batch_row:
                break

        if batch_row is None:
            return {"ok": False, "message": "Сначала нужно выполнить нанесение контуров."}

        operation = get_cutting_operation(batch_row[1], CUTTING_LAYOUT_OPERATION)

        if operation is None:
            return {"ok": False, "message": "Для изделия не найдена операция настила."}

        raw_layers = payload.get("color_layers") or {}
        color_layers = {}
        colors = split_group_concat(batch_row[6])

        for color in colors:
            try:
                layers = int(raw_layers.get(color) or 0)
            except (TypeError, ValueError):
                return {"ok": False, "message": "Количество слоёв должно быть целым числом."}

            if layers < 0:
                return {"ok": False, "message": "Количество слоёв не может быть отрицательным."}

            if layers > 0:
                color_layers[color] = layers

        if not color_layers:
            return {"ok": False, "message": "Укажите слои хотя бы по одному цвету."}

        if not add_cutting_layout(batch_id, shift[0], employee[0], operation["id"], color_layers):
            return {"ok": False, "message": "Настил уже недоступен."}

        sizes = parse_cutting_sizes_text(batch_row[5])
        added_count = 0

        for color, layers in color_layers.items():
            for product_size in sizes:
                add_shift_operation(shift[0], employee[0], operation["id"], product_size, color, layers)
                added_count += 1

        add_edit_log(
            telegram_id,
            "employee",
            "Выполнил формирование настила из миниаппа",
            "cutting_batch",
            batch_id,
            f"Цветов: {len(color_layers)}, строк отчёта: {added_count}",
        )

        return {
            "ok": True,
            "message": "Настил сохранён. Следующий этап: раскрой.",
            "production": get_production_state_for_telegram(telegram_id),
        }

    if stage == "cutting":
        batch_row = None

        for product_name in PRODUCT_ROUTE_MAPS:
            for row in get_cutting_batches_for_cutting(product_name):
                if row[0] == batch_id:
                    batch_row = row
                    break
            if batch_row:
                break

        if batch_row is None:
            return {"ok": False, "message": "Сначала нужно выполнить формирование настила."}

        operation = get_cutting_operation(batch_row[1], CUTTING_CUT_OPERATION)

        if operation is None:
            return {"ok": False, "message": "Для изделия не найдена операция раскроя."}

        try:
            progress = int(payload.get("progress") or 0)
        except (TypeError, ValueError):
            progress = 0

        if progress not in {25, 50, 75, 100}:
            return {"ok": False, "message": "Выберите готовность: 25, 50, 75 или 100%."}

        if not update_cutting_batch_progress(batch_id, shift[0], employee[0], operation["id"], progress):
            return {"ok": False, "message": "Раскрой уже недоступен."}

        set_shift_operation_quantity(
            shift[0],
            employee[0],
            operation["id"],
            "готовность",
            "без цвета",
            progress,
        )
        add_edit_log(
            telegram_id,
            "employee",
            "Обновил процент раскроя из миниаппа",
            "cutting_batch",
            batch_id,
            f"{progress}%",
        )

        message = "Раскрой завершён. Следующий этап: формирование готового кроя." if progress == 100 else "Готовность раскроя сохранена."

        return {
            "ok": True,
            "message": message,
            "production": get_production_state_for_telegram(telegram_id),
        }

    if stage == "formation":
        batch_row = None

        for product_name in PRODUCT_ROUTE_MAPS:
            for row in get_cutting_batches_for_formation(product_name):
                if row[0] == batch_id:
                    batch_row = row
                    break
            if batch_row:
                break

        if batch_row is None:
            return {"ok": False, "message": "Сначала нужно завершить раскрой на 100%."}

        operation = get_cutting_operation(batch_row[1], CUTTING_FORM_OPERATION)

        if operation is None:
            return {"ok": False, "message": "Для изделия не найдена операция формирования готового кроя."}

        result_rows = get_cutting_batch_result_rows(batch_id)

        if not mark_cutting_batch_formed(batch_id, shift[0], employee[0], operation["id"]):
            return {"ok": False, "message": "Готовый крой уже недоступен."}

        for product_size, color, quantity in result_rows:
            if quantity > 0:
                add_shift_operation(shift[0], employee[0], operation["id"], product_size, color, quantity)

        add_edit_log(
            telegram_id,
            "employee",
            "Сформировал готовый крой из миниаппа",
            "cutting_batch",
            batch_id,
            f"На склад передано строк: {len([row for row in result_rows if row[2] > 0])}",
        )

        return {
            "ok": True,
            "message": "Готовый крой принят на склад.",
            "production": get_production_state_for_telegram(telegram_id),
        }

    return {"ok": False, "message": "Неизвестный этап."}


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
    is_admin_user = is_admin(telegram_id)

    return {
        **shift_state,
        "is_admin": is_admin_user,
        "report": get_current_report_for_telegram(telegram_id),
        "history": get_employee_history_for_telegram(telegram_id, {}),
        "routes": get_routes_payload(telegram_id),
        "production": get_production_state_for_telegram(telegram_id),
        "admin": get_admin_dashboard(telegram_id) if is_admin_user else None,
        "features": {
            "can_work": bool(employee and employee.get("status") == "active"),
            "can_admin": is_admin_user,
            "routes_enabled": ROUTES_MINIAPP_ENABLED,
        },
    }


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
                "/api/production/submit-cutting-stage",
                "/api/routes/create-batch",
                "/api/routes/start",
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
            elif path == "/api/production/submit-cutting-stage":
                result = submit_cutting_stage_for_telegram(telegram_id, payload)
            elif path == "/api/routes/create-batch":
                result = create_route_batch_for_telegram(telegram_id, payload)
            elif path == "/api/routes/start":
                try:
                    batch_id = int(payload.get("batch_id") or 0)
                except (TypeError, ValueError):
                    batch_id = 0

                result = start_route_task_for_telegram(telegram_id, batch_id)
            elif path == "/api/routes/complete":
                try:
                    batch_id = int(payload.get("batch_id") or 0)
                except (TypeError, ValueError):
                    batch_id = 0

                result = complete_route_task_for_telegram(telegram_id, batch_id, payload)
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
