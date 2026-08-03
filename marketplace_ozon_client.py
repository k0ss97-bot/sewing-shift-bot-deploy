"""Reliable, read-only transport for the Ozon Seller API.

The module deliberately exposes only calls that read data.  Pagination returns
an explicit result object and fails closed when completeness cannot be proven.
It is independent from the legacy marketplace module so it can be used by the
PostgreSQL shadow sync without importing SQLite or application runtime state.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from email.utils import parsedate_to_datetime
from http.client import HTTPException, HTTPResponse
import json
import random
import socket
import threading
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


JSONDict = dict[str, Any]


@dataclass(frozen=True)
class Page:
    """One successfully received API page."""

    endpoint: str
    number: int
    request_cursor: str
    next_cursor: str
    items: tuple[JSONDict, ...]
    total: int | None
    retries: int

    @property
    def received_count(self) -> int:
        return len(self.items)


@dataclass(frozen=True)
class PageResult:
    """Complete or explicitly partial pagination outcome."""

    endpoint: str
    pages: tuple[Page, ...]
    items: tuple[JSONDict, ...]
    total: int | None
    termination_reason: str
    complete: bool
    next_cursor: str
    retries: int
    unique_count: int
    duplicate_count: int

    @property
    def page_count(self) -> int:
        return len(self.pages)

    @property
    def expected_count(self) -> int | None:
        return self.total

    @property
    def received_count(self) -> int:
        return len(self.items)


class OzonClientError(RuntimeError):
    """A secret-safe Ozon client failure.

    Payloads, response bodies, request headers and low-level exception text are
    intentionally never included in the message or attributes.
    """

    def __init__(
        self,
        message: str,
        *,
        code: str,
        endpoint: str = "",
        status: int | None = None,
        retryable: bool = False,
        retries: int = 0,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.endpoint = endpoint
        self.status = status
        self.retryable = retryable
        self.retries = retries


class OzonPaginationError(OzonClientError):
    """Pagination stopped without proof that all requested rows were read."""

    def __init__(
        self,
        *,
        code: str,
        endpoint: str,
        partial_result: PageResult,
        cause: OzonClientError | None = None,
    ) -> None:
        super().__init__(
            f"Ozon pagination is incomplete for {endpoint} ({code}).",
            code=code,
            endpoint=endpoint,
            status=cause.status if cause is not None else None,
            retryable=cause.retryable if cause is not None else code == "page_request_failed",
            retries=partial_result.retries,
        )
        self.cause_code = cause.code if cause is not None else ""
        self.partial_result = partial_result


class OzonCircuitOpenError(OzonClientError):
    """Requests are temporarily blocked after repeated provider failures."""


class MinIntervalRateLimiter:
    """Thread-safe scheduler shared by all calls made through one client."""

    def __init__(
        self,
        min_interval: float,
        *,
        monotonic: Callable[[], float] = time.monotonic,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        if min_interval < 0:
            raise ValueError("min_interval must not be negative")
        self._min_interval = float(min_interval)
        self._monotonic = monotonic
        self._sleeper = sleeper
        self._lock = threading.Lock()
        self._next_slot = 0.0

    def wait(self) -> None:
        """Reserve one request slot, then wait outside the scheduler lock."""

        with self._lock:
            now = self._monotonic()
            slot = max(now, self._next_slot)
            self._next_slot = slot + self._min_interval
        delay = slot - now
        if delay > 0:
            self._sleeper(delay)


class _CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int,
        recovery_timeout: float,
        *,
        monotonic: Callable[[], float],
    ) -> None:
        if failure_threshold < 1:
            raise ValueError("circuit_failure_threshold must be positive")
        if recovery_timeout < 0:
            raise ValueError("circuit_recovery_timeout must not be negative")
        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout
        self._monotonic = monotonic
        self._lock = threading.Lock()
        self._failures = 0
        self._open_until = 0.0
        self._half_open_probe = False

    def before_request(self, endpoint: str) -> None:
        with self._lock:
            now = self._monotonic()
            if self._open_until > now:
                raise OzonCircuitOpenError(
                    f"Ozon circuit is temporarily open for {endpoint}.",
                    code="circuit_open",
                    endpoint=endpoint,
                    retryable=True,
                )
            if self._open_until:
                if self._half_open_probe:
                    raise OzonCircuitOpenError(
                        f"Ozon circuit recovery probe is already running for {endpoint}.",
                        code="circuit_open",
                        endpoint=endpoint,
                        retryable=True,
                    )
                self._half_open_probe = True

    def record_success(self) -> None:
        with self._lock:
            self._failures = 0
            self._open_until = 0.0
            self._half_open_probe = False

    def record_failure(self) -> None:
        with self._lock:
            self._failures += 1
            if self._half_open_probe or self._failures >= self._failure_threshold:
                self._open_until = self._monotonic() + self._recovery_timeout
            self._half_open_probe = False


@dataclass(frozen=True)
class _RequestResult:
    payload: JSONDict
    retries: int


@dataclass(frozen=True)
class _PaginationSpec:
    endpoint: str
    cursor_request_field: str
    cursor_response_fields: tuple[str, ...]
    item_fields: tuple[str, ...] = ("items", "products")


class OzonReadOnlyClient:
    """Unified Ozon client containing only explicitly allow-listed reads."""

    base_url = "https://api-seller.ozon.ru"
    _READ_ENDPOINTS = {
        "/v1/roles": "POST",
        "/v3/product/list": "POST",
        "/v3/product/info/list": "POST",
        "/v5/product/info/prices": "POST",
        "/v4/product/info/stocks": "POST",
    }
    _CATALOG = _PaginationSpec(
        endpoint="/v3/product/list",
        cursor_request_field="last_id",
        cursor_response_fields=("last_id", "cursor"),
    )
    _PRICES = _PaginationSpec(
        endpoint="/v5/product/info/prices",
        cursor_request_field="cursor",
        cursor_response_fields=("cursor", "last_id"),
    )
    _STOCKS = _PaginationSpec(
        endpoint="/v4/product/info/stocks",
        cursor_request_field="cursor",
        cursor_response_fields=("cursor", "last_id"),
    )

    def __init__(
        self,
        client_id: str,
        api_key: str,
        *,
        timeout: float = 25.0,
        min_interval: float = 0.2,
        max_retries: int = 3,
        backoff_base: float = 0.5,
        backoff_cap: float = 8.0,
        jitter_ratio: float = 0.25,
        circuit_failure_threshold: int = 5,
        circuit_recovery_timeout: float = 30.0,
        pagination_page_cap: int = 1_000,
        page_limit: int = 100,
        rate_limiter: MinIntervalRateLimiter | None = None,
        opener: Callable[..., HTTPResponse] | None = None,
        sleeper: Callable[[float], None] | None = None,
        monotonic: Callable[[], float] | None = None,
        wall_clock: Callable[[], float] | None = None,
        random_value: Callable[[], float] | None = None,
    ) -> None:
        normalized_client_id = str(client_id).strip()
        normalized_api_key = str(api_key).strip()
        if not normalized_client_id or not normalized_api_key:
            raise OzonClientError(
                "Ozon credentials are not configured.",
                code="not_configured",
            )
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        if max_retries < 0:
            raise ValueError("max_retries must not be negative")
        if backoff_base < 0 or backoff_cap < 0:
            raise ValueError("backoff values must not be negative")
        if not 0 <= jitter_ratio <= 1:
            raise ValueError("jitter_ratio must be between zero and one")
        if pagination_page_cap < 1:
            raise ValueError("pagination_page_cap must be positive")
        if not 1 <= page_limit <= 1_000:
            raise ValueError("page_limit must be between 1 and 1000")

        self._client_id = normalized_client_id
        self._api_key = normalized_api_key
        self._timeout = float(timeout)
        self._max_retries = max_retries
        self._backoff_base = float(backoff_base)
        self._backoff_cap = float(backoff_cap)
        self._jitter_ratio = float(jitter_ratio)
        self._pagination_page_cap = pagination_page_cap
        self._page_limit = page_limit
        self._opener = opener or urlopen
        self._sleeper = sleeper or time.sleep
        self._monotonic = monotonic or time.monotonic
        self._wall_clock = wall_clock or time.time
        self._random_value = random_value or random.random
        self._rate_limiter = rate_limiter or MinIntervalRateLimiter(
            min_interval,
            monotonic=self._monotonic,
            sleeper=self._sleeper,
        )
        self._circuit = _CircuitBreaker(
            circuit_failure_threshold,
            circuit_recovery_timeout,
            monotonic=self._monotonic,
        )

    def roles(self) -> JSONDict:
        """Return the official role response without auth headers or secrets."""

        return self._request("/v1/roles", {}, method="POST").payload

    def capabilities(self) -> JSONDict:
        """Return a conservative, role-derived read-only capability summary."""

        response = self.roles()
        role_values = _extract_roles_strict(response)
        role_names: list[str] = []
        method_paths: list[str] = []
        for role in role_values:
            if isinstance(role, str):
                name = role.strip()
            elif isinstance(role, Mapping):
                name = _as_text(
                    role.get("name")
                    or role.get("role")
                    or role.get("title")
                    or role.get("code")
                )
            else:
                raise _invalid_roles_response()
            if name and name not in role_names:
                role_names.append(name)
            if isinstance(role, Mapping):
                methods = role.get("methods")
                if methods is None:
                    methods = []
                if not isinstance(methods, list):
                    raise _invalid_roles_response()
                for method in methods:
                    if isinstance(method, str):
                        path = method.strip()
                    elif isinstance(method, Mapping):
                        path = _as_text(method.get("path") or method.get("method") or method.get("name"))
                    else:
                        raise _invalid_roles_response()
                    if path and path not in method_paths:
                        method_paths.append(path)
        lowered = " ".join(role_names).lower()
        return {
            "endpoint": "/v1/roles",
            "available": True,
            "role_names": role_names,
            "method_paths": method_paths,
            "method_semantics": "provider_reported_uninterpreted",
            "admin_read_only": "admin read only" in lowered,
            "notification": "notification" in lowered,
            "stock_scope": ["FBS", "rFBS", "FBP"],
            "fbo_stock_complete": False,
        }

    def iter_catalog_pages(
        self,
        start_cursor: str = "",
        *,
        max_pages: int | None = None,
    ) -> PageResult:
        """Read every catalog page using Ozon's ``last_id`` checkpoint."""

        return self._paginate(self._CATALOG, start_cursor, max_pages=max_pages)

    def iter_price_pages(
        self,
        start_cursor: str = "",
        *,
        max_pages: int | None = None,
    ) -> PageResult:
        """Read every current-price page using its cursor."""

        return self._paginate(self._PRICES, start_cursor, max_pages=max_pages)

    def iter_stock_pages(
        self,
        start_cursor: str = "",
        *,
        max_pages: int | None = None,
    ) -> PageResult:
        """Read every current-stock page using its cursor."""

        return self._paginate(self._STOCKS, start_cursor, max_pages=max_pages)

    def product_details(self, product_ids: Iterable[str | int]) -> list[JSONDict]:
        """Read product details in allow-listed batches of at most 100 IDs."""

        unique_ids: list[str] = []
        seen: set[str] = set()
        for value in product_ids:
            if isinstance(value, bool) or value is None:
                continue
            normalized = str(value).strip()
            if normalized and normalized not in seen:
                seen.add(normalized)
                unique_ids.append(normalized)

        details: list[JSONDict] = []
        for offset in range(0, len(unique_ids), 100):
            batch = unique_ids[offset : offset + 100]
            response = self._request(
                "/v3/product/info/list",
                {"product_id": batch},
                method="POST",
            ).payload
            batch_details = _extract_items_strict(
                response,
                ("items", "products"),
                endpoint="/v3/product/info/list",
            )
            returned_ids = {
                _as_text(item.get("id") or item.get("product_id"))
                for item in batch_details
                if _as_text(item.get("id") or item.get("product_id"))
            }
            if any(product_id not in returned_ids for product_id in batch):
                raise OzonClientError(
                    "Ozon returned an incomplete product-details batch.",
                    code="details_incomplete",
                    endpoint="/v3/product/info/list",
                )
            details.extend(batch_details)
        return details

    def _paginate(
        self,
        spec: _PaginationSpec,
        start_cursor: str,
        *,
        max_pages: int | None,
    ) -> PageResult:
        cursor = _as_text(start_cursor)
        resume_mode = bool(cursor)
        page_cap = self._pagination_page_cap if max_pages is None else max_pages
        if page_cap < 1:
            raise ValueError("max_pages must be positive")
        page_cap = min(page_cap, self._pagination_page_cap)

        pages: list[Page] = []
        all_items: list[JSONDict] = []
        seen_cursors = {cursor} if cursor else set()
        observed_total: int | None = None
        total_retries = 0

        for page_number in range(1, page_cap + 1):
            payload: JSONDict = {
                "filter": {"visibility": "ALL"},
                "limit": self._page_limit,
            }
            if cursor:
                payload[spec.cursor_request_field] = cursor

            try:
                request_result = self._request(spec.endpoint, payload, method="POST")
                page_items = _extract_items_strict(
                    request_result.payload,
                    spec.item_fields,
                    endpoint=spec.endpoint,
                )
            except OzonClientError as error:
                if not pages:
                    raise
                partial_result = self._page_result(
                    spec.endpoint,
                    pages,
                    all_items,
                    observed_total,
                    "page_request_failed",
                    False,
                    cursor,
                    total_retries + error.retries,
                )
                raise OzonPaginationError(
                    code="page_request_failed",
                    endpoint=spec.endpoint,
                    partial_result=partial_result,
                    cause=error,
                ) from error

            next_cursor = _extract_cursor(
                request_result.payload,
                spec.cursor_response_fields,
            )
            page_total = _extract_total(request_result.payload)
            if page_total is not None:
                observed_total = page_total
            total_retries += request_result.retries
            all_items.extend(page_items)
            pages.append(
                Page(
                    endpoint=spec.endpoint,
                    number=page_number,
                    request_cursor=cursor,
                    next_cursor=next_cursor,
                    items=tuple(page_items),
                    total=page_total,
                    retries=request_result.retries,
                )
            )

            unique_count = _unique_item_count(all_items)
            if not page_items and not next_cursor:
                if not resume_mode and observed_total is not None and unique_count != observed_total:
                    self._raise_partial(
                        "total_mismatch",
                        spec.endpoint,
                        pages,
                        all_items,
                        observed_total,
                        "",
                        total_retries,
                    )
                reason = "resumed_empty_page" if resume_mode else "empty_page"
                return self._page_result(
                    spec.endpoint,
                    pages,
                    all_items,
                    observed_total,
                    reason,
                    True,
                    "",
                    total_retries,
                )

            if next_cursor:
                if next_cursor == cursor or next_cursor in seen_cursors:
                    self._raise_partial(
                        "repeated_cursor",
                        spec.endpoint,
                        pages,
                        all_items,
                        observed_total,
                        next_cursor,
                        total_retries,
                    )
                if page_number >= page_cap:
                    self._raise_partial(
                        "safety_cap",
                        spec.endpoint,
                        pages,
                        all_items,
                        observed_total,
                        next_cursor,
                        total_retries,
                    )
                seen_cursors.add(next_cursor)
                cursor = next_cursor
                # Cursor presence is authoritative: even a short page may have
                # a subsequent page and therefore must not end pagination.
                continue

            if not resume_mode and observed_total is not None and unique_count == observed_total:
                return self._page_result(
                    spec.endpoint,
                    pages,
                    all_items,
                    observed_total,
                    "total_reached",
                    True,
                    "",
                    total_retries,
                )
            if resume_mode and observed_total is not None:
                # The returned total describes the whole collection, while
                # this result contains only the tail after ``start_cursor``.
                # An exhausted official cursor completes that tail; the
                # repository reconciles it together with committed pages.
                return self._page_result(
                    spec.endpoint,
                    pages,
                    all_items,
                    observed_total,
                    "resumed_cursor_exhausted",
                    True,
                    "",
                    total_retries,
                )
            if len(page_items) < self._page_limit:
                if not resume_mode and observed_total is not None and unique_count != observed_total:
                    self._raise_partial(
                        "total_mismatch",
                        spec.endpoint,
                        pages,
                        all_items,
                        observed_total,
                        "",
                        total_retries,
                    )
                reason = "empty_page" if not page_items else "short_page"
                if resume_mode:
                    reason = f"resumed_{reason}"
                return self._page_result(
                    spec.endpoint,
                    pages,
                    all_items,
                    observed_total,
                    reason,
                    True,
                    "",
                    total_retries,
                )

            # A full page with neither a next cursor nor a reconciled total is
            # not evidence of completion.  Return an explicit partial failure.
            code = (
                "missing_cursor_before_total"
                if observed_total is not None
                else "missing_cursor_full_page"
            )
            self._raise_partial(
                code,
                spec.endpoint,
                pages,
                all_items,
                observed_total,
                "",
                total_retries,
            )

        # The loop can only naturally finish if its implementation changes;
        # retain an explicit fail-closed guard for that case.
        self._raise_partial(
            "safety_cap",
            spec.endpoint,
            pages,
            all_items,
            observed_total,
            cursor,
            total_retries,
        )

    @staticmethod
    def _page_result(
        endpoint: str,
        pages: Sequence[Page],
        items: Sequence[JSONDict],
        total: int | None,
        termination_reason: str,
        complete: bool,
        next_cursor: str,
        retries: int,
    ) -> PageResult:
        unique_count = _unique_item_count(items)
        return PageResult(
            endpoint=endpoint,
            pages=tuple(pages),
            items=tuple(items),
            total=total,
            termination_reason=termination_reason,
            complete=complete,
            next_cursor=next_cursor,
            retries=retries,
            unique_count=unique_count,
            duplicate_count=len(items) - unique_count,
        )

    def _raise_partial(
        self,
        code: str,
        endpoint: str,
        pages: Sequence[Page],
        items: Sequence[JSONDict],
        total: int | None,
        next_cursor: str,
        retries: int,
    ) -> None:
        partial_result = self._page_result(
            endpoint,
            pages,
            items,
            total,
            code,
            False,
            next_cursor,
            retries,
        )
        raise OzonPaginationError(
            code=code,
            endpoint=endpoint,
            partial_result=partial_result,
        )

    def _request(
        self,
        endpoint: str,
        payload: Mapping[str, Any] | None = None,
        *,
        method: str,
    ) -> _RequestResult:
        normalized_method = method.upper()
        if self._READ_ENDPOINTS.get(endpoint) != normalized_method:
            raise OzonClientError(
                "Ozon endpoint is not present in the read-only allow-list.",
                code="endpoint_not_allowed",
                endpoint=endpoint if endpoint in self._READ_ENDPOINTS else "",
            )
        self._circuit.before_request(endpoint)

        body = None
        if normalized_method == "POST":
            body = json.dumps(
                dict(payload or {}),
                ensure_ascii=False,
                separators=(",", ":"),
            ).encode("utf-8")
        request = Request(
            f"{self.base_url}{endpoint}",
            data=body,
            method=normalized_method,
            headers={
                "Client-Id": self._client_id,
                "Api-Key": self._api_key,
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "marketplace-analytics-readonly/1.0",
            },
        )

        for attempt in range(self._max_retries + 1):
            self._rate_limiter.wait()
            try:
                with self._opener(request, timeout=self._timeout) as response:
                    raw = response.read(16 * 1024 * 1024 + 1)
                if len(raw) > 16 * 1024 * 1024:
                    self._circuit.record_failure()
                    raise OzonClientError(
                        f"Ozon response is too large for {endpoint}.",
                        code="response_too_large",
                        endpoint=endpoint,
                        retries=attempt,
                    )
                if not raw:
                    parsed: Any = {}
                else:
                    try:
                        parsed = json.loads(raw.decode("utf-8"))
                    except (UnicodeDecodeError, json.JSONDecodeError) as error:
                        self._circuit.record_failure()
                        raise OzonClientError(
                            f"Ozon returned invalid JSON for {endpoint}.",
                            code="invalid_response",
                            endpoint=endpoint,
                            retries=attempt,
                        ) from None
                if not isinstance(parsed, dict):
                    self._circuit.record_failure()
                    raise OzonClientError(
                        f"Ozon returned an unexpected response for {endpoint}.",
                        code="invalid_response",
                        endpoint=endpoint,
                        retries=attempt,
                    )
                self._circuit.record_success()
                return _RequestResult(parsed, attempt)
            except HTTPError as error:
                status = int(error.code)
                retryable = status in (408, 425, 429) or 500 <= status <= 599
                retry_after = _retry_after_seconds(error.headers, self._wall_clock)
                error.close()
                if retryable and attempt < self._max_retries:
                    self._sleep_before_retry(attempt, retry_after)
                    continue
                if retryable:
                    self._circuit.record_failure()
                else:
                    # A 4xx response proves the provider is reachable and
                    # must not leave a half-open circuit probe stuck.
                    self._circuit.record_success()
                code = (
                    "rate_limit"
                    if status == 429
                    else "provider_5xx"
                    if 500 <= status <= 599
                    else "authentication"
                    if status in (401, 403)
                    else "api_error"
                )
                raise OzonClientError(
                    f"Ozon request failed for {endpoint} with HTTP {status}.",
                    code=code,
                    endpoint=endpoint,
                    status=status,
                    retryable=retryable,
                    retries=attempt,
                ) from None
            except (URLError, HTTPException, TimeoutError, socket.timeout, ConnectionError, OSError) as error:
                if attempt < self._max_retries:
                    self._sleep_before_retry(attempt, None)
                    continue
                self._circuit.record_failure()
                is_timeout = isinstance(error, (TimeoutError, socket.timeout)) or (
                    isinstance(error, URLError)
                    and isinstance(error.reason, (TimeoutError, socket.timeout))
                )
                code = "timeout" if is_timeout else "network_error"
                raise OzonClientError(
                    f"Ozon network request failed for {endpoint} ({code}).",
                    code=code,
                    endpoint=endpoint,
                    retryable=True,
                    retries=attempt,
                ) from None

        raise AssertionError("unreachable retry loop")

    def _sleep_before_retry(self, attempt: int, retry_after: float | None) -> None:
        exponential = min(self._backoff_cap, self._backoff_base * (2**attempt))
        delay = max(exponential, retry_after or 0.0)
        jitter = delay * self._jitter_ratio * max(0.0, min(1.0, self._random_value()))
        self._sleeper(delay + jitter)


