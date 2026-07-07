import hashlib
import hmac
import json
import logging
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qsl, urlparse

from database import (
    add_edit_log,
    add_feedback_entry,
    add_operation,
    admin_close_shift,
    close_shift,
    complete_route_batch_step,
    create_route_batch,
    create_shift,
    delete_shift_by_id,
    ensure_admin_employee,
    get_active_route_batches,
    get_all_employees,
    get_all_operations,
    get_database_status,
    get_employee_by_telegram_id,
    get_employee_period_operation_totals,
    get_employee_period_summary,
    get_employee_shifts_by_period,
    get_employees_by_status,
    get_feedback_entries_by_shift,
    get_month_employee_summary,
    get_month_operation_rows,
    get_month_shift_details,
    get_open_shifts,
    get_open_shift_for_today,
    get_pending_employees,
    get_period_employee_summary,
    get_period_operation_rows,
    get_period_shift_details,
    get_product_colors,
    get_product_sizes,
    get_recent_shifts,
    get_recent_edit_logs,
    get_route_batch_by_id,
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
from route_maps import PRODUCT_ROUTE_MAPS


AUTH_MAX_AGE_SECONDS = 7 * 24 * 60 * 60


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
            "Отчёт за месяц",
            "Отчёт за период",
            "Excel за период",
            "Отчёт по сотруднику",
            "Править отчёт",
            "Выгрузить отчёт",
            "Партии раскроя",
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
    {
        "id": "files",
        "title": "Файлы",
        "buttons": [
            "Журнал",
            "Скачать базу",
            "Проверка базы",
            "Загрузить базу",
            "Создать копию базы",
            "Ошибки",
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


def edit_log_to_dict(row):
    changed_at, changed_by, role, action, entity_type, entity_id, details = row

    return {
        "changed_at": changed_at,
        "changed_by": changed_by,
        "role": role,
        "action": action,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "details": details,
    }


def get_admin_dashboard(telegram_id: int):
    if not is_admin(telegram_id):
        return {"ok": False, "message": "Нет прав администратора."}

    employees = get_all_employees()
    month_start, today = month_bounds()

    return {
        "ok": True,
        "menu": ADMIN_MENU,
        "positions": POSITIONS,
        "period_defaults": {"start_date": month_start, "end_date": today},
        "employees": [employee_admin_to_dict(employee) for employee in employees],
        "active_employees": [
            employee_admin_to_dict(employee) for employee in get_employees_by_status("active")
        ],
        "inactive_employees": [
            employee_admin_to_dict(employee) for employee in get_employees_by_status("inactive")
        ],
        "pending_employees": [
            pending_employee_to_dict(employee) for employee in get_pending_employees()
        ],
        "open_shifts": [open_shift_to_dict(shift) for shift in get_open_shifts()],
        "recent_shifts": [recent_shift_to_dict(shift) for shift in get_recent_shifts(20)],
        "operations": [
            operation_admin_to_dict(operation) for operation in get_all_operations()
        ],
        "files": {
            "database": get_database_status(),
            "logs": [edit_log_to_dict(row) for row in get_recent_edit_logs(25)],
        },
        "reports": get_admin_report_payload("month", month_start, today),
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

    if report_type == "period":
        title = f"Отчёт за период: {start_date} — {end_date}"
        summary_rows = get_period_employee_summary(start_date, end_date)
        operation_rows = get_period_operation_rows(start_date, end_date)
        shift_rows = get_period_shift_details(start_date, end_date)
    else:
        month_start, today = month_bounds()
        start_date = month_start
        end_date = today
        title = f"Отчёт за месяц: {start_date} — {end_date}"
        summary_rows = get_month_employee_summary()
        operation_rows = get_month_operation_rows()
        shift_rows = get_month_shift_details()

    return {
        "type": "period" if report_type == "period" else "month",
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
    report_type = (payload.get("report_type") or "month").strip()
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
        "routes": {
            "catalog": get_route_catalog(),
            "tasks": get_route_tasks_for_telegram(telegram_id).get("tasks", []),
        },
        "admin": get_admin_dashboard(telegram_id) if is_admin(telegram_id) else None,
        "features": {
            "can_work": bool(employee and employee.get("status") == "active"),
            "can_admin": is_admin(telegram_id),
        },
    }


MINIAPP_HTML = """<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Шагаем вместе</title>
  <script src="https://telegram.org/js/telegram-web-app.js"></script>
  <style>
    :root {
      color-scheme: light dark;
      --bg: var(--tg-theme-bg-color, #f4f5f7);
      --text: var(--tg-theme-text-color, #18212f);
      --muted: var(--tg-theme-hint-color, #667085);
      --card: var(--tg-theme-secondary-bg-color, #ffffff);
      --accent: var(--tg-theme-button-color, #2775f6);
      --accent-text: var(--tg-theme-button-text-color, #ffffff);
      --danger: #d92d20;
      --success: #039855;
      --border: rgba(100, 116, 139, 0.22);
      --soft: rgba(100, 116, 139, 0.10);
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      min-height: 100vh;
      background: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    .page {
      width: min(860px, 100%);
      margin: 0 auto;
      padding: 14px;
    }

    .topbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 12px;
    }

    h1, h2, h3, p {
      margin-top: 0;
      letter-spacing: 0;
    }

    h1 {
      margin-bottom: 0;
      font-size: 22px;
      line-height: 1.2;
    }

    h2 {
      margin-bottom: 12px;
      font-size: 18px;
    }

    h3 {
      margin-bottom: 8px;
      font-size: 15px;
    }

    .status {
      padding: 6px 10px;
      border: 1px solid var(--border);
      border-radius: 8px;
      color: var(--muted);
      font-size: 13px;
      white-space: nowrap;
    }

    .tabs {
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 6px;
      margin-bottom: 12px;
      position: sticky;
      top: 0;
      z-index: 2;
      padding: 4px 0;
      background: var(--bg);
    }

    .tab {
      min-height: 38px;
      padding: 8px;
      color: var(--text);
      background: var(--soft);
      border: 1px solid var(--border);
      border-radius: 8px;
      font-size: 13px;
      font-weight: 700;
    }

    .tab.active {
      color: var(--accent-text);
      background: var(--accent);
      border-color: var(--accent);
    }

    .tab[hidden] {
      display: none;
    }

    .section {
      display: none;
    }

    .section.active {
      display: block;
    }

    .card {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 14px;
      margin-bottom: 10px;
    }

    .label {
      margin: 0 0 5px;
      color: var(--muted);
      font-size: 13px;
    }

    .value {
      margin: 0;
      font-size: 18px;
      font-weight: 800;
      line-height: 1.25;
    }

    .grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
      margin-top: 12px;
    }

    .three {
      grid-template-columns: repeat(3, minmax(0, 1fr));
    }

    button, select, input, textarea {
      width: 100%;
      border-radius: 8px;
      font: inherit;
    }

    button {
      min-height: 46px;
      border: 0;
      padding: 11px 12px;
      font-weight: 800;
      color: var(--accent-text);
      background: var(--accent);
    }

    button.secondary {
      color: var(--text);
      background: transparent;
      border: 1px solid var(--border);
    }

    button.danger {
      background: var(--danger);
    }

    button.success {
      background: var(--success);
    }

    button:disabled {
      opacity: 0.45;
    }

    select, input, textarea {
      min-height: 44px;
      padding: 10px;
      border: 1px solid var(--border);
      color: var(--text);
      background: var(--card);
    }

    textarea {
      min-height: 118px;
      resize: vertical;
    }

    .message {
      margin-top: 10px;
      color: var(--muted);
      font-size: 14px;
      line-height: 1.35;
    }

    .message.ok {
      color: var(--success);
    }

    .message.error {
      color: var(--danger);
    }

    .rows {
      display: grid;
      gap: 9px;
      margin-top: 12px;
    }

    .row {
      display: flex;
      justify-content: space-between;
      gap: 16px;
      padding-top: 9px;
      border-top: 1px solid var(--border);
      color: var(--muted);
      font-size: 14px;
    }

    .row strong {
      color: var(--text);
      text-align: right;
      overflow-wrap: anywhere;
    }

    .list {
      display: grid;
      gap: 8px;
    }

    .item {
      padding: 10px;
      border: 1px solid var(--border);
      border-radius: 8px;
      background: var(--soft);
    }

    .item-title {
      margin: 0 0 5px;
      font-weight: 800;
      line-height: 1.3;
    }

    .item-meta {
      margin: 0;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.35;
    }

    .empty {
      color: var(--muted);
      font-size: 14px;
      line-height: 1.35;
    }

    .form {
      display: grid;
      gap: 10px;
    }

    .pill-row {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }

    .pill {
      padding: 5px 8px;
      border: 1px solid var(--border);
      border-radius: 999px;
      color: var(--muted);
      font-size: 12px;
    }

    .pill-button {
      width: auto;
      min-height: 34px;
      padding: 7px 10px;
      color: var(--text);
      background: var(--soft);
      border: 1px solid var(--border);
      border-radius: 999px;
      font-size: 12px;
      font-weight: 800;
    }

    .pill-button.active {
      color: var(--accent-text);
      background: var(--accent);
      border-color: var(--accent);
    }

    @media (max-width: 560px) {
      .tabs {
        grid-template-columns: repeat(3, minmax(0, 1fr));
      }

      .grid, .three {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body>
  <main class="page">
    <div class="topbar">
      <h1>Шагаем вместе</h1>
      <div class="status" id="connection">Загрузка</div>
    </div>

    <nav class="tabs">
      <button class="tab active" data-tab="shift">Смена</button>
      <button class="tab" data-tab="report">Отчёт</button>
      <button class="tab" data-tab="feedback">Связь</button>
      <button class="tab" data-tab="routes">Маршруты</button>
      <button class="tab" data-tab="admin" id="adminTab" hidden>Админ</button>
    </nav>

    <section class="section active" id="section-shift">
      <div class="card">
        <p class="label">Сотрудник</p>
        <p class="value" id="employeeName">Проверяем доступ</p>
        <div class="rows">
          <div class="row"><span>Должность</span><strong id="employeePosition">-</strong></div>
          <div class="row"><span>Статус профиля</span><strong id="employeeStatus">-</strong></div>
        </div>
      </div>

      <div class="card">
        <p class="label">Смена</p>
        <p class="value" id="shiftStatus">-</p>
        <div class="rows">
          <div class="row"><span>Дата</span><strong id="shiftDate">-</strong></div>
          <div class="row"><span>Начало</span><strong id="shiftStart">-</strong></div>
          <div class="row"><span>Окончание</span><strong id="shiftEnd">-</strong></div>
          <div class="row"><span>Отработано</span><strong id="shiftTotal">-</strong></div>
        </div>
        <div class="grid">
          <button id="openButton">Открыть смену</button>
          <button id="closeButton" class="danger">Закрыть смену</button>
          <button id="refreshButton" class="secondary">Обновить</button>
        </div>
        <div class="message" id="message"></div>
      </div>
    </section>

    <section class="section" id="section-report">
      <div class="card">
        <h2>Текущий отчёт</h2>
        <div class="rows">
          <div class="row"><span>Смена</span><strong id="reportShift">-</strong></div>
          <div class="row"><span>Строк операций</span><strong id="reportCount">0</strong></div>
        </div>
      </div>
      <div class="card">
        <h3>Операции</h3>
        <div class="list" id="reportOperations"></div>
      </div>
      <div class="card">
        <h3>Обратная связь за смену</h3>
        <div class="list" id="reportFeedback"></div>
      </div>
    </section>

    <section class="section" id="section-feedback">
      <div class="card">
        <h2>Обратная связь</h2>
        <div class="form">
          <select id="feedbackCategory">
            <option value="Производство">Производство</option>
            <option value="Бытовое">Бытовое</option>
          </select>
          <textarea id="feedbackMessage" placeholder="Напишите сообщение"></textarea>
          <button id="sendFeedbackButton">Отправить</button>
        </div>
        <div class="message" id="feedbackStatus"></div>
      </div>
    </section>

    <section class="section" id="section-routes">
      <div class="card">
        <h2>Маршрутные карты</h2>
        <div class="form">
          <select id="routeProductSelect"></select>
          <div class="list" id="routeSteps"></div>
        </div>
      </div>

      <div class="card">
        <h2>Создать партию</h2>
        <div class="form">
          <select id="batchProductSelect"></select>
          <select id="batchSizeSelect"></select>
          <select id="batchColorSelect"></select>
          <input id="batchQuantityInput" inputmode="numeric" placeholder="Количество">
          <button id="createBatchButton">Создать партию</button>
        </div>
        <div class="message" id="routeCreateStatus"></div>
      </div>

      <div class="card">
        <h2>Доступные задания</h2>
        <div class="list" id="routeTasks"></div>
      </div>
    </section>

    <section class="section" id="section-admin">
      <div class="card">
        <h2>Админ меню</h2>
        <div class="grid three" id="adminMenu"></div>
        <div class="message" id="adminStatus"></div>
      </div>
      <div class="card">
        <h3 id="adminPanelTitle">Раздел</h3>
        <div class="pill-row" id="adminPanelButtons"></div>
        <div class="list" id="adminPanelContent"></div>
      </div>
      <div class="card">
        <h3>Блок отчёта</h3>
        <div class="form">
          <div class="grid">
            <button id="adminReportToday">Отчёт за сегодня</button>
            <button id="adminReportMonth" class="secondary">Отчёт за месяц</button>
          </div>
          <div class="grid">
            <input id="adminReportStart" type="date">
            <input id="adminReportEnd" type="date">
          </div>
          <button id="adminReportPeriod" class="secondary">Отчёт за период</button>
          <select id="adminEmployeeSelect"></select>
          <button id="adminEmployeeReport" class="secondary">Отчёт по сотруднику</button>
        </div>
        <div class="list" id="adminReportOutput"></div>
      </div>
    </section>
  </main>

  <script>
    const tg = window.Telegram && window.Telegram.WebApp;
    const urlParams = new URLSearchParams(window.location.search);
    const debugTelegramId = urlParams.get("debug_tg_id");
    const authToken = urlParams.get("auth");
    const state = {
      initData: tg ? tg.initData : "",
      loading: false,
      tab: "shift",
      adminSection: "requests",
      data: null,
    };

    if (tg) {
      tg.ready();
      tg.expand();
    }

    const $ = (id) => document.getElementById(id);

    function escapeHtml(value) {
      return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }

    function setText(id, value) {
      $(id).textContent = value || "-";
    }

    function setLoading(isLoading) {
      state.loading = isLoading;
      $("connection").textContent = isLoading ? "Обновление" : "Готово";
      document.querySelectorAll("button").forEach((button) => {
        if (!button.classList.contains("tab")) {
          button.disabled = isLoading;
        }
      });
    }

    function empty(text) {
      return `<p class="empty">${escapeHtml(text)}</p>`;
    }

    function item(title, meta = "") {
      return `
        <div class="item">
          <p class="item-title">${escapeHtml(title)}</p>
          ${meta ? `<p class="item-meta">${meta}</p>` : ""}
        </div>
      `;
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

    function renderShift(data) {
      const employee = data.employee;
      const shift = data.shift;

      setText("employeeName", employee ? employee.full_name : "Нет доступа");
      setText("employeePosition", employee ? employee.position : "-");
      setText("employeeStatus", employee ? employee.status : "-");

      if (!shift) {
        setText("shiftStatus", "Смена не открыта");
        setText("shiftDate", "-");
        setText("shiftStart", "-");
        setText("shiftEnd", "-");
        setText("shiftTotal", "-");
      } else if (shift.status === "open") {
        setText("shiftStatus", "Смена открыта");
        setText("shiftDate", shift.date);
        setText("shiftStart", shift.start_time);
        setText("shiftEnd", "-");
        setText("shiftTotal", "-");
      } else {
        setText("shiftStatus", "Смена закрыта");
        setText("shiftDate", shift.date);
        setText("shiftStart", shift.start_time);
        setText("shiftEnd", shift.end_time);
        setText("shiftTotal", shift.total_minutes_text);
      }

      $("message").textContent = data.message || "";
      $("openButton").disabled = state.loading || !data.ok || data.has_open_shift || (shift && shift.status === "closed");
      $("closeButton").disabled = state.loading || !data.ok || !data.has_open_shift;
    }

    function renderReport(report) {
      const shift = report && report.shift;
      const operations = report && report.operations ? report.operations : [];
      const feedback = report && report.feedback ? report.feedback : [];

      setText("reportShift", shift ? `${shift.date}, ${shift.status === "open" ? "открыта" : "закрыта"}` : "Нет смены");
      setText("reportCount", String(operations.length));

      $("reportOperations").innerHTML = operations.length
        ? operations.map((row, index) => item(
            `${index + 1}. ${row.operation_name}`,
            [
              row.product_size && row.product_size !== "без размера" ? `Размер: ${escapeHtml(row.product_size)}` : "",
              row.product_color && row.product_color !== "без цвета" ? `Цвет: ${escapeHtml(row.product_color)}` : "",
              `Количество: ${escapeHtml(row.quantity)} ${escapeHtml(row.unit)}`
            ].filter(Boolean).join("<br>")
          )).join("")
        : empty(report && report.message ? report.message : "Операции ещё не добавлены.");

      $("reportFeedback").innerHTML = feedback.length
        ? feedback.map((row) => item(
            `${row.category} — ${row.date} ${row.time}`,
            escapeHtml(row.message)
          )).join("")
        : empty("Сообщений по этой смене нет.");
    }

    function getSelectedRouteProduct() {
      const catalog = state.data && state.data.routes ? state.data.routes.catalog : [];
      return catalog.find((product) => product.product_name === $("routeProductSelect").value) || catalog[0];
    }

    function optionList(items, selectedValue = "") {
      return items.map((itemValue) => {
        const selected = itemValue === selectedValue ? " selected" : "";
        return `<option value="${escapeHtml(itemValue)}"${selected}>${escapeHtml(itemValue)}</option>`;
      }).join("");
    }

    function renderRouteSelectors() {
      const catalog = state.data && state.data.routes ? state.data.routes.catalog : [];

      if (!catalog.length) {
        $("routeProductSelect").innerHTML = "";
        $("batchProductSelect").innerHTML = "";
        $("routeSteps").innerHTML = empty("Маршрутные карты пока не настроены.");
        return;
      }

      const currentProduct = $("routeProductSelect").value || catalog[0].product_name;
      const batchProduct = $("batchProductSelect").value || catalog[0].product_name;
      $("routeProductSelect").innerHTML = optionList(catalog.map((product) => product.product_name), currentProduct);
      $("batchProductSelect").innerHTML = optionList(catalog.map((product) => product.product_name), batchProduct);
      renderSelectedRoute();
      renderBatchOptions();
    }

    function renderSelectedRoute() {
      const product = getSelectedRouteProduct();

      if (!product) {
        $("routeSteps").innerHTML = empty("Выберите изделие.");
        return;
      }

      $("routeSteps").innerHTML = product.steps.map((step) => item(
        `${step.number}. ${step.operation}`,
        `Кто делает: ${escapeHtml(step.position)}<br>После этапа: ${escapeHtml(step.status_after)}`
      )).join("");
    }

    function renderBatchOptions() {
      const catalog = state.data && state.data.routes ? state.data.routes.catalog : [];
      const product = catalog.find((item) => item.product_name === $("batchProductSelect").value) || catalog[0];

      if (!product) {
        return;
      }

      $("batchSizeSelect").innerHTML = optionList(product.sizes.length ? product.sizes : ["без размера"]);
      $("batchColorSelect").innerHTML = optionList(product.raw_colors.length ? product.raw_colors : ["без цвета"]);
    }

    function renderRoutes(routes) {
      renderRouteSelectors();
      const tasks = routes && routes.tasks ? routes.tasks : [];

      $("routeTasks").innerHTML = tasks.length
        ? tasks.map((task) => `
            <div class="item">
              <p class="item-title">#${escapeHtml(task.id)} ${escapeHtml(task.operation)}</p>
              <p class="item-meta">
                ${escapeHtml(task.identity)}<br>
                Сейчас: ${escapeHtml(task.current_status)}<br>
                Кто делает: ${escapeHtml(task.position)}<br>
                После этапа: ${escapeHtml(task.status_after)}
              </p>
              <button class="success" data-complete-route="${escapeHtml(task.id)}">Завершить этап</button>
            </div>
          `).join("")
        : empty("Доступных маршрутных заданий пока нет.");

      document.querySelectorAll("[data-complete-route]").forEach((button) => {
        button.addEventListener("click", () => completeRouteTask(button.dataset.completeRoute));
      });
    }

    function minutesText(totalMinutes) {
      const minutes = Number(totalMinutes || 0);
      const hours = Math.floor(minutes / 60);
      const tail = String(minutes % 60).padStart(2, "0");
      return `${hours}:${tail}`;
    }

    function renderAdminMenu(admin) {
      $("adminMenu").innerHTML = (admin.menu || []).map((section) => `
        <button class="${state.adminSection === section.id ? "" : "secondary"}" data-admin-section="${escapeHtml(section.id)}">
          ${escapeHtml(section.title)}
        </button>
      `).join("");

      document.querySelectorAll("[data-admin-section]").forEach((button) => {
        button.addEventListener("click", () => {
          state.adminSection = button.dataset.adminSection;
          renderAdmin(state.data.admin);
        });
      });
    }

    function renderAdminSectionButtons(section) {
      $("adminPanelButtons").innerHTML = (section.buttons || []).map((buttonText) => (
        `<button class="pill-button" data-admin-tool="${escapeHtml(buttonText)}">${escapeHtml(buttonText)}</button>`
      )).join("");

      document.querySelectorAll("[data-admin-tool]").forEach((button) => {
        button.addEventListener("click", () => handleAdminTool(button.dataset.adminTool));
      });
    }

    function employeeActions(employee) {
      return `
        <div class="grid">
          <button class="success" data-employee-status="${escapeHtml(employee.id)}" data-status-value="active">Активен</button>
          <button class="danger" data-employee-status="${escapeHtml(employee.id)}" data-status-value="inactive">Отключить</button>
          <button class="secondary" data-employee-position="${escapeHtml(employee.id)}">Должность</button>
        </div>
      `;
    }

    function renderEmployeesList(employees) {
      return employees.length
        ? employees.map((employee) => `
            <div class="item">
              <p class="item-title">${escapeHtml(employee.full_name)}</p>
              <p class="item-meta">
                ID: ${escapeHtml(employee.id)}<br>
                Telegram ID: ${escapeHtml(employee.telegram_id)}<br>
                Должность: ${escapeHtml(employee.position || "-")}<br>
                Статус: ${escapeHtml(employee.status)}
              </p>
              ${employeeActions(employee)}
            </div>
          `).join("")
        : empty("Сотрудников нет.");
    }

    function renderOpenShifts(shifts) {
      return shifts.length
        ? shifts.map((shift) => `
            <div class="item">
              <p class="item-title">#${escapeHtml(shift.id)} ${escapeHtml(shift.employee)}</p>
              <p class="item-meta">${escapeHtml(shift.date)} с ${escapeHtml(shift.start_time)}</p>
              <button class="danger" data-admin-close-shift="${escapeHtml(shift.id)}">Закрыть смену</button>
            </div>
          `).join("")
        : empty("Открытых смен нет.");
    }

    function renderRecentShifts(shifts) {
      return shifts.length
        ? shifts.map((shift) => `
            <div class="item">
              <p class="item-title">#${escapeHtml(shift.id)} ${escapeHtml(shift.employee)}</p>
              <p class="item-meta">
                ${escapeHtml(shift.date)} ${escapeHtml(shift.start_time)}-${escapeHtml(shift.end_time || "")}<br>
                Статус: ${escapeHtml(shift.status)}<br>
                Строк отчёта: ${escapeHtml(shift.operation_count)}
              </p>
              <button class="danger" data-admin-delete-shift="${escapeHtml(shift.id)}">Удалить смену</button>
            </div>
          `).join("")
        : empty("Смен пока нет.");
    }

    function renderOperationsList(operations) {
      const visibleOperations = operations.slice(0, 80);
      const tailMessage = operations.length > visibleOperations.length
        ? `<p class="empty">Показаны первые ${visibleOperations.length} из ${operations.length}. Для точного изменения используйте номер операции.</p>`
        : "";

      return [
        tailMessage,
        visibleOperations.length
          ? visibleOperations.map((operation) => `
              <div class="item">
                <p class="item-title">${escapeHtml(operation.name)}</p>
                <p class="item-meta">
                  Номер: ${escapeHtml(operation.number)}<br>
                  Должность: ${escapeHtml(operation.position)}<br>
                  Группа: ${escapeHtml(operation.group)}<br>
                  Папка: ${escapeHtml(operation.folder)}<br>
                  Ед.: ${escapeHtml(operation.unit)}<br>
                  Статус: ${operation.active ? "активна" : "скрыта"}
                </p>
                <div class="grid">
                  <button class="secondary" data-admin-edit-operation="${escapeHtml(operation.number)}">Изменить</button>
                  <button class="${operation.active ? "danger" : "success"}" data-admin-toggle-operation="${escapeHtml(operation.number)}" data-operation-action="${operation.active ? "hide" : "restore"}">
                    ${operation.active ? "Скрыть" : "Вернуть"}
                  </button>
                </div>
              </div>
            `).join("")
          : empty("Операций нет."),
      ].join("");
    }

    function renderAdminReport(report) {
      if (!report) {
        $("adminReportOutput").innerHTML = empty("Выберите отчёт.");
        return;
      }

      const summary = report.summary || [];
      const shifts = report.shifts || report.employee_shifts || [];
      const operations = report.operations || report.employee_operations || [];
      const totalShifts = summary.reduce((sum, row) => sum + Number(row.shift_count || 0), 0);
      const totalMinutes = summary.reduce((sum, row) => sum + Number(row.total_minutes || 0), 0);

      let output = item(report.title || "Отчёт", `Период: ${escapeHtml(report.start_date)} — ${escapeHtml(report.end_date)}`);

      if (report.employee_summary) {
        const employee = report.employee_summary;
        output += item(
          employee.full_name,
          `Должность: ${escapeHtml(employee.position || "-")}<br>Смен: ${escapeHtml(employee.shift_count)}<br>Часы: ${escapeHtml(employee.total_time)}`
        );
      } else if (summary.length) {
        output += item("Итого", `Смен: ${escapeHtml(totalShifts)}<br>Часы: ${escapeHtml(minutesText(totalMinutes))}`);
        output += summary.map((row) => item(
          row.full_name,
          `Смен: ${escapeHtml(row.shift_count)}<br>Часы: ${escapeHtml(row.total_time)}`
        )).join("");
      }

      output += shifts.length
        ? item("Смены по дням", shifts.slice(0, 40).map((shift) => (
            `${escapeHtml(shift.date)} — ${escapeHtml(shift.employee || "")} ${escapeHtml(shift.start_time || "")}-${escapeHtml(shift.end_time || "")}, ${escapeHtml(shift.total_time || "")}, ${escapeHtml(shift.status || "")}`
          )).join("<br>"))
        : empty("Смен за период нет.");

      output += operations.length
        ? item("Операции", operations.slice(0, 60).map((row) => {
            if (row.employee) {
              return `${escapeHtml(row.date)} — ${escapeHtml(row.employee)} — ${escapeHtml(row.group)} — ${escapeHtml(row.operation)} — ${escapeHtml(row.size || "-")} / ${escapeHtml(row.color || "-")} — ${escapeHtml(row.quantity)} ${escapeHtml(row.unit)}`;
            }

            return `${escapeHtml(row.operation)} — ${escapeHtml(row.quantity)} ${escapeHtml(row.unit)}`;
          }).join("<br>"))
        : empty("Операций за период нет.");

      $("adminReportOutput").innerHTML = output;
    }

    function renderAdminSection(admin) {
      const section = (admin.menu || []).find((item) => item.id === state.adminSection) || (admin.menu || [])[0];

      if (!section) {
        return;
      }

      $("adminPanelTitle").textContent = section.title;
      renderAdminSectionButtons(section);

      if (section.id === "requests") {
        $("adminPanelContent").innerHTML = admin.pending_employees.length
          ? admin.pending_employees.map((employee) => `
              <div class="item">
                <p class="item-title">${escapeHtml(employee.full_name)}</p>
                <p class="item-meta">
                  ID: ${escapeHtml(employee.id)}<br>
                  Telegram ID: ${escapeHtml(employee.telegram_id)}<br>
                  Должность: ${escapeHtml(employee.position || "-")}<br>
                  Дата заявки: ${escapeHtml(employee.registered_at)}
                </p>
                <div class="grid">
                  <button class="success" data-employee-status="${escapeHtml(employee.id)}" data-status-value="active">Подтвердить</button>
                  <button class="danger" data-employee-status="${escapeHtml(employee.id)}" data-status-value="inactive">Отклонить</button>
                </div>
              </div>
            `).join("")
          : empty("Новых заявок нет.");
      } else if (section.id === "reports") {
        $("adminPanelContent").innerHTML = empty("Используйте блок отчёта ниже. Кнопки этого раздела сохранены как в Telegram-боте.");
      } else if (section.id === "shifts") {
        $("adminPanelContent").innerHTML = [
          item("Открытые смены", ""),
          renderOpenShifts(admin.open_shifts),
          item("Последние смены", ""),
          renderRecentShifts(admin.recent_shifts),
        ].join("");
      } else if (section.id === "employees") {
        $("adminPanelContent").innerHTML = renderEmployeesList(admin.employees);
      } else if (section.id === "operations") {
        $("adminPanelContent").innerHTML = renderOperationsList(admin.operations);
      } else if (section.id === "files") {
        const database = admin.files.database || {};
        const logs = admin.files.logs || [];
        $("adminPanelContent").innerHTML = [
          item(
            "Проверка базы",
            `Путь: ${escapeHtml(database.path)}<br>Файл найден: ${database.exists ? "да" : "нет"}<br>Размер: ${escapeHtml(database.size)} байт<br>Папка копий: ${escapeHtml(database.backup_dir)}<br>Копий базы: ${escapeHtml(database.backup_count)}`
          ),
          logs.length
            ? item("Журнал", logs.slice(0, 20).map((log) => (
                `${escapeHtml(log.changed_at)} — ${escapeHtml(log.action)} — ${escapeHtml(log.details || "")}`
              )).join("<br>"))
            : empty("Журнал пока пуст."),
        ].join("");
      }

      bindAdminActionButtons();
    }

    function renderAdmin(admin) {
      $("adminTab").hidden = !(state.data && state.data.is_admin);

      if (!admin || !admin.ok) {
        return;
      }

      $("adminStatus").textContent = admin.message || "";
      renderAdminMenu(admin);
      renderAdminSection(admin);

      const defaults = admin.period_defaults || {};
      if (!$("adminReportStart").value) {
        $("adminReportStart").value = defaults.start_date || "";
      }
      if (!$("adminReportEnd").value) {
        $("adminReportEnd").value = defaults.end_date || "";
      }

      $("adminEmployeeSelect").innerHTML = optionList(
        (admin.employees || []).map((employee) => `${employee.id} — ${employee.full_name}`)
      );
      renderAdminReport(admin.reports);
    }

    function render(data) {
      state.data = data;
      renderShift(data);
      renderReport(data.report);
      renderRoutes(data.routes);
      renderAdmin(data.admin);
    }

    async function refreshState(message = "") {
      setLoading(true);

      try {
        const data = await api("/api/app/state", {message});
        setLoading(false);
        render(data);
      } catch (error) {
        setLoading(false);
        $("connection").textContent = "Ошибка";
        $("message").textContent = "Не удалось связаться с сервером.";
      }
    }

    async function shiftAction(action) {
      setLoading(true);
      const data = await api(`/api/shift/${action}`);
      setLoading(false);
      render(data);
    }

    async function sendFeedback() {
      const result = await api("/api/feedback/send", {
        category: $("feedbackCategory").value,
        message: $("feedbackMessage").value,
      });

      $("feedbackStatus").textContent = result.message || "";
      $("feedbackStatus").className = `message ${result.ok ? "ok" : "error"}`;

      if (result.ok) {
        $("feedbackMessage").value = "";
        await refreshState(result.message);
      }
    }

    async function createBatch() {
      const result = await api("/api/routes/create-batch", {
        product_name: $("batchProductSelect").value,
        product_size: $("batchSizeSelect").value,
        product_color: $("batchColorSelect").value,
        quantity: $("batchQuantityInput").value,
      });

      $("routeCreateStatus").textContent = result.message || "";
      $("routeCreateStatus").className = `message ${result.ok ? "ok" : "error"}`;

      if (result.ok) {
        $("batchQuantityInput").value = "";
        await refreshState(result.message);
      }
    }

    async function completeRouteTask(batchId) {
      const result = await api("/api/routes/complete", {batch_id: batchId});
      $("routeCreateStatus").textContent = result.message || "";
      $("routeCreateStatus").className = `message ${result.ok ? "ok" : "error"}`;
      await refreshState(result.message || "");
    }

    function selectedAdminEmployeeId() {
      const value = $("adminEmployeeSelect").value || "";
      return value.split(" — ")[0] || "";
    }

    async function loadAdminReport(reportType) {
      const result = await api("/api/admin/report", {
        report_type: reportType,
        start_date: $("adminReportStart").value,
        end_date: $("adminReportEnd").value,
        employee_id: selectedAdminEmployeeId(),
      });

      if (result.ok) {
        renderAdminReport(result.report);
      } else {
        $("adminReportOutput").innerHTML = empty(result.message || "Не удалось получить отчёт.");
      }
    }

    async function updateAdminFromResult(result) {
      if (!result.ok) {
        $("adminStatus").textContent = result.message || "Ошибка.";
        $("adminStatus").className = "message error";
        return;
      }

      state.data.admin = result;
      $("adminStatus").className = "message ok";
      renderAdmin(result);
    }

    async function setEmployeeStatus(employeeId, status) {
      const result = await api("/api/admin/employee/status", {
        employee_id: employeeId,
        status,
      });
      updateAdminFromResult(result);
    }

    async function setEmployeePosition(employeeId) {
      const positions = state.data.admin.positions || [];
      const position = prompt(`Новая должность: ${positions.join(", ")}`);

      if (!position) {
        return;
      }

      const result = await api("/api/admin/employee/position", {
        employee_id: employeeId,
        position,
      });
      updateAdminFromResult(result);
    }

    async function closeShiftAsAdmin(shiftId) {
      const endTime = prompt("Время закрытия смены, например 18:00");

      if (!endTime) {
        return;
      }

      const result = await api("/api/admin/shift/close", {
        shift_id: shiftId,
        end_time: endTime,
      });
      updateAdminFromResult(result);
    }

    async function deleteShiftAsAdmin(shiftId) {
      if (!confirm(`Удалить смену #${shiftId}? Это удалит и строки отчёта этой смены.`)) {
        return;
      }

      const result = await api("/api/admin/shift/delete", {shift_id: shiftId});
      updateAdminFromResult(result);
    }

    async function operationAction(action, number, extra = {}) {
      const result = await api("/api/admin/operation", {
        action,
        number,
        ...extra,
      });
      updateAdminFromResult(result);
    }

    async function editOperation(number) {
      const field = prompt("Что изменить: name, position, operation_group, folder");

      if (!field) {
        return;
      }

      const value = prompt("Новое значение");

      if (!value) {
        return;
      }

      operationAction("update", number, {field, value});
    }

    async function addOperationFromPrompt() {
      const name = prompt("Название операции");

      if (!name) {
        return;
      }

      const position = prompt("Должность: Швея, Упаковщик, Раскройщик, Ремонт") || "";
      const operationGroup = prompt("Группа") || "";
      const folder = prompt("Папка/изделие") || "";
      operationAction("add", 0, {name, position, operation_group: operationGroup, folder});
    }

    function handleAdminTool(toolName) {
      if (toolName === "Отчёт за сегодня") {
        loadAdminReport("today");
      } else if (toolName === "Отчёт за месяц" || toolName === "Выгрузить отчёт") {
        loadAdminReport("month");
      } else if (toolName === "Отчёт за период" || toolName === "Excel за период") {
        loadAdminReport("period");
      } else if (toolName === "Отчёт по сотруднику") {
        loadAdminReport("employee");
      } else if (toolName === "Добавить операцию") {
        addOperationFromPrompt();
      } else if (toolName === "Скрыть операцию" || toolName === "Вернуть операцию" || toolName === "Изменить операцию" || toolName === "Удалить смену") {
        $("adminStatus").textContent = "Выберите нужную строку в списке ниже.";
      } else if (toolName === "Проверка базы" || toolName === "Журнал" || toolName === "Ошибки" || toolName === "Скачать базу" || toolName === "Загрузить базу" || toolName === "Создать копию базы") {
        state.adminSection = "files";
        renderAdmin(state.data.admin);
      } else if (toolName === "Список сотрудников" || toolName === "Активные сотрудники" || toolName === "Неактивные сотрудники" || toolName === "Сменить должность" || toolName === "Активировать сотрудника" || toolName === "Отключить сотрудника") {
        state.adminSection = "employees";
        renderAdmin(state.data.admin);
      } else if (toolName === "Открытые смены" || toolName === "Последние смены") {
        state.adminSection = "shifts";
        renderAdmin(state.data.admin);
      } else if (toolName === "Список операций") {
        state.adminSection = "operations";
        renderAdmin(state.data.admin);
      } else {
        $("adminStatus").textContent = "Эта команда пока оставлена кнопкой меню. Данные раздела показаны ниже.";
      }
    }

    function bindAdminActionButtons() {
      document.querySelectorAll("[data-employee-status]").forEach((button) => {
        button.addEventListener("click", () => setEmployeeStatus(button.dataset.employeeStatus, button.dataset.statusValue));
      });
      document.querySelectorAll("[data-employee-position]").forEach((button) => {
        button.addEventListener("click", () => setEmployeePosition(button.dataset.employeePosition));
      });
      document.querySelectorAll("[data-admin-close-shift]").forEach((button) => {
        button.addEventListener("click", () => closeShiftAsAdmin(button.dataset.adminCloseShift));
      });
      document.querySelectorAll("[data-admin-delete-shift]").forEach((button) => {
        button.addEventListener("click", () => deleteShiftAsAdmin(button.dataset.adminDeleteShift));
      });
      document.querySelectorAll("[data-admin-toggle-operation]").forEach((button) => {
        button.addEventListener("click", () => operationAction(button.dataset.operationAction, button.dataset.adminToggleOperation));
      });
      document.querySelectorAll("[data-admin-edit-operation]").forEach((button) => {
        button.addEventListener("click", () => editOperation(button.dataset.adminEditOperation));
      });
    }

    function activateTab(tabName) {
      state.tab = tabName;
      document.querySelectorAll(".tab").forEach((button) => {
        button.classList.toggle("active", button.dataset.tab === tabName);
      });
      document.querySelectorAll(".section").forEach((section) => {
        section.classList.toggle("active", section.id === `section-${tabName}`);
      });
    }

    document.querySelectorAll(".tab").forEach((button) => {
      button.addEventListener("click", () => activateTab(button.dataset.tab));
    });

    $("openButton").addEventListener("click", () => shiftAction("open"));
    $("closeButton").addEventListener("click", () => shiftAction("close"));
    $("refreshButton").addEventListener("click", () => refreshState());
    $("sendFeedbackButton").addEventListener("click", sendFeedback);
    $("routeProductSelect").addEventListener("change", renderSelectedRoute);
    $("batchProductSelect").addEventListener("change", renderBatchOptions);
    $("createBatchButton").addEventListener("click", createBatch);
    $("adminReportToday").addEventListener("click", () => loadAdminReport("today"));
    $("adminReportMonth").addEventListener("click", () => loadAdminReport("month"));
    $("adminReportPeriod").addEventListener("click", () => loadAdminReport("period"));
    $("adminEmployeeReport").addEventListener("click", () => loadAdminReport("employee"));

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
                "/api/feedback/send",
                "/api/routes/create-batch",
                "/api/routes/complete",
                "/api/admin/dashboard",
                "/api/admin/report",
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

            if path == "/api/app/state":
                result = get_app_state(telegram_id, payload.get("message", ""))
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
