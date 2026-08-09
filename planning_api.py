"""Administrative planning read models and deterministic calculations.

The endpoints backed by this module never mutate WMS balances or production
tasks.  They expose the audited calculation engines introduced by migrations
013-017 and report whether the corresponding PostgreSQL schema is available.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Mapping

from business_metrics import (
    calculate_inventory_turnover,
    calculate_unit_economics,
    moving_average_forecast,
)
from quality_metrics import calculate_oee
from wms.capacity import calculate_capacity_plan
from wms.connection import get_pg_connection
from wms.mrp import calculate_material_plan
from wms.optimization import (
    build_pick_waves,
    plan_cycle_counts,
    plan_replenishment,
    slotting_order,
)


PLANNING_MODULES = (
    "mrp", "capacity", "oee", "unit_economics", "inventory_turnover",
    "forecast", "replenishment", "pick_waves", "cycle_count", "slotting",
)


def json_value(value):
    if isinstance(value, Decimal):
        return int(value) if value == value.to_integral_value() else float(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Mapping):
        return {str(key): json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_value(item) for item in value]
    return value


def calculate_planning_model(payload: Mapping) -> dict[str, object]:
    module = str(payload.get("module") or "").strip().lower()
    if module not in PLANNING_MODULES:
        raise ValueError("Выберите доступный модуль планирования.")

    if module == "mrp":
        result = calculate_material_plan(
            payload.get("demands") or [],
            payload.get("bom_lines") or [],
            payload.get("available_rows") or [],
        )
    elif module == "capacity":
        result = calculate_capacity_plan(payload.get("jobs") or [], payload.get("resources") or [])
    elif module == "oee":
        result = calculate_oee(payload.get("inputs") or {})
    elif module == "unit_economics":
        result = calculate_unit_economics(payload.get("inputs") or {})
    elif module == "inventory_turnover":
        inputs = payload.get("inputs") or {}
        result = calculate_inventory_turnover(
            period_cogs=inputs.get("period_cogs"),
            average_inventory_cost=inputs.get("average_inventory_cost"),
            period_days=inputs.get("period_days") or 365,
        )
    elif module == "forecast":
        result = moving_average_forecast(
            payload.get("history") or [],
            horizon_days=int(payload.get("horizon_days", 7)),
            window_days=int(payload.get("window_days", 7)),
        )
    elif module == "replenishment":
        rows = plan_replenishment(payload.get("rows") or [])
        result = {"status": "ready", "recommendation_count": len(rows), "rows": rows}
    elif module == "pick_waves":
        rows = build_pick_waves(
            payload.get("shipments") or [], maximum_units=int(payload.get("maximum_units") or 200)
        )
        result = {"status": "ready", "wave_count": len(rows), "rows": rows}
    elif module == "cycle_count":
        requested_today = payload.get("today") or date.today().isoformat()
        rows = plan_cycle_counts(
            payload.get("locations") or [],
            today=date.fromisoformat(str(requested_today)[:10]),
            maximum_locations=int(payload.get("maximum_locations") or 20),
        )
        result = {"status": "ready", "location_count": len(rows), "rows": rows}
    else:
        rows = slotting_order(payload.get("products") or [])
        result = {"status": "ready", "product_count": len(rows), "rows": rows}

    return {"ok": True, "module": module, "result": json_value(result)}


def _count(cursor, relation: str) -> int:
    cursor.execute(f"SELECT count(*) FROM {relation}")
    return int(cursor.fetchone()[0])


def get_planning_overview() -> dict[str, object]:
    """Return migration/schema readiness and non-sensitive aggregate counts."""

    connection = get_pg_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT filename
                FROM schema_migrations
                WHERE filename IN (
                    '013_bom_mrp.sql', '014_capacity_skills.sql', '015_qms_oee.sql',
                    '016_wms_optimization.sql', '017_costing_forecast.sql',
                    '018_operational_migration_control.sql'
                )
                ORDER BY filename
                """
            )
            migrations = [str(row[0]) for row in cursor.fetchall()]
            if len(migrations) < 6:
                connection.rollback()
                return {
                    "ok": True,
                    "available": False,
                    "migrations": migrations,
                    "message": "Операционные миграции PostgreSQL ещё не применены полностью.",
                    "counts": {},
                }
            counts = {
                "active_bom": _count(cursor, "marketplace.product_bom_versions WHERE status='active'"),
                "mrp_runs": _count(cursor, "marketplace.mrp_runs"),
                "resources": _count(cursor, "planning.resources WHERE is_active"),
                "skills": _count(cursor, "planning.resource_skills"),
                "nonconformances": _count(cursor, "quality.nonconformances WHERE status NOT IN ('closed','scrapped')"),
                "capa_open": _count(cursor, "quality.capa_actions WHERE status NOT IN ('effective','cancelled')"),
                "oee_snapshots": _count(cursor, "quality.oee_snapshots"),
                "replenishment_tasks": _count(cursor, "wms_replenishment_tasks WHERE status NOT IN ('completed','cancelled')"),
                "cycle_count_plans": _count(cursor, "wms_cycle_count_plans WHERE status NOT IN ('completed','cancelled')"),
                "picking_waves": _count(cursor, "wms_picking_waves WHERE status NOT IN ('completed','cancelled')"),
                "active_costs": _count(cursor, "analytics.product_cost_versions WHERE status='active'"),
                "forecast_runs": _count(cursor, "analytics.forecast_runs"),
            }
        connection.rollback()
        return {
            "ok": True,
            "available": True,
            "migrations": migrations,
            "counts": counts,
            "modules": list(PLANNING_MODULES),
        }
    except Exception:
        connection.rollback()
        return {
            "ok": True,
            "available": False,
            "migrations": [],
            "counts": {},
            "message": "PostgreSQL планирования временно недоступен.",
        }
