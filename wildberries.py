"""Read-only Wildberries integration backed by the shared marketplace model."""

from __future__ import annotations

import base64
import json
import os
import sqlite3
import time
from datetime import date, datetime, timedelta
from email.utils import parsedate_to_datetime
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from database import get_db_connection, local_now
from marketplace_extended import dashboard_extension, ensure_schema as ensure_extended_schema


def _text(value) -> str:
    return "" if value is None else str(value).strip()


def _number(value) -> float:
    try:
        return float(str(value or 0).replace(",", "."))
    except (TypeError, ValueError):
        return 0.0


def _first_present(payload: dict, *keys: str):
    """Return the first API field that is present, preserving numeric zero."""
    for key in keys:
        if key in payload and payload[key] not in (None, ""):
            return payload[key]
    return None


def _int(value) -> int:
    try:
        return int(float(value or 0))
    except (TypeError, ValueError):
        return 0


def _json(value) -> str:
    return json.dumps(value if value is not None else {}, ensure_ascii=False, separators=(",", ":"))


def _now() -> str:
    # Snapshot filters need enough precision to distinguish consecutive runs.
    return local_now().isoformat(timespec="microseconds")


def _token_seller_id(token: str) -> str:
    try:
        payload = token.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        return _text(json.loads(base64.urlsafe_b64decode(payload))["sid"])
    except Exception:
        return ""


class WildberriesError(RuntimeError):
    pass


class WildberriesAPIError(WildberriesError):
    """A safe, structured WB API failure that never contains credentials."""

    def __init__(
        self,
        message: str,
        *,
        code: str,
        capability: str,
        http_status: int | None = None,
        retry_after_seconds: float | None = None,
        request_id: str = "",
        safe_response: dict | None = None,
    ):
        super().__init__(message)
        self.code = code
        self.capability = capability
        self.http_status = http_status
        self.retry_after_seconds = retry_after_seconds
        self.request_id = _text(request_id)
        self.safe_response = safe_response or {}

    def capability_status(self) -> dict:
        payload = {
            "status": self.code,
            "safe_message": str(self),
            "http_status": self.http_status,
            "retry_after_seconds": self.retry_after_seconds,
            "request_id": self.request_id,
            "safe_response": self.safe_response,
        }
        return {key: value for key, value in payload.items() if value is not None}


# Minimum gaps documented by WB for the read-only methods used below.  Scopes
# are deliberately separate: a slow finance report must not throttle catalog
# pagination, while every page of the same report shares one limiter.
WB_RATE_INTERVALS = {
    "catalog": 0.6,
    "prices": 0.6,
    "stocks": 20.0,
    "fbs_warehouses": 0.6,
    "fbs_stocks": 0.6,
    "orders": 60.0,
    "sales": 60.0,
    "finance": 60.0,
    "feedbacks": 0.334,
    "supplies": 0.2,
    "funnel": 20.0,
    "advertising.count": 0.2,
    "advertising.campaigns": 0.2,
    "advertising.stats": 20.0,
    "advertising.balance": 1.0,
}
WB_MAX_INLINE_RETRY_SECONDS = 65.0
WB_MAX_RETRY_AFTER_SECONDS = 24 * 60 * 60
WB_ORDERS_HISTORY_DAYS = 90
WB_SALES_HISTORY_DAYS = 90
WB_FINANCE_HISTORY_DAYS = 90
WB_FUNNEL_REQUEST_DAYS = 30
WB_FUNNEL_MAX_WINDOW_DAYS = 7
WB_ADVERTISING_HISTORY_DAYS = 30
WB_SNAPSHOT_SENTINEL = "9999-12-31T23:59:59"


def _capability_for_scope(scope: str) -> str:
    return _text(scope).split(".", 1)[0] or "unknown"


def _retry_after_seconds(headers, *, fallback: float, now: datetime | None = None) -> float:
    """Read WB's rate-limit headers, with HTTP Retry-After as a fallback."""
    for name in ("X-Ratelimit-Retry", "Retry-After", "X-Ratelimit-Reset"):
        raw = _text(headers.get(name) if headers is not None else "")
        if not raw:
            continue
        try:
            return max(1.0, min(float(raw), WB_MAX_RETRY_AFTER_SECONDS))
        except (TypeError, ValueError):
            if name != "Retry-After":
                continue
            try:
                target = parsedate_to_datetime(raw)
                current = now or datetime.now(target.tzinfo)
                return max(1.0, min((target - current).total_seconds(), WB_MAX_RETRY_AFTER_SECONDS))
            except (TypeError, ValueError, OverflowError):
                continue
    return max(1.0, min(float(fallback), WB_MAX_RETRY_AFTER_SECONDS))


def _safe_error_message(error: Exception, *, capability: str = "sync", token: str = "") -> str:
    if isinstance(error, WildberriesAPIError):
        message = str(error)
    elif isinstance(error, WildberriesError):
        message = str(error)
    else:
        message = f"{capability}: внутренняя ошибка синхронизации."
    if token:
        message = message.replace(token, "[redacted]")
    return message[:500]


WB_ANALYTICS_SCHEMA = """
CREATE TABLE IF NOT EXISTS marketplace_wb_funnel_daily (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    report_date TEXT NOT NULL,
    nm_id TEXT NOT NULL DEFAULT '',
    open_count INTEGER NOT NULL DEFAULT 0,
    cart_count INTEGER NOT NULL DEFAULT 0,
    order_count INTEGER NOT NULL DEFAULT 0,
    order_sum REAL NOT NULL DEFAULT 0,
    buyout_count INTEGER NOT NULL DEFAULT 0,
    buyout_sum REAL NOT NULL DEFAULT 0,
    payload_json TEXT NOT NULL DEFAULT '{}',
    updated_at TEXT NOT NULL,
    UNIQUE(account_id, report_date, nm_id)
);
CREATE TABLE IF NOT EXISTS marketplace_ad_campaigns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    marketplace TEXT NOT NULL,
    campaign_id TEXT NOT NULL,
    name TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT '',
    payment_type TEXT NOT NULL DEFAULT '',
    daily_budget REAL NOT NULL DEFAULT 0,
    payload_json TEXT NOT NULL DEFAULT '{}',
    updated_at TEXT NOT NULL,
    UNIQUE(account_id, marketplace, campaign_id)
);
CREATE TABLE IF NOT EXISTS marketplace_ad_daily (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    marketplace TEXT NOT NULL,
    campaign_id TEXT NOT NULL,
    report_date TEXT NOT NULL,
    views INTEGER NOT NULL DEFAULT 0,
    clicks INTEGER NOT NULL DEFAULT 0,
    spend REAL NOT NULL DEFAULT 0,
    orders INTEGER NOT NULL DEFAULT 0,
    revenue REAL NOT NULL DEFAULT 0,
    payload_json TEXT NOT NULL DEFAULT '{}',
    updated_at TEXT NOT NULL,
    UNIQUE(account_id, marketplace, campaign_id, report_date)
);
CREATE TABLE IF NOT EXISTS marketplace_ad_balances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    marketplace TEXT NOT NULL,
    observed_date TEXT NOT NULL,
    balance REAL NOT NULL DEFAULT 0,
    net REAL NOT NULL DEFAULT 0,
    bonus REAL NOT NULL DEFAULT 0,
    payload_json TEXT NOT NULL DEFAULT '{}',
    updated_at TEXT NOT NULL,
    UNIQUE(account_id, marketplace, observed_date)
);
CREATE TABLE IF NOT EXISTS marketplace_wb_feedbacks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    feedback_id TEXT NOT NULL,
    nm_id TEXT NOT NULL DEFAULT '',
    product_name TEXT NOT NULL DEFAULT '',
    rating REAL NOT NULL DEFAULT 0,
    text TEXT NOT NULL DEFAULT '',
    answer_text TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT '',
    answered INTEGER NOT NULL DEFAULT 0,
    payload_json TEXT NOT NULL DEFAULT '{}',
    updated_at TEXT NOT NULL,
    UNIQUE(account_id, feedback_id)
);
CREATE TABLE IF NOT EXISTS marketplace_wb_capabilities (
    account_id INTEGER NOT NULL,
    capability TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'unknown',
    safe_message TEXT NOT NULL DEFAULT '',
    http_status INTEGER,
    retry_after_seconds REAL,
    row_count INTEGER NOT NULL DEFAULT 0,
    details_json TEXT NOT NULL DEFAULT '{}',
    checked_at TEXT NOT NULL,
    PRIMARY KEY(account_id, capability)
);
CREATE INDEX IF NOT EXISTS idx_wb_funnel_account_date ON marketplace_wb_funnel_daily(account_id, report_date);
CREATE INDEX IF NOT EXISTS idx_ad_daily_account_date ON marketplace_ad_daily(account_id, marketplace, report_date);
CREATE INDEX IF NOT EXISTS idx_wb_feedbacks_account_date ON marketplace_wb_feedbacks(account_id, created_at DESC);
"""


def ensure_wildberries_schema(
    conn: sqlite3.Connection | None = None,
    *,
    ensure_dependencies: bool = True,
) -> None:
    """Create the WB read model before any latency-sensitive dashboard read."""
    owned = conn is None
    connection = conn or get_db_connection()
    try:
        if ensure_dependencies:
            from marketplaces import ensure_schema as ensure_marketplace_schema

            ensure_marketplace_schema(connection)
            ensure_extended_schema(connection)
        connection.executescript(WB_ANALYTICS_SCHEMA)
        connection.commit()
    finally:
        if owned:
            connection.close()


