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


def import_legacy_data(
    source_path: str | Path,
    target_path: str | Path,
    *,
    apply: bool = False,
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
        used_operation_ids = {
            row[0] for row in source.execute("SELECT DISTINCT operation_id FROM shift_operations")
        }
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
    return parser


def main() -> int:
    arguments = build_parser().parse_args()
    summary = import_legacy_data(arguments.source, arguments.target, apply=arguments.apply)
    result = asdict(summary)
    result["mode"] = "applied" if arguments.apply else "dry-run"
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
