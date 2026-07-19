#!/usr/bin/env python3
"""Merge employees, shifts, and completed operation rows from a legacy bot DB."""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta
from pathlib import Path


REQUIRED_TABLES = {"employees", "operations", "shifts", "shift_operations"}
FULL_IMPORT_TABLES = {
    "cutting_batch_colors",
    "cutting_batch_matrix",
    "cutting_batch_sizes",
    "cutting_batches",
    "data_repairs",
    "edit_logs",
    "fabric_stock",
    "fabric_stock_movements",
    "feedback_entries",
    "production_task_attachments",
    "production_task_colors",
    "production_task_fabric_rolls",
    "production_task_items",
    "production_task_sizes",
    "production_tasks",
    "route_batch_defects",
    "route_batch_history",
    "route_batch_inputs",
    "route_batches",
    "warehouse_stock",
    "warehouse_stock_movements",
}


@dataclass
class ImportSummary:
    source_fingerprint: str
    employees_added: int = 0
    employees_matched: int = 0
    operations_added: int = 0
    operations_matched: int = 0
    shifts_added: int = 0
    shifts_matched: int = 0
    stale_shifts_closed: int = 0
    operation_rows_added: int = 0
    operation_rows_updated: int = 0
    operation_rows_skipped: int = 0
    feedback_entries_added: int = 0
    fabric_stocks_added: int = 0
    fabric_stocks_matched: int = 0
    fabric_movements_added: int = 0
    production_tasks_added: int = 0
    production_tasks_matched: int = 0
    production_task_rows_added: int = 0
    cutting_batches_added: int = 0
    cutting_batches_matched: int = 0
    cutting_batch_rows_added: int = 0
    warehouse_stocks_added: int = 0
    warehouse_stocks_matched: int = 0
    warehouse_movements_added: int = 0
    route_batches_added: int = 0
    route_batches_matched: int = 0
    route_batch_rows_added: int = 0
    edit_logs_added: int = 0
    business_snapshot_imported: int = 0
    business_snapshot_skipped: int = 0


