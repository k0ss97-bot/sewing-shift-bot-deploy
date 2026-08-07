"""Audit the durable production-to-WMS delivery boundary.

The reconciler is deliberately read-only toward PostgreSQL.  It compares the
SQLite packaging outbox with immutable WMS production receipts, records a
bounded diagnostic report in SQLite and never repairs stock automatically.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Any

from database import get_db_connection, local_now
from wms.connection import get_pg_connection


PRODUCT_KEY_FIELDS = (
    "item_type",
    "product_name",
    "product_size",
    "product_color",
    "stage_name",
    "ready_for_position",
)
DETAIL_LIMIT = 200
STUCK_AFTER_MINUTES = 30


def _product_key(value: Any) -> dict[str, str]:
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except (TypeError, ValueError, json.JSONDecodeError):
            value = {}
    value = value if isinstance(value, dict) else {}
    return {field: str(value.get(field) or "").strip() for field in PRODUCT_KEY_FIELDS}


def _outbox_product_key(entry: dict) -> dict[str, str]:
    return {field: str(entry.get(field) or "").strip() for field in PRODUCT_KEY_FIELDS}


def _parse_datetime(value: Any) -> datetime | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None


def analyse_reconciliation(
    *,
    outbox_entries: list[dict],
    packaging_without_outbox: list[dict],
    movements: list[dict],
    negative_sqlite_stock: list[dict],
    invalid_wms_stock: list[dict],
    now: datetime | None = None,
    stuck_after_minutes: int = STUCK_AFTER_MINUTES,
) -> dict:
    """Compare already collected rows without mutating either data store."""

    now = now or local_now()
    movement_groups: dict[str, list[dict]] = {}
    for movement in movements:
        movement_groups.setdefault(str(movement.get("request_key") or ""), []).append(movement)
    outbox_by_key = {
        str(entry.get("request_key") or ""): entry
        for entry in outbox_entries
        if str(entry.get("request_key") or "")
    }

    details: dict[str, list[dict]] = {
        "packaging_without_outbox": list(packaging_without_outbox)[:DETAIL_LIMIT],
        "outbox_without_receipt": [],
        "receipt_without_outbox": [],
        "duplicate_request_keys": [],
        "product_key_mismatch": [],
        "quantity_mismatch": [],
        "source_mismatch": [],
        "invalid_sqlite_stock": list(negative_sqlite_stock)[:DETAIL_LIMIT],
        "invalid_wms_stock": list(invalid_wms_stock)[:DETAIL_LIMIT],
        "stuck_outbox": [],
    }

    stuck_before = now - timedelta(minutes=max(1, int(stuck_after_minutes)))
    for request_key, entry in outbox_by_key.items():
        matching = movement_groups.get(request_key, [])
        if not matching:
            details["outbox_without_receipt"].append(
                {
                    "outbox_id": entry.get("id"),
                    "route_batch_id": entry.get("route_batch_id"),
                    "request_key": request_key,
                    "status": entry.get("status"),
                    "quantity": int(entry.get("quantity") or 0),
                }
            )
        else:
            movement = matching[0]
            if _outbox_product_key(entry) != _product_key(movement.get("product_key")):
                details["product_key_mismatch"].append(
                    {
                        "outbox_id": entry.get("id"),
                        "movement_id": movement.get("id"),
                        "request_key": request_key,
                        "route_batch_id": entry.get("route_batch_id"),
                    }
                )
            if int(entry.get("quantity") or 0) != int(movement.get("quantity") or 0):
                details["quantity_mismatch"].append(
                    {
                        "outbox_id": entry.get("id"),
                        "movement_id": movement.get("id"),
                        "request_key": request_key,
                        "outbox_quantity": int(entry.get("quantity") or 0),
                        "movement_quantity": int(movement.get("quantity") or 0),
                    }
                )
            if int(entry.get("route_batch_id") or 0) != int(movement.get("source_id") or 0):
                details["source_mismatch"].append(
                    {
                        "outbox_id": entry.get("id"),
                        "movement_id": movement.get("id"),
                        "request_key": request_key,
                        "route_batch_id": entry.get("route_batch_id"),
                        "source_id": movement.get("source_id"),
                    }
                )

        created_at = _parse_datetime(entry.get("created_at"))
        comparable_before = stuck_before
        if created_at is not None and created_at.tzinfo is not None and comparable_before.tzinfo is None:
            comparable_before = comparable_before.replace(tzinfo=created_at.tzinfo)
        if (
            str(entry.get("status") or "") in {"pending", "failed"}
            and created_at is not None
            and created_at <= comparable_before
        ):
            details["stuck_outbox"].append(
                {
                    "outbox_id": entry.get("id"),
                    "route_batch_id": entry.get("route_batch_id"),
                    "status": entry.get("status"),
                    "attempts": int(entry.get("attempts") or 0),
                    "created_at": str(entry.get("created_at") or ""),
                    "last_error": str(entry.get("last_error") or "")[:160],
                }
            )

    for request_key, matching in movement_groups.items():
        if request_key not in outbox_by_key:
            for movement in matching[:DETAIL_LIMIT]:
                details["receipt_without_outbox"].append(
                    {
                        "movement_id": movement.get("id"),
                        "request_key": request_key,
                        "source_id": movement.get("source_id"),
                        "quantity": int(movement.get("quantity") or 0),
                    }
                )
        if len(matching) > 1:
            details["duplicate_request_keys"].append(
                {
                    "request_key": request_key,
                    "movement_ids": [row.get("id") for row in matching[:20]],
                    "count": len(matching),
                }
            )

    details = {key: rows[:DETAIL_LIMIT] for key, rows in details.items()}
    summary = {key: len(rows) for key, rows in details.items()}
    issue_count = sum(summary.values())
    return {
        "ok": issue_count == 0,
        "status": "ok" if issue_count == 0 else "warning",
        "issue_count": issue_count,
        "summary": summary,
        "details": details,
        "checked_at": now.isoformat(),
    }


def _sqlite_rows(conn) -> tuple[list[dict], list[dict], list[dict]]:
    conn.row_factory = __import__("sqlite3").Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM wms_receipt_outbox ORDER BY id")
    outbox = [dict(row) for row in cursor.fetchall()]
    cursor.execute(
        """
        SELECT
            route.id AS route_batch_id,
            route.product_name,
            route.product_size,
            route.product_color,
            route.good_quantity,
            history.completed_at
        FROM route_batches AS route
        JOIN route_batch_history AS history
          ON history.batch_id = route.id AND history.operation_name = 'Упаковка'
        LEFT JOIN wms_receipt_outbox AS outbox ON outbox.route_batch_id = route.id
        WHERE route.status = 'done'
          AND COALESCE(route.good_quantity, 0) > 0
          AND outbox.id IS NULL
        ORDER BY route.id
        """
    )
    packaging_without_outbox = [dict(row) for row in cursor.fetchall()]
    cursor.execute(
        """
        SELECT id, item_type, product_name, product_size, product_color,
               stage_name, ready_for_position, quantity
        FROM warehouse_stock
        WHERE quantity < 0
        ORDER BY id
        """
    )
    invalid_stock = [dict(row) for row in cursor.fetchall()]
    return outbox, packaging_without_outbox, invalid_stock


def _postgres_rows(conn) -> tuple[list[dict], list[dict]]:
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, request_key, product_key, quantity, source_id, occurred_at
            FROM wms_movements
            WHERE movement_type = 'production_receipt'
              AND source_type = 'production'
            ORDER BY id
            """
        )
        movements = [dict(row) for row in cursor.fetchall()]
        cursor.execute(
            """
            SELECT id, product_name, product_size, product_color, quantity,
                   reserved_quantity, location_id, item_state
            FROM warehouse_stock
            WHERE quantity < 0
               OR reserved_quantity < 0
               OR reserved_quantity > quantity
            ORDER BY id
            """
        )
        invalid_stock = [dict(row) for row in cursor.fetchall()]
    conn.rollback()
    return movements, invalid_stock


