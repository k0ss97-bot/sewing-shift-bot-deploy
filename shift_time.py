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
    pause_intervals=None,
):
    """Return gross, break and net minutes for a shift.

    ``pause_intervals`` may contain pairs of ISO datetime strings or datetime
    objects.  Manual pauses and the configured lunch window are merged before
    subtraction, so an employee is never charged twice when both overlap.
    """
    if not shift_date or not start_time or not end_time:
        return {"gross_minutes": None, "break_minutes": 0, "pause_minutes": 0, "net_minutes": None}

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
    break_intervals = [(pause_start, pause_end)]
    manual_intervals = []
    for raw_start, raw_end in pause_intervals or []:
        try:
            interval_start = raw_start if isinstance(raw_start, datetime) else datetime.fromisoformat(str(raw_start))
            interval_end = raw_end if isinstance(raw_end, datetime) else datetime.fromisoformat(str(raw_end))
        except (TypeError, ValueError):
            continue
        if interval_start.tzinfo is not None:
            interval_start = interval_start.replace(tzinfo=None)
        if interval_end.tzinfo is not None:
            interval_end = interval_end.replace(tzinfo=None)
        interval_start = max(start, interval_start)
        interval_end = min(end, interval_end)
        if interval_end <= interval_start:
            continue
        manual_intervals.append((interval_start, interval_end))
        break_intervals.append((interval_start, interval_end))

    def merged_minutes(intervals):
        clipped = []
        for interval_start, interval_end in intervals:
            interval_start = max(start, interval_start)
            interval_end = min(end, interval_end)
            if interval_end > interval_start:
                clipped.append((interval_start, interval_end))
        if not clipped:
            return 0
        clipped.sort(key=lambda item: item[0])
        merged = [list(clipped[0])]
        for interval_start, interval_end in clipped[1:]:
            if interval_start <= merged[-1][1]:
                merged[-1][1] = max(merged[-1][1], interval_end)
            else:
                merged.append([interval_start, interval_end])
        return sum(int((interval_end - interval_start).total_seconds() // 60) for interval_start, interval_end in merged)

    break_minutes = merged_minutes(break_intervals)
    manual_pause_minutes = merged_minutes(manual_intervals)
    return {
        "gross_minutes": gross,
        "break_minutes": min(gross, break_minutes),
        "pause_minutes": min(gross, manual_pause_minutes),
        "net_minutes": max(0, gross - min(gross, break_minutes)),
        "lunch_start": lunch_start,
        "lunch_end": lunch_end,
    }