def _mapping_nodes(payload: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
    queue: list[Mapping[str, Any]] = [payload]
    while queue:
        node = queue.pop(0)
        yield node
        for key in ("result", "data"):
            child = node.get(key)
            if isinstance(child, Mapping):
                queue.append(child)


def _extract_sequence(
    payload: Mapping[str, Any],
    fields: Sequence[str],
) -> list[Any]:
    for node in _mapping_nodes(payload):
        for field in fields:
            value = node.get(field)
            if isinstance(value, list):
                return value
        result = node.get("result")
        if isinstance(result, list):
            return result
    return []


def _invalid_roles_response() -> OzonClientError:
    return OzonClientError(
        "Ozon returned an invalid capability collection for /v1/roles.",
        code="invalid_response",
        endpoint="/v1/roles",
    )


def _extract_roles_strict(payload: Mapping[str, Any]) -> list[Any]:
    """Extract roles without interpreting a missing or malformed response as access."""

    for node in _mapping_nodes(payload):
        for field in ("roles", "items"):
            if field not in node:
                continue
            values = node[field]
            if not isinstance(values, list):
                raise _invalid_roles_response()
            return list(values)
        if "result" in node and isinstance(node["result"], list):
            return list(node["result"])
    raise _invalid_roles_response()


def _extract_items(
    payload: Mapping[str, Any],
    fields: Sequence[str],
) -> list[JSONDict]:
    return [
        dict(value)
        for value in _extract_sequence(payload, fields)
        if isinstance(value, Mapping)
    ]


def _extract_items_strict(
    payload: Mapping[str, Any],
    fields: Sequence[str],
    *,
    endpoint: str,
) -> list[JSONDict]:
    """Extract a provider collection without treating a malformed shape as empty."""
    for node in _mapping_nodes(payload):
        for field in fields:
            if field not in node:
                continue
            values = node[field]
            if not isinstance(values, list) or any(not isinstance(value, Mapping) for value in values):
                raise OzonClientError(
                    f"Ozon returned an invalid item collection for {endpoint}.",
                    code="invalid_response",
                    endpoint=endpoint,
                )
            return [dict(value) for value in values]
        if "result" in node and isinstance(node["result"], list):
            values = node["result"]
            if any(not isinstance(value, Mapping) for value in values):
                raise OzonClientError(
                    f"Ozon returned an invalid item collection for {endpoint}.",
                    code="invalid_response",
                    endpoint=endpoint,
                )
            return [dict(value) for value in values]
    raise OzonClientError(
        f"Ozon response did not contain an item collection for {endpoint}.",
        code="invalid_response",
        endpoint=endpoint,
    )


def _extract_cursor(payload: Mapping[str, Any], fields: Sequence[str]) -> str:
    for node in _mapping_nodes(payload):
        for field in fields:
            value = _as_text(node.get(field))
            if value:
                return value
    return ""


def _extract_total(payload: Mapping[str, Any]) -> int | None:
    for node in _mapping_nodes(payload):
        for field in ("total", "total_count"):
            value = node.get(field)
            if isinstance(value, bool):
                continue
            if isinstance(value, int) and value >= 0:
                return value
            if isinstance(value, float) and value >= 0 and value.is_integer():
                return int(value)
            if isinstance(value, str) and value.strip().isdigit():
                return int(value.strip())
    return None


def _unique_item_count(items: Sequence[Mapping[str, Any]]) -> int:
    identities: set[str] = set()
    for index, item in enumerate(items):
        identity = ""
        for field in ("product_id", "id", "offer_id", "sku"):
            value = _as_text(item.get(field))
            if value:
                identity = f"{field}:{value}"
                break
        if not identity:
            try:
                identity = "json:" + json.dumps(
                    dict(item),
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                )
            except (TypeError, ValueError):
                # JSON responses should never reach this fallback, but keeping
                # the row distinct is safer than reporting a false duplicate.
                identity = f"unidentified:{index}"
        identities.add(identity)
    return len(identities)


def _as_text(value: Any) -> str:
    if value is None or isinstance(value, bool):
        return ""
    return str(value).strip()


def _retry_after_seconds(
    headers: Mapping[str, Any] | None,
    wall_clock: Callable[[], float],
) -> float | None:
    if headers is None:
        return None
    value = headers.get("Retry-After")
    if value is None:
        return None
    text = str(value).strip()
    try:
        return max(0.0, float(text))
    except ValueError:
        pass
    try:
        parsed = parsedate_to_datetime(text)
        return max(0.0, parsed.timestamp() - wall_clock())
    except (TypeError, ValueError, OverflowError):
        return None


__all__ = [
    "MinIntervalRateLimiter",
    "OzonCircuitOpenError",
    "OzonClientError",
    "OzonPaginationError",
    "OzonReadOnlyClient",
    "Page",
    "PageResult",
]
