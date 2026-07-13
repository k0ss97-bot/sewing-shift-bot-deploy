"""Build a deterministic demo database for reviewing the administrator report."""

from __future__ import annotations

import argparse
import json
import math
import os
import sqlite3
import tempfile
from collections import defaultdict
from datetime import date, datetime, time, timedelta
from pathlib import Path


ADMIN_TELEGRAM_ID = 9001
DEFECTS_PER_PRODUCT = 12
SHIFT_START = "08:00"
SHIFT_END = "20:00"
SHIFT_MINUTES = 12 * 60

POSITIONS_PER_TEAM = {
    "Раскройщик": 1,
    "Швея": 5,
    "Упаковщик": 2,
}

DEFECT_REASONS = {
    "Раскройщик": "Ошибка раскроя",
    "Швея": "Дефект строчки",
    "Упаковщик": "Повреждение фурнитуры",
}


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--db-dir",
        default="/private/tmp/sewing-admin-report-demo",
        help="Directory for the isolated demo bot.db.",
    )
    parser.add_argument("--through", default=date.today().isoformat(), help="Last demo date (YYYY-MM-DD).")
    parser.add_argument("--plan-per-product", type=int, default=300)
    parser.add_argument("--summary-json", default="")
    parser.add_argument("--export-xlsx", default="")
    return parser.parse_args()


def iso_at(day: date, hour: int, minute: int = 0):
    return datetime.combine(day, time(hour, minute)).isoformat(timespec="seconds")


def month_dates(through: date):
    first = through.replace(day=1)
    return [first + timedelta(days=offset) for offset in range((through - first).days + 1)]


def distribute_quantity(total: int, combinations: int):
    base, remainder = divmod(total, combinations)
    return [base + (1 if index < remainder else 0) for index in range(combinations)]


def team_for_day(day: date, month_start: date):
    block = (day - month_start).days // 2
    return "А" if block % 2 == 0 else "Б"


def reset_business_data(cursor):
    tables = [
        "route_batch_defects",
        "route_batch_history",
        "route_batch_inputs",
        "route_batches",
        "production_task_attachments",
        "production_task_fabric_rolls",
        "production_task_items",
        "production_task_colors",
        "production_task_sizes",
        "cutting_batch_matrix",
        "cutting_batch_colors",
        "cutting_batch_sizes",
        "cutting_batches",
        "production_tasks",
        "warehouse_stock_movements",
        "warehouse_stock",
        "fabric_stock_movements",
        "fabric_stock",
        "feedback_entries",
        "shift_operations",
        "shifts",
        "employees",
        "edit_logs",
        "data_repairs",
    ]

    for table in tables:
        cursor.execute(f"DELETE FROM {table}")

    placeholders = ", ".join("?" for _ in tables)
    cursor.execute(f"DELETE FROM sqlite_sequence WHERE name IN ({placeholders})", tables)


def create_employees(cursor, registered_at: str):
    cursor.execute(
        """
        INSERT INTO employees (telegram_id, full_name, position, role, status, registered_at)
        VALUES (?, ?, 'Администратор', 'admin', 'active', ?)
        """,
        (ADMIN_TELEGRAM_ID, "Демо-администратор", registered_at),
    )
    admin_id = cursor.lastrowid
    teams = {}
    next_telegram_id = 910000

    for team_name in ("А", "Б"):
        teams[team_name] = defaultdict(list)
        for position, count in POSITIONS_PER_TEAM.items():
            for index in range(1, count + 1):
                next_telegram_id += 1
                suffix = f" {index}" if count > 1 else ""
                full_name = f"Смена {team_name} · {position}{suffix}"
                cursor.execute(
                    """
                    INSERT INTO employees (telegram_id, full_name, position, role, status, registered_at)
                    VALUES (?, ?, ?, 'employee', 'active', ?)
                    """,
                    (next_telegram_id, full_name, position, registered_at),
                )
                teams[team_name][position].append(cursor.lastrowid)

    return admin_id, teams


