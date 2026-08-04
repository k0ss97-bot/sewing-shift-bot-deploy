"""PostgreSQL repository for the authoritative read-only Ozon projection.

The module owns the additive ``marketplace`` schema introduced by migrations
005 and 006.  It never stores Ozon credentials or mutates provider state.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import json
from typing import Any, Iterable

from wms.connection import get_pg_connection


DATASETS = ("catalog", "prices", "stocks", "orders")
FRESHNESS_SECONDS = {
    "catalog": 2 * 60 * 60,
    "prices": 45 * 60,
    "stocks": 20 * 60,
    "orders": 20 * 60,
}
SYNC_CADENCE_SECONDS = {"catalog": 30 * 60, "prices": 15 * 60, "stocks": 5 * 60, "orders": 5 * 60}

OZON_COLOR_ATTRIBUTE_IDS = {10096}
OZON_SIZE_ATTRIBUTE_IDS = {4295, 9533, 4508}


class MarketplacePGUnavailable(RuntimeError):
    """The PostgreSQL marketplace projection cannot be read or written."""


@dataclass(frozen=True)
class RunContext:
    run_id: int
    account_id: int
    dataset: str
    cursor: str
    page_number: int
    resumed: bool


def _text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def _truthy_flag(value: Any) -> bool:
    if value is True or (isinstance(value, int) and not isinstance(value, bool) and value == 1):
        return True
    return isinstance(value, str) and value.strip().casefold() in {"1", "true", "yes", "on"}


def _decimal(value: Any) -> Decimal | None:
    if value is None or value == "":
        return None
    try:
        number = Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        return None
    try:
        return number if number.is_finite() and number >= 0 else None
    except InvalidOperation:
        return None


def _first_value(source: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = source.get(key)
        if value is not None and value != "":
            return value
    return None


def _timestamp(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return value
    text = _text(value)
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _json(value: Any) -> str:
    payload = value if isinstance(value, (dict, list)) else {}
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def _json_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(value, dict):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    return value


def _row_dict(row: Any, cursor: Any | None = None) -> dict[str, Any]:
    if row is None:
        return {}
    try:
        return dict(row)
    except (TypeError, ValueError):
        columns = [item[0] for item in (getattr(cursor, "description", None) or [])]
        return dict(zip(columns, row))


def product_identity(row: dict[str, Any]) -> tuple[str, str, str]:
    external_id = _text(row.get("product_id") or row.get("id"))
    offer_id = _text(row.get("offer_id") or row.get("offerId"))
    sku = _text(row.get("sku") or row.get("fbo_sku") or row.get("fbs_sku"))
    external_id = external_id or offer_id or sku
    return external_id, offer_id, sku


def _nested_text(value: Any, keys: tuple[str, ...]) -> str:
    if isinstance(value, dict):
        for key in keys:
            candidate = value.get(key)
            if candidate not in (None, "") and not isinstance(candidate, (dict, list)):
                return _text(candidate)
        for child in value.values():
            found = _nested_text(child, keys)
            if found:
                return found
    elif isinstance(value, list):
        for child in value:
            found = _nested_text(child, keys)
            if found:
                return found
    return ""


def _attribute_value(attributes: Any, identifiers: set[int]) -> str:
    for attribute in attributes if isinstance(attributes, list) else []:
        if not isinstance(attribute, dict):
            continue
        try:
            attribute_id = int(attribute.get("id"))
        except (TypeError, ValueError):
            continue
        if attribute_id not in identifiers:
            continue
        for value in attribute.get("values") or []:
            if isinstance(value, dict) and _text(value.get("value")):
                return _text(value["value"])
    return ""


def _product_image(row: dict[str, Any]) -> str:
    for field in ("primary_image", "images", "color_image", "images360"):
        value = row.get(field)
        for candidate in value if isinstance(value, list) else [value]:
            if isinstance(candidate, str) and candidate.startswith("https://"):
                return candidate
    return ""


def _product_barcodes(row: dict[str, Any]) -> list[str]:
    found: list[str] = []
    values = row.get("barcodes") if isinstance(row.get("barcodes"), list) else []
    for value in [row.get("barcode"), *values]:
        barcode = _text(value)
        if barcode and barcode not in found:
            found.append(barcode)
    return found


def _normalized_barcode(value: Any) -> str:
    barcode = "".join(character for character in _text(value) if ord(character) >= 32).strip()
    if len(barcode) >= 3 and barcode[0] == "]" and barcode[1].isalpha() and barcode[2].isdigit():
        barcode = barcode[3:].strip()
    return barcode


def _production_link_fields(item: dict[str, Any]) -> dict[str, Any]:
    """Build the same safe production/WMS link without a SQLite side table."""

    from marketplaces import product_group_for, production_target_for_marketplace_product

    group_key, group_name = product_group_for(
        item.get("name"), item.get("offer_id"), item.get("sku"),
        item.get("barcode"), item.get("size"),
    )
    target = production_target_for_marketplace_product(item)
    if target:
        product_name, size, color = target
        route_configured = 1
    else:
        product_name = (
            _text(item.get("name")) if group_key == "other" else _text(group_name)
        ) or _text(item.get("offer_id") or item.get("sku")) or "Товар Ozon"
        size = _text(item.get("size")) or "Не указан"
        color = _text(item.get("color")) or "Не указан"
        route_configured = 0
    return {
        "group_key": group_key,
        "group_name": group_name,
        "production_status": "linked",
        "route_configured": route_configured,
        "production_product_name": product_name,
        "production_size": size,
        "production_color": color,
    }


def _warehouse_key(warehouse_type: Any, warehouse_name: Any) -> str:
    kind = _text(warehouse_type).casefold() or "stock"
    name = _text(warehouse_name)
    return f"{kind}:{name}" if name else kind


def _wms_finished_stock(conn: Any) -> tuple[dict[tuple[str, str, str], int], bool]:
    """Read physical finished-goods balances without touching marketplace data."""

    try:
        from wms.repository import get_stock_rows

        balances: dict[tuple[str, str, str], int] = {}
        for stock_row in get_stock_rows(conn):
            key = stock_row.product_key
            if key.item_type != "finished" or stock_row.item_state != "SELLABLE":
                continue
            identity = (key.product_name, key.product_size, key.product_color)
            available = max(0, int(stock_row.quantity or 0) - int(stock_row.reserved_quantity or 0))
            balances[identity] = balances.get(identity, 0) + available
        conn.rollback()
        return balances, True
    except Exception:
        conn.rollback()
        return {}, False


def normalize_product(row: dict[str, Any]) -> dict[str, Any] | None:
    external_id, offer_id, sku = product_identity(row)
    if not external_id:
        return None
    barcodes = _product_barcodes(row)
    attributes = row.get("attributes") if isinstance(row.get("attributes"), list) else []
    visibility = _text(row.get("visibility") or row.get("status") or "unknown") or "unknown"
    archived_tokens = {"archived", "archive", "disabled", "inactive"}
    return {
        "external_product_id": external_id,
        "offer_id": offer_id,
        "sku": sku,
        "barcode": barcodes[0] if barcodes else "",
        "name": _text(row.get("name") or row.get("title") or offer_id or sku),
        "size": _text(row.get("size")) or _attribute_value(attributes, OZON_SIZE_ATTRIBUTE_IDS)
        or _nested_text(row, ("Размер", "размер")),
        "color": _text(row.get("color")) or _attribute_value(attributes, OZON_COLOR_ATTRIBUTE_IDS)
        or _nested_text(row, ("Цвет", "цвет")),
        "image_url": _product_image(row),
        "barcodes": barcodes,
        "attributes": {"attributes": attributes},
        "visibility": visibility,
        "is_archived": _truthy_flag(row.get("is_archived"))
        or _truthy_flag(row.get("archived"))
        or visibility.casefold() in archived_tokens,
        "source_updated_at": _timestamp(row.get("updated_at") or row.get("source_updated_at")),
        "payload": row,
    }


def normalize_order(row: dict[str, Any]) -> dict[str, Any] | None:
    external_id = _text(row.get("order_id") or row.get("posting_number") or row.get("order_number"))
    if not external_id:
        return None
    return {
        "external_order_id": external_id,
        "posting_number": _text(row.get("posting_number") or row.get("order_number")),
        "warehouse_type": _text(row.get("warehouse_type") or "FBS") or "FBS",
        "status": _text(row.get("status")),
        "shipment_date": _timestamp(
            row.get("shipment_date") or row.get("in_process_at") or row.get("created_at")
        ),
        "source_updated_at": _timestamp(row.get("updated_at") or row.get("source_updated_at")),
        "items": [item for item in (row.get("products") or row.get("items") or []) if isinstance(item, dict)],
        "payload": row,
    }


def normalize_price(row: dict[str, Any]) -> dict[str, Any] | None:
    external_id, offer_id, sku = product_identity(row)
    if not external_id:
        return None
    price = row.get("price") if isinstance(row.get("price"), dict) else row
    marketing = row.get("marketing_actions") if isinstance(row.get("marketing_actions"), dict) else {}
    raw_currency = _first_value(price, "currency_code", "currency")
    currency = (_text(raw_currency or "RUB").upper() or "RUB")
    if len(currency) != 3 or not currency.isascii() or not currency.isalpha():
        return None
    marketing_value = _first_value(price, "marketing_price", "marketing_seller_price")
    if marketing_value is None:
        marketing_value = marketing.get("value")
    current_value = _first_value(price, "price", "current_price", "marketing_seller_price")
    current_price = _decimal(current_value)
    if current_price is None:
        return None
    optional_values = {
        "old_price": _first_value(price, "old_price", "oldPrice"),
        "marketing_price": marketing_value,
        "minimum_price": _first_value(price, "min_price", "minimum_price"),
    }
    if any(value not in (None, "") and _decimal(value) is None for value in optional_values.values()):
        return None
    normalized = {
        "external_product_id": external_id,
        "offer_id": offer_id,
        "sku": sku,
        "current_price": current_price,
        "old_price": _decimal(optional_values["old_price"]),
        "marketing_price": _decimal(optional_values["marketing_price"]),
        "minimum_price": _decimal(optional_values["minimum_price"]),
        "currency": currency,
        "source_updated_at": _timestamp(row.get("updated_at") or row.get("source_updated_at")),
        "payload": row,
    }
    return normalized


def normalize_stock_rows(row: dict[str, Any]) -> list[dict[str, Any]]:
    external_id, offer_id, sku = product_identity(row)
    if not external_id:
        return []
    source_rows = row.get("stocks") if isinstance(row.get("stocks"), list) else [row]
    normalized: list[dict[str, Any]] = []
    for source in source_rows:
        if not isinstance(source, dict):
            continue
        raw_present = source.get("present") if "present" in source else source.get("stock")
        raw_reserved = source.get("reserved")
        raw_available = source.get("available")
        present = _decimal(raw_present)
        reserved = _decimal(raw_reserved)
        available = _decimal(raw_available)
        if present is None:
            continue
        if reserved is None:
            continue
        if raw_available not in (None, "") and available is None:
            continue
        available_derived = available is None
        if available is None and present is not None:
            available = max(Decimal(0), present - (reserved or Decimal(0)))
        normalized.append({
            "external_product_id": external_id,
            "offer_id": offer_id,
            "sku": sku,
            "warehouse_type": _text(source.get("type") or source.get("warehouse_type") or row.get("type")),
            "warehouse_name": _text(source.get("warehouse_name") or source.get("warehouse") or row.get("warehouse_name")),
            "stock": present,
            "reserved": reserved,
            "available": available,
            "source_updated_at": _timestamp(source.get("updated_at") or row.get("updated_at") or row.get("source_updated_at")),
            "payload": {**row, "_stock_row": source, "_available_derived": available_derived},
        })
    return normalized


def _hash_fields(*values: Any) -> str:
    canonical = json.dumps([str(value) if value is not None else None for value in values], separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class MarketplacePGRepository:
    """Transaction boundary and query API for the marketplace schema."""

    def __init__(self, connection_factory=get_pg_connection):
        self.connection_factory = connection_factory
        self._lock_connections: dict[int, Any] = {}

    def _connection(self):
        try:
            return self.connection_factory()
        except Exception as error:
            raise MarketplacePGUnavailable("PostgreSQL marketplace storage is unavailable.") from error

    def ensure_account(self, account_key: str, account_name: str) -> int:
        conn = self._connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO marketplace.accounts
                       (marketplace,account_key,account_name,updated_at)
                       VALUES ('ozon',%s,%s,now())
                       ON CONFLICT(account_key) DO UPDATE SET
                         account_name=excluded.account_name,updated_at=now()
                       RETURNING id""",
                    (account_key, account_name),
                )
                account_id = int(cur.fetchone()[0])
            conn.commit()
            return account_id
        except Exception as error:
            conn.rollback()
            raise MarketplacePGUnavailable("PostgreSQL marketplace migration 005 is not available.") from error

    def acquire_sync_lock(self, account_id: int) -> bool:
        """Acquire a session advisory lock so workers in different processes cannot overlap."""
        if account_id in self._lock_connections:
            return True
        conn = self._connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT pg_try_advisory_lock(hashtext(%s))", (f"marketplace:ozon:{account_id}",))
                acquired = bool(cur.fetchone()[0])
            if acquired:
                self._lock_connections[account_id] = conn
            else:
                conn.close()
            return acquired
        except Exception as error:
            conn.rollback()
            conn.close()
            raise MarketplacePGUnavailable("Could not acquire the marketplace sync lock.") from error

    def release_sync_lock(self, account_id: int) -> None:
        conn = self._lock_connections.pop(account_id, None)
        if conn is None:
            return
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT pg_advisory_unlock(hashtext(%s))", (f"marketplace:ozon:{account_id}",))
            conn.commit()
        except Exception:
            conn.rollback()
        finally:
            conn.close()

    def upsert_endpoint_registry(self, rows: Iterable[dict[str, Any]]) -> None:
        conn = self._connection()
        try:
            with conn.cursor() as cur:
                for row in rows:
                    cur.execute(
                        """INSERT INTO marketplace.endpoint_registry
                           (marketplace,dataset,method,path,pagination_kind,request_limit,
                            verification_status,verified_at,official_url,notes,read_only,enabled,updated_at)
                           VALUES ('ozon',%s,%s,%s,%s,%s,'verified',%s,%s,%s,TRUE,TRUE,now())
                           ON CONFLICT(marketplace,dataset,method,path) DO UPDATE SET
                             pagination_kind=excluded.pagination_kind,
                             request_limit=excluded.request_limit,
                             verification_status=excluded.verification_status,
                             verified_at=excluded.verified_at,
                             official_url=excluded.official_url,
                             notes=excluded.notes,read_only=TRUE,enabled=TRUE,updated_at=now()""",
                        (
                            row["dataset"], row["method"], row["path"],
                            row.get("pagination_kind", "none"), row.get("request_limit"),
                            row.get("verified_at"), row.get("official_url"), row.get("notes", ""),
                        ),
                    )
            conn.commit()
        except Exception as error:
            conn.rollback()
            raise MarketplacePGUnavailable("Could not update the verified endpoint registry.") from error

    def upsert_capabilities(self, account_id: int, capabilities: dict[str, Any]) -> None:
        conn = self._connection()
        try:
            with conn.cursor() as cur:
                for name, value in capabilities.items():
                    details = value if isinstance(value, dict) else {"value": value}
                    status = _text(details.get("status") or "unknown")
                    if status not in {"unknown", "available", "unavailable", "permission_required", "error"}:
                        status = "unknown"
                    cur.execute(
                        """INSERT INTO marketplace.account_capabilities
                           (account_id,capability,status,checked_at,safe_message,details_json)
                           VALUES (%s,%s,%s,now(),%s,%s::jsonb)
                           ON CONFLICT(account_id,capability) DO UPDATE SET
                             status=excluded.status,checked_at=excluded.checked_at,
                             safe_message=excluded.safe_message,details_json=excluded.details_json""",
                        (account_id, name, status, _text(details.get("message"))[:500], _json(details)),
                    )
            conn.commit()
        except Exception as error:
            conn.rollback()
            raise MarketplacePGUnavailable("Could not persist marketplace capabilities.") from error

    def capabilities_due(self, account_id: int, max_age_seconds: int = 24 * 60 * 60) -> bool:
        conn = self._connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT MAX(checked_at) IS NULL OR
                              EXTRACT(EPOCH FROM (now()-MAX(checked_at))) >= %s
                         FROM marketplace.account_capabilities
                        WHERE account_id=%s AND capability='roles'""",
                    (max_age_seconds, account_id),
                )
                due = bool(cur.fetchone()[0])
            conn.rollback()
            return due
        except Exception as error:
            conn.rollback()
            raise MarketplacePGUnavailable("Could not read capability freshness.") from error

    def datasets_due(self, account_id: int) -> tuple[str, ...]:
        """Return scheduled datasets whose last usable run is older than policy."""
        conn = self._connection()
        due: list[str] = []
        try:
            with conn.cursor() as cur:
                for dataset in DATASETS:
                    cur.execute(
                        """SELECT EXTRACT(EPOCH FROM (now()-MAX(finished_at)))
                             FROM marketplace.sync_runs
                            WHERE account_id=%s AND dataset=%s
                              AND (status='success' OR (status='partial' AND termination_reason='fbo_stock_scope_unavailable'))""",
                        (account_id, dataset),
                    )
                    row = cur.fetchone()
                    age = row[0] if row else None
                    if age is None or float(age) >= SYNC_CADENCE_SECONDS[dataset]:
                        due.append(dataset)
            conn.rollback()
            return tuple(due)
        except Exception as error:
            conn.rollback()
            raise MarketplacePGUnavailable("Could not evaluate marketplace sync cadence.") from error

    def start_or_resume_run(self, account_id: int, dataset: str, trigger_kind: str = "scheduled") -> RunContext:
        if dataset not in DATASETS:
            raise ValueError(f"Unsupported Phase 1A dataset: {dataset}")
        conn = self._connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT c.run_id,c.cursor_value,c.page_number,r.status
                         FROM marketplace.sync_checkpoints c
                         LEFT JOIN marketplace.sync_runs r ON r.id=c.run_id
                        WHERE c.account_id=%s AND c.dataset=%s""",
                    (account_id, dataset),
                )
                checkpoint = cur.fetchone()
                if checkpoint and checkpoint[0] and _text(checkpoint[1]) and checkpoint[3] in ("running", "partial", "failed"):
                    run_id = int(checkpoint[0])
                    cur.execute(
                        """UPDATE marketplace.sync_runs SET status='running',trigger_kind='retry',
                           finished_at=NULL,error_summary=NULL WHERE id=%s""",
                        (run_id,),
                    )
                    context = RunContext(run_id, account_id, dataset, _text(checkpoint[1]), int(checkpoint[2] or 0), True)
                else:
                    cursor_before = _text(checkpoint[1]) if checkpoint else ""
                    cur.execute(
                        """INSERT INTO marketplace.sync_runs
                           (account_id,dataset,trigger_kind,status,checkpoint_before)
                           VALUES (%s,%s,%s,'running',%s) RETURNING id""",
                        (account_id, dataset, trigger_kind, cursor_before),
                    )
                    run_id = int(cur.fetchone()[0])
                    cur.execute(
                        """INSERT INTO marketplace.sync_checkpoints
                           (account_id,dataset,cursor_value,page_number,run_id,state,updated_at)
                           VALUES (%s,%s,'',0,%s,'{}'::jsonb,now())
                           ON CONFLICT(account_id,dataset) DO UPDATE SET
                             cursor_value='',page_number=0,run_id=excluded.run_id,state='{}'::jsonb,updated_at=now()""",
                        (account_id, dataset, run_id),
                    )
                    context = RunContext(run_id, account_id, dataset, "", 0, False)
            conn.commit()
            return context
        except Exception as error:
            conn.rollback()
            raise MarketplacePGUnavailable("Could not start the marketplace sync run.") from error

    def persist_page(
        self,
        context: RunContext,
        *,
        local_page_number: int,
        request_cursor: str,
        response_cursor: str,
        rows: list[dict[str, Any]],
        retry_count: int = 0,
        expected_count: int | None = None,
    ) -> dict[str, int]:
        """Persist one page and advance its checkpoint in the same transaction."""
        conn = self._connection()
        page_number = context.page_number + int(local_page_number)
        inserted = updated = skipped = 0
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT rows_received,retry_count FROM marketplace.sync_pages WHERE run_id=%s AND page_number=%s",
                    (context.run_id, page_number),
                )
                previous = cur.fetchone()
                if previous is not None:
                    # Page rows, telemetry and checkpoint are committed in one
                    # transaction. A replay of that page is therefore a no-op.
                    conn.rollback()
                    return {"inserted": 0, "updated": 0, "skipped": 0}
                for source in rows:
                    if context.dataset == "catalog":
                        outcome = self._upsert_product(cur, context, source)
                    elif context.dataset == "prices":
                        outcome = self._upsert_price(cur, context, source)
                    elif context.dataset == "stocks":
                        outcomes = [self._upsert_stock(cur, context, item) for item in normalize_stock_rows(source)]
                        if not outcomes:
                            outcome = "skipped"
                        else:
                            inserted += outcomes.count("inserted")
                            updated += outcomes.count("updated")
                            skipped += outcomes.count("skipped")
                            continue
                    else:
                        outcome = self._upsert_order(cur, context, source)
                    inserted += outcome == "inserted"
                    updated += outcome == "updated"
                    skipped += outcome == "skipped"
                cur.execute(
                    """INSERT INTO marketplace.sync_pages
                       (run_id,page_number,request_cursor,response_cursor,rows_received,retry_count,
                        status,finished_at,committed_at)
                       VALUES (%s,%s,%s,%s,%s,%s,'success',now(),now())
                       ON CONFLICT(run_id,page_number) DO UPDATE SET
                         request_cursor=excluded.request_cursor,response_cursor=excluded.response_cursor,
                         rows_received=excluded.rows_received,retry_count=excluded.retry_count,
                         status='success',finished_at=now(),committed_at=now()""",
                    (context.run_id, page_number, request_cursor, response_cursor, len(rows), retry_count),
                )
                received_delta = len(rows)
                retry_delta = retry_count
                cur.execute(
                    """UPDATE marketplace.sync_runs SET
                         expected_count=COALESCE(%s,expected_count),
                         received_count=GREATEST(0,received_count+%s),
                         inserted_count=inserted_count+%s,
                         updated_count=updated_count+%s,
                         skipped_count=skipped_count+%s,
                         page_count=GREATEST(page_count,%s),
                         retry_count=GREATEST(0,retry_count+%s),checkpoint_after=%s
                       WHERE id=%s""",
                    (expected_count, received_delta, inserted, updated, skipped, page_number, retry_delta, response_cursor, context.run_id),
                )
                cur.execute(
                    """INSERT INTO marketplace.sync_checkpoints
                       (account_id,dataset,cursor_value,page_number,run_id,state,updated_at)
                       VALUES (%s,%s,%s,%s,%s,%s::jsonb,now())
                       ON CONFLICT(account_id,dataset) DO UPDATE SET
                         cursor_value=excluded.cursor_value,page_number=excluded.page_number,
                         run_id=excluded.run_id,state=excluded.state,updated_at=now()""",
                    (context.account_id, context.dataset, response_cursor, page_number, context.run_id,
                     _json({"rows_received": len(rows), "expected_count": expected_count})),
                )
            conn.commit()
            return {"inserted": inserted, "updated": updated, "skipped": skipped}
        except Exception:
            conn.rollback()
            raise

    def _ensure_product_stub(self, cur: Any, context: RunContext, external_id: str, offer_id: str, sku: str) -> None:
        cur.execute(
            """INSERT INTO marketplace.products_current
               (account_id,external_product_id,offer_id,sku,name,visibility,payload_json,last_seen_run_id)
               VALUES (%s,%s,%s,%s,%s,'unknown','{}'::jsonb,%s)
               ON CONFLICT(account_id,external_product_id,offer_id) DO NOTHING""",
            (context.account_id, external_id, offer_id, sku, offer_id or sku or external_id, context.run_id),
        )

    def _upsert_product(self, cur: Any, context: RunContext, source: dict[str, Any]) -> str:
        item = normalize_product(source)
        if item is None:
            return "skipped"
        key = (context.account_id, item["external_product_id"], item["offer_id"])
        cur.execute(
            """SELECT sku,barcode,name,size,color,image_url,barcodes_json,attributes_json,
                      visibility,is_archived,payload_json
                 FROM marketplace.products_current
                WHERE account_id=%s AND external_product_id=%s AND offer_id=%s""",
            key,
        )
        old = cur.fetchone()
        cur.execute(
            """INSERT INTO marketplace.products_current
               (account_id,external_product_id,offer_id,sku,barcode,name,size,color,image_url,
                barcodes_json,attributes_json,visibility,is_archived,payload_json,
                source_updated_at,received_at,last_seen_run_id)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s::jsonb,%s,%s,%s::jsonb,%s,now(),%s)
               ON CONFLICT(account_id,external_product_id,offer_id) DO UPDATE SET
                 sku=excluded.sku,barcode=excluded.barcode,name=excluded.name,
                 size=excluded.size,color=excluded.color,image_url=excluded.image_url,
                 barcodes_json=excluded.barcodes_json,attributes_json=excluded.attributes_json,
                 visibility=excluded.visibility,is_archived=excluded.is_archived,
                 payload_json=excluded.payload_json,source_updated_at=excluded.source_updated_at,
                 received_at=now(),last_seen_run_id=excluded.last_seen_run_id""",
            (*key, item["sku"], item["barcode"], item["name"], item["size"], item["color"],
             item["image_url"], _json(item["barcodes"]), _json(item["attributes"]),
             item["visibility"], item["is_archived"], _json(item["payload"]),
             item["source_updated_at"], context.run_id),
        )
        return "inserted" if old is None else "updated"

    def _upsert_price(self, cur: Any, context: RunContext, source: dict[str, Any]) -> str:
        item = normalize_price(source)
        if item is None:
            return "skipped"
        self._ensure_product_stub(cur, context, item["external_product_id"], item["offer_id"], item["sku"])
        key = (context.account_id, item["external_product_id"], item["offer_id"])
        cur.execute(
            "SELECT current_price,old_price,marketing_price,minimum_price,currency FROM marketplace.prices_current WHERE account_id=%s AND external_product_id=%s AND offer_id=%s",
            key,
        )
        old = cur.fetchone()
        values = (item["current_price"], item["old_price"], item["marketing_price"], item["minimum_price"], item["currency"])
        changed = old is None or tuple(old) != values
        row_hash = _hash_fields(*key, *values)
        cur.execute(
            """INSERT INTO marketplace.prices_current
               (account_id,external_product_id,offer_id,current_price,old_price,marketing_price,
                minimum_price,currency,payload_json,source_updated_at,received_at,last_seen_run_id)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s,now(),%s)
               ON CONFLICT(account_id,external_product_id,offer_id) DO UPDATE SET
                 current_price=excluded.current_price,old_price=excluded.old_price,
                 marketing_price=excluded.marketing_price,minimum_price=excluded.minimum_price,
                 currency=excluded.currency,payload_json=excluded.payload_json,
                 source_updated_at=excluded.source_updated_at,received_at=now(),
                 last_seen_run_id=excluded.last_seen_run_id""",
            (*key, *values, _json(item["payload"]), item["source_updated_at"], context.run_id),
        )
        if changed:
            cur.execute(
                """INSERT INTO marketplace.prices_history
                   (account_id,external_product_id,offer_id,current_price,old_price,marketing_price,
                    minimum_price,currency,payload_json,observed_at,source_updated_at,run_id,row_hash)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb,now(),%s,%s,%s)
                   ON CONFLICT(run_id,account_id,external_product_id,offer_id,row_hash) DO NOTHING""",
                (*key, *values, _json(item["payload"]), item["source_updated_at"], context.run_id, row_hash),
            )
        return "inserted" if old is None else ("updated" if changed else "skipped")

    def _upsert_stock(self, cur: Any, context: RunContext, item: dict[str, Any]) -> str:
        self._ensure_product_stub(cur, context, item["external_product_id"], item["offer_id"], item["sku"])
        key = (
            context.account_id, item["external_product_id"], item["offer_id"],
            item["warehouse_type"], item["warehouse_name"],
        )
        cur.execute(
            """SELECT stock,reserved,available FROM marketplace.stocks_current
               WHERE account_id=%s AND external_product_id=%s AND offer_id=%s
                 AND warehouse_type=%s AND warehouse_name=%s""",
            key,
        )
        old = cur.fetchone()
        values = (item["stock"], item["reserved"], item["available"])
        changed = old is None or tuple(old) != values
        row_hash = _hash_fields(*key, *values)
        cur.execute(
            """INSERT INTO marketplace.stocks_current
               (account_id,external_product_id,offer_id,warehouse_type,warehouse_name,
                stock,reserved,available,payload_json,source_updated_at,received_at,last_seen_run_id)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s,now(),%s)
               ON CONFLICT(account_id,external_product_id,offer_id,warehouse_type,warehouse_name)
               DO UPDATE SET stock=excluded.stock,reserved=excluded.reserved,
                 available=excluded.available,payload_json=excluded.payload_json,
                 source_updated_at=excluded.source_updated_at,received_at=now(),
                 last_seen_run_id=excluded.last_seen_run_id""",
            (*key, *values, _json(item["payload"]), item["source_updated_at"], context.run_id),
        )
        cur.execute(
            """INSERT INTO marketplace.stocks_history
               (account_id,external_product_id,offer_id,warehouse_type,warehouse_name,
                stock,reserved,available,payload_json,observed_at,source_updated_at,run_id,row_hash)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb,now(),%s,%s,%s)
               ON CONFLICT(run_id,account_id,external_product_id,offer_id,warehouse_type,warehouse_name)
               DO UPDATE SET stock=excluded.stock,reserved=excluded.reserved,
                 available=excluded.available,payload_json=excluded.payload_json,
                 observed_at=excluded.observed_at,source_updated_at=excluded.source_updated_at,
                 row_hash=excluded.row_hash""",
            (*key, *values, _json(item["payload"]), item["source_updated_at"], context.run_id, row_hash),
        )
        return "inserted" if old is None else ("updated" if changed else "skipped")

    def _upsert_order(self, cur: Any, context: RunContext, source: dict[str, Any]) -> str:
        item = normalize_order(source)
        if item is None:
            return "skipped"
        key = (context.account_id, item["external_order_id"])
        cur.execute(
            """SELECT posting_number,warehouse_type,status,shipment_date,payload_json
                 FROM marketplace.orders_current
                WHERE account_id=%s AND external_order_id=%s""",
            key,
        )
        old = cur.fetchone()
        cur.execute(
            """INSERT INTO marketplace.orders_current
               (account_id,external_order_id,posting_number,warehouse_type,status,shipment_date,
                payload_json,source_updated_at,received_at,last_seen_run_id)
               VALUES (%s,%s,%s,%s,%s,%s,%s::jsonb,%s,now(),%s)
               ON CONFLICT(account_id,external_order_id) DO UPDATE SET
                 posting_number=excluded.posting_number,warehouse_type=excluded.warehouse_type,
                 status=excluded.status,shipment_date=excluded.shipment_date,
                 payload_json=excluded.payload_json,source_updated_at=excluded.source_updated_at,
                 received_at=now(),last_seen_run_id=excluded.last_seen_run_id""",
            (*key, item["posting_number"], item["warehouse_type"], item["status"],
             item["shipment_date"], _json(item["payload"]), item["source_updated_at"], context.run_id),
        )
        cur.execute(
            "DELETE FROM marketplace.order_items_current WHERE account_id=%s AND external_order_id=%s",
            key,
        )
        for line_number, source_item in enumerate(item["items"], start=1):
            external_id, offer_id, sku = product_identity(source_item)
            quantity = _decimal(source_item.get("quantity")) or Decimal(0)
            price = _decimal(source_item.get("price"))
            currency = _text(source_item.get("currency_code") or source_item.get("currency") or "RUB").upper()
            if len(currency) != 3 or not currency.isascii() or not currency.isalpha():
                currency = "RUB"
            cur.execute(
                """INSERT INTO marketplace.order_items_current
                   (account_id,external_order_id,line_number,external_product_id,offer_id,sku,
                    name,quantity,price,currency,payload_json)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb)""",
                (*key, line_number, external_id, offer_id, sku,
                 _text(source_item.get("name") or offer_id or sku), quantity, price, currency,
                 _json(source_item)),
            )
        return "inserted" if old is None else "updated"

    def finish_run(
        self,
        context: RunContext,
        *,
        status: str,
        unique_count: int,
        expected_count: int | None,
        termination_reason: str,
        retry_count: int = 0,
        safe_error: str = "",
    ) -> dict[str, Any]:
        if status not in {"success", "partial", "failed", "cancelled"}:
            raise ValueError(f"Invalid terminal run status: {status}")
        conn = self._connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """UPDATE marketplace.sync_runs SET status=%s,unique_count=%s,
                         expected_count=COALESCE(%s,expected_count),retry_count=GREATEST(retry_count,%s),
                         termination_reason=%s,error_summary=%s,finished_at=now()
                       WHERE id=%s
                       RETURNING id,dataset,status,expected_count,received_count,unique_count,
                                 inserted_count,updated_count,skipped_count,page_count,retry_count,
                                 checkpoint_after,termination_reason,error_summary,started_at,finished_at""",
                    (status, unique_count, expected_count, retry_count, termination_reason,
                     safe_error[:500] or None, context.run_id),
                )
                run = _row_dict(cur.fetchone(), cur)
                if context.dataset == "catalog" and status == "success":
                    cur.execute(
                        """UPDATE marketplace.products_current SET is_archived=TRUE,received_at=now()
                           WHERE account_id=%s AND last_seen_run_id IS DISTINCT FROM %s AND is_archived=FALSE""",
                        (context.account_id, context.run_id),
                    )
                if context.dataset == "prices" and status == "success":
                    cur.execute(
                        """DELETE FROM marketplace.prices_current
                           WHERE account_id=%s AND last_seen_run_id IS DISTINCT FROM %s""",
                        (context.account_id, context.run_id),
                    )
                stocks_snapshot_complete = (
                    context.dataset == "stocks"
                    and (
                        status == "success"
                        or (status == "partial" and termination_reason == "fbo_stock_scope_unavailable")
                    )
                )
                if stocks_snapshot_complete:
                    cur.execute(
                        """DELETE FROM marketplace.stocks_current
                           WHERE account_id=%s AND last_seen_run_id IS DISTINCT FROM %s""",
                        (context.account_id, context.run_id),
                    )
                if termination_reason == "checkpoint_rejected":
                    cur.execute(
                        """UPDATE marketplace.sync_checkpoints
                              SET cursor_value=NULL,page_number=0,run_id=NULL,
                                  state=%s::jsonb,updated_at=now()
                            WHERE account_id=%s AND dataset=%s""",
                        (_json({"reset_reason": termination_reason, "failed_run_id": context.run_id}), context.account_id, context.dataset),
                    )
                usable_completion = status == "success" or (
                    context.dataset == "stocks"
                    and status == "partial"
                    and termination_reason == "fbo_stock_scope_unavailable"
                )
                if usable_completion:
                    cur.execute(
                        """UPDATE marketplace.sync_checkpoints SET cursor_value=NULL,page_number=0,
                           run_id=NULL,state=%s::jsonb,updated_at=now()
                           WHERE account_id=%s AND dataset=%s""",
                        (
                            _json({
                                "last_success_run_id": context.run_id
                                if status == "success" else None,
                                "last_usable_run_id": context.run_id,
                            }),
                            context.account_id,
                            context.dataset,
                        ),
                    )
            conn.commit()
            return _json_value(run)
        except Exception as error:
            conn.rollback()
            raise MarketplacePGUnavailable("Could not finish the marketplace sync run.") from error

    def run_unique_count(self, context: RunContext) -> int:
        """Reconcile a resumed run against rows already committed for that run."""
        table = {
            "catalog": "marketplace.products_current",
            "prices": "marketplace.prices_current",
            "stocks": "marketplace.stocks_current",
            "orders": "marketplace.orders_current",
        }[context.dataset]
        conn = self._connection()
        try:
            with conn.cursor() as cur:
                if context.dataset == "stocks":
                    cur.execute(
                        f"""SELECT COUNT(*) FROM (
                              SELECT external_product_id,offer_id FROM {table}
                               WHERE account_id=%s AND last_seen_run_id=%s
                               GROUP BY external_product_id,offer_id
                            ) rows_seen""",
                        (context.account_id, context.run_id),
                    )
                else:
                    cur.execute(
                        f"SELECT COUNT(*) FROM {table} WHERE account_id=%s AND last_seen_run_id=%s",
                        (context.account_id, context.run_id),
                    )
                value = int(cur.fetchone()[0])
            conn.rollback()
            return value
        except Exception as error:
            conn.rollback()
            raise MarketplacePGUnavailable("Could not reconcile the marketplace sync run.") from error

    def run_received_count(self, context: RunContext) -> int:
        """Return provider rows committed across all pages of a run."""
        conn = self._connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT received_count FROM marketplace.sync_runs WHERE id=%s",
                    (context.run_id,),
                )
                row = cur.fetchone()
                value = 0 if row is None else int(row[0] or 0)
            conn.rollback()
            return value
        except Exception as error:
            conn.rollback()
            raise MarketplacePGUnavailable("Could not reconcile provider row totals.") from error

    def run_expected_count(self, context: RunContext) -> int | None:
        conn = self._connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT expected_count FROM marketplace.sync_runs WHERE id=%s", (context.run_id,))
                row = cur.fetchone()
                value = None if row is None or row[0] is None else int(row[0])
            conn.rollback()
            return value
        except Exception as error:
            conn.rollback()
            raise MarketplacePGUnavailable("Could not read the marketplace reconciliation target.") from error

    def fail_run(
        self,
        context: RunContext,
        error: Exception,
        *,
        retry_count: int = 0,
        partial: bool = False,
        unique_count: int = 0,
        expected_count: int | None = None,
        termination_reason: str = "transport_error",
    ) -> dict[str, Any]:
        error_code = _text(getattr(error, "cause_code", "") or getattr(error, "code", ""))
        safe_message = error.__class__.__name__ + (f" ({error_code})" if error_code else "")
        conn = self._connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO marketplace.sync_errors
                       (run_id,dataset,page_number,error_class,error_code,http_status,safe_message,retry_count)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (
                        context.run_id, context.dataset, None,
                        error.__class__.__name__, error_code or None,
                        getattr(error, "status", None), safe_message, retry_count,
                    ),
                )
            conn.commit()
        except Exception as persist_error:
            conn.rollback()
            raise MarketplacePGUnavailable("Could not persist the marketplace sync error.") from persist_error
        return self.finish_run(
            context, status="partial" if partial else "failed", unique_count=unique_count,
            expected_count=expected_count, termination_reason=termination_reason, retry_count=retry_count,
            safe_error=safe_message,
        )

    def data_quality(self, account_key: str) -> dict[str, Any]:
        conn = self._connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT id,account_name FROM marketplace.accounts WHERE account_key=%s", (account_key,))
                account = cur.fetchone()
                if account is None:
                    conn.rollback()
                    return {"state": "no_data", "account": None, "datasets": [], "capabilities": [], "totals": {}}
                account_id = int(account[0])
                cur.execute(
                    """SELECT capability,status,checked_at,safe_message,details_json
                         FROM marketplace.account_capabilities WHERE account_id=%s ORDER BY capability""",
                    (account_id,),
                )
                capabilities = [_json_value(_row_dict(row, cur)) for row in cur.fetchall()]
                datasets = []
                for dataset in DATASETS:
                    cur.execute(
                        """SELECT id,dataset,status,expected_count,received_count,unique_count,
                                  inserted_count,updated_count,skipped_count,page_count,retry_count,
                                  checkpoint_after,termination_reason,error_summary,started_at,finished_at,
                                  (SELECT MAX(success.finished_at) FROM marketplace.sync_runs success
                                    WHERE success.account_id=%s AND success.dataset=%s AND success.status='success') AS last_success_at,
                                  (SELECT MAX(usable.finished_at) FROM marketplace.sync_runs usable
                                    WHERE usable.account_id=%s AND usable.dataset=%s
                                      AND (usable.status='success' OR
                                           (usable.status='partial' AND usable.termination_reason='fbo_stock_scope_unavailable'))) AS last_usable_at,
                                  EXTRACT(EPOCH FROM (now()-COALESCE(finished_at,started_at))) AS age_seconds
                             FROM marketplace.sync_runs
                            WHERE account_id=%s AND dataset=%s ORDER BY started_at DESC LIMIT 1""",
                        (account_id, dataset, account_id, dataset, account_id, dataset),
                    )
                    row = _row_dict(cur.fetchone(), cur)
                    if not row:
                        datasets.append({"dataset": dataset, "status": "no_data", "value_state": "no_data", "freshness": "unknown"})
                        continue
                    age = int(row.get("age_seconds") or 0)
                    raw_status = row.get("status")
                    status = "error" if raw_status == "failed" else raw_status
                    usable = raw_status == "success" or (
                        raw_status == "partial" and row.get("termination_reason") == "fbo_stock_scope_unavailable"
                    )
                    freshness = "fresh" if usable and age <= FRESHNESS_SECONDS[dataset] else ("stale" if usable else status)
                    unique = int(row.get("unique_count") or 0)
                    row.update({
                        "status": status,
                        "freshness": freshness,
                        "age_seconds": age,
                        "value_state": "zero" if usable and unique == 0 else ("value" if usable else status),
                    })
                    datasets.append(_json_value(row))
                cur.execute("SELECT COUNT(*) FROM marketplace.products_current WHERE account_id=%s AND is_archived=FALSE", (account_id,))
                products = int(cur.fetchone()[0])
                cur.execute(
                    """SELECT COUNT(*) FROM marketplace.prices_current pr
                         JOIN marketplace.products_current p
                           USING(account_id,external_product_id,offer_id)
                        WHERE pr.account_id=%s AND p.is_archived=FALSE""",
                    (account_id,),
                )
                prices = int(cur.fetchone()[0])
                cur.execute(
                    """SELECT COUNT(*),COALESCE(SUM(s.stock),0),COALESCE(SUM(s.reserved),0),COALESCE(SUM(s.available),0)
                         FROM marketplace.stocks_current s
                         JOIN marketplace.products_current p
                           USING(account_id,external_product_id,offer_id)
                        WHERE s.account_id=%s AND p.is_archived=FALSE""",
                    (account_id,),
                )
                stock_totals = cur.fetchone()
                cur.execute(
                    """SELECT COUNT(*) FROM marketplace.orders_current
                        WHERE account_id=%s AND lower(status) NOT IN ('cancelled','delivered')""",
                    (account_id,),
                )
                open_orders = int(cur.fetchone()[0])
            conn.rollback()
            overall = "ready" if datasets and all(item["status"] == "success" for item in datasets) else (
                "no_data" if all(item["status"] == "no_data" for item in datasets) else "attention"
            )
            return _json_value({
                "state": overall,
                "account": {"key": account_key, "name": account[1]},
                "datasets": datasets,
                "capabilities": capabilities,
                "totals": {
                    "products": products,
                    "prices": prices,
                    "stock_rows": int(stock_totals[0]),
                    "stock_present": stock_totals[1],
                    "stock_reserved": stock_totals[2],
                    "stock_available": stock_totals[3],
                    "open_orders": open_orders,
                },
            })
        except MarketplacePGUnavailable:
            raise
        except Exception as error:
            conn.rollback()
            raise MarketplacePGUnavailable("Could not read marketplace data quality.") from error

    def products_page(self, account_key: str, *, query: str = "", page: int = 1, page_size: int = 50, include_archived: bool = False) -> dict[str, Any]:
        page = max(1, int(page or 1))
        page_size = min(200, max(1, int(page_size or 50)))
        conn = self._connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM marketplace.accounts WHERE account_key=%s", (account_key,))
                account = cur.fetchone()
                if account is None:
                    conn.rollback()
                    return {"items": [], "page": page, "page_size": page_size, "total": 0, "pages": 0}
                account_id = int(account[0])
                where = ["p.account_id=%s"]
                params: list[Any] = [account_id]
                if not include_archived:
                    where.append("p.is_archived=FALSE")
                if _text(query):
                    where.append("(p.name ILIKE %s OR p.offer_id ILIKE %s OR p.sku ILIKE %s OR p.barcode ILIKE %s)")
                    term = f"%{_text(query)}%"
                    params.extend([term, term, term, term])
                predicate = " AND ".join(where)
                cur.execute(f"SELECT COUNT(*) FROM marketplace.products_current p WHERE {predicate}", tuple(params))
                total = int(cur.fetchone()[0])
                pages = (total + page_size - 1) // page_size
                page = min(page, max(1, pages))
                cur.execute(
                    f"""SELECT p.external_product_id,p.offer_id,p.sku,p.barcode,p.name,p.size,p.color,
                               p.image_url,p.barcodes_json,p.attributes_json,p.visibility,p.is_archived,
                               p.received_at,pr.current_price,pr.old_price,pr.marketing_price,pr.currency,
                               s.stock,s.reserved,s.available
                          FROM marketplace.products_current p
                          LEFT JOIN marketplace.prices_current pr USING(account_id,external_product_id,offer_id)
                          LEFT JOIN (
                              SELECT account_id,external_product_id,offer_id,SUM(stock) stock,
                                     SUM(reserved) reserved,SUM(available) available
                                FROM marketplace.stocks_current GROUP BY account_id,external_product_id,offer_id
                          ) s USING(account_id,external_product_id,offer_id)
                         WHERE {predicate}
                         ORDER BY p.name,p.offer_id,p.external_product_id LIMIT %s OFFSET %s""",
                    tuple(params + [page_size, (page - 1) * page_size]),
                )
                items = [_json_value(_row_dict(row, cur)) for row in cur.fetchall()]
            conn.rollback()
            return {"items": items, "page": page, "page_size": page_size, "total": total, "pages": pages}
        except Exception as error:
            conn.rollback()
            raise MarketplacePGUnavailable("Could not read the marketplace product page.") from error

    def dashboard(self, account_key: str) -> dict[str, Any]:
        """Return the Ozon dashboard read model exclusively from PostgreSQL."""

        conn = self._connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id,account_name,enabled,updated_at FROM marketplace.accounts WHERE account_key=%s",
                    (account_key,),
                )
                account = cur.fetchone()
                if account is None:
                    conn.rollback()
                    return {
                        "ok": True, "configured": True, "read_only": True,
                        "accounts": [], "summary": {"products": 0, "stock_rows": 0, "open_orders": 0},
                        "products_rows": [], "product_groups": [], "warehouses": [],
                        "orders_rows": [], "sync_runs": [],
                    }
                account_id = int(account[0])
                cur.execute(
                    """SELECT p.external_product_id AS id,p.external_product_id,p.name,p.offer_id,p.sku,
                              p.barcode,p.size,p.color,p.image_url,p.barcodes_json,p.attributes_json,
                              p.received_at AS updated_at,pr.current_price,pr.old_price,
                              COALESCE(s.stock,0) AS available
                         FROM marketplace.products_current p
                         LEFT JOIN marketplace.prices_current pr
                           USING(account_id,external_product_id,offer_id)
                         LEFT JOIN (
                             SELECT account_id,external_product_id,offer_id,SUM(available) AS stock
                               FROM marketplace.stocks_current
                              GROUP BY account_id,external_product_id,offer_id
                         ) s USING(account_id,external_product_id,offer_id)
                        WHERE p.account_id=%s AND p.is_archived=FALSE
                        ORDER BY p.name,p.offer_id,p.external_product_id""",
                    (account_id,),
                )
                products = [_json_value(_row_dict(row, cur)) for row in cur.fetchall()]
                cur.execute(
                    """SELECT warehouse_type,warehouse_name,COUNT(*) AS rows,SUM(available) AS available
                         FROM marketplace.stocks_current WHERE account_id=%s
                         GROUP BY warehouse_type,warehouse_name ORDER BY warehouse_type,warehouse_name""",
                    (account_id,),
                )
                stock_rows = [_json_value(_row_dict(row, cur)) for row in cur.fetchall()]
                cur.execute(
                    """SELECT external_product_id,offer_id,warehouse_type,warehouse_name,
                              SUM(available) AS available
                         FROM marketplace.stocks_current WHERE account_id=%s
                        GROUP BY external_product_id,offer_id,warehouse_type,warehouse_name""",
                    (account_id,),
                )
                product_stock_rows = [_json_value(_row_dict(row, cur)) for row in cur.fetchall()]
                cur.execute(
                    """SELECT o.external_order_id AS id,o.external_order_id,o.posting_number,o.status,
                              o.warehouse_type,o.shipment_date,o.received_at AS updated_at,
                              COALESCE(SUM(i.quantity),0) AS quantity
                         FROM marketplace.orders_current o
                         LEFT JOIN marketplace.order_items_current i
                           USING(account_id,external_order_id)
                        WHERE o.account_id=%s
                        GROUP BY o.account_id,o.external_order_id,o.posting_number,o.status,
                                 o.warehouse_type,o.shipment_date,o.received_at
                        ORDER BY o.received_at DESC LIMIT 500""",
                    (account_id,),
                )
                orders = [_json_value(_row_dict(row, cur)) for row in cur.fetchall()]
                cur.execute(
                    """SELECT i.external_product_id,i.offer_id,i.sku,i.quantity,o.posting_number,
                              DATE(COALESCE(o.shipment_date,o.received_at)) AS day
                         FROM marketplace.order_items_current i
                         JOIN marketplace.orders_current o USING(account_id,external_order_id)
                        WHERE i.account_id=%s""",
                    (account_id,),
                )
                order_history_rows = [_json_value(_row_dict(row, cur)) for row in cur.fetchall()]
                cur.execute(
                    """SELECT id,status,dataset,expected_count,unique_count AS products_count,
                              CASE WHEN dataset='prices' THEN unique_count ELSE 0 END AS prices_count,
                              CASE WHEN dataset='stocks' THEN unique_count ELSE 0 END AS stocks_count,
                              CASE WHEN dataset='orders' THEN unique_count ELSE 0 END AS orders_count,
                              error_summary AS error_message,started_at,finished_at
                         FROM marketplace.sync_runs WHERE account_id=%s
                        ORDER BY started_at DESC LIMIT 12""",
                    (account_id,),
                )
                runs = [_json_value(_row_dict(row, cur)) for row in cur.fetchall()]
            conn.rollback()
            warehouses = [
                {
                    "key": _warehouse_key(row.get("warehouse_type"), row.get("warehouse_name")),
                    "name": _text(row.get("warehouse_name")) or _text(row.get("warehouse_type")) or "Склад Ozon",
                }
                for row in stock_rows
            ]
            stock_by_product: dict[tuple[str, str], dict[str, int]] = {}
            for row in product_stock_rows:
                key = (_text(row.get("external_product_id")), _text(row.get("offer_id")))
                warehouse_key = _warehouse_key(row.get("warehouse_type"), row.get("warehouse_name"))
                stock_by_product.setdefault(key, {})[warehouse_key] = int(Decimal(str(row.get("available") or 0)))
            product_history: dict[str, dict[str, dict[str, Any]]] = {}
            for row in order_history_rows:
                day = _text(row.get("day"))[:10]
                if not day:
                    continue
                for identity in {
                    _text(row.get("external_product_id")),
                    _text(row.get("offer_id")),
                    _text(row.get("sku")),
                }:
                    if not identity:
                        continue
                    bucket = product_history.setdefault(identity, {}).setdefault(
                        day, {"date": day, "orders": set(), "units": 0, "returns": 0, "accruals": 0.0},
                    )
                    if _text(row.get("posting_number")):
                        bucket["orders"].add(_text(row.get("posting_number")))
                    bucket["units"] += int(Decimal(str(row.get("quantity") or 0)))
            wms_stock, wms_stock_available = _wms_finished_stock(conn)
            groups: dict[str, dict[str, Any]] = {}
            for product in products:
                product.update(_production_link_fields(product))
                product["warehouse_stocks"] = stock_by_product.get(
                    (_text(product.get("external_product_id")), _text(product.get("offer_id"))),
                    {},
                )
                production_identity = (
                    _text(product.get("production_product_name")),
                    _text(product.get("production_size")),
                    _text(product.get("production_color")),
                )
                product["production_available"] = wms_stock.get(production_identity, 0)
                product["production_linked"] = bool(product.get("production_status") == "linked")
                product["production_stock_available"] = wms_stock_available
                merged_history: dict[str, dict[str, Any]] = {}
                for identity in {
                    _text(product.get("external_product_id")),
                    _text(product.get("offer_id")),
                    _text(product.get("sku")),
                }:
                    for day, source in product_history.get(identity, {}).items():
                        target = merged_history.setdefault(
                            day, {"date": day, "orders": set(), "units": 0, "returns": 0, "accruals": 0.0},
                        )
                        target["orders"].update(source["orders"])
                        target["units"] = max(int(target["units"]), int(source["units"]))
                product["history"] = [
                    {**entry, "orders": len(entry["orders"])}
                    for entry in sorted(merged_history.values(), key=lambda value: value["date"])
                ]
                group_key = product["group_key"]
                group_name = product["group_name"]
                group = groups.setdefault(group_key, {
                    "key": group_key, "name": group_name, "products": 0,
                    "articles": set(), "colors": set(), "sizes": set(), "available": 0,
                    "production_available": 0, "production_linked_products": 0,
                    "production_stock_available": wms_stock_available,
                    "production_keys": set(), "prices": [],
                })
                if not group.get("image_url") and product.get("image_url"):
                    group["image_url"] = product["image_url"]
                group["products"] += 1
                article = _text(product.get("offer_id") or product.get("sku"))
                if article:
                    group["articles"].add(article)
                if _text(product.get("color")):
                    group["colors"].add(_text(product.get("color")))
                if _text(product.get("size")):
                    group["sizes"].add(_text(product.get("size")))
                group["available"] += int(Decimal(str(product.get("available") or 0)))
                if production_identity not in group["production_keys"]:
                    group["production_keys"].add(production_identity)
                    group["production_available"] += int(product.get("production_available") or 0)
                if product.get("production_linked"):
                    group["production_linked_products"] += 1
                if product.get("current_price") is not None:
                    group["prices"].append(float(product["current_price"]))
            group_rows = [
                {
                    **group,
                    "articles": len(group["articles"]),
                    "colors": sorted(group["colors"]),
                    "sizes": sorted(group["sizes"]),
                    "price_min": min(group["prices"]) if group["prices"] else None,
                    "price_max": max(group["prices"]) if group["prices"] else None,
                }
                for group in sorted(groups.values(), key=lambda item: _text(item["name"]).casefold())
            ]
            for group in group_rows:
                group.pop("prices", None)
                group.pop("production_keys", None)
            open_orders = sum(
                _text(row.get("status")).casefold() not in {"cancelled", "delivered"}
                for row in orders
            )
            return _json_value({
                "ok": True,
                "configured": True,
                "read_only": True,
                "source": "postgresql",
                "accounts": [{
                    "id": account_id, "marketplace": "ozon", "account_name": account[1],
                    "enabled": bool(account[2]), "last_sync_at": account[3], "last_error": "",
                }],
                "summary": {
                    "products": len(products), "stock_rows": len(stock_rows),
                    "open_orders": open_orders,
                },
                "products_rows": products,
                "product_groups": group_rows,
                "warehouses": warehouses,
                "orders_rows": orders,
                "sync_runs": runs,
                "analytics": {},
            })
        except Exception as error:
            conn.rollback()
            raise MarketplacePGUnavailable("Could not read the PostgreSQL marketplace dashboard.") from error

    def warehouse_catalog(self, account_key: str) -> dict[str, Any]:
        page = self.products_page(account_key, page=1, page_size=200, include_archived=False)
        all_items = list(page["items"])
        for number in range(2, int(page.get("pages") or 0) + 1):
            all_items.extend(
                self.products_page(account_key, page=number, page_size=200, include_archived=False)["items"]
            )
        for item in all_items:
            item.update(_production_link_fields(item))
        return _json_value({
            "ok": True,
            "marketplace": "ozon",
            "source": "postgresql",
            "account_name": account_key,
            "products": all_items,
        })

    def marketplace_metadata_for_wms_product_keys(
        self,
        account_key: str,
        product_keys: list[dict[str, Any]],
    ) -> list[dict[str, Any] | None]:
        """Resolve WMS identities from the PostgreSQL catalogue only."""

        catalog = self.warehouse_catalog(account_key)
        products = list(catalog.get("products") or [])
        resolved: list[dict[str, Any] | None] = []
        for product_key in product_keys:
            if _text(product_key.get("item_type")) != "finished":
                resolved.append(None)
                continue
            wms_name = _text(product_key.get("product_name")).casefold()
            wms_size = _text(product_key.get("product_size")).casefold()
            wms_color = _text(product_key.get("product_color")).casefold()
            direct = next(
                (
                    product for product in products
                    if (_text(product.get("offer_id")) and _text(product.get("offer_id")).casefold() in wms_name)
                    or (_text(product.get("sku")) and _text(product.get("sku")).casefold() in wms_name)
                ),
                None,
            )
            linked = direct or next(
                (
                    product for product in products
                    if product.get("production_status") == "linked"
                    and _text(product.get("production_product_name")).casefold() == wms_name
                    and _text(product.get("production_size")).casefold() == wms_size
                    and _text(product.get("production_color")).casefold() == wms_color
                ),
                None,
            )
            if linked is None:
                resolved.append(None)
                continue
            alternate_barcodes = {
                _normalized_barcode(value)
                for value in (linked.get("barcodes_json") or linked.get("barcodes") or [])
                if _normalized_barcode(value)
            }
            primary_barcode = _normalized_barcode(linked.get("barcode"))
            if primary_barcode:
                alternate_barcodes.add(primary_barcode)
            resolved.append({
                key: linked.get(key)
                for key in (
                    "external_product_id", "name", "group_name", "offer_id", "sku",
                    "barcode", "size", "color", "image_url", "route_configured",
                    "production_product_name", "production_size", "production_color",
                )
            } | {"id": linked.get("external_product_id"), "barcodes": sorted(alternate_barcodes)})
        return resolved

    def resolve_production_product_by_barcode(
        self,
        account_key: str,
        barcode: str,
    ) -> dict[str, Any] | None:
        """Resolve a scanner code using primary and alternate PostgreSQL barcodes."""

        wanted = _normalized_barcode(barcode)
        if not wanted:
            return None
        products = self.warehouse_catalog(account_key).get("products") or []
        for product in products:
            candidates = {
                _normalized_barcode(value)
                for value in (product.get("barcodes_json") or product.get("barcodes") or [])
                if _normalized_barcode(value)
            }
            primary = _normalized_barcode(product.get("barcode"))
            if primary:
                candidates.add(primary)
            if wanted not in candidates or product.get("production_status") != "linked":
                continue
            return {
                "item_type": "finished",
                "product_name": product["production_product_name"],
                "product_size": product["production_size"],
                "product_color": product["production_color"],
                "stage_name": "Упаковано",
                "ready_for_position": "Склад",
            }
        return None
