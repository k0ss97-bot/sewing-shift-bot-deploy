"""Server-side, read-only aggregation for the unified analytics overview.

The module deliberately receives existing local readers as dependencies.  It
does not know marketplace credentials and never performs provider HTTP calls.
Missing or unverified facts stay ``None``; in particular, a transport failure
must never become a business zero.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import logging
import re
from typing import Any, Callable, Iterable
from zoneinfo import ZoneInfo


LOGGER = logging.getLogger(__name__)
FORMULA_VERSION = "analytics-overview-v1"
VALID_STATUSES = {
    "fresh",
    "stale",
    "partial",
    "no_data",
    "error",
    "unknown",
    "unavailable",
    "permission_required",
}
MAX_PERIOD_DAYS = 366
MAX_FRESH_AGE = timedelta(hours=6)
LOCAL_TZ = ZoneInfo("Asia/Yekaterinburg")


class AnalyticsOverviewRequestError(ValueError):
    """A safe client-visible validation error."""

    def __init__(self, message: str, *, code: str = "invalid_period"):
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class PeriodWindow:
    start: date
    end: date
    label: str
    preset: str

    def as_dict(self) -> dict[str, str]:
        return {
            "start_date": self.start.isoformat(),
            "end_date": self.end.isoformat(),
            "label": self.label,
        }


def _now(value: datetime | date | None = None) -> datetime:
    if isinstance(value, datetime):
        return value.astimezone(LOCAL_TZ) if value.tzinfo else value.replace(tzinfo=LOCAL_TZ)
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day, tzinfo=LOCAL_TZ)
    return datetime.now(LOCAL_TZ)


def _generated_at(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _parse_iso_date(value: object, field: str) -> date:
    raw = str(value or "").strip()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw):
        raise AnalyticsOverviewRequestError(f"{field} должен быть датой YYYY-MM-DD.")
    try:
        return date.fromisoformat(raw)
    except ValueError as error:
        raise AnalyticsOverviewRequestError(f"{field} содержит некорректную дату.") from error


def resolve_period(payload: dict[str, Any] | None, *, current: datetime | date | None = None) -> PeriodWindow:
    """Validate a compact period request without querying any data source."""
    if payload is None:
        payload = {}
    if not isinstance(payload, dict):
        raise AnalyticsOverviewRequestError("Ожидается JSON-объект.", code="invalid_request")

    today = _now(current).date()
    raw_start = payload.get("start_date")
    raw_end = payload.get("end_date")
    if raw_start not in (None, "") or raw_end not in (None, ""):
        if raw_start in (None, "") or raw_end in (None, ""):
            raise AnalyticsOverviewRequestError("Укажите одновременно start_date и end_date.")
        start = _parse_iso_date(raw_start, "start_date")
        end = _parse_iso_date(raw_end, "end_date")
        preset = "custom"
    else:
        raw_preset = str(payload.get("period") or "last_30_days").strip().casefold()
        aliases = {
            "7": "last_7_days",
            "7d": "last_7_days",
            "last7": "last_7_days",
            "last_7_days": "last_7_days",
            "последние 7 дней": "last_7_days",
            "30": "last_30_days",
            "30d": "last_30_days",
            "last30": "last_30_days",
            "last_30_days": "last_30_days",
            "последние 30 дней": "last_30_days",
            "90": "last_90_days",
            "90d": "last_90_days",
            "last90": "last_90_days",
            "last_90_days": "last_90_days",
            "последние 90 дней": "last_90_days",
            "month": "current_month",
            "this_month": "current_month",
            "current_month": "current_month",
            "текущий месяц": "current_month",
        }
        preset = aliases.get(raw_preset, "")
        if not preset:
            raise AnalyticsOverviewRequestError("Неизвестный период аналитики.")
        if preset == "current_month":
            start = today.replace(day=1)
        else:
            days = {"last_7_days": 7, "last_30_days": 30, "last_90_days": 90}[preset]
            start = today - timedelta(days=days - 1)
        end = today

    if start > end:
        raise AnalyticsOverviewRequestError("start_date не может быть позже end_date.")
    if (end - start).days + 1 > MAX_PERIOD_DAYS:
        raise AnalyticsOverviewRequestError(f"Период не может превышать {MAX_PERIOD_DAYS} дней.")
    label = f"{start.strftime('%d.%m.%Y')} — {end.strftime('%d.%m.%Y')}"
    return PeriodWindow(start=start, end=end, label=label, preset=preset)


def _text(value: object, *, limit: int = 500) -> str:
    return " ".join(str(value or "").replace("\x00", "").split())[:limit]


def _decimal(value: object) -> Decimal | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        result = Decimal(str(value).replace(",", "."))
    except (InvalidOperation, TypeError, ValueError):
        return None
    return result if result.is_finite() else None


def _money(value: Decimal | object | None) -> str | None:
    number = value if isinstance(value, Decimal) else _decimal(value)
    if number is None:
        return None
    return format(number.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), ".2f")


def _quantity(value: Decimal | object | None) -> str | None:
    number = value if isinstance(value, Decimal) else _decimal(value)
    if number is None:
        return None
    rendered = format(number, "f")
    return rendered.rstrip("0").rstrip(".") if "." in rendered else rendered


def _integer(value: object) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        return int(value)
    except (TypeError, ValueError, OverflowError):
        return None


def _date_key(value: object) -> str | None:
    raw = str(value or "").strip()[:10]
    try:
        return date.fromisoformat(raw).isoformat()
    except (TypeError, ValueError):
        return None


def _in_period(value: object, period: PeriodWindow) -> bool:
    key = _date_key(value)
    return bool(key and period.start.isoformat() <= key <= period.end.isoformat())


def _as_dict(value: object) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_rows(value: object) -> list[dict[str, Any]]:
    return [row for row in value if isinstance(row, dict)] if isinstance(value, list) else []


def _status(value: object, *, fallback: str = "unknown") -> str:
    raw = str(value or "").strip().casefold()
    mapping = {
        "available": "fresh",
        "ready": "fresh",
        "success": "fresh",
        "ok": "fresh",
        "value": "fresh",
        "zero": "fresh",
        "disabled": "unavailable",
        "not_configured": "unavailable",
        "failed": "error",
        "rate_limited": "partial",
        "authentication": "permission_required",
        "unauthorized": "permission_required",
        "forbidden": "permission_required",
        "payment_required": "permission_required",
        "invalid_response": "error",
        "http_error": "error",
    }
    normalized = mapping.get(raw, raw)
    return normalized if normalized in VALID_STATUSES else fallback


def _latest_timestamp(values: Iterable[object]) -> str | None:
    latest: tuple[datetime, str] | None = None
    for value in values:
        raw = str(value or "").strip()
        if not raw:
            continue
        try:
            parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            if not parsed.tzinfo:
                parsed = parsed.replace(tzinfo=LOCAL_TZ)
            parsed = parsed.astimezone(timezone.utc)
        except ValueError:
            continue
        if latest is None or parsed > latest[0]:
            latest = (parsed, raw)
    return latest[1] if latest else None


def _timestamp_freshness(value: object, generated_at: str) -> str:
    """Classify a persisted observation without silently treating old data as fresh."""
    raw = str(value or "").strip()
    if not raw:
        return "unknown"
    try:
        observed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        generated = datetime.fromisoformat(generated_at.replace("Z", "+00:00"))
        if not observed.tzinfo:
            observed = observed.replace(tzinfo=LOCAL_TZ)
        if not generated.tzinfo:
            generated = generated.replace(tzinfo=timezone.utc)
    except ValueError:
        return "unknown"
    age = generated.astimezone(timezone.utc) - observed.astimezone(timezone.utc)
    return "stale" if age > MAX_FRESH_AGE else "fresh"


def _dataset_timestamp(row: dict[str, Any]) -> str | None:
    """Return the newest persisted observation proving a PG dataset state."""
    return _latest_timestamp(
        (
            row.get("finished_at"),
            row.get("last_success_at"),
            row.get("last_usable_at"),
            row.get("updated_at"),
        )
    )


def _dataset_data_status(row: dict[str, Any], generated_at: str) -> str:
    """Never promote a dataset to fresh when no observation time proves it."""
    normalized = _status(row.get("freshness") or row.get("status"))
    if normalized != "fresh":
        return normalized
    return _timestamp_freshness(_dataset_timestamp(row), generated_at)


def _data_meta(
    *,
    status: str,
    generated_at: str,
    partial: bool = False,
    sources: Iterable[str] = (),
    warnings: Iterable[str] = (),
    max_source_updated_at: str | None = None,
    last_successful_sync_at: str | None = None,
) -> dict[str, Any]:
    normalized = _status(status)
    warning_rows = list(dict.fromkeys(_text(item) for item in warnings if _text(item)))
    return {
        "status": normalized,
        "generated_at": generated_at,
        "max_source_updated_at": max_source_updated_at,
        "last_successful_sync_at": last_successful_sync_at,
        "partial": bool(partial or normalized == "partial"),
        "sources": list(dict.fromkeys(str(item) for item in sources if str(item))),
        "warnings": warning_rows,
        "formula_version": FORMULA_VERSION,
    }


def _safe_read(name: str, reader: Callable[..., object], *args: object) -> tuple[dict[str, Any], str | None]:
    try:
        value = reader(*args)
        if not isinstance(value, dict):
            raise TypeError("reader did not return an object")
        return value, None
    except Exception as error:  # source failures are represented, not leaked
        LOGGER.warning("Analytics source unavailable: %s (%s)", name, error.__class__.__name__)
        return {}, f"Источник {name} временно недоступен."


def _account(payload: dict[str, Any], marketplace: str) -> dict[str, Any]:
    rows = _as_rows(payload.get("accounts"))
    for row in rows:
        if str(row.get("marketplace") or "").casefold() == marketplace:
            return row
    return rows[0] if len(rows) == 1 else {}


def _successful_sync(payload: dict[str, Any]) -> bool:
    return any(str(row.get("status") or "").casefold() == "success" for row in _as_rows(payload.get("sync_runs")))


def _successful_sync_count(payload: dict[str, Any], field: str) -> int | None:
    for row in _as_rows(payload.get("sync_runs")):
        if str(row.get("status") or "").casefold() == "success" and field in row:
            return _integer(row.get(field))
    return None


def _capability_rows(provider: dict[str, Any]) -> list[dict[str, Any]]:
    analytics = _as_dict(provider.get("analytics"))
    rows = _as_rows(analytics.get("capability_rows"))
    if rows:
        return rows
    statuses = _as_dict(analytics.get("capability_statuses"))
    return [{"capability": key, **_as_dict(value)} for key, value in statuses.items()]


def _capability(provider: dict[str, Any], name: str) -> dict[str, Any]:
    for row in _capability_rows(provider):
        if str(row.get("capability") or "").casefold() == name.casefold():
            return row
    return {}


def _capability_available(provider: dict[str, Any], name: str, fallback: bool = False) -> bool:
    row = _capability(provider, name)
    if row:
        return _status(row.get("status")) == "fresh"
    explicit = _as_dict(_as_dict(provider.get("analytics")).get("capabilities")).get(name)
    return bool(explicit) if explicit is not None else fallback


def _capability_data_status(provider: dict[str, Any], name: str, generated_at: str) -> str:
    row = _capability(provider, name)
    if row:
        status = _status(row.get("status"))
        if status != "fresh":
            return status
        account = _account(provider, "wildberries")
        return _timestamp_freshness(
            row.get("checked_at") or account.get("last_sync_at"),
            generated_at,
        )
    explicit = _as_dict(_as_dict(provider.get("analytics")).get("capabilities")).get(name)
    if explicit is not True:
        return "no_data"
    return _timestamp_freshness(
        _account(provider, "wildberries").get("last_sync_at"),
        generated_at,
    )


def _capability_coverage(
    provider: dict[str, Any], name: str
) -> tuple[date, date] | None:
    """Return the explicitly persisted inclusive coverage for a capability."""
    row = _capability(provider, name)
    coverage = _as_dict(row.get("coverage"))
    start_key = _date_key(
        row.get("coverage_start_date")
        or row.get("coverage_start")
        or coverage.get("start_date")
        or coverage.get("start")
    )
    end_key = _date_key(
        row.get("coverage_end_date")
        or row.get("coverage_end")
        or coverage.get("end_date")
        or coverage.get("end")
    )
    if not start_key or not end_key:
        return None
    start = date.fromisoformat(start_key)
    end = date.fromisoformat(end_key)
    return (start, end) if start <= end else None


def _coverage_contains(coverage: tuple[date, date] | None, period: PeriodWindow) -> bool:
    return bool(coverage and coverage[0] <= period.start and coverage[1] >= period.end)


def _complete_daily_series(
    values: dict[str, Decimal], period: PeriodWindow
) -> dict[str, Decimal]:
    """Fill confirmed missing days with business zero inside a covered period."""
    result: dict[str, Decimal] = {}
    current = period.start
    while current <= period.end:
        key = current.isoformat()
        result[key] = values.get(key, Decimal("0"))
        current += timedelta(days=1)
    return result


def _complete_daily_orders(values: dict[str, int], period: PeriodWindow) -> dict[str, int]:
    """Fill confirmed missing order days with zero inside a covered period."""
    result: dict[str, int] = {}
    current = period.start
    while current <= period.end:
        key = current.isoformat()
        result[key] = values.get(key, 0)
        current += timedelta(days=1)
    return result


def _ozon_quality(payload: dict[str, Any]) -> dict[str, Any]:
    phase = payload.get("phase1a")
    return phase if isinstance(phase, dict) else payload


def _quality_dataset(quality: dict[str, Any], name: str) -> dict[str, Any]:
    for row in _as_rows(quality.get("datasets")):
        if str(row.get("dataset") or "").casefold() == name:
            return row
    return {}


def _quality_source_available(quality: dict[str, Any]) -> bool:
    """Whether the envelope contains a usable PostgreSQL quality observation."""
    if not quality or quality.get("enabled") is False:
        return False
    return _status(quality.get("state")) not in {"error", "unavailable"}


def _usable_dataset(row: dict[str, Any]) -> bool:
    raw = str(row.get("status") or "").casefold()
    return raw == "success" or (
        raw == "partial" and str(row.get("termination_reason") or "") == "fbo_stock_scope_unavailable"
    )


def _provider_status(
    marketplace: str,
    provider: dict[str, Any],
    quality: dict[str, Any],
    *,
    configured: bool,
    generated_at: str,
) -> tuple[str, list[str], list[str]]:
    if not configured:
        return "unavailable", ["Коннектор не настроен."], []
    warnings: list[str] = []
    missing: list[str] = []
    if provider and provider.get("ok") is False:
        return "error", ["Локальный snapshot коннектора завершён с ошибкой."], ["snapshot"]
    if marketplace == "ozon" and quality:
        state = _status(quality.get("state"))
        dataset_statuses = []
        for row in _as_rows(quality.get("datasets")):
            normalized = _dataset_data_status(row, generated_at)
            dataset_statuses.append(normalized)
            if normalized != "fresh":
                missing.append(str(row.get("dataset") or "unknown"))
                warnings.append(f"Ozon {row.get('dataset') or 'dataset'}: {normalized}.")
        if any(item in {"error", "permission_required", "unavailable"} for item in dataset_statuses):
            return ("partial" if "fresh" in dataset_statuses else "error"), warnings, missing
        if any(item == "partial" for item in dataset_statuses):
            return "partial", warnings, missing
        if any(item == "stale" for item in dataset_statuses):
            return "stale", warnings, missing
        if dataset_statuses and all(item == "fresh" for item in dataset_statuses):
            return "fresh", warnings, missing
        if state in VALID_STATUSES and state != "unknown":
            return state, warnings, missing
    if marketplace == "wildberries":
        rows = _capability_rows(provider)
        if rows:
            statuses = [
                _capability_data_status(provider, str(row.get("capability") or ""), generated_at)
                for row in rows
            ]
            for row, normalized in zip(rows, statuses):
                if normalized != "fresh":
                    capability_name = str(row.get("capability") or "unknown")
                    missing.append(capability_name)
                    warnings.append(f"Wildberries {capability_name}: {normalized}.")
            if all(item == "fresh" for item in statuses):
                return "fresh", warnings, missing
            if "fresh" in statuses:
                return "partial", warnings, missing
            if "permission_required" in statuses:
                return "permission_required", warnings, missing
            if "error" in statuses:
                return "error", warnings, missing
            if statuses and all(item == "stale" for item in statuses):
                return "stale", warnings, missing
            return "partial", warnings, missing
    account = _account(provider, marketplace)
    if account.get("last_error") and not account.get("last_sync_at"):
        return "error", ["Последняя синхронизация завершилась ошибкой."], missing
    if account.get("last_sync_at"):
        return _timestamp_freshness(account.get("last_sync_at"), generated_at), warnings, missing
    if _successful_sync(provider):
        return "unknown", ["Время успешной синхронизации не сохранено."], missing
    return "no_data", ["Подтверждённой успешной синхронизации пока нет."], missing


def _finance_rows(
    provider: dict[str, Any], period: PeriodWindow, *, amount_key: str = "net"
) -> dict[str, Decimal]:
    """Return a confirmed daily finance component for a selected period.

    ``finance_daily`` preserves both the positive accruals (``revenue``) and
    the final amount after all charges (``net``).  Keeping the key explicit
    prevents the analytics UI from labelling net payout as sales.
    """
    result: dict[str, Decimal] = {}
    for row in _as_rows(_as_dict(provider.get("analytics")).get("finance_daily")):
        day = _date_key(row.get("date"))
        amount = _decimal(row.get(amount_key))
        if day and amount is not None and period.start.isoformat() <= day <= period.end.isoformat():
            result[day] = result.get(day, Decimal("0")) + amount
    return result


def _order_rows(provider: dict[str, Any], period: PeriodWindow) -> dict[str, int]:
    result: dict[str, int] = {}
    for row in _as_rows(provider.get("orders_rows")):
        day = _date_key(row.get("shipment_date") or row.get("updated_at"))
        if day and period.start.isoformat() <= day <= period.end.isoformat():
            result[day] = result.get(day, 0) + 1
    return result


def _known_stock(
    marketplace: str,
    provider: dict[str, Any],
    quality: dict[str, Any],
    generated_at: str,
) -> tuple[Decimal | None, str, list[str], list[str]]:
    warnings: list[str] = []
    if marketplace == "ozon":
        dataset = _quality_dataset(quality, "stocks")
        totals = _as_dict(quality.get("totals"))
        if dataset and _usable_dataset(dataset):
            amount = _decimal(totals.get("stock_available"))
            if amount is not None:
                if str(dataset.get("status") or "").casefold() == "partial":
                    warnings.append("Ozon: подтверждены seller-scheme остатки; полный FBO ledger недоступен.")
                    return amount, "partial", warnings, ["postgres.marketplace_phase1a"]
                return (
                    amount,
                    _dataset_data_status(dataset, generated_at),
                    warnings,
                    ["postgres.marketplace_phase1a"],
                )
        successful_stock_count = _successful_sync_count(provider, "stocks_count")
        if successful_stock_count is not None:
            values = [_decimal(row.get("available")) for row in _as_rows(provider.get("products_rows"))]
            known = [item for item in values if item is not None]
            if known:
                return (
                    sum(known, Decimal("0")),
                    "stale",
                    ["Использован legacy SQLite snapshot остатков Ozon."],
                    ["sqlite.marketplace_dashboard"],
                )
            if successful_stock_count == 0:
                return (
                    Decimal("0"),
                    "stale",
                    ["Использован подтверждённый пустой legacy snapshot остатков Ozon."],
                    ["sqlite.marketplace_dashboard"],
                )
        return None, "no_data", ["Нет подтверждённого набора остатков Ozon."], []

    capability = _capability(provider, "stocks")
    available = _capability_available(
        provider,
        "stocks",
        fallback=bool(provider.get("warehouses")) or bool(_integer(_as_dict(provider.get("summary")).get("stock_rows"))),
    )
    if not available:
        status = _status(capability.get("status")) if capability else "no_data"
        return None, status, ["Остатки Wildberries не подтверждены API."], []
    values = [_decimal(row.get("available")) for row in _as_rows(provider.get("products_rows"))]
    known = [item for item in values if item is not None]
    return (
        sum(known, Decimal("0")),
        _capability_data_status(provider, "stocks", generated_at),
        warnings,
        ["sqlite.marketplace_dashboard"],
    )


def _known_products(
    marketplace: str,
    provider: dict[str, Any],
    quality: dict[str, Any],
    generated_at: str,
) -> tuple[int | None, str, list[str]]:
    if marketplace == "ozon":
        dataset = _quality_dataset(quality, "catalog")
        value = _integer(_as_dict(quality.get("totals")).get("products"))
        if dataset and _usable_dataset(dataset) and value is not None:
            return (
                value,
                _dataset_data_status(dataset, generated_at),
                ["postgres.marketplace_phase1a"],
            )
    if marketplace == "wildberries" and _capability_available(
        provider, "catalog", fallback=bool(provider.get("products_rows"))
    ):
        value = _integer(_as_dict(provider.get("summary")).get("products"))
        return (
            value if value is not None else len(_as_rows(provider.get("products_rows"))),
            _capability_data_status(provider, "catalog", generated_at),
            ["sqlite.marketplace_dashboard"],
        )
    if _successful_sync(provider):
        value = _integer(_as_dict(provider.get("summary")).get("products"))
        return value, "stale", ["sqlite.marketplace_dashboard"] if value is not None else []
    return None, "no_data", []


def _provider_metric_timestamp(
    marketplace: str,
    metric: str,
    provider: dict[str, Any],
    quality: dict[str, Any],
    sources: Iterable[str],
) -> str | None:
    """Return only an observation timestamp belonging to an actual metric source."""
    source_set = set(sources)
    candidates: list[object] = []
    if "postgres.marketplace_phase1a" in source_set:
        dataset_name = {"products": "catalog", "stock_available": "stocks"}.get(metric)
        if dataset_name:
            candidates.append(_dataset_timestamp(_quality_dataset(quality, dataset_name)))
    if "sqlite.marketplace_dashboard" in source_set:
        account = _account(provider, marketplace)
        if marketplace == "wildberries":
            capability_name = {
                "products": "catalog",
                "stock_available": "stocks",
                "orders": "orders",
                "net_payout": "finance",
            }.get(metric)
            capability = _capability(provider, capability_name or "")
            if capability:
                candidates.append(
                    capability.get("checked_at")
                    or capability.get("last_successful_snapshot_started_at")
                    or capability.get("snapshot_started_at")
                    or account.get("last_sync_at")
                )
            else:
                candidates.append(account.get("last_sync_at"))
        else:
            candidates.append(account.get("last_sync_at"))
    return _latest_timestamp(candidates)


def _provider_payload(
    marketplace: str,
    label: str,
    provider: dict[str, Any],
    quality: dict[str, Any],
    period: PeriodWindow,
    generated_at: str,
) -> tuple[dict[str, Any], dict[str, Decimal], dict[str, int]]:
    configured = bool(provider.get("configured") or quality.get("configured") or quality.get("account"))
    account = _account(provider, marketplace)
    status, warnings, missing = _provider_status(
        marketplace,
        provider,
        quality,
        configured=configured,
        generated_at=generated_at,
    )
    products, products_status, product_sources = _known_products(
        marketplace, provider, quality, generated_at
    )
    stock, stock_status, stock_warnings, stock_sources = _known_stock(
        marketplace, provider, quality, generated_at
    )
    warnings.extend(stock_warnings)
    finance = _finance_rows(provider, period)
    recognized_daily = _finance_rows(provider, period, amount_key="revenue")
    orders_daily = _order_rows(provider, period)

    if marketplace == "wildberries":
        orders_available = _capability_available(provider, "orders", fallback=bool(provider.get("orders_rows")))
        orders_data_status = _capability_data_status(provider, "orders", generated_at)
        orders_coverage = _capability_coverage(provider, "orders")
        if not orders_available:
            # Explicit permission/transport failures invalidate historical rows
            # for both the KPI and the chart.
            orders_daily = {}
            orders = None
            orders_status = orders_data_status
        elif _coverage_contains(orders_coverage, period):
            orders_daily = _complete_daily_orders(orders_daily, period)
            orders = sum(orders_daily.values())
            orders_status = orders_data_status
        elif orders_coverage:
            orders_daily = {}
            orders = None
            orders_status = "partial"
            warnings.append(
                "Wildberries orders: выбранный период выходит за подтверждённое покрытие выгрузки."
            )
            missing.append("orders_coverage")
            if status in {"fresh", "stale"}:
                status = "partial"
        else:
            orders_daily = {}
            orders = None
            orders_status = "no_data"
            warnings.append(
                "Wildberries orders: нет подтверждённого покрытия выбранного периода."
            )
            missing.append("orders_coverage")
            if status in {"fresh", "stale"}:
                status = "partial"
    else:
        # The legacy Ozon reader used to swallow a postings error and save a
        # zero in an otherwise successful run.  Only actual stored rows prove
        # that this dataset exists until a fail-closed orders adapter lands.
        orders_available = bool(provider.get("orders_rows"))
        orders_status = (
            _timestamp_freshness(account.get("last_sync_at"), generated_at)
            if orders_available
            else "no_data"
        )
        orders = sum(orders_daily.values()) if orders_available else None
    if marketplace == "wildberries":
        finance_available = _capability_available(provider, "finance", fallback=bool(finance))
        finance_data_status = _capability_data_status(provider, "finance", generated_at)
        finance_coverage = _capability_coverage(provider, "finance")
        finance_covered = _coverage_contains(finance_coverage, period)
        if not finance_available:
            # Historical rows cannot override an explicit current capability
            # failure.  Keep them out of both totals and chart series.
            finance = {}
            recognized_daily = {}
            net = None
            recognized_sales = None
            finance_status = finance_data_status
        elif finance_covered:
            finance = _complete_daily_series(finance, period)
            recognized_daily = _complete_daily_series(recognized_daily, period)
            net = sum(finance.values(), Decimal("0"))
            recognized_sales = sum(recognized_daily.values(), Decimal("0"))
            finance_status = finance_data_status
        elif finance:
            net = sum(finance.values(), Decimal("0"))
            recognized_sales = sum(recognized_daily.values(), Decimal("0")) if recognized_daily else None
            finance_status = "partial"
            warnings.append(
                "Wildberries finance: выбранный период не полностью покрыт подтверждённой выгрузкой."
            )
            missing.append("finance_coverage")
            if status in {"fresh", "stale"}:
                status = "partial"
        else:
            net = None
            recognized_sales = None
            finance_status = "no_data"
            warnings.append(
                "Wildberries finance: нет подтверждённого покрытия выбранного периода."
            )
            missing.append("finance_coverage")
            if status in {"fresh", "stale"}:
                status = "partial"
    else:
        net = sum(finance.values(), Decimal("0")) if finance else None
        recognized_sales = sum(recognized_daily.values(), Decimal("0")) if recognized_daily else None
        finance_status = (
            _timestamp_freshness(account.get("last_sync_at"), generated_at)
            if finance
            else "no_data"
        )
    source_times = [account.get("last_sync_at")]
    if marketplace == "ozon":
        for row in _as_rows(quality.get("datasets")):
            source_times.extend([row.get("finished_at"), row.get("last_success_at"), row.get("last_usable_at")])
    max_updated = _latest_timestamp(source_times)
    last_success = _latest_timestamp(
        [account.get("last_sync_at")]
        + [row.get("last_success_at") or row.get("last_usable_at") for row in _as_rows(quality.get("datasets"))]
    )
    provider_sources = []
    if provider and provider.get("ok") is not False:
        provider_sources.append("sqlite.marketplace_dashboard")
    if marketplace == "ozon" and _quality_source_available(quality):
        provider_sources.append("postgres.marketplace_phase1a")
    orders_sources = ["sqlite.marketplace_dashboard"] if orders is not None else []
    finance_sources = ["sqlite.marketplace_dashboard"] if net is not None else []
    recognized_sources = ["sqlite.marketplace_dashboard"] if recognized_sales is not None else []
    metric_sources = {
        "products": product_sources,
        "stock_available": stock_sources,
        "orders": orders_sources,
        "net_payout": finance_sources,
        "recognized_sales": recognized_sources,
    }
    metric_timestamps = {
        metric: _provider_metric_timestamp(
            marketplace,
            metric,
            provider,
            quality,
            sources,
        )
        for metric, sources in metric_sources.items()
    }
    meta = _data_meta(
        status=status,
        generated_at=generated_at,
        partial=status == "partial",
        sources=provider_sources,
        warnings=warnings,
        max_source_updated_at=max_updated,
        last_successful_sync_at=last_success,
    )
    metrics_alias = {
        "recognized": _money(recognized_sales),
        "gmv": None,
        "net": _money(net),
        "orders": orders,
        "stock": _quantity(stock),
    }
    return {
        "marketplace": marketplace,
        "label": label,
        "configured": configured,
        "status": status,
        "last_sync_at": account.get("last_sync_at") or last_success,
        "last_error": _text(account.get("last_error") or provider.get("error") or provider.get("message")) or None,
        "products": products,
        "stock_available": _quantity(stock),
        "orders": orders,
        "recognized_sales": _money(recognized_sales),
        "net_payout": _money(net),
        "meta": meta,
        # Compatibility fields for the first overview client.
        "metrics": metrics_alias,
        "missing_capabilities": list(dict.fromkeys(missing)),
        "metric_status": {
            "products": products_status,
            "stock_available": stock_status,
            "orders": orders_status,
            "recognized_sales": finance_status,
            "net_payout": finance_status,
        },
        "metric_sources": metric_sources,
        "metric_timestamps": metric_timestamps,
    }, finance, orders_daily


def _combined_series(
    ozon_finance: dict[str, Decimal],
    wb_finance: dict[str, Decimal],
    ozon_orders: dict[str, int],
    wb_orders: dict[str, int],
) -> dict[str, list[dict[str, Any]]]:
    finance = []
    for day in sorted(set(ozon_finance) | set(wb_finance)):
        ozon = ozon_finance.get(day)
        wb = wb_finance.get(day)
        finance.append({
            "date": day,
            "ozon": _money(ozon),
            "wildberries": _money(wb),
            "wb": _money(wb),
            "total": _money(ozon + wb) if ozon is not None and wb is not None else None,
        })
    orders = []
    for day in sorted(set(ozon_orders) | set(wb_orders)):
        ozon = ozon_orders.get(day)
        wb = wb_orders.get(day)
        orders.append({
            "date": day,
            "ozon": ozon,
            "wildberries": wb,
            "wb": wb,
            "total": ozon + wb if ozon is not None and wb is not None else None,
        })
    return {"finance": finance, "orders": orders}


def _aggregate_known(values: Iterable[object], *, money: bool = False, quantity: bool = False) -> object:
    rows = list(values)
    known = [_decimal(value) for value in rows]
    known = [value for value in known if value is not None]
    if not known:
        return None
    total = sum(known, Decimal("0"))
    if money:
        return _money(total)
    if quantity:
        return _quantity(total)
    return int(total)


def _metric(
    code: str,
    label: str,
    value: object,
    unit: str,
    *,
    status: str,
    generated_at: str,
    sources: Iterable[str],
    partial: bool = False,
    warnings: Iterable[str] = (),
    max_source_updated_at: str | None = None,
    last_successful_sync_at: str | None = None,
) -> dict[str, Any]:
    meta = _data_meta(
        status=status,
        generated_at=generated_at,
        sources=sources,
        partial=partial,
        warnings=warnings,
        max_source_updated_at=max_source_updated_at,
        last_successful_sync_at=last_successful_sync_at,
    )
    return {
        "code": code,
        "key": code,
        "label": label,
        "value": value,
        "unit": unit,
        "meta": meta,
        "status": meta["status"],
        "source_hint": ", ".join(meta["sources"]),
    }


def _metrics(providers: list[dict[str, Any]], production: dict[str, Any], generated_at: str) -> list[dict[str, Any]]:
    product_values = [row.get("products") for row in providers]
    stock_values = [row.get("stock_available") for row in providers]
    order_values = [row.get("orders") for row in providers]
    recognized_values = [row.get("recognized_sales") for row in providers]
    net_values = [row.get("net_payout") for row in providers]

    def aggregate_status(value_key: str, status_key: str) -> tuple[str, bool]:
        known_rows = [row for row in providers if row.get(value_key) is not None]
        if not known_rows:
            return "no_data", False
        if len(known_rows) != len(providers):
            return "partial", True
        statuses = [
            _status(_as_dict(row.get("metric_status")).get(status_key), fallback="unknown")
            for row in known_rows
        ]
        statuses = [
            "unknown"
            if status == "fresh"
            and not _as_dict(row.get("metric_timestamps")).get(status_key)
            else status
            for row, status in zip(known_rows, statuses)
        ]
        if all(status == "fresh" for status in statuses):
            return "fresh", False
        if all(status == "stale" for status in statuses):
            return "stale", False
        return "partial", True

    def aggregate_sources(value_key: str, source_key: str) -> list[str]:
        sources: list[str] = []
        for provider in providers:
            if provider.get(value_key) is None:
                continue
            source_map = _as_dict(provider.get("metric_sources"))
            values = source_map.get(source_key)
            if isinstance(values, list):
                sources.extend(str(value) for value in values if str(value))
        return list(dict.fromkeys(sources))

    def aggregate_timestamp(value_key: str, timestamp_key: str) -> str | None:
        values: list[object] = []
        for provider in providers:
            if provider.get(value_key) is None:
                continue
            values.append(_as_dict(provider.get("metric_timestamps")).get(timestamp_key))
        return _latest_timestamp(values)

    products_status, products_partial = aggregate_status("products", "products")
    stocks_status, stocks_partial = aggregate_status("stock_available", "stock_available")
    orders_status, orders_partial = aggregate_status("orders", "orders")
    recognized_status, recognized_partial = aggregate_status("recognized_sales", "recognized_sales")
    net_status, net_partial = aggregate_status("net_payout", "net_payout")
    production_status = _status(_as_dict(production.get("meta")).get("status"))
    production_sources = _as_dict(production.get("meta")).get("sources")
    if not isinstance(production_sources, list):
        production_sources = []
    production_updated_at = _as_dict(production.get("meta")).get("max_source_updated_at")

    def marketplace_metric(
        code: str,
        label: str,
        value: object,
        unit: str,
        *,
        status: str,
        partial: bool,
        value_key: str,
        source_key: str,
    ) -> dict[str, Any]:
        observed_at = aggregate_timestamp(value_key, source_key)
        # A supposedly fresh persisted metric without any source observation is
        # unverified.  Keep the value visible, but do not label it fresh.
        verified_status = "unknown" if status == "fresh" and not observed_at else status
        return _metric(
            code,
            label,
            value,
            unit,
            status=verified_status,
            partial=partial or verified_status == "unknown",
            generated_at=generated_at,
            sources=aggregate_sources(value_key, source_key),
            max_source_updated_at=observed_at,
            last_successful_sync_at=observed_at,
        )

    def production_metric(code: str, label: str, value: object, unit: str) -> dict[str, Any]:
        known = value is not None
        status = production_status if known else (
            production_status if production_status in {"error", "unavailable", "permission_required"} else "no_data"
        )
        return _metric(
            code,
            label,
            value,
            unit,
            status=status,
            generated_at=generated_at,
            sources=production_sources if known and status not in {"error", "no_data", "unavailable"} else [],
            max_source_updated_at=production_updated_at if known else None,
            last_successful_sync_at=_as_dict(production.get("meta")).get("last_successful_sync_at") if known else None,
        )

    rows = [
        marketplace_metric("marketplace_products", "Товары в продаже", _aggregate_known(product_values), "шт.", status=products_status, partial=products_partial, value_key="products", source_key="products"),
        marketplace_metric("stock_available", "Остатки на площадках", _aggregate_known(stock_values, quantity=True), "шт.", status=stocks_status, partial=stocks_partial, value_key="stock_available", source_key="stock_available"),
        marketplace_metric("orders", "Заказы за период", _aggregate_known(order_values), "шт.", status=orders_status, partial=orders_partial, value_key="orders", source_key="orders"),
        marketplace_metric("recognized_sales", "Продажи до удержаний", _aggregate_known(recognized_values, money=True), "RUB", status=recognized_status, partial=recognized_partial, value_key="recognized_sales", source_key="recognized_sales"),
        marketplace_metric("net_payout", "Начислено после удержаний", _aggregate_known(net_values, money=True), "RUB", status=net_status, partial=net_partial, value_key="net_payout", source_key="net_payout"),
        production_metric("production_plan", "План производства", production.get("plan"), "шт."),
        production_metric("production_fact", "Годная продукция", production.get("fact"), "шт."),
        production_metric("production_active", "Производство в работе", production.get("active_quantity"), "шт."),
        production_metric("quality_fpy", "Качество FPY", production.get("fpy"), "%"),
    ]
    for code, label, unit in (
        ("contribution_margin", "Маржинальный доход", "RUB"),
        ("recommendations", "Рекомендации", "шт."),
        ("geo", "География продаж", "регионов"),
    ):
        rows.append(_metric(
            code,
            label,
            None,
            unit,
            status="unavailable",
            generated_at=generated_at,
            sources=[],
            warnings=["Формула или подтверждённый источник ещё не подключены."],
        ))
    return rows


def _supplies_meta(
    ozon_provider: dict[str, Any],
    wb_provider: dict[str, Any],
    shipments: list[dict[str, Any]],
    *,
    dashboard_error: str | None,
    generated_at: str,
) -> dict[str, Any]:
    """Classify the local supply view without treating an empty table as zero."""
    if dashboard_error:
        return _data_meta(
            status="no_data",
            generated_at=generated_at,
            sources=[],
            warnings=[dashboard_error],
        )

    if shipments:
        observed_at = _latest_timestamp(
            value
            for row in shipments
            for value in (row.get("last_synced_at"), row.get("updated_at"))
        )
        freshness = _timestamp_freshness(observed_at, generated_at)
        status = freshness if freshness in {"fresh", "stale"} else "partial"
        warnings = [] if status == "fresh" else [
            "Поставки найдены, но время актуального marketplace snapshot не подтверждено."
        ]
        return _data_meta(
            status=status,
            generated_at=generated_at,
            partial=status == "partial",
            sources=["sqlite.marketplace_dashboard"],
            warnings=warnings,
            max_source_updated_at=observed_at,
            last_successful_sync_at=observed_at,
        )

    capability_states: list[str] = []
    confirmed_times: list[object] = []
    warnings: list[str] = []
    for marketplace, provider in (("ozon", ozon_provider), ("wildberries", wb_provider)):
        configured = bool(provider.get("configured") or _account(provider, marketplace))
        if not configured:
            continue
        capability = _capability(provider, "supplies")
        if not capability:
            capability_states.append("no_data")
            warnings.append(f"{marketplace.title()}: capability supplies не подтверждён.")
            continue
        normalized = _status(capability.get("status"))
        observed_at = _latest_timestamp(
            (
                capability.get("checked_at"),
                capability.get("last_successful_snapshot_started_at"),
                capability.get("snapshot_started_at"),
                _account(provider, marketplace).get("last_sync_at"),
            )
        )
        if normalized == "fresh":
            normalized = _timestamp_freshness(observed_at, generated_at)
        capability_states.append(normalized)
        if normalized == "fresh":
            confirmed_times.append(observed_at)
        if normalized != "fresh":
            warnings.append(f"{marketplace.title()}: supplies — {normalized}.")

    if capability_states and all(item == "fresh" for item in capability_states):
        status = "fresh"
    elif "fresh" in capability_states:
        status = "partial"
    else:
        status = "no_data"
    observed_at = _latest_timestamp(confirmed_times)
    has_confirmed_source = bool(confirmed_times)
    return _data_meta(
        status=status,
        generated_at=generated_at,
        partial=status == "partial",
        sources=["sqlite.marketplace_dashboard"] if has_confirmed_source else [],
        warnings=warnings or [
            "Пустая локальная таблица поставок не подтверждает нулевое количество у площадок."
        ],
        max_source_updated_at=observed_at,
        last_successful_sync_at=observed_at,
    )


def _risks(
    providers: list[dict[str, Any]],
    ozon_quality: dict[str, Any],
    wb_provider: dict[str, Any],
    production: dict[str, Any],
    supplies: dict[str, Any],
) -> list[dict[str, Any]]:
    risks: list[dict[str, Any]] = []

    def add(
        risk_id: str,
        severity: str,
        title: str,
        reason: str,
        action: str,
        entity_type: str,
        entity_id: object,
        *,
        marketplace: str | None = None,
        risk_type: str = "data_quality",
        meta: dict[str, Any] | None = None,
    ) -> None:
        risks.append({
            "id": risk_id,
            "severity": severity,
            "title": _text(title, limit=180),
            "reason": _text(reason),
            "action": _text(action),
            "entity_type": entity_type,
            "entity_id": str(entity_id or ""),
            "meta": meta or {},
            "type": risk_type,
            "marketplace": marketplace,
            "detail": _text(reason),
        })

    for provider in providers:
        marketplace = str(provider.get("marketplace") or "")
        if provider.get("configured") and provider.get("status") not in {"fresh"}:
            add(
                f"provider-{marketplace}-{provider.get('status')}",
                "high" if provider.get("status") in {"error", "permission_required"} else "medium",
                f"Данные {provider.get('label')} требуют внимания",
                "; ".join(_as_dict(provider.get("meta")).get("warnings") or []) or "Источник не полностью доступен.",
                "Проверьте capability, токен и журнал последней синхронизации.",
                "marketplace",
                marketplace,
                marketplace=marketplace,
            )
    for row in _as_rows(ozon_quality.get("datasets")):
        normalized = _status(row.get("freshness") or row.get("status"))
        if normalized != "fresh":
            dataset = str(row.get("dataset") or "unknown")
            add(
                f"ozon-dataset-{dataset}",
                "high" if normalized == "error" else "medium",
                f"Ozon: {dataset} — {normalized}",
                row.get("error_summary") or row.get("termination_reason") or "Набор данных неполный или несвежий.",
                "Откройте контроль данных Ozon и проверьте последний run.",
                "dataset",
                dataset,
                marketplace="ozon",
            )
    for row in _capability_rows(wb_provider):
        normalized = _status(row.get("status"))
        if normalized != "fresh":
            capability = str(row.get("capability") or "unknown")
            add(
                f"wb-capability-{capability}",
                "high" if normalized in {"error", "permission_required"} else "medium",
                f"Wildberries: недоступен раздел {capability}",
                row.get("safe_message") or f"Capability имеет статус {normalized}.",
                "Проверьте разрешения токена и повторите синхронизацию после Retry-After.",
                "capability",
                capability,
                marketplace="wildberries",
            )
    for index, alert in enumerate(_as_rows(production.get("alerts"))[:20]):
        alert_type = str(alert.get("type") or "production")
        add(
            f"production-{alert_type}-{alert.get('batch_id') or index}",
            "high" if alert_type in {"blocked", "overdue", "defect"} else "medium",
            alert.get("title") or "Производственный риск",
            alert.get("detail") or "Производственное задание требует внимания.",
            "Откройте производственное задание и назначьте ответственное действие.",
            "production_batch",
            alert.get("batch_id") or index,
            risk_type="production",
        )
    attention_statuses = {"SHORTAGE", "SYNC_ERROR", "DOCUMENTS_REQUIRED"}
    for row in _as_rows(supplies.get("shipments")):
        status = str(row.get("canonical_status") or row.get("status") or "").upper()
        if status in attention_statuses:
            identifier = row.get("external_supply_id") or row.get("number") or row.get("id")
            add(
                f"supply-{identifier}-{status}",
                "high" if status in {"SHORTAGE", "SYNC_ERROR"} else "medium",
                f"Поставка {identifier}: {status}",
                "Поставка не может продолжить обычный складской поток.",
                "Откройте поставку и устраните блокирующую причину.",
                "supply",
                identifier,
                marketplace=str(row.get("marketplace") or "") or None,
                risk_type="supply",
            )
    return risks[:50]


def analytics_overview(
    payload: dict[str, Any] | None,
    *,
    dashboard_reader: Callable[[], dict[str, Any]],
    data_quality_reader: Callable[[], dict[str, Any]],
    production_reader: Callable[[str, str], dict[str, Any]],
    current: datetime | date | None = None,
) -> dict[str, Any]:
    """Build the complete overview from local read models only."""
    try:
        period = resolve_period(payload, current=current)
    except AnalyticsOverviewRequestError as error:
        return {"ok": False, "code": error.code, "message": str(error)}

    now = _now(current)
    generated_at = _generated_at(now)
    dashboard, dashboard_error = _safe_read("marketplace dashboard", dashboard_reader)
    quality_envelope, quality_error = _safe_read("Ozon data quality", data_quality_reader)
    production_source, production_error = _safe_read(
        "production control", production_reader, period.start.isoformat(), period.end.isoformat()
    )
    quality_failure_status: str | None = "unavailable" if quality_error else None
    if dashboard_error is None and dashboard.get("ok") is False:
        dashboard_error = "Источник marketplace dashboard вернул ошибку."
        dashboard = {}
    if quality_error is None and quality_envelope.get("ok") is False:
        code = str(quality_envelope.get("code") or "").casefold()
        quality_failure_status = (
            "unavailable"
            if code in {"postgres_unavailable", "not_configured", "phase1a_disabled"}
            else "error"
        )
        quality_error = "Источник Ozon data quality вернул ошибку и исключён из расчёта."
        quality_envelope = {}
    if production_error is None and production_source.get("ok") is False:
        production_error = "Источник production control вернул ошибку."
        production_source = {}
    source_errors = [item for item in (dashboard_error, quality_error, production_error) if item]
    if len(source_errors) == 3:
        return {
            "ok": False,
            "code": "analytics_unavailable",
            "message": "Источники аналитики временно недоступны.",
            "period": period.as_dict(),
            "meta": _data_meta(
                status="error", generated_at=generated_at, sources=[], warnings=source_errors
            ),
        }

    ozon_provider = dashboard
    wb_provider = _as_dict(ozon_provider.get("wildberries"))
    quality = _ozon_quality(quality_envelope)
    production_has_data = not production_error and (
        any(
            key in production_source and production_source.get(key) is not None
            for key in ("plan", "fact", "active_quantity", "fpy")
        )
        or bool(_as_rows(production_source.get("alerts")))
        or bool(_as_rows(production_source.get("stages")))
    )
    production_source_updated_at = _latest_timestamp(
        (
            production_source.get("max_source_updated_at"),
            production_source.get("updated_at"),
        )
    ) if production_has_data else None
    production_meta = _data_meta(
        status="error" if production_error else ("fresh" if production_has_data else "no_data"),
        generated_at=generated_at,
        sources=["sqlite.production_control"] if production_has_data else [],
        warnings=[production_error] if production_error else [],
        max_source_updated_at=production_source_updated_at,
        last_successful_sync_at=_latest_timestamp(
            (production_source.get("last_successful_sync_at"), production_source_updated_at)
        ) if production_has_data else None,
    )
    if production_error:
        production = {
            "start_date": period.start.isoformat(),
            "end_date": period.end.isoformat(),
            "plan": None,
            "fact": None,
            "defect_quantity": None,
            "fpy": None,
            "active_tasks": None,
            "active_quantity": None,
            "stages": [],
            "alerts": [],
            "details": {},
            "meta": production_meta,
        }
    else:
        production = {**production_source, "meta": production_meta}

    ozon, ozon_finance, ozon_orders = _provider_payload(
        "ozon", "Ozon", ozon_provider, quality, period, generated_at
    )
    wb, wb_finance, wb_orders = _provider_payload(
        "wildberries", "Wildberries", wb_provider, {}, period, generated_at
    )
    providers = [ozon, wb]
    series = _combined_series(ozon_finance, wb_finance, ozon_orders, wb_orders)

    supply_counts = _as_dict(ozon_provider.get("supply_counts"))
    canonical_supplies = _as_rows(ozon_provider.get("supplies"))
    warehouse_shipments = _as_rows(ozon_provider.get("warehouse_shipments"))
    shipments = canonical_supplies or warehouse_shipments
    supplies_meta = _supplies_meta(
        ozon_provider,
        wb_provider,
        shipments,
        dashboard_error=dashboard_error,
        generated_at=generated_at,
    )
    supplies = {
        "counts": {str(key): _integer(value) for key, value in supply_counts.items()} if supply_counts else {},
        "shipments": shipments,
        "rows": shipments,
        "warehouse_shipments": warehouse_shipments,
        "meta": supplies_meta,
    }

    quality_has_source = quality_error is None and _quality_source_available(quality)
    if quality_error:
        quality_status = quality_failure_status or "unavailable"
        quality_state = quality_status
        quality_meta = _data_meta(
            status=quality_status,
            generated_at=generated_at,
            sources=[],
            warnings=[quality_error],
        )
    elif quality_has_source:
        quality_status = ozon["status"]
        quality_state = quality.get("state") or "unknown"
        quality_updated_at = _latest_timestamp(
            _dataset_timestamp(row) for row in _as_rows(quality.get("datasets"))
        )
        quality_meta = _data_meta(
            status=quality_status,
            generated_at=generated_at,
            sources=["postgres.marketplace_phase1a"],
            warnings=ozon["meta"]["warnings"],
            max_source_updated_at=quality_updated_at,
            last_successful_sync_at=quality_updated_at,
        )
    else:
        quality_status = _status(quality.get("state"), fallback="no_data")
        if quality_status == "unknown":
            quality_status = "no_data"
        quality_state = quality.get("state") or quality_status
        quality_meta = _data_meta(
            status=quality_status,
            generated_at=generated_at,
            sources=[],
            warnings=["PostgreSQL Phase 1A не предоставил подтверждённый snapshot."],
        )
    ozon_quality_payload = {
        "status": quality_status,
        "state": quality_state,
        "datasets": _as_rows(quality.get("datasets")),
        "capabilities": _as_rows(quality.get("capabilities")),
        "totals": _as_dict(quality.get("totals")),
        "meta": quality_meta,
    }
    wb_quality_payload = {
        "status": wb["status"],
        "capabilities": _capability_rows(wb_provider),
        "last_sync_at": wb.get("last_sync_at"),
        "last_error": wb.get("last_error"),
        "meta": wb["meta"],
    }
    data_quality = {
        "ozon": ozon_quality_payload,
        "wildberries": wb_quality_payload,
        "providers": [ozon_quality_payload, wb_quality_payload],
        "datasets": ozon_quality_payload["datasets"],
    }
    risks = _risks(providers, quality, wb_provider, production, supplies)

    source_times = [row.get("last_sync_at") for row in providers]
    source_times.append(production_source_updated_at)
    max_updated = _latest_timestamp(source_times)
    component_statuses = [
        _status(row.get("status"), fallback="unknown") for row in providers
    ] + [
        _status(production_meta.get("status"), fallback="unknown"),
        _status(supplies_meta.get("status"), fallback="unknown"),
    ]
    if quality_error:
        component_statuses.append(quality_failure_status or "unavailable")
    if component_statuses and all(item == "fresh" for item in component_statuses):
        overall_status = "fresh"
    elif component_statuses and len(set(component_statuses)) == 1:
        overall_status = component_statuses[0]
    elif any(item in {"fresh", "stale", "partial"} for item in component_statuses):
        overall_status = "partial"
    elif "error" in component_statuses:
        overall_status = "error"
    elif "permission_required" in component_statuses:
        overall_status = "permission_required"
    elif "unavailable" in component_statuses:
        overall_status = "unavailable"
    else:
        overall_status = "no_data"
    warnings = (
        source_errors
        + [warning for row in providers for warning in row["meta"]["warnings"]]
        + list(supplies_meta.get("warnings") or [])
    )
    meta = _data_meta(
        status=overall_status,
        generated_at=generated_at,
        partial=overall_status == "partial",
        sources=[
            source
            for source, failed in (
                ("sqlite.marketplace_dashboard", dashboard_error),
                (
                    "postgres.marketplace_phase1a",
                    quality_error or (None if quality_has_source else "no confirmed source"),
                ),
                (
                    "sqlite.production_control",
                    production_error or (None if production_has_data else "no confirmed source"),
                ),
            )
            if failed is None and (source != "sqlite.marketplace_dashboard" or bool(dashboard))
        ],
        warnings=warnings,
        max_source_updated_at=max_updated,
        last_successful_sync_at=_latest_timestamp(source_times),
    )
    return {
        "ok": True,
        "period": period.as_dict(),
        "metrics": _metrics(providers, production, generated_at),
        "series": series,
        "providers": providers,
        "marketplaceBreakdown": providers,
        "risks": risks,
        "supplies": supplies,
        "catalog_reconciliation": _as_dict(dashboard.get("catalog_reconciliation")),
        "data_quality": data_quality,
        "production": production,
        "meta": meta,
    }


def analytics_overview_http_status(result: dict[str, Any]) -> int:
    if result.get("ok"):
        return 200
    return {
        "invalid_request": 400,
        "invalid_period": 400,
        "forbidden": 403,
        "analytics_unavailable": 503,
    }.get(str(result.get("code") or ""), 500)
