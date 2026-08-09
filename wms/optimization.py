"""Pure WMS planning helpers; callers explicitly release resulting work."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Iterable, Mapping


def _nonnegative_int(value, field: str) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{field} must be an integer") from error
    if number < 0:
        raise ValueError(f"{field} must be non-negative")
    return number


def plan_replenishment(rows: Iterable[Mapping]) -> list[dict[str, object]]:
    """Recommend pick-face top-ups without changing any warehouse balance."""

    recommendations = []
    for row in rows:
        current = _nonnegative_int(row.get("pick_available"), "pick_available")
        minimum = _nonnegative_int(row.get("pick_minimum"), "pick_minimum")
        maximum = _nonnegative_int(row.get("pick_maximum"), "pick_maximum")
        reserve = _nonnegative_int(row.get("reserve_available"), "reserve_available")
        if maximum < minimum:
            raise ValueError("pick_maximum must not be less than pick_minimum")
        if current >= minimum or reserve == 0:
            continue
        quantity = min(maximum - current, reserve)
        from_location_id = int(row.get("from_location_id") or 0)
        to_location_id = int(row.get("to_location_id") or 0)
        if from_location_id <= 0 or to_location_id <= 0 or from_location_id == to_location_id:
            raise ValueError("replenishment requires two different valid locations")
        recommendations.append({
            "product_key": row.get("product_key") or {},
            "from_location_id": from_location_id,
            "to_location_id": to_location_id,
            "recommended_quantity": quantity,
            "reason": f"Pick-остаток {current} ниже минимума {minimum}; цель {maximum}",
        })
    return recommendations


def build_pick_waves(shipments: Iterable[Mapping], *, maximum_units: int = 200) -> list[dict[str, object]]:
    """Cluster shipments by marketplace/destination with a hard unit limit."""

    limit = _nonnegative_int(maximum_units, "maximum_units")
    if limit <= 0:
        raise ValueError("maximum_units must be positive")
    groups: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    seen = set()
    for row in shipments:
        shipment_id = int(row.get("shipment_task_id") or 0)
        if shipment_id <= 0 or shipment_id in seen:
            raise ValueError("shipment_task_id must be positive and unique")
        seen.add(shipment_id)
        quantity = _nonnegative_int(row.get("total_quantity"), "total_quantity")
        if quantity <= 0:
            raise ValueError("shipment quantity must be positive")
        groups[(str(row.get("marketplace") or "").lower(), str(row.get("destination") or ""))].append({
            "shipment_task_id": shipment_id,
            "total_quantity": quantity,
            "due_at": str(row.get("due_at") or "9999-12-31"),
        })

    waves = []
    for (marketplace, destination), rows in sorted(groups.items()):
        rows.sort(key=lambda item: (item["due_at"], item["shipment_task_id"]))
        current = []
        current_quantity = 0
        for row in rows:
            if current and current_quantity + row["total_quantity"] > limit:
                waves.append({"marketplace": marketplace, "destination": destination, "shipments": current, "total_quantity": current_quantity})
                current, current_quantity = [], 0
            current.append(row["shipment_task_id"])
            current_quantity += row["total_quantity"]
            # Oversized single shipments remain visible as one exceptional wave.
            if current_quantity >= limit:
                waves.append({"marketplace": marketplace, "destination": destination, "shipments": current, "total_quantity": current_quantity})
                current, current_quantity = [], 0
        if current:
            waves.append({"marketplace": marketplace, "destination": destination, "shipments": current, "total_quantity": current_quantity})
    for index, wave in enumerate(waves, 1):
        wave["sequence_no"] = index
    return waves


def _as_date(value) -> date | None:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value)[:10])


def plan_cycle_counts(
    locations: Iterable[Mapping], *, today: date, maximum_locations: int = 20
) -> list[dict[str, object]]:
    """Prioritize never-counted, fast-moving and discrepancy-prone locations."""

    limit = _nonnegative_int(maximum_locations, "maximum_locations")
    if limit <= 0:
        return []
    planned = []
    for row in locations:
        location_id = int(row.get("location_id") or 0)
        if location_id <= 0:
            raise ValueError("location_id must be positive")
        last_counted = _as_date(row.get("last_counted_at"))
        days = 3650 if last_counted is None else max(0, (today - last_counted).days)
        try:
            velocity = Decimal(str(row.get("movement_velocity") or 0))
            discrepancy = Decimal(str(row.get("discrepancy_rate") or 0))
        except (InvalidOperation, ValueError) as error:
            raise ValueError("cycle-count metrics must be numeric") from error
        if velocity < 0 or discrepancy < 0:
            raise ValueError("cycle-count metrics must be non-negative")
        score = Decimal(days) + min(velocity, Decimal(1000)) * Decimal("2") + min(discrepancy, Decimal(1)) * Decimal(1000)
        reasons = []
        if last_counted is None:
            reasons.append("ячейка ни разу не пересчитывалась")
        if velocity >= 10:
            reasons.append("высокая оборачиваемость")
        if discrepancy > 0:
            reasons.append("были расхождения")
        planned.append({
            "location_id": location_id,
            "priority_score": score,
            "reason": ", ".join(reasons) or f"прошло {days} дн. после пересчёта",
        })
    planned.sort(key=lambda row: (-row["priority_score"], row["location_id"]))
    for index, row in enumerate(planned[:limit], 1):
        row["sequence_no"] = index
    return planned[:limit]


def slotting_order(products: Iterable[Mapping]) -> list[dict[str, object]]:
    """Rank products for the nearest pick slots by confirmed pick frequency."""

    ranked = []
    for row in products:
        article = str(row.get("article") or "").strip()
        if not article:
            raise ValueError("article is required for slotting")
        picks = _nonnegative_int(row.get("pick_count"), "pick_count")
        units = _nonnegative_int(row.get("picked_units"), "picked_units")
        ranked.append({"article": article, "pick_count": picks, "picked_units": units})
    ranked.sort(key=lambda row: (-row["pick_count"], -row["picked_units"], row["article"].casefold()))
    for index, row in enumerate(ranked, 1):
        row["recommended_pick_priority"] = index
    return ranked
