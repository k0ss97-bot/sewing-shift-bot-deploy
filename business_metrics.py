"""Transparent unit economics, turnover and baseline demand forecasting."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Iterable, Mapping


MONEY = Decimal("0.01")
SIX_PLACES = Decimal("0.000001")


def _nonnegative(value, field: str, *, optional: bool = False) -> Decimal | None:
    if optional and value in (None, ""):
        return None
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as error:
        raise ValueError(f"{field} must be numeric") from error
    if not number.is_finite() or number < 0:
        raise ValueError(f"{field} must be non-negative")
    return number


def calculate_unit_economics(inputs: Mapping) -> dict[str, object]:
    quantity = _nonnegative(inputs.get("quantity"), "quantity")
    revenue = _nonnegative(inputs.get("revenue"), "revenue")
    unit_cost = _nonnegative(inputs.get("unit_cost"), "unit_cost", optional=True)
    fees = _nonnegative(inputs.get("marketplace_fees") or 0, "marketplace_fees")
    logistics = _nonnegative(inputs.get("logistics_cost") or 0, "logistics_cost")
    returns = _nonnegative(inputs.get("returns_cost") or 0, "returns_cost")
    other = _nonnegative(inputs.get("other_variable_cost") or 0, "other_variable_cost")
    if unit_cost is None:
        return {
            "status": "unavailable", "revenue": revenue.quantize(MONEY),
            "cogs": None, "contribution_margin": None, "margin_percent": None,
            "warnings": ["Не задана активная себестоимость изделия"],
        }
    cogs = quantity * unit_cost
    contribution = revenue - cogs - fees - logistics - returns - other
    margin_percent = contribution / revenue * 100 if revenue else None
    return {
        "status": "ready" if revenue else "partial",
        "revenue": revenue.quantize(MONEY, rounding=ROUND_HALF_UP),
        "cogs": cogs.quantize(MONEY, rounding=ROUND_HALF_UP),
        "contribution_margin": contribution.quantize(MONEY, rounding=ROUND_HALF_UP),
        "margin_percent": margin_percent.quantize(SIX_PLACES, rounding=ROUND_HALF_UP) if margin_percent is not None else None,
        "warnings": [] if revenue else ["Выручка за период равна нулю; процент маржи не рассчитывается"],
    }


def calculate_inventory_turnover(*, period_cogs, average_inventory_cost, period_days=365) -> dict[str, object]:
    cogs = _nonnegative(period_cogs, "period_cogs")
    inventory = _nonnegative(average_inventory_cost, "average_inventory_cost")
    days = _nonnegative(period_days, "period_days")
    if inventory == 0:
        return {"status": "unavailable", "turnover": None, "days_on_hand": None, "warnings": ["Средняя стоимость остатка равна нулю"]}
    turnover = cogs / inventory
    days_on_hand = days / turnover if turnover else None
    return {
        "status": "ready" if turnover else "partial",
        "turnover": turnover.quantize(SIX_PLACES, rounding=ROUND_HALF_UP),
        "days_on_hand": days_on_hand.quantize(SIX_PLACES, rounding=ROUND_HALF_UP) if days_on_hand is not None else None,
        "warnings": [] if turnover else ["За период нет подтверждённой себестоимости продаж"],
    }


def moving_average_forecast(
    history: Iterable[Mapping], *, horizon_days: int, window_days: int = 7
) -> dict[str, object]:
    """Explainable baseline forecast; never represented as actual sales."""

    if not 1 <= int(horizon_days) <= 366:
        raise ValueError("horizon_days must be between 1 and 366")
    if int(window_days) <= 0:
        raise ValueError("window_days must be positive")
    values = []
    for row in history:
        units = _nonnegative(row.get("units"), "units")
        values.append(units)
    if not values:
        return {"status": "unavailable", "method": "moving_average", "forecast_units": [], "warnings": ["Нет истории продаж"]}
    window = values[-int(window_days):]
    average = sum(window, Decimal(0)) / len(window)
    forecast = [average.quantize(SIX_PLACES, rounding=ROUND_HALF_UP) for _ in range(int(horizon_days))]
    warnings = []
    status = "ready"
    if len(values) < int(window_days):
        status = "partial"
        warnings.append(f"Доступно только {len(values)} дн. истории вместо {int(window_days)}")
    return {
        "status": status,
        "method": "moving_average",
        "history_points": len(values),
        "window_points": len(window),
        "forecast_units": forecast,
        "warnings": warnings,
    }
