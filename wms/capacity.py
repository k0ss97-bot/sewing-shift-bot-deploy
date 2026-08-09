"""Deterministic finite-capacity planning with explicit skill constraints."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Iterable, Mapping


SIX_PLACES = Decimal("0.000001")
PRIORITY = {"urgent": 3, "high": 2, "normal": 1, "low": 0}


def _positive(value, field: str) -> Decimal:
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as error:
        raise ValueError(f"{field} must be numeric") from error
    if not number.is_finite() or number <= 0:
        raise ValueError(f"{field} must be positive")
    return number


def calculate_capacity_plan(
    jobs: Iterable[Mapping],
    resources: Iterable[Mapping],
) -> dict[str, object]:
    """Assign work without exceeding capacity or bypassing skill certification.

    ``standard_minutes`` describe workload at proficiency 1.0. A resource with
    proficiency 1.25 consumes 0.8 clock minutes per standard minute. Jobs may
    be split unless ``splittable`` is false.
    """

    normalized_resources = []
    for row in resources:
        resource_id = int(row.get("resource_id") or 0)
        if resource_id <= 0:
            raise ValueError("resource_id must be positive")
        capacity = _positive(row.get("capacity_minutes"), "capacity_minutes")
        skills = {
            str(code): _positive(proficiency, "proficiency")
            for code, proficiency in dict(row.get("skills") or {}).items()
        }
        normalized_resources.append(
            {
                "resource_id": resource_id,
                "name": str(row.get("name") or resource_id),
                "remaining_clock_minutes": capacity,
                "skills": skills,
            }
        )

    normalized_jobs = []
    seen_jobs = set()
    for row in jobs:
        job_key = str(row.get("job_key") or "").strip()
        if not job_key or job_key in seen_jobs:
            raise ValueError("job_key must be non-empty and unique")
        seen_jobs.add(job_key)
        quantity = _positive(row.get("quantity"), "quantity")
        minutes_per_unit = _positive(row.get("standard_minutes_per_unit"), "standard_minutes_per_unit")
        operation_code = str(row.get("operation_code") or "").strip()
        if not operation_code:
            raise ValueError("operation_code is required")
        normalized_jobs.append(
            {
                "job_key": job_key,
                "operation_code": operation_code,
                "quantity": quantity,
                "minutes_per_unit": minutes_per_unit,
                "required_standard_minutes": quantity * minutes_per_unit,
                "priority": str(row.get("priority") or "normal").lower(),
                "due_at": str(row.get("due_at") or "9999-12-31"),
                "splittable": row.get("splittable") is not False,
            }
        )
    normalized_jobs.sort(
        key=lambda row: (-PRIORITY.get(row["priority"], 1), row["due_at"], row["job_key"])
    )

    assignments = []
    unassigned_jobs = []
    for job in normalized_jobs:
        remaining_standard = job["required_standard_minutes"]
        eligible = [
            resource for resource in normalized_resources
            if job["operation_code"] in resource["skills"]
            and resource["remaining_clock_minutes"] > 0
        ]
        eligible.sort(
            key=lambda resource: (
                -(resource["remaining_clock_minutes"] * resource["skills"][job["operation_code"]]),
                resource["resource_id"],
            )
        )
        total_eligible_standard = sum(
            (resource["remaining_clock_minutes"] * resource["skills"][job["operation_code"]] for resource in eligible),
            Decimal(0),
        )
        if not job["splittable"] and total_eligible_standard < remaining_standard:
            eligible = []
        elif not job["splittable"]:
            eligible = [
                next(
                    resource for resource in eligible
                    if resource["remaining_clock_minutes"] * resource["skills"][job["operation_code"]]
                    >= remaining_standard
                )
            ]

        sequence = 1
        for resource in eligible:
            if remaining_standard <= 0:
                break
            proficiency = resource["skills"][job["operation_code"]]
            available_standard = resource["remaining_clock_minutes"] * proficiency
            assigned_standard = min(remaining_standard, available_standard)
            clock_minutes = assigned_standard / proficiency
            assigned_quantity = assigned_standard / job["minutes_per_unit"]
            resource["remaining_clock_minutes"] -= clock_minutes
            remaining_standard -= assigned_standard
            assignments.append(
                {
                    "job_key": job["job_key"],
                    "operation_code": job["operation_code"],
                    "resource_id": resource["resource_id"],
                    "resource_name": resource["name"],
                    "standard_minutes": assigned_standard.quantize(SIX_PLACES, rounding=ROUND_HALF_UP),
                    "clock_minutes": clock_minutes.quantize(SIX_PLACES, rounding=ROUND_HALF_UP),
                    "assigned_quantity": assigned_quantity.quantize(SIX_PLACES, rounding=ROUND_HALF_UP),
                    "assignment_status": "assigned",
                    "reason": "",
                    "sequence_no": sequence,
                }
            )
            sequence += 1

        if remaining_standard > 0:
            reason = "Нет сотрудника с нужным навыком" if not any(
                job["operation_code"] in resource["skills"] for resource in normalized_resources
            ) else "Недостаточно доступной мощности"
            uncovered_quantity = remaining_standard / job["minutes_per_unit"]
            assignments.append(
                {
                    "job_key": job["job_key"], "operation_code": job["operation_code"],
                    "resource_id": None, "resource_name": "",
                    "standard_minutes": remaining_standard.quantize(SIX_PLACES, rounding=ROUND_HALF_UP),
                    "clock_minutes": Decimal(0).quantize(SIX_PLACES),
                    "assigned_quantity": uncovered_quantity.quantize(SIX_PLACES, rounding=ROUND_HALF_UP),
                    "assignment_status": "unassigned", "reason": reason,
                    "sequence_no": sequence,
                }
            )
            unassigned_jobs.append(job["job_key"])

    return {
        "status": "over_capacity" if unassigned_jobs else "ready",
        "jobs_count": len(normalized_jobs),
        "assigned_count": len(seen_jobs - set(unassigned_jobs)),
        "unassigned_count": len(unassigned_jobs),
        "unassigned_job_keys": unassigned_jobs,
        "assignments": assignments,
        "resource_remaining_minutes": {
            resource["resource_id"]: resource["remaining_clock_minutes"].quantize(SIX_PLACES, rounding=ROUND_HALF_UP)
            for resource in normalized_resources
        },
    }