def create_shifts(cursor, days: list[date], teams):
    shift_ids = {}
    month_start = days[0]

    for day in days:
        team_name = team_for_day(day, month_start)
        employees = [employee_id for rows in teams[team_name].values() for employee_id in rows]
        for employee_id in employees:
            created_at = iso_at(day, 7, 55)
            closed_at = iso_at(day, 20, 0)
            cursor.execute(
                """
                INSERT INTO shifts (
                    employee_id, shift_date, start_time, end_time, total_minutes,
                    status, edit_until, created_at, closed_at
                )
                VALUES (?, ?, ?, ?, ?, 'closed', ?, ?, ?)
                """,
                (
                    employee_id,
                    day.isoformat(),
                    SHIFT_START,
                    SHIFT_END,
                    SHIFT_MINUTES,
                    iso_at(day + timedelta(days=1), 20, 0),
                    created_at,
                    closed_at,
                ),
            )
            shift_ids[(day, employee_id)] = cursor.lastrowid

    return shift_ids


def operation_resolver(cursor, get_operation_group):
    cursor.execute(
        """
        SELECT id, name, position, folder, unit
        FROM operations
        WHERE is_active = 1
        """
    )
    operation_rows = cursor.fetchall()
    cache = {}

    def resolve(product_name: str, position: str, operation_name: str):
        key = (product_name, position, operation_name)
        if key in cache:
            return cache[key]

        candidates = [
            row for row in operation_rows
            if row[1] == operation_name and row[2] == position
        ]
        if not candidates:
            raise RuntimeError(f"Не найдена операция маршрута: {position} · {product_name} · {operation_name}")

        candidates.sort(key=lambda row: (row[3] != product_name, row[0]))
        selected = candidates[0]
        cache[key] = {
            "id": selected[0],
            "name": selected[1],
            "position": selected[2],
            "folder": selected[3],
            "unit": selected[4],
            "group": get_operation_group(selected[2], selected[3], selected[1]),
        }
        return cache[key]

    return resolve


def scheduled_step(days: list[date], task_index: int, step_index: int, step_count: int):
    max_start = max(1, len(days) - 3)
    start_index = task_index % max_start
    available_span = min(3, len(days) - 1 - start_index)
    offset = round(step_index * available_span / max(1, step_count - 1))
    day = days[start_index + offset]
    slot = step_index % 4
    start_minutes = 8 * 60 + 20 + slot * 165
    start_hour, start_minute = divmod(start_minutes, 60)
    started_at = datetime.combine(day, time(start_hour, start_minute))
    completed_at = started_at + timedelta(minutes=75 + (task_index + step_index) % 35)
    return day, started_at.isoformat(timespec="seconds"), completed_at.isoformat(timespec="seconds")


def employee_for_step(day: date, month_start: date, teams, position: str, seed: int):
    team_name = team_for_day(day, month_start)
    employees = teams[team_name][position]
    return employees[seed % len(employees)]


def add_shift_operation(cursor, shift_id, employee_id, operation_id, size, color, quantity, timestamp):
    cursor.execute(
        """
        INSERT INTO shift_operations (
            shift_id, employee_id, operation_id, product_size, product_color,
            quantity, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(shift_id, operation_id, product_size, product_color)
        DO UPDATE SET
            employee_id = excluded.employee_id,
            quantity = shift_operations.quantity + excluded.quantity,
            updated_at = excluded.updated_at
        """,
        (shift_id, employee_id, operation_id, size, color, quantity, timestamp, timestamp),
    )


def get_or_create_stock(
    cursor,
    item_type,
    product_name,
    size,
    color,
    stage_name,
    ready_for,
    quantity,
    updated_at,
):
    cursor.execute(
        """
        INSERT INTO warehouse_stock (
            item_type, product_name, product_size, product_color, stage_name,
            ready_for_position, quantity, unit, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, 'шт', ?)
        ON CONFLICT(item_type, product_name, product_size, product_color, stage_name, ready_for_position, unit)
        DO UPDATE SET quantity = excluded.quantity, updated_at = excluded.updated_at
        """,
        (item_type, product_name, size, color, stage_name, ready_for, quantity, updated_at),
    )
    cursor.execute(
        """
        SELECT id FROM warehouse_stock
        WHERE item_type = ? AND product_name = ? AND product_size = ?
          AND product_color = ? AND stage_name = ? AND ready_for_position = ? AND unit = 'шт'
        """,
        (item_type, product_name, size, color, stage_name, ready_for),
    )
    return cursor.fetchone()[0]