def _result_row_count(value) -> int:
    if isinstance(value, list):
        return len(value)
    if isinstance(value, dict):
        if "products" in value or "history" in value:
            return len(value.get("products") or []) + len(value.get("history") or [])
        if "campaigns" in value or "stats" in value:
            return len(value.get("campaigns") or []) + len(value.get("stats") or [])
        return 1 if value else 0
    return 0


def _failed_capability(name: str, error: Exception, *, token: str = "") -> dict:
    if isinstance(error, WildberriesAPIError):
        payload = error.capability_status()
    else:
        payload = {
            "status": "error",
            "safe_message": _safe_error_message(error, capability=name, token=token),
        }
    payload["row_count"] = 0
    return payload


def _invalid_response(capability: str) -> WildberriesAPIError:
    return WildberriesAPIError(
        f"WB API вернул неожиданный формат для раздела «{capability}».",
        code="invalid_response",
        capability=capability,
    )


def _require_dict(value, capability: str) -> dict:
    if not isinstance(value, dict):
        raise _invalid_response(capability)
    return value


def _require_list(value, capability: str) -> list:
    if not isinstance(value, list):
        raise _invalid_response(capability)
    return value


def _save_capabilities(conn, account_id: int, capabilities: dict[str, dict]) -> None:
    checked_at = _now()
    for name, payload in capabilities.items():
        previous = conn.execute(
            "SELECT status,details_json FROM marketplace_wb_capabilities WHERE account_id=? AND capability=?",
            (account_id, name),
        ).fetchone()
        previous_status = _text(previous[0]) if previous else ""
        try:
            previous_details = json.loads(previous[1] or "{}") if previous else {}
        except (TypeError, json.JSONDecodeError):
            previous_details = {}
        details = {
            key: value
            for key, value in payload.items()
            if key not in {"safe_message", "status", "http_status", "retry_after_seconds", "row_count"}
        }
        previous_success = _text(previous_details.get("last_successful_snapshot_started_at"))
        if not previous_success and previous_status == "available":
            previous_success = _text(previous_details.get("snapshot_started_at"))
        current_snapshot = _text(payload.get("snapshot_started_at"))
        if payload.get("status") == "available" and current_snapshot:
            details["last_successful_snapshot_started_at"] = current_snapshot
        elif previous_success:
            details["last_successful_snapshot_started_at"] = previous_success
        conn.execute(
            """INSERT INTO marketplace_wb_capabilities
               (account_id,capability,status,safe_message,http_status,retry_after_seconds,row_count,details_json,checked_at)
               VALUES (?,?,?,?,?,?,?,?,?)
               ON CONFLICT(account_id,capability) DO UPDATE SET
                 status=excluded.status,safe_message=excluded.safe_message,http_status=excluded.http_status,
                 retry_after_seconds=excluded.retry_after_seconds,row_count=excluded.row_count,
                 details_json=excluded.details_json,checked_at=excluded.checked_at""",
            (
                account_id,
                name,
                _text(payload.get("status")) or "unknown",
                _text(payload.get("safe_message")),
                payload.get("http_status"),
                payload.get("retry_after_seconds"),
                max(0, _int(payload.get("row_count"))),
                _json(details),
                checked_at,
            ),
        )


def _persisted_retry_remaining(conn, account_id: int) -> float:
    """Return the longest active token cooldown saved by a previous worker."""
    rows = conn.execute(
        """SELECT checked_at,retry_after_seconds
             FROM marketplace_wb_capabilities
            WHERE account_id=? AND status='rate_limited' AND retry_after_seconds IS NOT NULL""",
        (account_id,),
    ).fetchall()
    remaining = 0.0
    for checked_at, retry_after in rows:
        try:
            checked = datetime.fromisoformat(str(checked_at))
            current = datetime.now(checked.tzinfo) if checked.tzinfo else local_now()
            deadline = checked + timedelta(seconds=max(0.0, float(retry_after or 0)))
            remaining = max(remaining, (deadline - current).total_seconds())
        except (TypeError, ValueError, OverflowError):
            continue
    return max(0.0, remaining)