def _record_run(conn, report: dict, *, started_at: str, error: str = "") -> dict:
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO production_wms_reconciliation_runs (
            status, issue_count, summary_json, details_json, error,
            started_at, finished_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            report["status"],
            int(report.get("issue_count") or 0),
            json.dumps(report.get("summary") or {}, ensure_ascii=False, sort_keys=True),
            json.dumps(report.get("details") or {}, ensure_ascii=False, sort_keys=True),
            str(error or "")[:500],
            started_at,
            report["checked_at"],
        ),
    )
    run_id = cursor.lastrowid
    conn.commit()
    report["run_id"] = int(run_id)
    return report


def run_production_wms_reconciliation(*, sqlite_conn=None, pg_conn=None) -> dict:
    """Run and journal one reconciliation pass.

    Connections can be injected for isolated tests.  PostgreSQL is queried but
    never mutated; its transaction is rolled back after the reads.
    """

    started_at = local_now().isoformat()
    owns_sqlite = sqlite_conn is None
    sqlite_conn = sqlite_conn or get_db_connection()
    try:
        outbox, packaging_without_outbox, invalid_sqlite = _sqlite_rows(sqlite_conn)
        try:
            movements, invalid_wms = _postgres_rows(pg_conn or get_pg_connection())
        except Exception as error:
            report = {
                "ok": False,
                "status": "unavailable",
                "issue_count": 1,
                "summary": {"postgres_unavailable": 1},
                "details": {"postgres_unavailable": [{"error": type(error).__name__}]},
                "checked_at": local_now().isoformat(),
            }
            return _record_run(
                sqlite_conn,
                report,
                started_at=started_at,
                error=type(error).__name__,
            )

        report = analyse_reconciliation(
            outbox_entries=outbox,
            packaging_without_outbox=packaging_without_outbox,
            movements=movements,
            negative_sqlite_stock=invalid_sqlite,
            invalid_wms_stock=invalid_wms,
        )
        return _record_run(sqlite_conn, report, started_at=started_at)
    finally:
        if owns_sqlite:
            sqlite_conn.close()


def get_latest_production_wms_reconciliation() -> dict | None:
    conn = get_db_connection(timeout=2)
    conn.row_factory = __import__("sqlite3").Row
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT * FROM production_wms_reconciliation_runs
            ORDER BY id DESC LIMIT 1
            """
        )
        row = cursor.fetchone()
    except Exception:
        row = None
    conn.close()
    if row is None:
        return None
    result = dict(row)
    for source, target in (("summary_json", "summary"), ("details_json", "details")):
        try:
            result[target] = json.loads(result.pop(source) or "{}")
        except (TypeError, ValueError, json.JSONDecodeError):
            result[target] = {}
    result["ok"] = result.get("status") == "ok"
    return result