def add_warehouse_movement(
    cursor,
    stock_id,
    item_type,
    product_name,
    size,
    color,
    stage_name,
    ready_for,
    quantity,
    movement_type,
    source_type,
    source_id,
    employee_id,
    created_at,
):
    cursor.execute(
        """
        INSERT INTO warehouse_stock_movements (
            stock_id, item_type, product_name, product_size, product_color,
            stage_name, ready_for_position, quantity, unit, movement_type,
            source_type, source_id, created_by_employee_id, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'шт', ?, ?, ?, ?, ?)
        """,
        (
            stock_id, item_type, product_name, size, color, stage_name, ready_for,
            quantity, movement_type, source_type, source_id, employee_id, created_at,
        ),
    )


def seed_production(
    cursor,
    days,
    teams,
    shifts,
    admin_id,
    plan_per_product,
    product_options,
    route_maps,
    cutting_route,
    resolve_operation,
):
    month_start = days[0]
    task_index = 0
    global_batch_index = 0
    material_rolls_used = defaultdict(int)

    for product_name, route in route_maps.items():
        colors = product_options[product_name]["colors"]
        sizes = product_options[product_name]["sizes"]
        combinations = [(color, size) for color in colors for size in sizes]
        quantities = distribute_quantity(plan_per_product, len(combinations))
        product_defects_left = min(DEFECTS_PER_PRODUCT, plan_per_product)

        color_quantities = defaultdict(dict)
        for (color, size), quantity in zip(combinations, quantities):
            color_quantities[color][size] = quantity

        for color_index, color in enumerate(colors):
            size_quantities = color_quantities[color]
            color_total = sum(size_quantities.values())
            rolls = max(1, math.ceil(color_total / 50))
            material_rolls_used[color] += rolls

            cutting_stages = []
            for step_index, step in enumerate(cutting_route):
                day, started_at, completed_at = scheduled_step(days, task_index, step_index, len(route))
                employee_id = employee_for_step(day, month_start, teams, step["position"], task_index + step_index)
                operation = resolve_operation(product_name, step["position"], step["operation"])
                cutting_stages.append((day, started_at, completed_at, employee_id, operation))

            task_created_at = cutting_stages[0][1]
            task_completed_at = cutting_stages[-1][2]
            last_cutter = cutting_stages[-1][3]
            cursor.execute(
                """
                INSERT INTO production_tasks (
                    product_name, status, created_by_employee_id, created_at, updated_at,
                    completed_at, note, assigned_employee_id, assigned_at, priority, due_date
                )
                VALUES (?, 'formed', ?, ?, ?, ?, ?, ?, ?, 'normal', ?)
                """,
                (
                    product_name,
                    admin_id,
                    task_created_at,
                    task_completed_at,
                    task_completed_at,
                    f"Демо-план: {plan_per_product} шт на изделие, цвет {color}",
                    last_cutter,
                    cutting_stages[0][1],
                    cutting_stages[-1][0].isoformat(),
                ),
            )
            production_task_id = cursor.lastrowid
            cursor.executemany(
                "INSERT INTO production_task_sizes (task_id, product_size) VALUES (?, ?)",
                [(production_task_id, size) for size in sizes],
            )
            cursor.execute(
                "INSERT INTO production_task_colors (task_id, product_color) VALUES (?, ?)",
                (production_task_id, color),
            )
            cursor.executemany(
                """
                INSERT INTO production_task_items (
                    task_id, product_size, product_color, contour_quantity, formed_quantity
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                [
                    (production_task_id, size, color, quantity, quantity)
                    for size, quantity in size_quantities.items()
                ],
            )
            cursor.execute(
                """
                INSERT INTO production_task_fabric_rolls (task_id, material_name, product_color, rolls)
                VALUES (?, 'Ткань', ?, ?)
                """,
                (production_task_id, color, rolls),
            )

            contour = cutting_stages[0]
            layout = cutting_stages[1]
            cutting = cutting_stages[2]
            formed = cutting_stages[3]
            cursor.execute(
                """
                INSERT INTO cutting_batches (
                    product_name, production_task_id, status,
                    contour_shift_id, contour_operation_id, contour_employee_id, contour_date,
                    layout_shift_id, layout_operation_id, layout_employee_id, layout_date,
                    cutting_shift_id, cutting_operation_id, cutting_employee_id, cutting_progress,
                    formed_shift_id, formed_operation_id, formed_employee_id, formed_date,
                    created_at, updated_at
                )
                VALUES (?, ?, 'formed', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 100, ?, ?, ?, ?, ?, ?)
                """,
                (
                    product_name,
                    production_task_id,
                    shifts[(contour[0], contour[3])], contour[4]["id"], contour[3], contour[0].isoformat(),
                    shifts[(layout[0], layout[3])], layout[4]["id"], layout[3], layout[0].isoformat(),
                    shifts[(cutting[0], cutting[3])], cutting[4]["id"], cutting[3],
                    shifts[(formed[0], formed[3])], formed[4]["id"], formed[3], formed[0].isoformat(),
                    task_created_at, task_completed_at,
                ),
            )
            cutting_batch_id = cursor.lastrowid
            cursor.executemany(
                "INSERT INTO cutting_batch_sizes (batch_id, product_size, quantity) VALUES (?, ?, ?)",
                [(cutting_batch_id, size, quantity) for size, quantity in size_quantities.items()],
            )
            cursor.execute(
                "INSERT INTO cutting_batch_colors (batch_id, product_color, layers) VALUES (?, ?, ?)",
                (cutting_batch_id, color, max(1, math.ceil(color_total / 30))),
            )
            cursor.executemany(
                """
                INSERT INTO cutting_batch_matrix (batch_id, product_size, product_color, quantity)
                VALUES (?, ?, ?, ?)
                """,
                [(cutting_batch_id, size, color, quantity) for size, quantity in size_quantities.items()],
            )

            for step_index, (day, _started_at, completed_at, employee_id, operation) in enumerate(cutting_stages):
                for size, quantity in size_quantities.items():
                    reported_quantity = 100 if operation["unit"] == "%" else quantity
                    add_shift_operation(
                        cursor,
                        shifts[(day, employee_id)],
                        employee_id,
                        operation["id"],
                        size,
                        color,
                        reported_quantity,
                        completed_at,
                    )

            first_route_step = route[len(cutting_route)]
            for size_index, size in enumerate(sizes):
                quantity = size_quantities[size]
                if quantity <= 0:
                    continue

                has_defect = product_defects_left > 0
                defect_quantity = 1 if has_defect else 0
                if has_defect:
                    product_defects_left -= 1
                good_quantity = quantity - defect_quantity
                first_route_day, route_created_at, _ = scheduled_step(
                    days, task_index, len(cutting_route), len(route)
                )
                final_step_index = len(route) - 1
                final_day, final_started_at, final_completed_at = scheduled_step(
                    days, task_index, final_step_index, len(route)
                )
                final_step = route[final_step_index]
                final_employee = employee_for_step(
                    final_day, month_start, teams, final_step["position"], global_batch_index + final_step_index
                )
                due_date = final_day - timedelta(days=1) if global_batch_index % 10 == 0 else final_day

                source_stock_id = get_or_create_stock(
                    cursor,
                    "semifinished",
                    product_name,
                    size,
                    color,
                    cutting_route[-1]["status_after"],
                    first_route_step["position"],
                    0,
                    route_created_at,
                )
                add_warehouse_movement(
                    cursor,
                    source_stock_id,
                    "semifinished",
                    product_name,
                    size,
                    color,
                    cutting_route[-1]["status_after"],
                    first_route_step["position"],
                    quantity,
                    "receipt",
                    "cutting_batch",
                    cutting_batch_id,
                    formed[3],
                    formed[2],
                )

                cursor.execute(
                    """
                    INSERT INTO route_batches (
                        product_name, product_size, product_color, quantity, route_step_index,
                        status, created_by_employee_id, created_at, updated_at, completed_at,
                        source_stock_id, assigned_employee_id, assigned_at, good_quantity,
                        defect_quantity, priority, due_date, source_cutting_batch_id
                    )
                    VALUES (?, ?, ?, ?, ?, 'done', ?, ?, ?, ?, ?, ?, ?, ?, ?, 'normal', ?, ?)
                    """,
                    (
                        product_name,
                        size,
                        color,
                        quantity,
                        len(route),
                        admin_id,
                        route_created_at,
                        final_completed_at,
                        final_completed_at,
                        source_stock_id,
                        final_employee,
                        final_started_at,
                        good_quantity,
                        defect_quantity,
                        due_date.isoformat(),
                        cutting_batch_id,
                    ),
                )
                route_batch_id = cursor.lastrowid
                cursor.execute(
                    """
                    INSERT INTO route_batch_inputs (batch_id, stock_id, input_role, quantity, created_at)
                    VALUES (?, ?, 'main', ?, ?)
                    """,
                    (route_batch_id, source_stock_id, quantity, route_created_at),
                )
                add_warehouse_movement(
                    cursor,
                    source_stock_id,
                    "semifinished",
                    product_name,
                    size,
                    color,
                    cutting_route[-1]["status_after"],
                    first_route_step["position"],
                    -quantity,
                    "issue",
                    "route_batch",
                    route_batch_id,
                    employee_for_step(
                        first_route_day,
                        month_start,
                        teams,
                        first_route_step["position"],
                        global_batch_index + len(cutting_route),
                    ),
                    route_created_at,
                )

                route_assignments = {}
                for step_index in range(len(cutting_route), len(route)):
                    step = route[step_index]
                    day, _started_at, completed_at = scheduled_step(days, task_index, step_index, len(route))
                    employee_id = employee_for_step(
                        day, month_start, teams, step["position"], global_batch_index + step_index
                    )
                    operation = resolve_operation(product_name, step["position"], step["operation"])
                    route_assignments[step_index] = (day, employee_id, operation, completed_at)
                    cursor.execute(
                        """
                        INSERT INTO route_batch_history (
                            batch_id, step_index, operation_name, position,
                            employee_id, quantity, completed_at
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            route_batch_id,
                            step_index,
                            step["operation"],
                            step["position"],
                            employee_id,
                            good_quantity,
                            completed_at,
                        ),
                    )
                    add_shift_operation(
                        cursor,
                        shifts[(day, employee_id)],
                        employee_id,
                        operation["id"],
                        size,
                        color,
                        good_quantity,
                        completed_at,
                    )

                if defect_quantity:
                    desired_position = ("Раскройщик", "Швея", "Упаковщик")[global_batch_index % 3]
                    defect_candidates = [
                        index for index, step in enumerate(route)
                        if step["position"] == desired_position
                    ]
                    defect_step_index = defect_candidates[global_batch_index % len(defect_candidates)]
                    defect_step = route[defect_step_index]
                    defect_day, _defect_started, defect_completed = scheduled_step(
                        days, task_index, defect_step_index, len(route)
                    )
                    defect_employee = employee_for_step(
                        defect_day,
                        month_start,
                        teams,
                        defect_step["position"],
                        global_batch_index + defect_step_index,
                    )
                    cursor.execute(
                        """
                        INSERT INTO route_batch_defects (
                            batch_id, employee_id, operation_name, position, product_name,
                            product_size, product_color, quantity, reason, disposition,
                            comment, created_at
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Списать', ?, ?)
                        """,
                        (
                            route_batch_id,
                            defect_employee,
                            defect_step["operation"],
                            defect_step["position"],
                            product_name,
                            size,
                            color,
                            defect_quantity,
                            DEFECT_REASONS[defect_step["position"]],
                            "Демонстрационная запись для проверки отчёта",
                            defect_completed,
                        ),
                    )

                finished_stock_id = get_or_create_stock(
                    cursor,
                    "finished",
                    product_name,
                    size,
                    color,
                    final_step["status_after"],
                    "Склад",
                    good_quantity,
                    final_completed_at,
                )
                add_warehouse_movement(
                    cursor,
                    finished_stock_id,
                    "finished",
                    product_name,
                    size,
                    color,
                    final_step["status_after"],
                    "Склад",
                    good_quantity,
                    "receipt",
                    "route_batch",
                    route_batch_id,
                    final_employee,
                    final_completed_at,
                )
                global_batch_index += 1

            task_index += 1

    for color, used_rolls in sorted(material_rolls_used.items()):
        received_rolls = used_rolls + 2
        cursor.execute(
            """
            INSERT INTO fabric_stock (material_name, product_color, quantity, unit, updated_at)
            VALUES ('Ткань', ?, 2, 'рул', ?)
            """,
            (color, iso_at(days[-1], 20, 0)),
        )
        cursor.execute(
            """
            INSERT INTO fabric_stock_movements (
                material_name, product_color, quantity, unit, movement_type,
                comment, created_by_employee_id, created_at
            )
            VALUES ('Ткань', ?, ?, 'рул', 'receipt', ?, ?, ?)
            """,
            (
                color,
                received_rolls,
                "Демо-приход ткани на месячный план",
                admin_id,
                iso_at(days[0], 7, 30),
            ),
        )
        cursor.execute(
            """
            INSERT INTO fabric_stock_movements (
                material_name, product_color, quantity, unit, movement_type,
                comment, created_by_employee_id, created_at
            )
            VALUES ('Ткань', ?, ?, 'рул', 'issue', ?, ?, ?)
            """,
            (
                color,
                -used_rolls,
                "Списание ткани в задания раскроя",
                admin_id,
                iso_at(days[0], 8, 0),
            ),
        )