class WildberriesClient:
    def __init__(
        self,
        token: str | None = None,
        *,
        client_secret: str | None = None,
        sleep: Callable[[float], None] = time.sleep,
        monotonic: Callable[[], float] = time.monotonic,
        max_attempts: int = 3,
    ):
        self.token = (token or os.getenv("WB_API_TOKEN", "")).strip()
        if not self.token:
            raise WildberriesError("WB_API_TOKEN не настроен.")
        self.client_secret = (
            client_secret
            if client_secret is not None
            else next(
                (
                    os.getenv(name, "").strip()
                    for name in (
                        "WB_CLIENT_SECRET",
                        "WB_API_CLIENT_SECRET",
                        "WB_SERVICE_SECRET",
                        "WILDBERRIES_CLIENT_SECRET",
                        "WILDBERRIES_SERVICE_SECRET",
                    )
                    if os.getenv(name, "").strip()
                ),
                "",
            )
        ).strip()
        self._sleep = sleep
        self._monotonic = monotonic
        self._max_attempts = max(1, int(max_attempts))
        self._next_request_at: dict[str, float] = {}
        self._global_retry_at = 0.0
        self._global_rate_limit_exhausted = False

    def _wait_for_slot(self, scope: str) -> None:
        while True:
            now = self._monotonic()
            deadline = max(self._next_request_at.get(scope, 0.0), self._global_retry_at)
            delay = deadline - now
            if delay <= 0:
                self._next_request_at[scope] = now + WB_RATE_INTERVALS.get(scope, 0.0)
                return
            self._sleep(delay)

    def _deferred_rate_limit_error(self, scope: str) -> WildberriesAPIError | None:
        if not self._global_rate_limit_exhausted:
            return None
        remaining = self._global_retry_at - self._monotonic()
        if remaining <= 0:
            self._global_retry_at = 0.0
            self._global_rate_limit_exhausted = False
            return None
        capability = _capability_for_scope(scope)
        return WildberriesAPIError(
            f"Глобальный лимит WB API ещё не восстановлен; раздел «{capability}» отложен на {remaining:.0f} с.",
            code="rate_limited",
            capability=capability,
            http_status=429,
            retry_after_seconds=remaining,
        )

    def request(self, url: str, payload=None, *, method: str | None = None, scope: str = "generic"):
        body = None if payload is None else _json(payload).encode("utf-8")
        request_method = method or ("POST" if body is not None else "GET")
        authorization = self.token if self.token.lower().startswith("bearer ") else f"Bearer {self.token}"
        headers = {
            "Authorization": authorization,
            "Accept": "application/json",
            "User-Agent": "ShagaemVmeste/1.0",
        }
        if self.client_secret:
            headers["X-Client-Secret"] = self.client_secret
        if body is not None:
            headers["Content-Type"] = "application/json"
        deferred = self._deferred_rate_limit_error(scope)
        if deferred is not None:
            raise deferred
        capability = _capability_for_scope(scope)
        for attempt in range(self._max_attempts):
            self._wait_for_slot(scope)
            try:
                with urlopen(Request(url, data=body, headers=headers, method=request_method), timeout=60) as response:
                    raw = response.read(32 * 1024 * 1024)
                    self._global_retry_at = 0.0
                    self._global_rate_limit_exhausted = False
                    if not raw:
                        return [] if getattr(response, "status", 200) == 204 else {}
                    return json.loads(raw.decode("utf-8"))
            except HTTPError as error:
                raw_error = error.read(1024 * 1024)
                safe_response = {}
                try:
                    error_payload = json.loads(raw_error.decode("utf-8"))
                    if isinstance(error_payload, dict):
                        safe_response = {
                            key: (_text(value)[:500] if not isinstance(value, (int, float, bool)) else value)
                            for key, value in error_payload.items()
                            if key in {"title", "detail", "code", "requestId", "origin", "status", "statusText", "timestamp"}
                        }
                except (UnicodeDecodeError, json.JSONDecodeError):
                    safe_response = {}
                request_id = _text(
                    safe_response.get("requestId")
                    or error.headers.get("X-Request-ID")
                    or error.headers.get("X-Requestid")
                    or error.headers.get("Request-ID")
                    or error.headers.get("X-Trace-ID")
                )
                error.close()
                if error.code == 429:
                    delay = _retry_after_seconds(
                        error.headers,
                        fallback=max(5 * (2 ** attempt), WB_RATE_INTERVALS.get(scope, 0.0)),
                    )
                    now = self._monotonic()
                    # A WB 429 header is authoritative and may be shorter than
                    # the nominal method interval when the token bucket refills.
                    self._next_request_at[scope] = now + delay
                    self._global_retry_at = now + delay
                    if attempt + 1 < self._max_attempts and delay <= WB_MAX_INLINE_RETRY_SECONDS:
                        continue
                    self._global_rate_limit_exhausted = True
                    raise WildberriesAPIError(
                        f"Глобальный лимит WB API исчерпан на разделе «{capability}»; повторите через {delay:.0f} с.",
                        code="rate_limited",
                        capability=capability,
                        http_status=429,
                        retry_after_seconds=delay,
                        request_id=request_id,
                        safe_response=safe_response,
                    ) from error
                if error.code in {500, 502, 503, 504} and attempt + 1 < self._max_attempts:
                    self._next_request_at[scope] = max(
                        self._next_request_at.get(scope, 0.0),
                        self._monotonic() + min(2 ** attempt, 16),
                    )
                    continue
                if error.code == 401:
                    code = "invalid_token"
                    message = "Токен или Client Secret Wildberries отклонён."
                elif error.code == 402:
                    code = "payment_required"
                    message = f"Раздел «{capability}» требует оплаченного доступа Wildberries."
                elif error.code == 403:
                    code = "forbidden"
                    detail = " ".join(_text(safe_response.get(key)) for key in ("detail", "code")).lower()
                    if "base token without secret" in detail or "x-client-secret" in detail:
                        message = (
                            "WB отклонил базовый токен без X-Client-Secret; "
                            "категория доступа выбрана, но сервисный секрет не настроен."
                        )
                    else:
                        message = f"WB запретил доступ к разделу «{capability}»."
                elif error.code == 404:
                    code = "endpoint_or_resource_not_found"
                    message = f"Метод или ресурс WB не найден для раздела «{capability}»."
                elif 500 <= error.code <= 599:
                    code = "wb_unavailable"
                    message = f"WB API временно недоступен для раздела «{capability}»."
                else:
                    code = "http_error"
                    message = f"WB API вернул HTTP {error.code} для раздела «{capability}»."
                raise WildberriesAPIError(
                    message,
                    code=code,
                    capability=capability,
                    http_status=error.code,
                    request_id=request_id,
                    safe_response=safe_response,
                ) from error
            except (URLError, TimeoutError) as error:
                if attempt + 1 < self._max_attempts:
                    self._next_request_at[scope] = max(
                        self._next_request_at.get(scope, 0.0),
                        self._monotonic() + min(2 ** attempt, 16),
                    )
                    continue
                raise WildberriesAPIError(
                    f"WB API временно недоступен для раздела «{capability}».",
                    code="unavailable",
                    capability=capability,
                ) from error
        raise WildberriesAPIError(
            f"WB API: исчерпаны повторные попытки для раздела «{capability}».",
            code="unavailable",
            capability=capability,
        )

    def cards(self) -> list[dict]:
        rows, cursor, seen = [], {}, set()
        for _ in range(500):
            response = self.request(
                "https://content-api.wildberries.ru/content/v2/get/cards/list",
                {"settings": {"cursor": {"limit": 100, **cursor}, "filter": {"withPhoto": -1}}},
                scope="catalog",
            )
            response = _require_dict(response, "catalog")
            if "cards" not in response:
                raise _invalid_response("catalog")
            cards = _require_list(response.get("cards"), "catalog")
            rows.extend(item for item in cards if isinstance(item, dict))
            next_cursor = response.get("cursor") if isinstance(response.get("cursor"), dict) else {}
            marker = (_text(next_cursor.get("updatedAt")), _text(next_cursor.get("nmID")))
            if len(cards) < 100:
                return rows
            if not all(marker) or _int(marker[1]) <= 0 or marker in seen:
                raise WildberriesAPIError(
                    "WB catalog pagination не вернул новый корректный cursor для полной страницы.",
                    code="invalid_response",
                    capability="catalog",
                )
            seen.add(marker)
            cursor = {"updatedAt": marker[0], "nmID": _int(marker[1])}
        raise WildberriesAPIError(
            "WB catalog pagination достиг защитного лимита страниц.",
            code="invalid_response",
            capability="catalog",
        )

    def prices(self) -> list[dict]:
        rows = []
        for offset in range(0, 1_000_000, 1000):
            query = urlencode({"limit": 1000, "offset": offset})
            response = self.request(
                f"https://discounts-prices-api.wildberries.ru/api/v2/list/goods/filter?{query}",
                scope="prices",
            )
            response = _require_dict(response, "prices")
            data = _require_dict(response.get("data"), "prices")
            page = _require_list(data.get("listGoods"), "prices")
            rows.extend(item for item in page if isinstance(item, dict))
            if len(page) < 1000:
                break
        return rows

    def stocks(self) -> list[dict]:
        rows = []
        limit = 250000
        for offset in range(0, 2_000_000, limit):
            response = self.request(
                "https://seller-analytics-api.wildberries.ru/api/analytics/v1/stocks-report/wb-warehouses",
                {"nmIds": [], "chrtIds": [], "limit": limit, "offset": offset},
                scope="stocks",
            )
            response = _require_dict(response, "stocks")
            data = _require_dict(response.get("data"), "stocks")
            page = _require_list(data.get("items"), "stocks")
            rows.extend(item for item in page if isinstance(item, dict))
            if len(page) < limit:
                break
        return rows

    def fbs_warehouses(self) -> list[dict]:
        response = self.request(
            "https://marketplace-api.wildberries.ru/api/v3/warehouses",
            scope="fbs_warehouses",
        )
        return _require_list(response, "fbs_warehouses")

    def fbs_stocks(self, chrt_ids: list[int]) -> list[dict]:
        normalized_ids = list(dict.fromkeys(_int(value) for value in chrt_ids if _int(value)))
        rows = []
        for warehouse in self.fbs_warehouses():
            warehouse_id = _int(warehouse.get("id"))
            if not warehouse_id:
                continue
            for index in range(0, len(normalized_ids), 1000):
                batch = normalized_ids[index:index + 1000]
                response = self.request(
                    f"https://marketplace-api.wildberries.ru/api/v3/stocks/{warehouse_id}",
                    {"chrtIds": batch},
                    scope="fbs_stocks",
                )
                response = _require_dict(response, "fbs_stocks")
                stocks = _require_list(response.get("stocks"), "fbs_stocks")
                for item in stocks:
                    if not isinstance(item, dict):
                        continue
                    rows.append({
                        **item,
                        "warehouseId": warehouse_id,
                        "warehouseName": _text(warehouse.get("name")) or f"Склад {warehouse_id}",
                    })
        return rows

    def orders(self, days: int = WB_ORDERS_HISTORY_DAYS) -> list[dict]:
        start = (local_now() - timedelta(days=days)).isoformat(timespec="seconds")
        query = urlencode({"dateFrom": start, "flag": 0})
        response = self.request(
            f"https://statistics-api.wildberries.ru/api/v1/supplier/orders?{query}",
            scope="orders",
        )
        return _require_list(response, "orders")

    def sales(self, days: int = WB_SALES_HISTORY_DAYS) -> list[dict]:
        start = (local_now() - timedelta(days=days)).isoformat(timespec="seconds")
        query = urlencode({"dateFrom": start, "flag": 0})
        response = self.request(
            f"https://statistics-api.wildberries.ru/api/v1/supplier/sales?{query}",
            scope="sales",
        )
        return _require_list(response, "sales")

    def finance(self, days: int = WB_FINANCE_HISTORY_DAYS) -> list[dict]:
        rows = []
        rrd_id = 0
        today = local_now().date()
        fields = ["rrdId", "nmId", "docTypeName", "retailAmount", "forPay", "acquiringFee", "srid", "saleDate", "createDate", "quantity", "title", "vendorCode"]
        for _ in range(500):
            response = self.request(
                "https://finance-api.wildberries.ru/api/finance/v1/sales-reports/detailed",
                {"dateFrom": (today - timedelta(days=days)).isoformat(), "dateTo": today.isoformat(), "limit": 5000, "rrdId": rrd_id, "period": "daily", "fields": fields},
                scope="finance",
            )
            page = _require_list(response, "finance")
            rows.extend(item for item in page if isinstance(item, dict))
            if not page:
                break
            next_rrd = _int(page[-1].get("rrdId"))
            if not next_rrd or next_rrd == rrd_id:
                break
            rrd_id = next_rrd
        return rows

    def feedbacks(self) -> list[dict]:
        rows = []
        for answered in (False, True):
            for skip in range(0, 25000, 5000):
                query = urlencode({"isAnswered": str(answered).lower(), "take": 5000, "skip": skip, "order": "dateDesc"})
                response = self.request(
                    f"https://feedbacks-api.wildberries.ru/api/v1/feedbacks?{query}",
                    scope="feedbacks",
                )
                response = _require_dict(response, "feedbacks")
                data = _require_dict(response.get("data"), "feedbacks")
                page = _require_list(data.get("feedbacks"), "feedbacks")
                rows.extend(item for item in page if isinstance(item, dict))
                if len(page) < 5000:
                    break
        return rows

    def supplies(self) -> list[dict]:
        response = self.request(
            "https://marketplace-api.wildberries.ru/api/v3/supplies?limit=1000&next=0",
            scope="supplies",
        )
        response = _require_dict(response, "supplies")
        return _require_list(response.get("supplies"), "supplies")

    def funnel(self, days: int = WB_FUNNEL_REQUEST_DAYS) -> dict:
        requested_days = max(1, int(days))
        loaded_days = min(requested_days, WB_FUNNEL_MAX_WINDOW_DAYS)
        end = local_now().date()
        start = end - timedelta(days=loaded_days - 1)
        requested_start = end - timedelta(days=requested_days - 1)
        previous_end = start - timedelta(days=1)
        previous_start = previous_end - timedelta(days=loaded_days - 1)
        products = []
        for offset in range(0, 100000, 1000):
            response = self.request(
                "https://seller-analytics-api.wildberries.ru/api/analytics/v3/sales-funnel/products",
                {"selectedPeriod": {"start": start.isoformat(), "end": end.isoformat()}, "pastPeriod": {"start": previous_start.isoformat(), "end": previous_end.isoformat()}, "nmIds": [], "brandNames": [], "subjectIds": [], "tagIds": [], "skipDeletedNm": True, "orderBy": {"field": "openCard", "mode": "desc"}, "limit": 1000, "offset": offset},
                scope="funnel",
            )
            if isinstance(response, list):
                page = response
            else:
                response = _require_dict(response, "funnel")
                data = response.get("data")
                if isinstance(data, dict):
                    if "products" in data:
                        page = _require_list(data.get("products"), "funnel")
                    elif "items" in data:
                        page = _require_list(data.get("items"), "funnel")
                    else:
                        raise _invalid_response("funnel")
                else:
                    page = _require_list(data, "funnel")
            products.extend(item for item in page if isinstance(item, dict))
            if len(page) < 1000:
                break
        history_response = self.request(
            "https://seller-analytics-api.wildberries.ru/api/analytics/v3/sales-funnel/grouped/history",
            {"selectedPeriod": {"start": start.isoformat(), "end": end.isoformat()}, "brandNames": [], "subjectIds": [], "tagIds": [], "skipDeletedNm": True, "aggregationLevel": "day"},
            scope="funnel",
        )
        if isinstance(history_response, list):
            history_data = history_response
        else:
            history_response = _require_dict(history_response, "funnel")
            history_data = _require_list(history_response.get("data"), "funnel")
        partial = loaded_days < requested_days
        return {
            "products": products,
            "history": history_data,
            "coverage_start_date": start.isoformat(),
            "coverage_end_date": end.isoformat(),
            "requested_coverage_start_date": requested_start.isoformat(),
            "requested_coverage_end_date": end.isoformat(),
            "coverage_complete": not partial,
            "coverage_basis": "report_date",
            "outside_coverage_status": "partial",
            "partial": partial,
            "partial_reason": "funnel_window_limited_to_7_days" if partial else "",
        }

    def advertising(self, days: int = WB_ADVERTISING_HISTORY_DAYS) -> dict:
        today = local_now().date()
        count_payload = self.request(
            "https://advert-api.wildberries.ru/adv/v1/promotion/count",
            scope="advertising.count",
        )
        count_payload = _require_dict(count_payload, "advertising")
        adverts = _require_list(count_payload.get("adverts"), "advertising")
        campaign_ids = []
        for group in adverts:
            for item in group.get("advert_list") or group.get("advertList") or []:
                campaign_id = _int(item.get("advertId") or item.get("advert_id") or item.get("id"))
                if campaign_id:
                    campaign_ids.append(campaign_id)
        campaign_ids = list(dict.fromkeys(campaign_ids))
        campaigns = []
        for index in range(0, len(campaign_ids), 50):
            ids = campaign_ids[index:index + 50]
            response = self.request(
                "https://advert-api.wildberries.ru/api/advert/v2/adverts?" + urlencode({"ids": ",".join(map(str, ids))}),
                scope="advertising.campaigns",
            )
            campaigns.extend(item for item in _require_list(response, "advertising") if isinstance(item, dict))
        stats = []
        stat_ids = [_int(item.get("advertId") or item.get("advert_id") or item.get("id")) for item in campaigns if _int(item.get("status")) in {7, 9, 11}]
        for index in range(0, len(stat_ids), 50):
            ids = [item for item in stat_ids[index:index + 50] if item]
            if not ids:
                continue
            response = self.request(
                "https://advert-api.wildberries.ru/adv/v3/fullstats?" + urlencode({"ids": ",".join(map(str, ids)), "beginDate": (today - timedelta(days=days)).isoformat(), "endDate": today.isoformat()}),
                scope="advertising.stats",
            )
            stats.extend(item for item in _require_list(response, "advertising") if isinstance(item, dict))
        balance = self.request(
            "https://advert-api.wildberries.ru/adv/v1/balance",
            scope="advertising.balance",
        )
        return {"campaigns": campaigns, "stats": stats, "balance": _require_dict(balance, "advertising")}


