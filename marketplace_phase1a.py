"""Orchestrate the authoritative PostgreSQL Ozon read model.

The feature flag still provides an instant code-path rollback without changing
or deleting the retained legacy SQLite marketplace data.
"""

from __future__ import annotations

from dataclasses import asdict
import os
import re
import threading
from typing import Any, Iterable

from marketplace_ozon_client import (
    OzonClientError,
    OzonPaginationError,
    OzonReadOnlyClient,
    Page,
    PageResult,
)
from marketplace_pg import DATASETS, MarketplacePGRepository, MarketplacePGUnavailable, RunContext, product_identity


FEATURE_FLAG = "MARKETPLACE_PHASE1A_ENABLED"
_SYNC_LOCK = threading.Lock()
_SYNC_STATE_LOCK = threading.Lock()
_SYNC_STATE: dict[str, Any] = {"running": False, "last_result": None}


VERIFIED_ENDPOINTS = (
    {
        "dataset": "capabilities",
        "method": "POST",
        "path": "/v1/roles",
        "pagination_kind": "none",
        "request_limit": None,
        "verified_at": "2026-08-02T00:00:00Z",
        "official_url": "https://docs.ozon.ru/api/seller/#operation/AccessAPI_RolesByToken",
        "notes": "Roles and reported methods are diagnostic; exact-vs-prefix method semantics are not assumed.",
    },
    {
        "dataset": "catalog",
        "method": "POST",
        "path": "/v3/product/list",
        "pagination_kind": "cursor",
        "request_limit": 1000,
        "verified_at": "2026-08-02T00:00:00Z",
        "official_url": "https://docs.ozon.ru/api/seller/#operation/ProductAPI_GetProductList",
        "notes": "Ozon names the cursor last_id; total is reconciled against unique products.",
    },
    {
        "dataset": "catalog_details",
        "method": "POST",
        "path": "/v3/product/info/list",
        "pagination_kind": "none",
        "request_limit": 1000,
        "verified_at": "2026-08-02T00:00:00Z",
        "official_url": "https://docs.ozon.ru/api/seller/#operation/ProductAPI_GetProductInfoList",
        "notes": "Only one identifier type is sent per batch; implementation uses product_id batches of 100.",
    },
    {
        "dataset": "catalog_attributes",
        "method": "POST",
        "path": "/v4/product/info/attributes",
        "pagination_kind": "cursor",
        "request_limit": 100,
        "verified_at": "2026-08-04T00:00:00Z",
        "official_url": "https://docs.ozon.ru/api/seller/#operation/ProductAPI_GetProductAttributesV4",
        "notes": "Product characteristics provide source colour and size without parsing seller articles.",
    },
    {
        "dataset": "prices",
        "method": "POST",
        "path": "/v5/product/info/prices",
        "pagination_kind": "cursor",
        "request_limit": 1000,
        "verified_at": "2026-08-02T00:00:00Z",
        "official_url": "https://docs.ozon.ru/api/seller/#operation/ProductAPI_GetProductInfoPrices",
        "notes": "The application builds its own change history; the API returns current prices.",
    },
    {
        "dataset": "stocks",
        "method": "POST",
        "path": "/v4/product/info/stocks",
        "pagination_kind": "cursor",
        "request_limit": 1000,
        "verified_at": "2026-08-02T00:00:00Z",
        "official_url": "https://docs.ozon.ru/api/seller/#operation/ProductAPI_GetProductInfoStocks",
        "notes": "Seller-scheme component of the combined stock snapshot.",
    },
    {
        "dataset": "stocks",
        "method": "POST",
        "path": "/v2/analytics/stock_on_warehouses",
        "pagination_kind": "offset",
        "request_limit": 100,
        "verified_at": "2026-08-04T07:25:00Z",
        "official_url": "https://docs.ozon.ru/api/seller/#operation/AnalyticsAPI_AnalyticsGetStockOnWarehousesV2",
        "notes": "FBO balances by Ozon warehouse; merged with seller-scheme stocks.",
    },
    {
        "dataset": "orders",
        "method": "POST",
        "path": "/v3/posting/fbs/list",
        "pagination_kind": "offset",
        "request_limit": 100,
        "verified_at": "2026-08-04T00:00:00Z",
        "official_url": "https://docs.ozon.ru/api/seller/#operation/PostingAPI_GetFbsPostingListV3",
        "notes": "Read-only retained FBS order history.",
    },
    {
        "dataset": "orders", "method": "POST", "path": "/v3/posting/fbo/list",
        "pagination_kind": "offset", "request_limit": 100,
        "verified_at": "2026-08-04T07:25:00Z",
        "official_url": "https://docs.ozon.ru/api/seller/#operation/PostingAPI_GetFboPostingListV3",
        "notes": "Read-only retained FBO order history.",
    },
    {
        "dataset": "returns", "method": "POST", "path": "/v1/returns/list",
        "pagination_kind": "cursor", "request_limit": 500,
        "verified_at": "2026-08-04T07:25:00Z",
        "official_url": "https://docs.ozon.ru/api/seller/#operation/ReturnsAPI_ReturnAPIGetReturnsList",
        "notes": "Returns retained in PostgreSQL with status history.",
    },
    {
        "dataset": "finance", "method": "POST", "path": "/v3/finance/transaction/list",
        "pagination_kind": "page", "request_limit": 1000,
        "verified_at": "2026-08-04T07:25:00Z",
        "official_url": "https://docs.ozon.ru/api/seller/#operation/FinanceAPI_FinanceTransactionListV3",
        "notes": "One-year financial transaction history, synchronized in bounded date windows.",
    },
    {
        "dataset": "rating", "method": "POST", "path": "/v1/rating/summary",
        "pagination_kind": "none", "request_limit": None,
        "verified_at": "2026-08-04T07:25:00Z",
        "official_url": "https://docs.ozon.ru/api/seller/#operation/RatingAPI_RatingSummaryV1",
        "notes": "Daily rating snapshots retained in PostgreSQL.",
    },
)