def validate_demo(cursor, through: date, plan_per_product: int, product_options):
    product_names = list(product_options)
    expected_plan = plan_per_product * len(product_names)
    expected_defects = DEFECTS_PER_PRODUCT * len(product_names)
    expected_good = expected_plan - expected_defects

    cursor.execute("SELECT COUNT(*) FROM employees WHERE role != 'admin'")
    employee_count = cursor.fetchone()[0]
    cursor.execute("SELECT position, COUNT(*) FROM employees WHERE role != 'admin' GROUP BY position")
    employees_by_position = dict(cursor.fetchall())
    cursor.execute("SELECT COUNT(*) FROM shifts")
    shift_count = cursor.fetchone()[0]
    cursor.execute(
        """
        SELECT shifts.shift_date, employees.full_name, employees.position
        FROM shifts
        JOIN employees ON employees.id = shifts.employee_id
        ORDER BY shifts.shift_date, employees.full_name
        """
    )
    shifts_by_date = defaultdict(list)
    for shift_date, full_name, position in cursor.fetchall():
        shifts_by_date[shift_date].append((full_name, position))
    cursor.execute("SELECT COALESCE(SUM(quantity), 0) FROM route_batches WHERE status != 'cancelled'")
    route_plan = cursor.fetchone()[0]
    cursor.execute("SELECT COALESCE(SUM(good_quantity), 0) FROM route_batches WHERE status = 'done'")
    route_good = cursor.fetchone()[0]
    cursor.execute("SELECT COALESCE(SUM(quantity), 0) FROM route_batch_defects")
    defect_quantity = cursor.fetchone()[0]
    cursor.execute("SELECT COALESCE(SUM(quantity), 0) FROM warehouse_stock WHERE item_type = 'finished'")
    finished_quantity = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM production_tasks WHERE status = 'formed'")
    cutting_task_count = cursor.fetchone()[0]
    cursor.execute(
        """
        SELECT employees.full_name, COUNT(shift_operations.id)
        FROM employees
        LEFT JOIN shift_operations ON shift_operations.employee_id = employees.id
        WHERE employees.role != 'admin'
        GROUP BY employees.id
        HAVING COUNT(shift_operations.id) = 0
        """
    )
    employees_without_operations = [row[0] for row in cursor.fetchall()]
    cursor.execute(
        """
        SELECT product_name, SUM(quantity)
        FROM route_batches
        WHERE status != 'cancelled'
        GROUP BY product_name
        ORDER BY product_name
        """
    )
    product_plans = dict(cursor.fetchall())
    cursor.execute(
        """
        SELECT route_batches.product_name, route_batches.product_color
        FROM route_batches
        JOIN route_batch_history ON route_batch_history.batch_id = route_batches.id
        WHERE route_batches.status != 'cancelled'
        GROUP BY route_batches.product_name, route_batches.product_color
        """
    )
    completed_product_colors = set(cursor.fetchall())

    errors = []
    if employee_count != 16:
        errors.append(f"ожидалось 16 сотрудников, получено {employee_count}")
    if employees_by_position != {"Раскройщик": 2, "Упаковщик": 4, "Швея": 10}:
        errors.append(f"неверный состав смен: {employees_by_position}")
    expected_days = month_dates(through)
    if shift_count != len(expected_days) * sum(POSITIONS_PER_TEAM.values()):
        errors.append(f"неверное количество закрытых смен: {shift_count}")
    for day in expected_days:
        day_rows = shifts_by_date.get(day.isoformat(), [])
        position_counts = {
            position: sum(1 for _full_name, employee_position in day_rows if employee_position == position)
            for position in POSITIONS_PER_TEAM
        }
        expected_team = team_for_day(day, expected_days[0])
        if position_counts != POSITIONS_PER_TEAM or any(
            not full_name.startswith(f"Смена {expected_team} ·") for full_name, _position in day_rows
        ):
            errors.append(f"нарушен график 2/2 или состав смены за {day.isoformat()}")
    if route_plan != expected_plan:
        errors.append(f"план {route_plan}, ожидалось {expected_plan}")
    if route_good != expected_good:
        errors.append(f"факт {route_good}, ожидалось {expected_good}")
    if defect_quantity != expected_defects:
        errors.append(f"брак {defect_quantity}, ожидалось {expected_defects}")
    if finished_quantity != expected_good:
        errors.append(f"готовый склад {finished_quantity}, ожидалось {expected_good}")
    if employees_without_operations:
        errors.append(f"нет операций у сотрудников: {', '.join(employees_without_operations)}")
    wrong_product_plans = {name: value for name, value in product_plans.items() if value != plan_per_product}
    if len(product_plans) != len(product_names) or wrong_product_plans:
        errors.append(f"неверный план по изделиям: {wrong_product_plans}")
    expected_product_colors = {
        (product_name, color)
        for product_name, options in product_options.items()
        for color in options["colors"]
    }
    missing_product_colors = expected_product_colors - completed_product_colors
    if missing_product_colors:
        errors.append(f"нет полного маршрута для изделия/цвета: {sorted(missing_product_colors)}")
    if errors:
        raise RuntimeError("; ".join(errors))

    return {
        "period": {"start": through.replace(day=1).isoformat(), "end": through.isoformat()},
        "teams": 2,
        "schedule": "2/2",
        "employees": employee_count,
        "employees_by_position": employees_by_position,
        "closed_shifts": shift_count,
        "products": len(product_names),
        "plan_per_product": plan_per_product,
        "plan": route_plan,
        "fact": route_good,
        "defects": defect_quantity,
        "finished_stock": finished_quantity,
        "cutting_tasks": cutting_task_count,
        "product_plans": product_plans,
    }