def _flatten_cards(cards: list[dict]) -> list[dict]:
    rows = []
    for card in cards:
        nm_id = _text(card.get("nmID"))
        vendor = _text(card.get("vendorCode"))
        title = _text(card.get("title") or card.get("subjectName") or vendor or nm_id)
        photos = card.get("photos") if isinstance(card.get("photos"), list) else []
        image = ""
        if photos and isinstance(photos[0], dict):
            image = _text(photos[0].get("big") or photos[0].get("c516x688") or photos[0].get("c246x328") or photos[0].get("square"))
        characteristics = card.get("characteristics") if isinstance(card.get("characteristics"), list) else []
        color = ""
        for characteristic in characteristics:
            if "цвет" in _text(characteristic.get("name")).lower():
                value = characteristic.get("value")
                color = _text(value[0] if isinstance(value, list) and value else value)
                break
        sizes = card.get("sizes") if isinstance(card.get("sizes"), list) else []
        if not sizes:
            sizes = [{}]
        for size_row in sizes:
            size = _text(size_row.get("techSize") or size_row.get("wbSize")) or "Не указан"
            chrt_id = _text(size_row.get("chrtID") or f"{nm_id}:{size}")
            skus = size_row.get("skus") if isinstance(size_row.get("skus"), list) else []
            barcode = _text(skus[0] if skus else "")
            payload = dict(card)
            payload["image_url"] = image
            payload["wb_nm_id"] = nm_id
            payload["wb_chrt_id"] = chrt_id
            rows.append({"external_product_id": chrt_id, "offer_id": f"{vendor}/{size}" if vendor else chrt_id,
                         "sku": nm_id, "barcode": barcode, "name": title, "size": size,
                         "color": color or "Не указан", "payload": payload})
    return rows


def _upsert_product(conn, account_id: int, row: dict, now: str) -> int:
    conn.execute(
        """INSERT INTO marketplace_products
           (account_id,external_product_id,offer_id,sku,barcode,name,size,color,payload_json,updated_at)
           VALUES (?,?,?,?,?,?,?,?,?,?)
           ON CONFLICT(account_id,external_product_id,offer_id) DO UPDATE SET
             sku=excluded.sku,barcode=excluded.barcode,name=excluded.name,size=excluded.size,
             color=excluded.color,payload_json=excluded.payload_json,updated_at=excluded.updated_at""",
        (account_id,row["external_product_id"],row["offer_id"],row["sku"],row["barcode"],row["name"],
         row["size"],row["color"],_json(row["payload"]),now),
    )
    return int(conn.execute(
        "SELECT id FROM marketplace_products WHERE account_id=? AND external_product_id=? AND offer_id=?",
        (account_id,row["external_product_id"],row["offer_id"]),
    ).fetchone()[0])


