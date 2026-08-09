"""Deterministic BOM explosion and material-shortage planning.

This module is deliberately read-only with respect to warehouse balances: an
MRP calculation may persist its audit snapshot, but never reserves or writes
off stock. Physical mutations stay in the existing WMS movement workflow.
"""

from __future__ import annotations

from collections import defaultdict
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import json
from typing import Iterable, Mapping


SIX_PLACES = Decimal("0.000001")


def _decimal(value, *, field: str, allow_zero: bool = True) -> Decimal:
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as error:
        raise ValueError(f"{field} must be numeric") from error
    if not number.is_finite() or number < 0 or (not allow_zero and number == 0):
        raise ValueError(f"{field} must be {'positive' if not allow_zero else 'non-negative'}")
    return number


def component_key(row: Mapping) -> tuple[str, str, str, str, str, str]:
    """Article is authoritative; descriptive fields distinguish legacy rows."""

    component_type = str(row.get("component_type") or "").strip().lower()
    if component_type not in {"material", "semifinished"}:
        raise ValueError("component_type must be material or semifinished")
    article = str(row.get("component_article") or "").strip().casefold()
    name = str(row.get("component_name") or "").strip().casefold()
    size = str(row.get("component_size") or "").strip().casefold()
    color = str(row.get("component_color") or "").strip().casefold()
    unit = str(row.get("unit") or "").strip().casefold()
    if not name or not unit:
        raise ValueError("component_name and unit are required")
    # When article exists it is the product identifier. Size/color/name stay in
    # the key only for components without an article.
    return (
        component_type,
        article,
        "" if article else name,
        "" if article else size,
        "" if article else color,
        unit,
    )


def calculate_material_plan(
    demands: Iterable[Mapping],
    bom_lines: Iterable[Mapping],
    available_rows: Iterable[Mapping],
) -> dict[str, object]:
    normalized_demands: dict[int, Decimal] = defaultdict(Decimal)
    for demand in demands:
        product_master_id = int(demand.get("product_master_id") or 0)
        if product_master_id <= 0:
            raise ValueError("product_master_id must be positive")
        normalized_demands[product_master_id] += _decimal(
            demand.get("quantity"), field="demand quantity", allow_zero=False
        )

    lines_by_product: dict[int, list[Mapping]] = defaultdict(list)
    for line in bom_lines:
        product_master_id = int(line.get("product_master_id") or 0)
        if product_master_id > 0:
            lines_by_product[product_master_id].append(line)

    required: dict[tuple[str, str, str, str, str, str], Decimal] = defaultdict(Decimal)
    identity: dict[tuple[str, str, str, str, str, str], Mapping] = {}
    missing_bom_product_ids: list[int] = []
    for product_master_id, demand_quantity in sorted(normalized_demands.items()):
        product_lines = lines_by_product.get(product_master_id) or []
        if not product_lines:
            missing_bom_product_ids.append(product_master_id)
            continue
        for line in product_lines:
            key = component_key(line)
            quantity_per = _decimal(line.get("quantity_per"), field="quantity_per", allow_zero=False)
            scrap_percent = _decimal(line.get("scrap_percent") or 0, field="scrap_percent")
            if scrap_percent > 100:
                raise ValueError("scrap_percent must not exceed 100")
            required[key] += demand_quantity * quantity_per * (Decimal(1) + scrap_percent / 100)
            identity[key] = line

    available: dict[tuple[str, str, str, str, str, str], Decimal] = defaultdict(Decimal)
    for row in available_rows:
        key = component_key(row)
        available[key] += _decimal(row.get("available_quantity") or 0, field="available_quantity")

    rows = []
    for key in sorted(required):
        line = identity[key]
        required_quantity = required[key].quantize(SIX_PLACES, rounding=ROUND_HALF_UP)
        available_quantity = available[key].quantize(SIX_PLACES, rounding=ROUND_HALF_UP)
        shortage_quantity = max(Decimal(0), required_quantity - available_quantity)
        rows.append(
            {
                "component_key": list(key),
                "component_type": str(line.get("component_type") or ""),
                "component_article": str(line.get("component_article") or ""),
                "component_name": str(line.get("component_name") or ""),
                "component_size": str(line.get("component_size") or ""),
                "component_color": str(line.get("component_color") or ""),
                "unit": str(line.get("unit") or ""),
                "required_quantity": required_quantity,
                "available_quantity": available_quantity,
                "shortage_quantity": shortage_quantity,
            }
        )

    shortage_count = sum(row["shortage_quantity"] > 0 for row in rows)
    status = "incomplete" if missing_bom_product_ids else "shortage" if shortage_count else "ready"
    return {
        "status": status,
        "demand_count": len(normalized_demands),
        "component_count": len(rows),
        "shortage_count": shortage_count,
        "missing_bom_product_ids": missing_bom_product_ids,
        "lines": rows,
    }


def persist_plan(
    connection,
    plan: Mapping,
    *,
    request_key: str,
    source_type: str = "manual",
    source_reference: str = "",
    employee_id: int | None = None,
) -> int:
    """Persist an immutable, idempotent planning snapshot; never alter stock."""

    if not str(request_key or "").strip():
        raise ValueError("request_key is required")
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO marketplace.mrp_runs (
                request_key, source_type, source_reference, status, demand_count,
                component_count, shortage_count, missing_bom_product_ids,
                created_by_employee_id
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s)
            ON CONFLICT (request_key) DO NOTHING
            RETURNING id
            """,
            (
                request_key, source_type, source_reference, plan["status"],
                plan["demand_count"], plan["component_count"], plan["shortage_count"],
                json.dumps(plan["missing_bom_product_ids"]), employee_id,
            ),
        )
        inserted = cursor.fetchone()
        if inserted is None:
            cursor.execute("SELECT id FROM marketplace.mrp_runs WHERE request_key=%s", (request_key,))
            return int(cursor.fetchone()[0])
        run_id = int(inserted[0])
        for row in plan["lines"]:
            cursor.execute(
                """
                INSERT INTO marketplace.mrp_run_lines (
                    run_id, component_key, component_type, component_article,
                    component_name, component_size, component_color, unit,
                    required_quantity, available_quantity, shortage_quantity
                ) VALUES (%s,%s::jsonb,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    run_id, json.dumps(row["component_key"], ensure_ascii=False),
                    row["component_type"], row["component_article"], row["component_name"],
                    row["component_size"], row["component_color"], row["unit"],
                    row["required_quantity"], row["available_quantity"], row["shortage_quantity"],
                ),
            )
    return run_id