def database_fingerprint(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()[:16]


def table_names(connection: sqlite3.Connection) -> set[str]:
    return {
        row[0]
        for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    }


def ensure_compatible(connection: sqlite3.Connection, label: str) -> None:
    missing = REQUIRED_TABLES - table_names(connection)
    if missing:
        raise ValueError(f"{label}: отсутствуют таблицы {', '.join(sorted(missing))}")


def ensure_full_import_compatible(connection: sqlite3.Connection, label: str) -> None:
    missing = FULL_IMPORT_TABLES - table_names(connection)
    if missing:
        raise ValueError(
            f"{label}: для полного импорта отсутствуют таблицы {', '.join(sorted(missing))}"
        )


def target_columns(connection: sqlite3.Connection, table: str) -> set[str]:
    return {row[1] for row in connection.execute(f'PRAGMA table_info("{table}")')}


def insert_compatible_row(
    connection: sqlite3.Connection,
    table: str,
    source_row: sqlite3.Row,
    *,
    overrides: dict[str, object] | None = None,
) -> int:
    values = dict(source_row)
    values.pop("id", None)
    values.update(overrides or {})
    allowed = target_columns(connection, table)
    columns = [column for column in values if column in allowed]
    placeholders = ", ".join("?" for _ in columns)
    quoted_columns = ", ".join(f'"{column}"' for column in columns)
    cursor = connection.execute(
        f'INSERT INTO "{table}" ({quoted_columns}) VALUES ({placeholders})',
        tuple(values[column] for column in columns),
    )
    return int(cursor.lastrowid)


def mapped_id(mapping: dict[int, int], source_id):
    if source_id is None:
        return None
    return mapping.get(int(source_id))


def close_stale_shift(row: sqlite3.Row, today: date, latest_operation_at: str | None):
    values = dict(row)
    if values["status"] != "open" or values["shift_date"] >= today.isoformat():
        return values, False

    start_time = values["start_time"]
    end_time = values["end_time"] or start_time
    total_minutes = int(values["total_minutes"] or 0)
    closed_at = values["closed_at"] or values["created_at"]

    if latest_operation_at:
        try:
            start_at = datetime.fromisoformat(f"{values['shift_date']}T{start_time}")
            operation_at = datetime.fromisoformat(latest_operation_at)
            elapsed = operation_at - start_at
            if timedelta(0) <= elapsed <= timedelta(hours=24):
                end_time = operation_at.strftime("%H:%M")
                total_minutes = int(elapsed.total_seconds() // 60)
                closed_at = latest_operation_at
        except (TypeError, ValueError):
            pass

    values.update(
        {
            "end_time": end_time,
            "total_minutes": total_minutes,
            "status": "closed",
            "edit_until": None,
            "closed_at": closed_at,
        }
    )
    return values, True


def import_business_snapshot(
    source: sqlite3.Connection,
    target: sqlite3.Connection,
    summary: ImportSummary,
    *,
    employee_ids: dict[int, int],
    operation_ids: dict[int, int],
    shift_ids: dict[int, int],
) -> None:
    ensure_full_import_compatible(source, "Исходная база")
    ensure_full_import_compatible(target, "Рабочая база")

    repair_key = f"full-bot-snapshot:{summary.source_fingerprint}"
    already_imported = target.execute(
        "SELECT 1 FROM data_repairs WHERE repair_key = ?",
        (repair_key,),
    ).fetchone()
    if already_imported:
        summary.business_snapshot_skipped = 1
        return

    feedback_ids: dict[int, int] = {}
    for row in source.execute("SELECT * FROM feedback_entries ORDER BY id"):
        target_employee_id = mapped_id(employee_ids, row["employee_id"])
        target_shift_id = mapped_id(shift_ids, row["shift_id"])
        if target_employee_id is None:
            continue
        existing = target.execute(
            """
            SELECT id
            FROM feedback_entries
            WHERE employee_id = ? AND shift_id IS ? AND category = ?
              AND message = ? AND created_at = ?
            """,
            (
                target_employee_id,
                target_shift_id,
                row["category"],
                row["message"],
                row["created_at"],
            ),
        ).fetchone()
        if existing is None:
            target_feedback_id = insert_compatible_row(
                target,
                "feedback_entries",
                row,
                overrides={
                    "employee_id": target_employee_id,
                    "shift_id": target_shift_id,
                },
            )
            summary.feedback_entries_added += 1
        else:
            target_feedback_id = int(existing["id"])
        feedback_ids[int(row["id"])] = target_feedback_id

    fabric_stock_ids: dict[int, int] = {}
    for row in source.execute("SELECT * FROM fabric_stock ORDER BY id"):
        existing = target.execute(
            """
            SELECT id
            FROM fabric_stock
            WHERE material_name = ? AND product_color = ? AND unit = ?
            """,
            (row["material_name"], row["product_color"], row["unit"]),
        ).fetchone()
        if existing is None:
            target_stock_id = insert_compatible_row(target, "fabric_stock", row)
            summary.fabric_stocks_added += 1
        else:
            target_stock_id = int(existing["id"])
            target.execute(
                """
                UPDATE fabric_stock
                SET quantity = quantity + ?,
                    updated_at = CASE WHEN updated_at < ? THEN ? ELSE updated_at END
                WHERE id = ?
                """,
                (row["quantity"], row["updated_at"], row["updated_at"], target_stock_id),
            )
            summary.fabric_stocks_matched += 1
        fabric_stock_ids[int(row["id"])] = target_stock_id

    for row in source.execute("SELECT * FROM fabric_stock_movements ORDER BY id"):
        target_employee_id = mapped_id(employee_ids, row["created_by_employee_id"])
        existing = target.execute(
            """
            SELECT id
            FROM fabric_stock_movements
            WHERE material_name = ? AND product_color = ? AND quantity = ?
              AND unit = ? AND movement_type = ? AND comment IS ?
              AND created_by_employee_id IS ? AND created_at = ?
            """,
            (
                row["material_name"],
                row["product_color"],
                row["quantity"],
                row["unit"],
                row["movement_type"],
                row["comment"],
                target_employee_id,
                row["created_at"],
            ),
        ).fetchone()
        if existing is None:
            insert_compatible_row(
                target,
                "fabric_stock_movements",
                row,
                overrides={"created_by_employee_id": target_employee_id},
            )
            summary.fabric_movements_added += 1

    production_task_ids: dict[int, int] = {}
    for row in source.execute("SELECT * FROM production_tasks ORDER BY id"):
        existing = target.execute(
            """
            SELECT id
            FROM production_tasks
            WHERE product_name = ? AND created_at = ?
            """,
            (row["product_name"], row["created_at"]),
        ).fetchone()
        overrides = {
            "created_by_employee_id": mapped_id(employee_ids, row["created_by_employee_id"]),
            "assigned_employee_id": mapped_id(employee_ids, row["assigned_employee_id"]),
        }
        if existing is None:
            target_task_id = insert_compatible_row(
                target,
                "production_tasks",
                row,
                overrides=overrides,
            )
            summary.production_tasks_added += 1
        else:
            target_task_id = int(existing["id"])
            summary.production_tasks_matched += 1
        production_task_ids[int(row["id"])] = target_task_id

    production_children = (
        ("production_task_sizes", ("product_size",)),
        ("production_task_colors", ("product_color",)),
        ("production_task_items", ("product_size", "product_color")),
        ("production_task_fabric_rolls", ("material_name", "product_color")),
    )
    for table, key_columns in production_children:
        for row in source.execute(f'SELECT * FROM "{table}" ORDER BY id'):
            target_task_id = mapped_id(production_task_ids, row["task_id"])
            if target_task_id is None:
                continue
            clauses = " AND ".join(f'"{column}" = ?' for column in key_columns)
            values = [target_task_id, *(row[column] for column in key_columns)]
            existing = target.execute(
                f'SELECT id FROM "{table}" WHERE task_id = ? AND {clauses}',
                values,
            ).fetchone()
            if existing is None:
                insert_compatible_row(
                    target,
                    table,
                    row,
                    overrides={"task_id": target_task_id},
                )
                summary.production_task_rows_added += 1

    for row in source.execute("SELECT * FROM production_task_attachments ORDER BY id"):
        target_task_id = mapped_id(production_task_ids, row["task_id"])
        if target_task_id is None:
            continue
        existing = target.execute(
            "SELECT id FROM production_task_attachments WHERE task_id = ?",
            (target_task_id,),
        ).fetchone()
        if existing is None:
            insert_compatible_row(
                target,
                "production_task_attachments",
                row,
                overrides={"task_id": target_task_id},
            )
            summary.production_task_rows_added += 1

    cutting_batch_ids: dict[int, int] = {}
    cutting_reference_columns = {
        "production_task_id": production_task_ids,
        "contour_shift_id": shift_ids,
        "contour_operation_id": operation_ids,
        "contour_employee_id": employee_ids,
        "layout_shift_id": shift_ids,
        "layout_operation_id": operation_ids,
        "layout_employee_id": employee_ids,
        "cutting_shift_id": shift_ids,
        "cutting_operation_id": operation_ids,
        "cutting_employee_id": employee_ids,
        "formed_shift_id": shift_ids,
        "formed_operation_id": operation_ids,
        "formed_employee_id": employee_ids,
    }
    for row in source.execute("SELECT * FROM cutting_batches ORDER BY id"):
        target_task_id = mapped_id(production_task_ids, row["production_task_id"])
        existing = target.execute(
            """
            SELECT id
            FROM cutting_batches
            WHERE product_name = ? AND production_task_id IS ? AND created_at = ?
            """,
            (row["product_name"], target_task_id, row["created_at"]),
        ).fetchone()
        overrides = {
            column: mapped_id(mapping, row[column])
            for column, mapping in cutting_reference_columns.items()
        }
        if existing is None:
            target_batch_id = insert_compatible_row(
                target,
                "cutting_batches",
                row,
                overrides=overrides,
            )
            summary.cutting_batches_added += 1
        else:
            target_batch_id = int(existing["id"])
            summary.cutting_batches_matched += 1
        cutting_batch_ids[int(row["id"])] = target_batch_id

    cutting_children = (
        ("cutting_batch_sizes", ("product_size",)),
        ("cutting_batch_colors", ("product_color",)),
        ("cutting_batch_matrix", ("product_size", "product_color")),
    )
    for table, key_columns in cutting_children:
        for row in source.execute(f'SELECT * FROM "{table}" ORDER BY id'):
            target_batch_id = mapped_id(cutting_batch_ids, row["batch_id"])
            if target_batch_id is None:
                continue
            clauses = " AND ".join(f'"{column}" = ?' for column in key_columns)
            values = [target_batch_id, *(row[column] for column in key_columns)]
            existing = target.execute(
                f'SELECT id FROM "{table}" WHERE batch_id = ? AND {clauses}',
                values,
            ).fetchone()
            if existing is None:
                insert_compatible_row(
                    target,
                    table,
                    row,
                    overrides={"batch_id": target_batch_id},
                )
                summary.cutting_batch_rows_added += 1

    warehouse_stock_ids: dict[int, int] = {}
    warehouse_key_columns = (
        "item_type",
        "product_name",
        "product_size",
        "product_color",
        "stage_name",
        "ready_for_position",
        "unit",
    )
    for row in source.execute("SELECT * FROM warehouse_stock ORDER BY id"):
        clauses = " AND ".join(f'"{column}" = ?' for column in warehouse_key_columns)
        existing = target.execute(
            f'SELECT id FROM warehouse_stock WHERE {clauses}',
            tuple(row[column] for column in warehouse_key_columns),
        ).fetchone()
        if existing is None:
            target_stock_id = insert_compatible_row(target, "warehouse_stock", row)
            summary.warehouse_stocks_added += 1
        else:
            target_stock_id = int(existing["id"])
            target.execute(
                """
                UPDATE warehouse_stock
                SET quantity = quantity + ?,
                    updated_at = CASE WHEN updated_at < ? THEN ? ELSE updated_at END
                WHERE id = ?
                """,
                (row["quantity"], row["updated_at"], row["updated_at"], target_stock_id),
            )
            summary.warehouse_stocks_matched += 1
        warehouse_stock_ids[int(row["id"])] = target_stock_id

    route_batch_ids: dict[int, int] = {}
    route_batch_new_ids: set[int] = set()
    route_rows = list(source.execute("SELECT * FROM route_batches ORDER BY id"))
    for row in route_rows:
        existing = target.execute(
            """
            SELECT id
            FROM route_batches
            WHERE product_name = ? AND product_size = ? AND product_color = ?
              AND quantity = ? AND created_at = ?
            """,
            (
                row["product_name"],
                row["product_size"],
                row["product_color"],
                row["quantity"],
                row["created_at"],
            ),
        ).fetchone()
        overrides = {
            "created_by_employee_id": mapped_id(employee_ids, row["created_by_employee_id"]),
            "assigned_employee_id": mapped_id(employee_ids, row["assigned_employee_id"]),
            "source_stock_id": mapped_id(warehouse_stock_ids, row["source_stock_id"]),
            "source_cutting_batch_id": mapped_id(
                cutting_batch_ids,
                row["source_cutting_batch_id"],
            ),
            "parent_batch_id": None,
        }
        if existing is None:
            target_batch_id = insert_compatible_row(
                target,
                "route_batches",
                row,
                overrides=overrides,
            )
            route_batch_new_ids.add(target_batch_id)
            summary.route_batches_added += 1
        else:
            target_batch_id = int(existing["id"])
            summary.route_batches_matched += 1
        route_batch_ids[int(row["id"])] = target_batch_id

    for row in route_rows:
        target_batch_id = mapped_id(route_batch_ids, row["id"])
        target_parent_id = mapped_id(route_batch_ids, row["parent_batch_id"])
        if target_batch_id in route_batch_new_ids and target_parent_id is not None:
            target.execute(
                "UPDATE route_batches SET parent_batch_id = ? WHERE id = ?",
                (target_parent_id, target_batch_id),
            )

    for row in source.execute("SELECT * FROM route_batch_inputs ORDER BY id"):
        target_batch_id = mapped_id(route_batch_ids, row["batch_id"])
        target_stock_id = mapped_id(warehouse_stock_ids, row["stock_id"])
        if target_batch_id is None or target_stock_id is None:
            continue
        existing = target.execute(
            """
            SELECT id
            FROM route_batch_inputs
            WHERE batch_id = ? AND stock_id = ? AND input_role = ?
            """,
            (target_batch_id, target_stock_id, row["input_role"]),
        ).fetchone()
        if existing is None:
            insert_compatible_row(
                target,
                "route_batch_inputs",
                row,
                overrides={"batch_id": target_batch_id, "stock_id": target_stock_id},
            )
            summary.route_batch_rows_added += 1

    for row in source.execute("SELECT * FROM route_batch_history ORDER BY id"):
        target_batch_id = mapped_id(route_batch_ids, row["batch_id"])
        if target_batch_id is None:
            continue
        existing = target.execute(
            "SELECT id FROM route_batch_history WHERE batch_id = ? AND step_index = ?",
            (target_batch_id, row["step_index"]),
        ).fetchone()
        if existing is None:
            insert_compatible_row(
                target,
                "route_batch_history",
                row,
                overrides={
                    "batch_id": target_batch_id,
                    "employee_id": mapped_id(employee_ids, row["employee_id"]),
                },
            )
            summary.route_batch_rows_added += 1

    for row in source.execute("SELECT * FROM route_batch_defects ORDER BY id"):
        target_batch_id = mapped_id(route_batch_ids, row["batch_id"])
        if target_batch_id is None:
            continue
        target_rework_id = mapped_id(route_batch_ids, row["rework_batch_id"])
        existing = target.execute(
            """
            SELECT id
            FROM route_batch_defects
            WHERE batch_id = ? AND operation_name = ? AND quantity = ?
              AND reason = ? AND disposition = ? AND created_at = ?
            """,
            (
                target_batch_id,
                row["operation_name"],
                row["quantity"],
                row["reason"],
                row["disposition"],
                row["created_at"],
            ),
        ).fetchone()
        if existing is None:
            insert_compatible_row(
                target,
                "route_batch_defects",
                row,
                overrides={
                    "batch_id": target_batch_id,
                    "employee_id": mapped_id(employee_ids, row["employee_id"]),
                    "rework_batch_id": target_rework_id,
                },
            )
            summary.route_batch_rows_added += 1

    for row in source.execute("SELECT * FROM warehouse_stock_movements ORDER BY id"):
        target_stock_id = mapped_id(warehouse_stock_ids, row["stock_id"])
        target_source_id = row["source_id"]
        if row["source_type"] == "cutting_batch":
            target_source_id = mapped_id(cutting_batch_ids, row["source_id"])
        elif row["source_type"] == "route_batch":
            target_source_id = mapped_id(route_batch_ids, row["source_id"])
        target_employee_id = mapped_id(employee_ids, row["created_by_employee_id"])
        existing = target.execute(
            """
            SELECT id
            FROM warehouse_stock_movements
            WHERE stock_id IS ? AND item_type = ? AND product_name = ?
              AND product_size = ? AND product_color = ? AND stage_name = ?
              AND ready_for_position = ? AND quantity = ? AND unit = ?
              AND movement_type = ? AND source_type IS ? AND source_id IS ?
              AND created_by_employee_id IS ? AND created_at = ?
            """,
            (
                target_stock_id,
                row["item_type"],
                row["product_name"],
                row["product_size"],
                row["product_color"],
                row["stage_name"],
                row["ready_for_position"],
                row["quantity"],
                row["unit"],
                row["movement_type"],
                row["source_type"],
                target_source_id,
                target_employee_id,
                row["created_at"],
            ),
        ).fetchone()
        if existing is None:
            insert_compatible_row(
                target,
                "warehouse_stock_movements",
                row,
                overrides={
                    "stock_id": target_stock_id,
                    "source_id": target_source_id,
                    "created_by_employee_id": target_employee_id,
                },
            )
            summary.warehouse_movements_added += 1

    entity_maps = {
        "cutting_batch": cutting_batch_ids,
        "employee": employee_ids,
        "fabric_stock": fabric_stock_ids,
        "feedback": feedback_ids,
        "operation": operation_ids,
        "production_task": production_task_ids,
        "route_batch": route_batch_ids,
        "shift": shift_ids,
    }
    for row in source.execute("SELECT * FROM edit_logs ORDER BY id"):
        entity_id = row["entity_id"]
        mapping = entity_maps.get(row["entity_type"])
        if mapping is not None:
            entity_id = mapped_id(mapping, entity_id)
        existing = target.execute(
            """
            SELECT id
            FROM edit_logs
            WHERE changed_by = ? AND role = ? AND action = ?
              AND entity_type = ? AND entity_id IS ? AND details IS ? AND changed_at = ?
            """,
            (
                row["changed_by"],
                row["role"],
                row["action"],
                row["entity_type"],
                entity_id,
                row["details"],
                row["changed_at"],
            ),
        ).fetchone()
        if existing is None:
            insert_compatible_row(
                target,
                "edit_logs",
                row,
                overrides={"entity_id": entity_id},
            )
            summary.edit_logs_added += 1

    target.execute(
        "INSERT INTO data_repairs (repair_key, applied_at) VALUES (?, ?)",
        (repair_key, datetime.now().isoformat(timespec="seconds")),
    )
    summary.business_snapshot_imported = 1


def import_legacy_data(
    source_path: str | Path,
    target_path: str | Path,
    *,
    apply: bool = False,
    include_business: bool = False,
    today: date | None = None,
) -> ImportSummary:
    source_path = Path(source_path).expanduser().resolve()
    target_path = Path(target_path).expanduser().resolve()
    if source_path == target_path:
        raise ValueError("Источник и рабочая база должны быть разными файлами.")
    if not source_path.is_file():
        raise FileNotFoundError(f"Не найдена исходная база: {source_path}")
    if not target_path.is_file():
        raise FileNotFoundError(f"Не найдена рабочая база: {target_path}")

    summary = ImportSummary(source_fingerprint=database_fingerprint(source_path))
    source = sqlite3.connect(f"file:{source_path}?mode=ro", uri=True)
    source.row_factory = sqlite3.Row
    target = sqlite3.connect(target_path, timeout=30)
    target.row_factory = sqlite3.Row
    target.execute("PRAGMA foreign_keys = ON")
    target.execute("PRAGMA busy_timeout = 30000")

    try:
        ensure_compatible(source, "Исходная база")
        ensure_compatible(target, "Рабочая база")
        target.execute("BEGIN IMMEDIATE")

        employee_ids: dict[int, int] = {}
        for employee in source.execute(
            """
            SELECT id, telegram_id, full_name, position, role, status, registered_at
            FROM employees
            ORDER BY id
            """
        ):
            existing = target.execute(
                """
                SELECT id, full_name, position, role, status
                FROM employees
                WHERE telegram_id = ?
                """,
                (employee["telegram_id"],),
            ).fetchone()
            if existing is None:
                cursor = target.execute(
                    """
                    INSERT INTO employees (
                        telegram_id, full_name, position, role, status, registered_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        employee["telegram_id"],
                        employee["full_name"],
                        employee["position"],
                        employee["role"] or "employee",
                        employee["status"] or "active",
                        employee["registered_at"],
                    ),
                )
                target_employee_id = cursor.lastrowid
                summary.employees_added += 1
            else:
                target_employee_id = existing["id"]
                target_status = existing["status"]
                if target_status == "pending" and employee["status"] == "active":
                    target_status = "active"
                target.execute(
                    """
                    UPDATE employees
                    SET full_name = CASE WHEN TRIM(COALESCE(full_name, '')) = '' THEN ? ELSE full_name END,
                        position = CASE WHEN TRIM(COALESCE(position, '')) = '' THEN ? ELSE position END,
                        status = ?
                    WHERE id = ?
                    """,
                    (employee["full_name"], employee["position"], target_status, target_employee_id),
                )
                summary.employees_matched += 1
            employee_ids[employee["id"]] = target_employee_id

        operation_ids: dict[int, int] = {}
        used_operation_ids = (
            {row[0] for row in source.execute("SELECT id FROM operations")}
            if include_business
            else {
                row[0]
                for row in source.execute("SELECT DISTINCT operation_id FROM shift_operations")
            }
        )
        for operation in source.execute("SELECT * FROM operations ORDER BY id"):
            if operation["id"] not in used_operation_ids:
                continue
            existing = target.execute(
                "SELECT id FROM operations WHERE number = ?",
                (operation["number"],),
            ).fetchone()
            if existing is None:
                cursor = target.execute(
                    """
                    INSERT INTO operations (
                        number, name, position, operation_group, folder, sort_order, unit, is_active
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        operation["number"],
                        operation["name"],
                        operation["position"],
                        operation["operation_group"],
                        operation["folder"],
                        operation["sort_order"],
                        operation["unit"],
                        operation["is_active"],
                    ),
                )
                target_operation_id = cursor.lastrowid
                summary.operations_added += 1
            else:
                target_operation_id = existing["id"]
                summary.operations_matched += 1
            operation_ids[operation["id"]] = target_operation_id

        shift_ids: dict[int, int] = {}
        import_today = today or date.today()
        for shift in source.execute("SELECT * FROM shifts ORDER BY id"):
            target_employee_id = employee_ids.get(shift["employee_id"])
            if target_employee_id is None:
                continue
            latest_operation = source.execute(
                "SELECT MAX(updated_at) FROM shift_operations WHERE shift_id = ?",
                (shift["id"],),
            ).fetchone()[0]
            shift_values, stale_closed = close_stale_shift(shift, import_today, latest_operation)
            if stale_closed:
                summary.stale_shifts_closed += 1

            existing = target.execute(
                """
                SELECT id, status
                FROM shifts
                WHERE employee_id = ? AND shift_date = ? AND start_time = ?
                ORDER BY id
                LIMIT 1
                """,
                (target_employee_id, shift_values["shift_date"], shift_values["start_time"]),
            ).fetchone()
            if existing is None:
                if shift_values["status"] == "open":
                    another_open = target.execute(
                        "SELECT 1 FROM shifts WHERE employee_id = ? AND status = 'open'",
                        (target_employee_id,),
                    ).fetchone()
                    if another_open is not None:
                        shift_values["status"] = "closed"
                        shift_values["end_time"] = shift_values["end_time"] or shift_values["start_time"]
                        shift_values["total_minutes"] = int(shift_values["total_minutes"] or 0)
                        shift_values["edit_until"] = None
                        shift_values["closed_at"] = shift_values["closed_at"] or shift_values["created_at"]
                        summary.stale_shifts_closed += 1
                cursor = target.execute(
                    """
                    INSERT INTO shifts (
                        employee_id, shift_date, start_time, end_time, total_minutes,
                        status, edit_until, created_at, closed_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        target_employee_id,
                        shift_values["shift_date"],
                        shift_values["start_time"],
                        shift_values["end_time"],
                        shift_values["total_minutes"],
                        shift_values["status"],
                        shift_values["edit_until"],
                        shift_values["created_at"],
                        shift_values["closed_at"],
                    ),
                )
                target_shift_id = cursor.lastrowid
                summary.shifts_added += 1
            else:
                target_shift_id = existing["id"]
                if existing["status"] == "open" and shift_values["status"] == "closed":
                    target.execute(
                        """
                        UPDATE shifts
                        SET end_time = ?, total_minutes = ?, status = 'closed',
                            edit_until = NULL, closed_at = ?
                        WHERE id = ?
                        """,
                        (
                            shift_values["end_time"],
                            shift_values["total_minutes"],
                            shift_values["closed_at"],
                            target_shift_id,
                        ),
                    )
                summary.shifts_matched += 1
            shift_ids[shift["id"]] = target_shift_id

        for operation_row in source.execute("SELECT * FROM shift_operations ORDER BY id"):
            target_shift_id = shift_ids.get(operation_row["shift_id"])
            target_employee_id = employee_ids.get(operation_row["employee_id"])
            target_operation_id = operation_ids.get(operation_row["operation_id"])
            quantity = int(operation_row["quantity"] or 0)
            if not target_shift_id or not target_employee_id or not target_operation_id or quantity <= 0:
                summary.operation_rows_skipped += 1
                continue

            product_size = operation_row["product_size"] or ""
            product_color = operation_row["product_color"] or ""
            existing = target.execute(
                """
                SELECT id, quantity
                FROM shift_operations
                WHERE shift_id = ? AND operation_id = ?
                  AND product_size = ? AND product_color = ?
                """,
                (target_shift_id, target_operation_id, product_size, product_color),
            ).fetchone()
            if existing is None:
                target.execute(
                    """
                    INSERT INTO shift_operations (
                        shift_id, employee_id, operation_id, product_size, product_color,
                        quantity, created_at, updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        target_shift_id,
                        target_employee_id,
                        target_operation_id,
                        product_size,
                        product_color,
                        quantity,
                        operation_row["created_at"],
                        operation_row["updated_at"],
                    ),
                )
                summary.operation_rows_added += 1
            elif quantity > int(existing["quantity"] or 0):
                target.execute(
                    """
                    UPDATE shift_operations
                    SET quantity = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (quantity, operation_row["updated_at"], existing["id"]),
                )
                summary.operation_rows_updated += 1
            else:
                summary.operation_rows_skipped += 1

        if include_business:
            import_business_snapshot(
                source,
                target,
                summary,
                employee_ids=employee_ids,
                operation_ids=operation_ids,
                shift_ids=shift_ids,
            )

        violations = target.execute("PRAGMA foreign_key_check").fetchall()
        if violations:
            raise ValueError(f"Проверка связей не пройдена: {len(violations)} нарушений")

        if apply:
            target.commit()
        else:
            target.rollback()
    except Exception:
        target.rollback()
        raise
    finally:
        source.close()
        target.close()

    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, help="Путь к старому bot.db")
    parser.add_argument("--target", required=True, help="Путь к рабочему bot.db сайта")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Применить импорт. Без флага выполняется проверка с откатом.",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Дополнительно перенести производство, раскрой, склад и журнал изменений.",
    )
    return parser


def main() -> int:
    arguments = build_parser().parse_args()
    summary = import_legacy_data(
        arguments.source,
        arguments.target,
        apply=arguments.apply,
        include_business=arguments.full,
    )
    result = asdict(summary)
    result["mode"] = "applied" if arguments.apply else "dry-run"
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