def sync_wildberries() -> dict:
    from marketplaces import _account, sync_production_links, upsert_marketplace_supply

    token = os.getenv("WB_API_TOKEN", "").strip()
    if not token:
        return {"ok": False, "message": "WB_API_TOKEN не настроен."}
    conn = get_db_connection()
    ensure_wildberries_schema(conn)
    account_id = _account(conn, "wildberries", os.getenv("WB_ACCOUNT_NAME", "Основной Wildberries"), _token_seller_id(token))
    retry_remaining = _persisted_retry_remaining(conn, account_id)
    if retry_remaining > 0:
        conn.close()
        return {
            "ok": False,
            "status": "deferred",
            "read_only": True,
            "retry_after_seconds": retry_remaining,
            "message": f"Wildberries sync отложен ещё на {retry_remaining:.0f} с из-за лимита API.",
        }
    started = _now()
    run_id = conn.execute(
        "INSERT INTO marketplace_sync_runs (account_id,status,started_at) VALUES (?,'running',?)",
        (account_id, started),
    ).lastrowid
    conn.commit()
    client = WildberriesClient(token)
    counts = {"products": 0, "prices": 0, "stocks": 0, "fbs_stocks": 0, "orders": 0, "sales": 0, "finance": 0, "feedbacks": 0, "supplies": 0, "funnel": 0, "campaigns": 0, "ad_days": 0}
    errors: list[str] = []
    capabilities: dict[str, dict] = {}
    links: dict = {}

    def safe(name, callback, default):
        try:
            value = callback()
            capabilities[name] = {
                # Transport success is not yet a usable snapshot.  The status
                # becomes available only after normalization and commit.
                "status": "pending",
                "safe_message": "Данные WB API получены; сохранение snapshot не завершено.",
                "row_count": _result_row_count(value),
                "snapshot_started_at": started,
            }
            return value
        except Exception as error:
            payload = _failed_capability(name, error, token=token)
            capabilities[name] = payload
            errors.append(f"{name}: {_text(payload.get('safe_message'))}")
            return default

    def complete_snapshot(name: str) -> None:
        payload = capabilities.get(name, {})
        if payload.get("status") == "pending":
            payload.update({
                "status": "available",
                "safe_message": "Данные WB API получены и snapshot сохранён.",
            })

    def fail_pending_snapshots() -> None:
        for name, payload in capabilities.items():
            if payload.get("status") != "pending":
                continue
            message = f"WB {name}: полученный ответ не удалось сохранить как целостный snapshot."
            payload.update({
                "status": "error",
                "safe_message": message,
                "persisted_row_count": 0,
            })
            errors.append(f"{name}: {message}")

    def add_date_coverage(name: str, history_days: int, *, basis: str) -> None:
        payload = capabilities.get(name, {})
        if payload.get("status") != "pending":
            return
        coverage_end = local_now().date()
        payload.update({
            "coverage_start_date": (coverage_end - timedelta(days=history_days)).isoformat(),
            "coverage_end_date": coverage_end.isoformat(),
            "coverage_complete": True,
            "coverage_basis": basis,
            "outside_coverage_status": "partial",
        })

    def block_on_catalog(name: str) -> None:
        capabilities[name] = {
            "status": "unavailable",
            "safe_message": f"Раздел «{name}» не синхронизирован: нет подтверждённого snapshot каталога.",
            "row_count": 0,
            "dependency": "catalog",
        }

    def mark_incomplete_snapshot(name: str, raw_rows: int, persisted_rows: int) -> None:
        payload = capabilities.get(name, {})
        if payload.get("status") != "available" or persisted_rows >= raw_rows:
            return
        unmatched_rows = max(0, raw_rows - persisted_rows)
        message = (
            f"WB {name}: {unmatched_rows} из {raw_rows} строк не сопоставлены "
            "с подтверждённым snapshot каталога."
        )
        payload.update({
            "status": "partial",
            "safe_message": message,
            "row_count": raw_rows,
            "persisted_row_count": persisted_rows,
            "unmatched_row_count": unmatched_rows,
        })
        errors.append(f"{name}: {message}")

    try:
        cards = safe("catalog", client.cards, [])
        flattened = _flatten_cards(cards)
        now = _now()
        product_ids = {}
        for row in flattened:
            pid = _upsert_product(conn, account_id, row, now)
            product_ids[(row["sku"], row["size"])] = pid
            if row["barcode"]:
                product_ids[("barcode", row["barcode"])] = pid
            product_ids[("external", row["external_product_id"])] = pid
        counts["products"] = len(flattened)
        links = sync_production_links(conn, account_id)
        conn.commit()
        complete_snapshot("catalog")

        catalog_available = capabilities.get("catalog", {}).get("status") == "available"
        if catalog_available:
            prices = safe("prices", client.prices, [])
        else:
            prices = []
            block_on_catalog("prices")
        raw_price_rows = 0
        for item in prices:
            nm_id = _text(item.get("nmID"))
            for size_row in item.get("sizes") or [{}]:
                raw_price_rows += 1
                size = _text(size_row.get("techSize") or size_row.get("wbSize")) or "Не указан"
                pid = product_ids.get(("external", _text(size_row.get("sizeID") or size_row.get("chrtID")))) or product_ids.get((nm_id, size))
                if not pid:
                    continue
                conn.execute(
                    "INSERT INTO marketplace_prices (product_id,current_price,old_price,marketing_price,currency,payload_json,observed_at) VALUES (?,?,?,?,?,?,?)",
                    (pid,_number(size_row.get("discountedPrice") or size_row.get("price")),_number(size_row.get("price") or size_row.get("basicPrice")),None,"RUB",_json({**item,"size":size_row}),now),
                )
                counts["prices"] += 1
        conn.commit()
        complete_snapshot("prices")
        mark_incomplete_snapshot("prices", raw_price_rows, counts["prices"])

        if catalog_available:
            stocks = safe("stocks", client.stocks, [])
        else:
            stocks = []
            block_on_catalog("stocks")
        for item in stocks:
            pid = product_ids.get(("external", _text(item.get("chrtId")))) or product_ids.get(("barcode", _text(item.get("barcode")))) or product_ids.get((_text(item.get("nmId")), _text(item.get("techSize")) or "Не указан"))
            if not pid:
                continue
            available = max(0, _int(item.get("quantity")))
            reserved = max(0, _int(item.get("inWayToClient")))
            conn.execute(
                "INSERT INTO marketplace_stocks (product_id,warehouse_type,warehouse_name,stock,reserved,available,payload_json,observed_at) VALUES (?,?,?,?,?,?,?,?)",
                (pid,"fbw",_text(item.get("warehouseName")) or "Склад Wildberries",available+reserved,reserved,available,_json(item),now),
            )
            counts["stocks"] += 1
        conn.commit()
        complete_snapshot("stocks")
        mark_incomplete_snapshot("stocks", len(stocks), counts["stocks"])

        if catalog_available:
            chrt_ids = sorted({
                _int(row.get("external_product_id"))
                for row in flattened
                if _int(row.get("external_product_id"))
            })
            fbs_stocks = safe("fbs_stocks", lambda: client.fbs_stocks(chrt_ids), [])
        else:
            fbs_stocks = []
            block_on_catalog("fbs_stocks")
        for item in fbs_stocks:
            pid = product_ids.get(("external", _text(item.get("chrtId"))))
            if not pid:
                continue
            available = max(0, _int(item.get("amount")))
            conn.execute(
                "INSERT INTO marketplace_stocks (product_id,warehouse_type,warehouse_name,stock,reserved,available,payload_json,observed_at) VALUES (?,?,?,?,?,?,?,?)",
                (pid,"fbs",_text(item.get("warehouseName")) or "Склад продавца WB",available,0,available,_json(item),now),
            )
            counts["fbs_stocks"] += 1
        conn.commit()
        complete_snapshot("fbs_stocks")
        mark_incomplete_snapshot("fbs_stocks", len(fbs_stocks), counts["fbs_stocks"])

        orders = safe("orders", client.orders, [])
        add_date_coverage("orders", WB_ORDERS_HISTORY_DAYS, basis="last_change_date")
        for index,item in enumerate(orders):
            external_id = _text(item.get("srid") or item.get("gNumber") or f"wb-order-{index}-{item.get('date','')}")
            status = "cancelled" if item.get("isCancel") else "ordered"
            conn.execute(
                """INSERT INTO marketplace_orders (account_id,external_order_id,posting_number,warehouse_type,status,shipment_date,payload_json,updated_at)
                   VALUES (?,?,?,?,?,?,?,?) ON CONFLICT(account_id,external_order_id) DO UPDATE SET
                   posting_number=excluded.posting_number,status=excluded.status,shipment_date=excluded.shipment_date,
                   payload_json=excluded.payload_json,updated_at=excluded.updated_at""",
                (account_id,external_id,_text(item.get("gNumber")),"FBW",status,_text(item.get("date")),_json(item),now),
            )
            order_id = conn.execute("SELECT id FROM marketplace_orders WHERE account_id=? AND external_order_id=?",(account_id,external_id)).fetchone()[0]
            conn.execute("DELETE FROM marketplace_order_items WHERE order_id=?",(order_id,))
            pid = product_ids.get(("barcode",_text(item.get("barcode"))))
            product = conn.execute("SELECT external_product_id,offer_id,sku,name FROM marketplace_products WHERE id=?",(pid,)).fetchone() if pid else None
            conn.execute(
                "INSERT INTO marketplace_order_items (order_id,external_product_id,offer_id,sku,name,quantity,payload_json) VALUES (?,?,?,?,?,?,?)",
                (order_id,product[0] if product else _text(item.get("chrtId")),product[1] if product else _text(item.get("supplierArticle")),product[2] if product else _text(item.get("nmId")),product[3] if product else _text(item.get("subject")),1,_json(item)),
            )
        counts["orders"] = len(orders)
        conn.commit()
        complete_snapshot("orders")

        sales = safe("sales", client.sales, [])
        add_date_coverage("sales", WB_SALES_HISTORY_DAYS, basis="last_change_date")
        counts["sales"] = len(sales)
        for index,item in enumerate(sales):
            if not item.get("isCancel") and "возврат" not in _text(item.get("saleID")).lower():
                continue
            external_id = _text(item.get("srid") or item.get("saleID") or f"wb-return-{index}")
            conn.execute(
                """INSERT INTO marketplace_returns
                   (account_id,external_id,scheme,status,posting_number,product_id,offer_id,sku,product_name,quantity,amount,returned_at,payload_json,updated_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(account_id,external_id) DO UPDATE SET
                   status=excluded.status,amount=excluded.amount,returned_at=excluded.returned_at,payload_json=excluded.payload_json,updated_at=excluded.updated_at""",
                (account_id,external_id,"WB","return",_text(item.get("gNumber")),_text(item.get("chrtId")),_text(item.get("supplierArticle")),_text(item.get("nmId")),_text(item.get("subject")),1,_number(item.get("finishedPrice") or item.get("priceWithDisc")),_text(item.get("date")),_json(item),now),
            )

        finance = safe("finance", client.finance, [])
        add_date_coverage("finance", WB_FINANCE_HISTORY_DAYS, basis="report_date")
        for index,item in enumerate(finance):
            accrual_date = _text(item.get("createDate") or item.get("saleDate") or item.get("rr_dt") or item.get("sale_dt") or item.get("create_dt"))[:10] or date.today().isoformat()
            external_id = _text(item.get("rrdId") or item.get("rrd_id") or f"wb-finance-{accrual_date}-{index}")
            conn.execute(
                """INSERT INTO marketplace_finance_accruals
                   (account_id,accrual_date,external_id,accrual_type,posting_number,sku,amount,currency,payload_json,updated_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?) ON CONFLICT(account_id,accrual_date,external_id) DO UPDATE SET
                   accrual_type=excluded.accrual_type,posting_number=excluded.posting_number,sku=excluded.sku,
                   amount=excluded.amount,payload_json=excluded.payload_json,updated_at=excluded.updated_at""",
                (account_id,accrual_date,external_id,_text(item.get("docTypeName") or item.get("supplier_oper_name") or item.get("doc_type_name")),_text(item.get("srid")),_text(item.get("nmId") or item.get("nm_id")),_number(_first_present(item, "forPay", "retailAmount", "ppvz_for_pay")),"RUB",_json(item),now),
            )
        counts["finance"] = len(finance)
        conn.commit()
        complete_snapshot("sales")
        complete_snapshot("finance")

        feedbacks = safe("feedbacks", client.feedbacks, [])
        counts["feedbacks"] = len(feedbacks)
        ratings = [_number(item.get("productValuation")) for item in feedbacks if _number(item.get("productValuation")) > 0]
        for index, item in enumerate(feedbacks):
            feedback_id = _text(item.get("id") or item.get("feedbackId") or f"wb-feedback-{index}-{item.get('createdDate','')}")
            product_details = item.get("productDetails") if isinstance(item.get("productDetails"), dict) else {}
            answer = item.get("answer") if isinstance(item.get("answer"), dict) else {}
            conn.execute(
                """INSERT INTO marketplace_wb_feedbacks
                   (account_id,feedback_id,nm_id,product_name,rating,text,answer_text,created_at,answered,payload_json,updated_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(account_id,feedback_id) DO UPDATE SET
                   nm_id=excluded.nm_id,product_name=excluded.product_name,rating=excluded.rating,
                   text=excluded.text,answer_text=excluded.answer_text,created_at=excluded.created_at,
                   answered=excluded.answered,payload_json=excluded.payload_json,updated_at=excluded.updated_at""",
                (
                    account_id, feedback_id,
                    _text(product_details.get("nmId") or item.get("nmId")),
                    _text(product_details.get("productName") or item.get("productName")),
                    _number(item.get("productValuation")), _text(item.get("text")),
                    _text(answer.get("text")), _text(item.get("createdDate")),
                    1 if answer or item.get("isAnswered") else 0, _json(item), now,
                ),
            )
        if ratings:
            conn.execute(
                """INSERT INTO marketplace_ratings (account_id,observed_date,rating,payload_json,updated_at)
                   VALUES (?,?,?,?,?) ON CONFLICT(account_id,observed_date) DO UPDATE SET
                   rating=excluded.rating,payload_json=excluded.payload_json,updated_at=excluded.updated_at""",
                (account_id,date.today().isoformat(),sum(ratings)/len(ratings),_json({"feedbacks":len(feedbacks)}),now),
            )

        supplies = safe("supplies", client.supplies, [])
        for supply in supplies:
            upsert_marketplace_supply(conn,supply,marketplace="wildberries",account_id=account_id)
        counts["supplies"] = len(supplies)

        funnel = safe("funnel", client.funnel, {"products": [], "history": []})
        if capabilities.get("funnel", {}).get("status") == "pending":
            for field in (
                "coverage_start_date",
                "coverage_end_date",
                "requested_coverage_start_date",
                "requested_coverage_end_date",
                "coverage_complete",
                "coverage_basis",
                "outside_coverage_status",
                "partial_reason",
            ):
                if field in funnel:
                    capabilities["funnel"][field] = funnel[field]
        funnel_day = local_now().date().isoformat()
        for item in funnel.get("products") or []:
            product = item.get("product") if isinstance(item.get("product"), dict) else item
            statistics = item.get("statistics") or item.get("statistic") or {}
            selected = statistics.get("selectedPeriod") or item.get("selectedPeriod") or statistics
            nm_id = _text(product.get("nmId") or product.get("nmID") or item.get("nmId") or item.get("nmID"))
            if not nm_id:
                continue
            conn.execute(
                """INSERT INTO marketplace_wb_funnel_daily
                   (account_id,report_date,nm_id,open_count,cart_count,order_count,order_sum,buyout_count,buyout_sum,payload_json,updated_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(account_id,report_date,nm_id) DO UPDATE SET
                   open_count=excluded.open_count,cart_count=excluded.cart_count,order_count=excluded.order_count,
                   order_sum=excluded.order_sum,buyout_count=excluded.buyout_count,buyout_sum=excluded.buyout_sum,
                   payload_json=excluded.payload_json,updated_at=excluded.updated_at""",
                (account_id,funnel_day,nm_id,_int(selected.get("openCount")),_int(selected.get("cartCount")),_int(selected.get("orderCount")),_number(selected.get("orderSum")),_int(selected.get("buyoutCount")),_number(selected.get("buyoutSum")),_json(item),now),
            )
            counts["funnel"] += 1
        history_totals = {}
        for group in funnel.get("history") or []:
            for row in group.get("history") or []:
                report_date = _text(row.get("date"))[:10]
                if not report_date:
                    continue
                total = history_totals.setdefault(report_date, {"openCount":0,"cartCount":0,"orderCount":0,"orderSum":0.0,"buyoutCount":0,"buyoutSum":0.0})
                for key in ("openCount","cartCount","orderCount","buyoutCount"):
                    total[key] += _int(row.get(key))
                for key in ("orderSum","buyoutSum"):
                    total[key] += _number(row.get(key))
        for report_date,total in history_totals.items():
            conn.execute(
                """INSERT INTO marketplace_wb_funnel_daily
                   (account_id,report_date,nm_id,open_count,cart_count,order_count,order_sum,buyout_count,buyout_sum,payload_json,updated_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(account_id,report_date,nm_id) DO UPDATE SET
                   open_count=excluded.open_count,cart_count=excluded.cart_count,order_count=excluded.order_count,
                   order_sum=excluded.order_sum,buyout_count=excluded.buyout_count,buyout_sum=excluded.buyout_sum,
                   payload_json=excluded.payload_json,updated_at=excluded.updated_at""",
                (account_id,report_date,"",total["openCount"],total["cartCount"],total["orderCount"],total["orderSum"],total["buyoutCount"],total["buyoutSum"],_json(total),now),
            )
        conn.commit()
        complete_snapshot("feedbacks")
        complete_snapshot("supplies")
        complete_snapshot("funnel")
        if capabilities.get("funnel", {}).get("status") == "available" and funnel.get("partial"):
            message = "WB funnel: загружено только безопасное API-окно до 7 дней из запрошенных 30."
            capabilities["funnel"].update({
                "status": "partial",
                "safe_message": message,
            })
            errors.append(f"funnel: {message}")

        advertising = safe("advertising", client.advertising, {"campaigns": [], "stats": [], "balance": {}})
        add_date_coverage("advertising", WB_ADVERTISING_HISTORY_DAYS, basis="report_date")
        for item in advertising.get("campaigns") or []:
            campaign_id = _text(item.get("advertId") or item.get("advert_id") or item.get("id"))
            if not campaign_id:
                continue
            conn.execute(
                """INSERT INTO marketplace_ad_campaigns
                   (account_id,marketplace,campaign_id,name,status,payment_type,daily_budget,payload_json,updated_at)
                   VALUES (?,?,?,?,?,?,?,?,?) ON CONFLICT(account_id,marketplace,campaign_id) DO UPDATE SET
                   name=excluded.name,status=excluded.status,payment_type=excluded.payment_type,
                   daily_budget=excluded.daily_budget,payload_json=excluded.payload_json,updated_at=excluded.updated_at""",
                (account_id,"wildberries",campaign_id,_text(item.get("name")),_text(item.get("status")),_text(item.get("paymentType") or item.get("payment_type")),_number(item.get("dailyBudget") or item.get("daily_budget")),_json(item),now),
            )
            counts["campaigns"] += 1
        for campaign in advertising.get("stats") or []:
            campaign_id = _text(campaign.get("advertId") or campaign.get("advert_id") or campaign.get("id"))
            for row in campaign.get("days") or campaign.get("stats") or []:
                report_date = _text(row.get("date"))[:10]
                if not report_date:
                    continue
                views = _int(row.get("views")); clicks = _int(row.get("clicks")); spend = _number(row.get("sum")); orders_count = _int(row.get("orders")); revenue = _number(row.get("sum_price") or row.get("sumPrice"))
                if not any((views,clicks,spend,orders_count,revenue)):
                    for app in row.get("apps") or []:
                        views += _int(app.get("views")); clicks += _int(app.get("clicks")); spend += _number(app.get("sum")); orders_count += _int(app.get("orders")); revenue += _number(app.get("sum_price") or app.get("sumPrice"))
                conn.execute(
                    """INSERT INTO marketplace_ad_daily
                       (account_id,marketplace,campaign_id,report_date,views,clicks,spend,orders,revenue,payload_json,updated_at)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(account_id,marketplace,campaign_id,report_date) DO UPDATE SET
                       views=excluded.views,clicks=excluded.clicks,spend=excluded.spend,orders=excluded.orders,
                       revenue=excluded.revenue,payload_json=excluded.payload_json,updated_at=excluded.updated_at""",
                    (account_id,"wildberries",campaign_id,report_date,views,clicks,spend,orders_count,revenue,_json(row),now),
                )
                counts["ad_days"] += 1
        balance = advertising.get("balance") or {}
        if capabilities.get("advertising", {}).get("status") == "pending" and any(
            key in balance for key in ("balance", "net", "bonus")
        ):
            conn.execute(
                """INSERT INTO marketplace_ad_balances
                   (account_id,marketplace,observed_date,balance,net,bonus,payload_json,updated_at)
                   VALUES (?,?,?,?,?,?,?,?) ON CONFLICT(account_id,marketplace,observed_date) DO UPDATE SET
                   balance=excluded.balance,net=excluded.net,bonus=excluded.bonus,payload_json=excluded.payload_json,updated_at=excluded.updated_at""",
                (account_id,"wildberries",date.today().isoformat(),_number(balance.get("balance")),_number(balance.get("net")),_number(balance.get("bonus")),_json(balance),now),
            )
        conn.commit()
        complete_snapshot("advertising")

        failed_capabilities = [
            name for name, payload in capabilities.items()
            if payload.get("status") != "available"
        ]
        # A successful empty catalog is a confirmed business zero, not a
        # transport error.  The capability state, rather than row truthiness,
        # determines whether the catalog call itself succeeded.
        catalog_available = capabilities.get("catalog", {}).get("status") == "available"
        status = "error" if not catalog_available else ("partial" if failed_capabilities else "success")
        error_message = " | ".join(errors)[:4000]
        finished = _now()
        _save_capabilities(conn, account_id, capabilities)
        conn.execute(
            "UPDATE marketplace_sync_runs SET status=?,products_count=?,prices_count=?,stocks_count=?,orders_count=?,error_message=?,finished_at=? WHERE id=?",
            (status,counts["products"],counts["prices"],counts["stocks"],counts["orders"],error_message,finished,run_id),
        )
        conn.execute(
            """UPDATE marketplace_accounts SET
                 last_sync_at=CASE WHEN ? THEN ? ELSE last_sync_at END,
                 last_error=?,updated_at=? WHERE id=?""",
            (1 if catalog_available else 0, finished, error_message, finished, account_id),
        )
        conn.commit()
        if status == "success":
            message = "Wildberries синхронизирован."
        elif status == "partial":
            message = f"Wildberries синхронизирован частично: недоступно разделов — {len(failed_capabilities)}."
        else:
            message = "Wildberries: каталог товаров не получен."
        return {
            "ok": status == "success",
            "status": status,
            "message": message,
            **counts,
            "links": links,
            "errors": errors,
            "capabilities": capabilities,
        }
    except Exception as error:
        conn.rollback()
        fail_pending_snapshots()
        message = _safe_error_message(error, token=token)
        if "sync" not in capabilities:
            capabilities["sync"] = _failed_capability("sync", error, token=token)
        _save_capabilities(conn, account_id, capabilities)
        finished = _now()
        conn.execute("UPDATE marketplace_sync_runs SET status='error',error_message=?,finished_at=? WHERE id=?",(message,finished,run_id))
        conn.execute("UPDATE marketplace_accounts SET last_error=?,updated_at=? WHERE id=?",(message,finished,account_id))
        conn.commit()
        return {"ok": False, "status": "error", "message": message, "capabilities": capabilities}
    finally:
        conn.close()