def phase1a_enabled() -> bool:
    return os.getenv(FEATURE_FLAG, "").strip().casefold() in {"1", "true", "yes", "on"}


def phase1a_configured() -> bool:
    return bool(os.getenv("OZON_CLIENT_ID", "").strip() and os.getenv("OZON_API_KEY", "").strip())


def account_key() -> str:
    value = os.getenv("OZON_ACCOUNT_KEY", "ozon-main").strip() or "ozon-main"
    return value if re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9._:-]{0,63}", value) else "ozon-main"


def account_name() -> str:
    return os.getenv("OZON_ACCOUNT_NAME", "Основной Ozon").strip() or "Основной Ozon"


def _env_float(name: str, default: float, *, minimum: float, maximum: float) -> float:
    try:
        value = float(os.getenv(name, str(default)) or default)
    except (TypeError, ValueError):
        value = default
    return min(maximum, max(minimum, value))


def _env_int(name: str, default: int, *, minimum: int, maximum: int) -> int:
    try:
        value = int(os.getenv(name, str(default)) or default)
    except (TypeError, ValueError):
        value = default
    return min(maximum, max(minimum, value))


def _client_from_environment() -> OzonReadOnlyClient:
    return OzonReadOnlyClient(
        os.getenv("OZON_CLIENT_ID", ""),
        os.getenv("OZON_API_KEY", ""),
        timeout=_env_float("OZON_READ_TIMEOUT_SECONDS", 25, minimum=1, maximum=120),
        min_interval=_env_float("OZON_READ_MIN_INTERVAL_SECONDS", 0.2, minimum=0, maximum=60),
        max_retries=_env_int("OZON_READ_MAX_RETRIES", 6, minimum=0, maximum=10),
        page_limit=_env_int("OZON_READ_PAGE_LIMIT", 1000, minimum=1, maximum=1000),
    )


def _capability_payload(raw: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        "roles": {
            "status": "available" if raw.get("available") else "unknown",
            "endpoint": raw.get("endpoint"),
            "role_names": raw.get("role_names") or [],
            "method_paths": raw.get("method_paths") or [],
            "method_semantics": "provider_reported_uninterpreted",
        },
        "stocks_fbo_complete": {
            "status": "unknown",
            "complete": False,
            "seller_scope": raw.get("stock_scope") or ["FBS", "rFBS", "FBP"],
            "message": "Ожидается combined-проверка seller-схем и FBO.",
        },
    }


def _capability_from_error(error: Exception) -> str:
    status = getattr(error, "status", None)
    return "permission_required" if status in (401, 403) else "error"


