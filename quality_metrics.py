"""Quality workflow rules and OEE calculations with explicit data quality."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Mapping


SIX_PLACES = Decimal("0.000001")
CAPA_TRANSITIONS = {
    "draft": {"approved", "cancelled"},
    "approved": {"in_progress", "cancelled"},
    "in_progress": {"verification", "cancelled"},
    "verification": {"effective", "ineffective", "in_progress"},
    "ineffective": {"in_progress", "cancelled"},
    "effective": set(),
    "cancelled": set(),
}


def can_transition_capa(current: str, target: str) -> bool:
    return str(target) in CAPA_TRANSITIONS.get(str(current), set())


def require_capa_transition(current: str, target: str) -> None:
    if not can_transition_capa(current, target):
        raise ValueError(f"CAPA transition {current!r} -> {target!r} is not allowed")


def _number(inputs: Mapping, key: str) -> Decimal | None:
    value = inputs.get(key)
    if value is None or value == "":
        return None
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as error:
        raise ValueError(f"{key} must be numeric") from error
    if not number.is_finite() or number < 0:
        raise ValueError(f"{key} must be non-negative")
    return number


def _rounded(value: Decimal | None) -> Decimal | None:
    return value.quantize(SIX_PLACES, rounding=ROUND_HALF_UP) if value is not None else None


def calculate_oee(inputs: Mapping) -> dict[str, object]:
    """Calculate Availability × Performance × Quality without fake zeroes."""

    planned = _number(inputs, "planned_production_minutes")
    downtime = _number(inputs, "unplanned_downtime_minutes")
    total_units = _number(inputs, "total_units")
    good_units = _number(inputs, "good_units")
    ideal_cycle = _number(inputs, "ideal_cycle_minutes")
    missing = [
        key for key, value in (
            ("planned_production_minutes", planned),
            ("unplanned_downtime_minutes", downtime),
            ("total_units", total_units),
            ("good_units", good_units),
            ("ideal_cycle_minutes", ideal_cycle),
        ) if value is None
    ]
    if missing:
        return {
            "status": "unavailable", "availability": None, "performance": None,
            "quality": None, "oee": None,
            "warnings": [f"Нет исходных данных: {', '.join(missing)}"],
        }
    if planned == 0:
        return {
            "status": "unavailable", "availability": None, "performance": None,
            "quality": None, "oee": None,
            "warnings": ["Плановое производственное время равно нулю"],
        }
    if downtime > planned:
        raise ValueError("unplanned_downtime_minutes must not exceed planned_production_minutes")
    if good_units > total_units:
        raise ValueError("good_units must not exceed total_units")

    operating = planned - downtime
    availability = operating / planned
    quality = good_units / total_units if total_units else None
    performance = ideal_cycle * total_units / operating if operating else None
    warnings = []
    if total_units == 0:
        warnings.append("За период нет подтверждённого выпуска")
    if operating == 0:
        warnings.append("Всё плановое время отмечено как простой")
    if performance is not None and performance > 1:
        warnings.append("Производительность выше 100%: проверьте идеальный цикл или количество")
        performance = Decimal(1)
    oee = availability * performance * quality if performance is not None and quality is not None else None
    status = "ready" if oee is not None else "partial"
    return {
        "status": status,
        "availability": _rounded(availability),
        "performance": _rounded(performance),
        "quality": _rounded(quality),
        "oee": _rounded(oee),
        "warnings": warnings,
    }