def main():
    args = parse_args()
    through = date.fromisoformat(args.through)
    if args.plan_per_product <= DEFECTS_PER_PRODUCT:
        raise SystemExit(f"План должен быть больше {DEFECTS_PER_PRODUCT} шт на изделие.")

    db_dir = Path(args.db_dir).expanduser().resolve()
    temporary_roots = {
        Path(tempfile.gettempdir()).resolve(),
        Path("/private/tmp").resolve(),
    }
    if not any(db_dir == root or root in db_dir.parents for root in temporary_roots):
        raise SystemExit("Демонстрационную базу разрешено создавать только во временной папке.")
    db_dir.mkdir(parents=True, exist_ok=True)
    database_path = db_dir / "bot.db"
    working_database = (Path.cwd() / "bot.db").resolve()
    if database_path == working_database:
        raise SystemExit("Демонстрационный прогон нельзя запускать на рабочей базе.")
    if database_path.exists():
        database_path.unlink()

    os.environ["DB_DIR"] = str(db_dir)
    os.environ["ADMIN_IDS"] = str(ADMIN_TELEGRAM_ID)

    from catalog import PRODUCT_OPTIONS
    from database import DB_NAME, get_operation_group, init_db
    from route_maps import CUTTING_ROUTE, PRODUCT_ROUTE_MAPS

    init_db()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    reset_business_data(cursor)
    days = month_dates(through)
    admin_id, teams = create_employees(cursor, iso_at(days[0], 7, 0))
    shifts = create_shifts(cursor, days, teams)
    resolve_operation = operation_resolver(cursor, get_operation_group)
    seed_production(
        cursor,
        days,
        teams,
        shifts,
        admin_id,
        args.plan_per_product,
        PRODUCT_OPTIONS,
        PRODUCT_ROUTE_MAPS,
        CUTTING_ROUTE,
        resolve_operation,
    )
    summary = validate_demo(
        cursor,
        through,
        args.plan_per_product,
        {product_name: PRODUCT_OPTIONS[product_name] for product_name in PRODUCT_ROUTE_MAPS},
    )
    conn.commit()
    conn.close()

    if args.export_xlsx:
        from miniapp_server import create_period_excel_bytes

        export_path = Path(args.export_xlsx).expanduser().resolve()
        export_path.parent.mkdir(parents=True, exist_ok=True)
        export_path.write_bytes(create_period_excel_bytes(summary["period"]["start"], summary["period"]["end"]))
        summary["export_xlsx"] = str(export_path)

    summary["database"] = str(database_path)
    summary["admin_telegram_id"] = ADMIN_TELEGRAM_ID

    if args.summary_json:
        summary_path = Path(args.summary_json).expanduser().resolve()
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