def _merge_catalog_page(
    client: OzonReadOnlyClient,
    page: Page,
    attributes_by_product: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    source_rows = [dict(item) for item in page.items]
    product_ids = [product_identity(row)[0] for row in source_rows if product_identity(row)[0]]
    details = client.product_details(product_ids)
    by_product: dict[str, dict[str, Any]] = {}
    by_offer: dict[str, dict[str, Any]] = {}
    for detail in details:
        external_id, offer_id, _sku = product_identity(detail)
        if external_id:
            by_product[external_id] = detail
        if offer_id:
            by_offer[offer_id] = detail
    merged: list[dict[str, Any]] = []
    for source in source_rows:
        external_id, offer_id, _sku = product_identity(source)
        detail = by_product.get(external_id) or by_offer.get(offer_id) or {}
        attribute_row = attributes_by_product.get(external_id, {})
        item = {**source, **detail}
        if isinstance(attribute_row.get("attributes"), list):
            item["attributes"] = attribute_row["attributes"]
        if not item.get("barcodes") and isinstance(attribute_row.get("barcodes"), list):
            item["barcodes"] = attribute_row["barcodes"]
        if external_id:
            item["product_id"] = external_id
        if offer_id and not item.get("offer_id"):
            item["offer_id"] = offer_id
        merged.append(item)
    return merged


def _persist_result(
    repository: MarketplacePGRepository,
    context: RunContext,
    result: PageResult,
    client: OzonReadOnlyClient,
    *,
    omit_last_page: bool = False,
) -> None:
    pages: Iterable[Page] = result.pages[:-1] if omit_last_page and result.pages else result.pages
    attributes_by_product: dict[str, dict[str, Any]] = {}
    if context.dataset == "catalog":
        for attribute_row in client.product_attributes():
            external_id, _offer_id, _sku = product_identity(attribute_row)
            if external_id:
                attributes_by_product[external_id] = attribute_row
    for page in pages:
        rows = (
            _merge_catalog_page(client, page, attributes_by_product)
            if context.dataset == "catalog"
            else [dict(item) for item in page.items]
        )
        repository.persist_page(
            context,
            local_page_number=page.number,
            request_cursor=page.request_cursor,
            response_cursor=page.next_cursor,
            rows=rows,
            retry_count=page.retries,
            expected_count=page.total if page.total is not None else result.total,
        )


def _dataset_result(
    repository: MarketplacePGRepository,
    client: OzonReadOnlyClient,
    account_id: int,
    dataset: str,
    trigger_kind: str,
) -> dict[str, Any]:
    context = repository.start_or_resume_run(account_id, dataset, trigger_kind)
    reader = getattr(client, {
        "catalog": "iter_catalog_pages",
        "prices": "iter_price_pages",
        "stocks": "iter_stock_pages",
        "orders": "iter_order_pages",
        "returns": "iter_return_pages",
        "finance": "iter_finance_pages",
        "rating": "iter_rating_pages",
    }[dataset])
    history_kwargs: dict[str, int] = {}
    if dataset == "orders":
        history_kwargs["history_days"] = 365 if trigger_kind == "manual" else 30
    elif dataset == "returns":
        history_kwargs["history_days"] = 730 if trigger_kind == "manual" else 90
    elif dataset == "finance":
        history_kwargs["history_days"] = 365 if trigger_kind == "manual" else 31

    def capability_updates(status: str, complete: bool, message: str) -> dict[str, dict[str, Any]]:
        names = (
            ("stocks_complete", "stocks_fbo_complete", "stocks_seller_schemes")
            if dataset == "stocks"
            else (dataset,)
        )
        return {
            name: {
                "status": status,
                "complete": complete,
                "scope_complete": complete,
                "message": message,
            }
            for name in names
        }

    try:
        result = reader(context.cursor, **history_kwargs)
        _persist_result(repository, context, result, client)
        unique_count = repository.run_unique_count(context)
        expected = result.total if result.total is not None else repository.run_expected_count(context)
        # The stocks endpoint returns one provider product row even when its
        # seller-stock collection is empty. Those products intentionally do
        # not become false zero stock rows, so transport completeness must be
        # reconciled against provider rows rather than normalized stock grains.
        reconciliation_count = (
            repository.run_received_count(context)
            if dataset == "stocks"
            else unique_count
        )
        reconciled = expected is None or reconciliation_count == expected
        status = "success" if result.complete and reconciled else "partial"
        reason = result.termination_reason if reconciled else "total_mismatch"
        run = repository.finish_run(
            context,
            status=status,
            unique_count=unique_count,
            expected_count=expected,
            termination_reason=reason,
            retry_count=result.retries,
            safe_error="" if status == "success" else "Provider totals could not be reconciled.",
        )
        repository.upsert_capabilities(
            account_id,
            capability_updates(
                "available" if status == "success" else "error",
                status == "success",
                "" if status == "success" else reason,
            ),
        )
        return {
            "dataset": dataset,
            "ok": status == "success",
            "status": status,
            "usable": status == "success",
            "run": run,
        }
    except OzonPaginationError as error:
        result = error.partial_result
        try:
            _persist_result(
                repository,
                context,
                result,
                client,
                omit_last_page=error.code == "repeated_cursor",
            )
        except Exception as persist_error:
            try:
                unique_count = repository.run_unique_count(context)
            except Exception:
                unique_count = 0
            try:
                saved_expected = repository.run_expected_count(context)
            except Exception:
                saved_expected = None
            expected = result.total if result.total is not None else saved_expected
            partial = unique_count > 0
            run = repository.fail_run(
                context,
                persist_error,
                retry_count=int(getattr(persist_error, "retries", result.retries) or 0),
                partial=partial,
                unique_count=unique_count,
                expected_count=expected,
                termination_reason="partial_persist_failed",
            )
            repository.upsert_capabilities(
                account_id,
                capability_updates(
                    _capability_from_error(persist_error),
                    False,
                    getattr(persist_error, "code", persist_error.__class__.__name__),
                ),
            )
            return {
                "dataset": dataset,
                "ok": False,
                "status": "partial" if partial else "failed",
                "usable": False,
                "run": run,
            }
        unique_count = repository.run_unique_count(context)
        expected = result.total if result.total is not None else repository.run_expected_count(context)
        run = repository.fail_run(
            context,
            error,
            retry_count=result.retries,
            partial=True,
            unique_count=unique_count,
            expected_count=expected,
            termination_reason=error.code,
        )
        repository.upsert_capabilities(
            account_id,
            capability_updates(
                _capability_from_error(error),
                False,
                getattr(error, "cause_code", "") or error.code,
            ),
        )
        return {"dataset": dataset, "ok": False, "status": "partial", "usable": False, "run": run}
    except Exception as error:
        retry_count = int(getattr(error, "retries", 0) or 0)
        unique_count = 0
        expected_count = None
        try:
            unique_count = repository.run_unique_count(context)
        except Exception:
            pass
        try:
            expected_count = repository.run_expected_count(context)
        except Exception:
            pass
        checkpoint_rejected = (
            context.resumed
            and getattr(error, "status", None) in (400, 404, 410, 422)
            and not bool(getattr(error, "retryable", False))
        )
        run = repository.fail_run(
            context,
            error,
            retry_count=retry_count,
            partial=unique_count > 0,
            unique_count=unique_count,
            expected_count=expected_count,
            termination_reason="checkpoint_rejected" if checkpoint_rejected else "transport_error",
        )
        repository.upsert_capabilities(
            account_id,
            capability_updates(
                _capability_from_error(error),
                False,
                getattr(error, "code", error.__class__.__name__),
            ),
        )
        return {"dataset": dataset, "ok": False, "status": "partial" if unique_count else "failed", "usable": False, "run": run}


def run_phase1a_sync(
    *,
    datasets: Iterable[str] | None = None,
    trigger_kind: str = "scheduled",
    client: OzonReadOnlyClient | None = None,
    repository: MarketplacePGRepository | None = None,
    require_enabled: bool = True,
) -> dict[str, Any]:
    """Synchronize the verified Phase 1A datasets into PostgreSQL."""
    if require_enabled and not phase1a_enabled():
        return {"ok": False, "code": "phase1a_disabled", "message": f"Включите {FEATURE_FLAG}=1 для PostgreSQL sync."}
    if client is None and not phase1a_configured():
        return {"ok": False, "code": "not_configured", "message": "Ozon read-only credentials are not configured."}
    raw_datasets = None if datasets is None or isinstance(datasets, (str, bytes)) else tuple(datasets)
    if datasets is not None and (raw_datasets is None or any(not isinstance(item, str) for item in raw_datasets)):
        return {"ok": False, "code": "invalid_dataset", "message": "Неизвестный PostgreSQL dataset."}
    requested = tuple(dict.fromkeys(item.strip() for item in raw_datasets)) if raw_datasets is not None else None
    if requested is not None and (not requested or any(dataset not in DATASETS for dataset in requested)):
        return {"ok": False, "code": "invalid_dataset", "message": "Неизвестный PostgreSQL dataset."}
    repository = repository or MarketplacePGRepository()
    client = client or _client_from_environment()
    account_id: int | None = None
    lock_acquired = False
    try:
        account_id = repository.ensure_account(account_key(), account_name())
        lock_acquired = repository.acquire_sync_lock(account_id)
        if not lock_acquired:
            return {"ok": False, "code": "already_running", "message": "Phase 1A уже выполняется другим worker-процессом."}
        repository.upsert_endpoint_registry(VERIFIED_ENDPOINTS)
        selected = requested or (
            repository.datasets_due(account_id)
            if trigger_kind == "scheduled"
            else DATASETS
        )
        if trigger_kind != "scheduled" or repository.capabilities_due(account_id):
            try:
                repository.upsert_capabilities(account_id, _capability_payload(client.capabilities()))
            except OzonClientError as error:
                repository.upsert_capabilities(
                    account_id,
                    {"roles": {"status": _capability_from_error(error), "message": error.code}},
                )
        if not selected:
            return {
                "ok": True, "status": "not_due", "read_only": True, "datasets": [],
                "message": "Phase 1A: все наборы данных свежее заданной cadence.",
            }
        results = [
            _dataset_result(repository, client, account_id, dataset, trigger_kind)
            for dataset in selected
        ]
        successful = sum(item["status"] == "success" for item in results)
        partial = sum(item["status"] == "partial" for item in results)
        return {
            "ok": all(item.get("usable", item.get("ok")) for item in results),
            "status": "success" if successful == len(results) else ("partial" if successful or partial else "failed"),
            "read_only": True,
            "datasets": results,
            "message": f"Phase 1A: успешно {successful} из {len(results)}; partial {partial}.",
        }
    except MarketplacePGUnavailable:
        return {"ok": False, "code": "postgres_unavailable", "message": "PostgreSQL schema marketplace недоступна; сохранённые SQLite-данные не изменены."}
    except OzonClientError as error:
        return {"ok": False, "code": error.code, "message": str(error), "read_only": True}
    finally:
        if lock_acquired and account_id is not None:
            repository.release_sync_lock(account_id)


def start_phase1a_sync(*, datasets: Iterable[str] | None = None) -> dict[str, Any]:
    """Start a non-blocking manual job, guarded against overlapping workers."""
    raw_datasets = None if datasets is None or isinstance(datasets, (str, bytes)) else tuple(datasets)
    if datasets is not None and (raw_datasets is None or any(not isinstance(item, str) for item in raw_datasets)):
        return {"ok": False, "accepted": False, "code": "invalid_dataset", "message": "Неизвестный PostgreSQL dataset."}
    selected = tuple(dict.fromkeys(item.strip() for item in raw_datasets)) if raw_datasets is not None else None
    if selected is not None and (not selected or any(item not in DATASETS for item in selected)):
        return {"ok": False, "accepted": False, "code": "invalid_dataset", "message": "Неизвестный PostgreSQL dataset."}
    if not phase1a_enabled():
        return {"ok": False, "accepted": False, "code": "phase1a_disabled", "message": f"Включите {FEATURE_FLAG}=1."}
    if not phase1a_configured():
        return {"ok": False, "accepted": False, "code": "not_configured", "message": "Ozon read-only credentials are not configured."}
    if not _SYNC_LOCK.acquire(blocking=False):
        return {"ok": True, "accepted": False, "code": "already_running", "message": "Phase 1A уже синхронизируется."}

    with _SYNC_STATE_LOCK:
        _SYNC_STATE.update({"running": True, "last_result": None})

    def worker() -> None:
        try:
            result = run_phase1a_sync(datasets=selected, trigger_kind="manual")
            with _SYNC_STATE_LOCK:
                _SYNC_STATE["last_result"] = result
        except Exception:
            with _SYNC_STATE_LOCK:
                _SYNC_STATE["last_result"] = {
                    "ok": False,
                    "code": "internal_error",
                    "message": "Phase 1A worker завершился с внутренней ошибкой.",
                }
        finally:
            with _SYNC_STATE_LOCK:
                _SYNC_STATE["running"] = False
            _SYNC_LOCK.release()

    threading.Thread(target=worker, name="marketplace-phase1a-sync", daemon=True).start()
    return {"ok": True, "accepted": True, "message": "Phase 1A запущена в фоне."}


def phase1a_data_quality() -> dict[str, Any]:
    enabled = phase1a_enabled()
    configured = phase1a_configured()
    with _SYNC_STATE_LOCK:
        worker = {"running": bool(_SYNC_STATE["running"]), "last_result": _SYNC_STATE["last_result"]}
    web_running = worker["running"]
    if not enabled:
        return {
            "ok": True,
            "phase1a": {"enabled": False, "configured": configured, "state": "disabled", "worker": worker},
            "message": f"PostgreSQL-контур выключен ({FEATURE_FLAG}=0); используется аварийный SQLite fallback.",
        }
    try:
        quality = MarketplacePGRepository().data_quality(account_key())
    except MarketplacePGUnavailable:
        quality = {"state": "unavailable", "datasets": [], "capabilities": [], "totals": {}}
    database_running = any(
        row.get("status") == "running" and int(row.get("age_seconds") or 0) <= 60 * 60
        for row in quality.get("datasets", [])
        if isinstance(row, dict)
    )
    worker["running"] = bool(worker["running"] or database_running)
    worker["source"] = "web" if web_running else ("postgres" if database_running else "idle")
    return {
        "ok": True,
        "phase1a": {"enabled": True, "configured": configured, **quality, "worker": worker},
        "read_only": True,
    }


def phase1a_products_page(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    if payload is not None and not isinstance(payload, dict):
        return {"ok": False, "code": "invalid_pagination", "message": "Параметры страницы должны быть объектом."}
    payload = payload or {}
    query = payload.get("query", "")
    include_archived = payload.get("include_archived", False)
    if not isinstance(query, str) or not isinstance(include_archived, bool):
        return {"ok": False, "code": "invalid_pagination", "message": "Некорректные параметры страницы товаров."}
    raw_page = payload.get("page", 1)
    raw_page_size = payload.get("page_size", 50)
    def page_integer(value: Any) -> int | None:
        if isinstance(value, int) and not isinstance(value, bool):
            return value
        if isinstance(value, str) and re.fullmatch(r"[0-9]+", value):
            try:
                return int(value)
            except (ValueError, OverflowError):
                return None
        return None

    page = page_integer(raw_page)
    page_size = page_integer(raw_page_size)
    if page is None or page_size is None:
        return {"ok": False, "code": "invalid_pagination", "message": "page и page_size должны быть целыми числами."}
    if not 1 <= page <= 100_000 or not 1 <= page_size <= 200:
        return {"ok": False, "code": "invalid_pagination", "message": "page должен быть 1..100000, page_size — 1..200."}
    if not phase1a_enabled():
        return {"ok": True, "available": False, "state": "disabled", "items": [], "total": None, "pages": None}
    try:
        page = MarketplacePGRepository().products_page(
            account_key(),
            query=query[:200],
            page=page,
            page_size=page_size,
            include_archived=include_archived,
        )
        return {"ok": True, "available": True, "state": "ready", **page}
    except MarketplacePGUnavailable:
        return {"ok": True, "available": False, "state": "unavailable", "items": [], "total": None, "pages": None}


def phase1a_dashboard() -> dict[str, Any]:
    if not phase1a_enabled():
        return {"ok": False, "code": "phase1a_disabled", "message": "PostgreSQL marketplace выключен."}
    try:
        return MarketplacePGRepository().dashboard(account_key())
    except MarketplacePGUnavailable:
        return {
            "ok": False,
            "code": "postgres_unavailable",
            "message": "Данные маркетплейса временно недоступны в PostgreSQL.",
            "read_only": True,
        }


def phase1a_warehouse_catalog() -> dict[str, Any]:
    if not phase1a_enabled():
        return {"ok": False, "code": "phase1a_disabled", "message": "PostgreSQL marketplace выключен."}
    try:
        return MarketplacePGRepository().warehouse_catalog(account_key())
    except MarketplacePGUnavailable:
        return {
            "ok": False,
            "code": "postgres_unavailable",
            "message": "Складской каталог временно недоступен в PostgreSQL.",
            "products": [],
        }


__all__ = [
    "FEATURE_FLAG",
    "VERIFIED_ENDPOINTS",
    "phase1a_data_quality",
    "phase1a_dashboard",
    "phase1a_enabled",
    "phase1a_products_page",
    "phase1a_warehouse_catalog",
    "run_phase1a_sync",
    "start_phase1a_sync",
]
