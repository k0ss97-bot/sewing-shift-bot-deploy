"""Shared shift-time calculations for the website and Hermes reports."""

from datetime import datetime, timedelta


DEFAULT_LUNCH_START = "13:00"
DEFAULT_LUNCH_END = "14:00"


def normalize_lunch_time(value: str | None, default: str) -> str:
    value = str(value or "").strip()
    try:
        return datetime.strptime(value, "%H:%M").strftime("%H:%M")
    except ValueError:
        return default


def calculate_shift_minutes(
    shift_date: str,
    start_time: str,
    end_time: str | None,
    lunch_start: str | None = None,
    lunch_end: str | None = None,
):
    """Return gross, lunch overlap and net minutes for a shift."""
    if not shift_date or not start_time or not end_time:
        return {"gross_minutes": None, "break_minutes": 0, "net_minutes": None}

    start = datetime.strptime(f"{shift_date} {start_time}", "%Y-%m-%d %H:%M")
    end = datetime.strptime(f"{shift_date} {end_time}", "%Y-%m-%d %H:%M")
    if end < start:
        end += timedelta(days=1)

    lunch_start = normalize_lunch_time(lunch_start, DEFAULT_LUNCH_START)
    lunch_end = normalize_lunch_time(lunch_end, DEFAULT_LUNCH_END)
    pause_start = datetime.strptime(f"{shift_date} {lunch_start}", "%Y-%m-%d %H:%M")
    pause_end = datetime.strptime(f"{shift_date} {lunch_end}", "%Y-%m-%d %H:%M")
    if pause_end <= pause_start:
        pause_end += timedelta(days=1)

    gross = max(0, int((end - start).total_seconds() // 60))
    overlap_start = max(start, pause_start)
    overlap_end = min(end, pause_end)
    break_minutes = max(0, int((overlap_end - overlap_start).total_seconds() // 60))
    return {
        "gross_minutes": gross,
        "break_minutes": min(gross, break_minutes),
        "net_minutes": max(0, gross - min(gross, break_minutes)),
        "lunch_start": lunch_start,
        "lunch_end": lunch_end,
    }