def dashboard(*, read_only: bool = False) -> dict:
    conn = get_db_connection(timeout=2) if read_only else get_db_connection()
    try:
        return _dashboard_with_connection(conn, read_only=read_only)
    finally:
        conn.close()


def _dashboard_with_connection(conn: sqlite3.Connection, *, read_only: bool) -> dict:
    from marketplaces import _marketplace_product_image, product_group_for

    conn.row_factory = sqlite3.Row
    token = os.getenv("WB_API_TOKEN", "").strip()
    account_row = conn.execute(
        "SELECT id FROM marketplace_accounts WHERE marketplace='wildberries' ORDER BY id LIMIT 1"
    ).fetchone()
    if not account_row:
        return {"ok": True, "configured": bool(token), "accounts": [], "summary": {"products": 0, "stock_rows": 0, "open_orders": 0}, "products_rows": [], "product_groups": [], "warehouses": [], "orders_rows": [], "sync_runs": [], "analytics": {}}
    account_id = int(account_row[0])
    capability_table_exists = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='marketplace_wb_capabilities'"
    ).fetchone()
    capability_rows = []
    if capability_table_exists:
        for source in conn.execute(
            """SELECT capability,status,safe_message,http_status,retry_after_seconds,row_count,checked_at,details_json
                 FROM marketplace_wb_capabilities WHERE account_id=? ORDER BY capability""",
            (account_id,),
        ):
            row = dict(source)
            try:
                details = json.loads(row.pop("details_json") or "{}")
            except (TypeError, json.JSONDecodeError):
                details = {}
            row["details"] = details
            for field in (
                "snapshot_started_at",
                "last_successful_snapshot_started_at",
                "coverage_start_date",
                "coverage_end_date",
                "requested_coverage_start_date",
                "requested_coverage_end_date",
                "coverage_complete",
                "coverage_basis",
                "outside_coverage_status",
                "partial_reason",
                "persisted_row_count",
                "unmatched_row_count",
                "dependency",
            ):
                if field in details:
                    row[field] = details[field]
            row["snapshot_started_at"] = _text(row.get("snapshot_started_at"))
            row["last_successful_snapshot_started_at"] = _text(
                row.get("last_successful_snapshot_started_at")
            )
            capability_rows.append(row)
    capability_statuses = {row["capability"]: row for row in capability_rows}

    def current_snapshot(name: str) -> tuple[str, bool]:
        payload = capability_statuses.get(name)
        if not payload:
            # Backward-compatible view before the first capability-aware sync.
            return "", True
        if payload.get("status") != "available":
            return WB_SNAPSHOT_SENTINEL, False
        marker = _text(payload.get("snapshot_started_at")) or _text(
            payload.get("last_successful_snapshot_started_at")
        )
        return (marker, True) if marker else (WB_SNAPSHOT_SENTINEL, False)

    catalog_snapshot_start, catalog_snapshot_usable = current_snapshot("catalog")
    price_snapshot_start, price_snapshot_usable = current_snapshot("prices")
    stock_snapshot_start, stock_snapshot_usable = current_snapshot("stocks")

    def coverage_payload(name: str) -> dict:
        payload = capability_statuses.get(name) or {}
        return {
            "status": _text(payload.get("status")) or "unknown",
            "coverage_start_date": _text(payload.get("coverage_start_date")) or None,
            "coverage_end_date": _text(payload.get("coverage_end_date")) or None,
            "coverage_complete": payload.get("coverage_complete"),
            "coverage_basis": _text(payload.get("coverage_basis")) or None,
            "outside_coverage_status": _text(payload.get("outside_coverage_status")) or None,
            "requested_coverage_start_date": _text(payload.get("requested_coverage_start_date")) or None,
            "requested_coverage_end_date": _text(payload.get("requested_coverage_end_date")) or None,
            "partial_reason": _text(payload.get("partial_reason")) or None,
        }

    def coverage_is_usable(name: str, allowed_statuses: set[str]) -> bool | None:
        payload = capability_statuses.get(name)
        if not payload:
            return None
        start = _text(payload.get("coverage_start_date"))
        end = _text(payload.get("coverage_end_date"))
        return bool(payload.get("status") in allowed_statuses and start and end and start <= end)

    def covered_rows(rows: list[dict], name: str, date_fields: tuple[str, ...], allowed_statuses: set[str]) -> list[dict]:
        usable = coverage_is_usable(name, allowed_statuses)
        if usable is None:
            return rows
        if not usable:
            return []
        payload = capability_statuses[name]
        start = _text(payload.get("coverage_start_date"))
        end = _text(payload.get("coverage_end_date"))
        result = []
        for row in rows:
            day = ""
            for field in date_fields:
                day = _text(row.get(field))[:10]
                if day:
                    break
            if day and start <= day <= end:
                result.append(row)
        return result
    rows = conn.execute(
        """SELECT p.id,p.external_product_id,p.name,p.offer_id,p.sku,p.barcode,p.size,p.color,p.payload_json,p.updated_at,
          (SELECT current_price FROM marketplace_prices WHERE product_id=p.id
             AND (?='' OR observed_at>=?) ORDER BY id DESC LIMIT 1) current_price,
          (SELECT old_price FROM marketplace_prices WHERE product_id=p.id
             AND (?='' OR observed_at>=?) ORDER BY id DESC LIMIT 1) old_price,
          COALESCE((SELECT SUM(available) FROM marketplace_stocks s WHERE s.product_id=p.id
             AND (?='' OR s.observed_at>=?) AND s.id IN
             (SELECT MAX(id) FROM marketplace_stocks GROUP BY product_id,warehouse_type,warehouse_name)),0) available,
          COALESCE(l.production_product_name,'') production_product_name,
          COALESCE(l.production_size,'') production_size,COALESCE(l.production_color,'') production_color,
          COALESCE(l.route_configured,0) route_configured
          FROM marketplace_products p LEFT JOIN marketplace_production_links l ON l.marketplace_product_id=p.id
          WHERE p.account_id=? AND (?='' OR p.updated_at>=?)
          ORDER BY p.name,p.color,CAST(p.size AS INTEGER),p.size""",
        (
            price_snapshot_start,
            price_snapshot_start,
            price_snapshot_start,
            price_snapshot_start,
            stock_snapshot_start,
            stock_snapshot_start,
            account_id,
            catalog_snapshot_start,
            catalog_snapshot_start,
        ),
    ).fetchall()
    products, groups = [], {}
    for source in rows:
        item = dict(source)
        if capability_statuses.get("stocks") and not stock_snapshot_usable:
            item["available"] = None
        item["image_url"] = _marketplace_product_image(item.pop("payload_json", ""))
        key,name = product_group_for(item.get("name"),item.get("offer_id"),item.get("sku"),item.get("barcode"),item.get("size"))
        item.update({"group_key":key,"group_name":name,"production_available":0,"production_linked":True,"production_stock_available":True,"warehouse_stocks":{}})
        for stock in conn.execute(
            """SELECT warehouse_name,available FROM marketplace_stocks
                WHERE product_id=? AND (?='' OR observed_at>=?)
                  AND id IN (SELECT MAX(id) FROM marketplace_stocks GROUP BY product_id,warehouse_type,warehouse_name)""",
            (item["id"], stock_snapshot_start, stock_snapshot_start),
        ):
            item["warehouse_stocks"][f"wb:{stock[0]}"] = _int(stock[1])
        products.append(item)
        group=groups.setdefault(key,{"key":key,"name":name,"products":0,"articles":set(),"available":0 if stock_snapshot_usable else None,"production_available":0,"production_linked_products":0,"production_stock_available":True,"prices":[]})
        group["products"]+=1
        if group["available"] is not None:
            group["available"]+=_int(item["available"])
        group["production_linked_products"]+=1
        group["articles"].add(item["offer_id"])
        if item.get("current_price") is not None: group["prices"].append(_number(item["current_price"]))
        if not group.get("image_url") and item.get("image_url"): group["image_url"]=item["image_url"]
    group_rows=[]
    for group in groups.values():
        prices=group.pop("prices"); group["articles"]=len(group["articles"]); group["price_min"]=min(prices) if prices else None; group["price_max"]=max(prices) if prices else None; group_rows.append(group)
    warehouses=[{"key":f"wb:{row[0]}","name":row[0]} for row in conn.execute("SELECT DISTINCT warehouse_name FROM marketplace_stocks WHERE product_id IN (SELECT id FROM marketplace_products WHERE account_id=?) AND (?='' OR observed_at>=?) AND trim(warehouse_name)<>'' ORDER BY warehouse_name",(account_id,stock_snapshot_start,stock_snapshot_start))]
    orders=[dict(row) for row in conn.execute("SELECT id,external_order_id,posting_number,status,shipment_date,updated_at FROM marketplace_orders WHERE account_id=? ORDER BY updated_at DESC",(account_id,))]
    if capability_statuses.get("orders") and capability_statuses["orders"].get("status") != "available":
        orders = []
    runs=[dict(row) for row in conn.execute("SELECT id,status,products_count,prices_count,stocks_count,orders_count,error_message,started_at,finished_at FROM marketplace_sync_runs WHERE account_id=? ORDER BY id DESC LIMIT 5",(account_id,))]
    account=conn.execute("SELECT account_name,last_sync_at,last_error FROM marketplace_accounts WHERE id=?",(account_id,)).fetchone()
    analytics=dashboard_extension(conn,account_id,ensure_schema_first=not read_only)
    finance_usable = coverage_is_usable("finance", {"available"})
    if capability_statuses.get("finance"):
        finance_snapshot_start, finance_snapshot_usable = current_snapshot("finance")
        finance_usable = bool(finance_usable and finance_snapshot_usable)
        if finance_usable:
            finance_coverage = capability_statuses["finance"]
            analytics["finance_daily"] = [dict(row) for row in conn.execute(
                """SELECT accrual_date AS date,
                          ROUND(SUM(CASE WHEN amount>0 THEN amount ELSE 0 END),2) AS revenue,
                          ROUND(SUM(amount),2) AS net,COUNT(*) AS records
                     FROM marketplace_finance_accruals
                    WHERE account_id=? AND updated_at>=?
                      AND accrual_date BETWEEN ? AND ?
                    GROUP BY accrual_date ORDER BY accrual_date""",
                (
                    account_id,
                    finance_snapshot_start,
                    finance_coverage["coverage_start_date"],
                    finance_coverage["coverage_end_date"],
                ),
            )]
        else:
            analytics["finance_daily"] = []
    else:
        analytics["finance_daily"] = covered_rows(
            analytics.get("finance_daily") or [], "finance", ("date",), {"available"},
        )
    if finance_usable is not None:
        # A completed empty interval is confirmed coverage, not missing data.
        analytics["finance_available"] = finance_usable
    if capability_statuses.get("sales") and capability_statuses["sales"].get("status") != "available":
        analytics["returns_rows"] = []
        analytics["returns_daily"] = []
    funnel_daily = [dict(row) for row in conn.execute(
        """SELECT report_date AS date,SUM(open_count) open_count,SUM(cart_count) cart_count,
                  SUM(order_count) order_count,SUM(order_sum) order_sum,SUM(buyout_count) buyout_count,
                  SUM(buyout_sum) buyout_sum
           FROM marketplace_wb_funnel_daily WHERE account_id=? AND nm_id=''
           GROUP BY report_date ORDER BY report_date""", (account_id,)
    )]
    funnel_products = [dict(row) for row in conn.execute(
        """SELECT nm_id,MAX(report_date) report_date,open_count,cart_count,order_count,order_sum,
                  buyout_count,buyout_sum
           FROM marketplace_wb_funnel_daily WHERE account_id=? AND nm_id<>''
           GROUP BY nm_id ORDER BY order_sum DESC LIMIT 1000""", (account_id,)
    )]
    funnel_daily = covered_rows(funnel_daily, "funnel", ("date",), {"available", "partial"})
    funnel_products = covered_rows(funnel_products, "funnel", ("report_date",), {"available", "partial"})
    campaigns = [dict(row) for row in conn.execute(
        "SELECT campaign_id,name,status,payment_type,daily_budget,updated_at FROM marketplace_ad_campaigns WHERE account_id=? AND marketplace='wildberries' ORDER BY updated_at DESC",
        (account_id,),
    )]
    advertising_daily = [dict(row) for row in conn.execute(
        """SELECT report_date AS date,SUM(views) views,SUM(clicks) clicks,SUM(spend) spend,
                  SUM(orders) orders,SUM(revenue) revenue
           FROM marketplace_ad_daily WHERE account_id=? AND marketplace='wildberries'
           GROUP BY report_date ORDER BY report_date""", (account_id,)
    )]
    advertising_usable = coverage_is_usable("advertising", {"available"})
    advertising_daily = covered_rows(
        advertising_daily, "advertising", ("date",), {"available"},
    )
    balance_row = conn.execute(
        "SELECT balance,net,bonus,observed_date FROM marketplace_ad_balances WHERE account_id=? AND marketplace='wildberries' ORDER BY observed_date DESC LIMIT 1",
        (account_id,),
    ).fetchone()
    if advertising_usable is False:
        campaigns = []
        balance_row = None
    advertising_summary = {
        "campaigns": len(campaigns),
        "active_campaigns": sum(1 for item in campaigns if str(item.get("status")) == "9"),
        "views": sum(_int(item.get("views")) for item in advertising_daily),
        "clicks": sum(_int(item.get("clicks")) for item in advertising_daily),
        "spend": sum(_number(item.get("spend")) for item in advertising_daily),
        "orders": sum(_int(item.get("orders")) for item in advertising_daily),
        "revenue": sum(_number(item.get("revenue")) for item in advertising_daily),
    }
    advertising_summary["ctr"] = round(advertising_summary["clicks"] * 100 / advertising_summary["views"], 2) if advertising_summary["views"] else 0
    advertising_summary["roas"] = round(advertising_summary["revenue"] / advertising_summary["spend"], 2) if advertising_summary["spend"] else 0
    feedback_table_exists = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='marketplace_wb_feedbacks'"
    ).fetchone()
    reviews = []
    review_total = None
    if feedback_table_exists:
        reviews = [dict(row) for row in conn.execute(
            """SELECT feedback_id,nm_id,product_name,rating,text,answer_text,created_at,answered
               FROM marketplace_wb_feedbacks WHERE account_id=?
               ORDER BY created_at DESC LIMIT 200""", (account_id,)
        )]
        review_total = conn.execute(
            "SELECT COUNT(*),AVG(NULLIF(rating,0)),SUM(CASE WHEN answered=0 THEN 1 ELSE 0 END) FROM marketplace_wb_feedbacks WHERE account_id=?",
            (account_id,),
        ).fetchone()
    analytics["sales_funnel_daily"] = funnel_daily
    analytics["sales_funnel_products"] = funnel_products
    analytics["advertising"] = {"summary": advertising_summary, "daily": advertising_daily, "campaigns": campaigns, "balance": dict(balance_row) if balance_row else {}}
    analytics["finance_status"] = coverage_payload("finance")["status"]
    analytics["finance_coverage"] = coverage_payload("finance")
    analytics["funnel_status"] = coverage_payload("funnel")["status"]
    analytics["funnel_coverage"] = coverage_payload("funnel")
    analytics["orders_status"] = coverage_payload("orders")["status"]
    analytics["orders_coverage"] = coverage_payload("orders")
    analytics["sales_status"] = coverage_payload("sales")["status"]
    analytics["sales_coverage"] = coverage_payload("sales")
    analytics["advertising_status"] = coverage_payload("advertising")["status"]
    analytics["advertising_coverage"] = coverage_payload("advertising")
    analytics["coverage"] = {
        name: coverage_payload(name)
        for name in ("orders", "sales", "finance", "funnel", "advertising")
    }
    analytics["reviews_rows"] = reviews
    analytics["reviews_summary"] = {
        "total": _int(review_total[0]) if review_total else 0,
        "rating": round(_number(review_total[1]), 2) if review_total and review_total[1] is not None else None,
        "unanswered": _int(review_total[2]) if review_total else 0,
    }
    def capability_available(name: str, fallback: bool) -> bool:
        payload = capability_statuses.get(name)
        return payload.get("status") == "available" if payload else fallback

    analytics["capability_rows"] = capability_rows
    analytics["capability_statuses"] = capability_statuses
    analytics["capabilities"] = {
        "catalog": capability_available("catalog", bool(products)),
        "prices": capability_available("prices", any(item.get("current_price") is not None for item in products)),
        "orders": capability_available("orders", bool(orders)),
        "sales": capability_available("sales", bool(analytics.get("returns_rows"))),
        "sales_funnel": capability_available("funnel", bool(funnel_daily or funnel_products)),
        "advertising": capability_available("advertising", bool(campaigns or advertising_daily or balance_row)),
        "reviews": capability_available("feedbacks", bool(reviews)),
        "stocks": capability_available("stocks", bool(warehouses)),
        "finance": capability_available("finance", bool(analytics.get("finance_daily"))),
        "supplies": capability_available("supplies", bool(analytics.get("supplies_rows"))),
    }
    stock_rows = (
        conn.execute(
            "SELECT COUNT(*) FROM marketplace_stocks WHERE product_id IN (SELECT id FROM marketplace_products WHERE account_id=?) AND (?='' OR observed_at>=?)",
            (account_id, stock_snapshot_start, stock_snapshot_start),
        ).fetchone()[0]
        if stock_snapshot_usable else None
    )
    return {"ok":True,"configured":bool(token),"accounts":[dict(account)] if account else [],"summary":{"products":len(products),"stock_rows":stock_rows,"open_orders":len(orders)},"products_rows":products,"product_groups":group_rows,"warehouses":warehouses,"orders_rows":orders,"sync_runs":runs,"analytics":analytics}
