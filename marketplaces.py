"""Read-only marketplace integrations for the production application.

The first adapter is Ozon Seller API.  It deliberately exposes no methods that
write prices, stocks, cards, orders or shipments back to a marketplace.  API
credentials stay in the server environment; only normalized snapshots and
sync diagnostics are stored in the local application database.
"""

from __future__ import annotations

import json
import os
import re
import sqlite3
import time
import uuid
from datetime import datetime, timedelta, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from database import get_db_connection, local_now


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS marketplace_accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    marketplace TEXT NOT NULL,
    account_name TEXT NOT NULL,
    seller_id TEXT NOT NULL DEFAULT '',
    enabled INTEGER NOT NULL DEFAULT 1,
    last_sync_at TEXT,
    last_error TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(marketplace, account_name)
);
CREATE TABLE IF NOT EXISTS marketplace_products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    external_product_id TEXT NOT NULL DEFAULT '',
    offer_id TEXT NOT NULL DEFAULT '',
    sku TEXT NOT NULL DEFAULT '',
    barcode TEXT NOT NULL DEFAULT '',
    name TEXT NOT NULL DEFAULT '',
    size TEXT NOT NULL DEFAULT '',
    color TEXT NOT NULL DEFAULT '',
    payload_json TEXT NOT NULL DEFAULT '{}',
    updated_at TEXT NOT NULL,
    UNIQUE(account_id, external_product_id, offer_id),
    FOREIGN KEY(account_id) REFERENCES marketplace_accounts(id)
);
CREATE TABLE IF NOT EXISTS marketplace_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    current_price REAL,
    old_price REAL,
    marketing_price REAL,
    currency TEXT NOT NULL DEFAULT 'RUB',
    payload_json TEXT NOT NULL DEFAULT '{}',
    observed_at TEXT NOT NULL,
    FOREIGN KEY(product_id) REFERENCES marketplace_products(id)
);
CREATE TABLE IF NOT EXISTS marketplace_stocks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    warehouse_type TEXT NOT NULL DEFAULT '',
    warehouse_name TEXT NOT NULL DEFAULT '',
    stock INTEGER NOT NULL DEFAULT 0,
    reserved INTEGER NOT NULL DEFAULT 0,
    available INTEGER NOT NULL DEFAULT 0,
    payload_json TEXT NOT NULL DEFAULT '{}',
    observed_at TEXT NOT NULL,
    FOREIGN KEY(product_id) REFERENCES marketplace_products(id)
);
CREATE TABLE IF NOT EXISTS marketplace_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    external_order_id TEXT NOT NULL,
    posting_number TEXT NOT NULL DEFAULT '',
    warehouse_type TEXT NOT NULL DEFAULT 'FBS',
    status TEXT NOT NULL DEFAULT '',
    shipment_date TEXT NOT NULL DEFAULT '',
    payload_json TEXT NOT NULL DEFAULT '{}',
    updated_at TEXT NOT NULL,
    UNIQUE(account_id, external_order_id),
    FOREIGN KEY(account_id) REFERENCES marketplace_accounts(id)
);
CREATE TABLE IF NOT EXISTS marketplace_order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    external_product_id TEXT NOT NULL DEFAULT '',
    offer_id TEXT NOT NULL DEFAULT '',
    sku TEXT NOT NULL DEFAULT '',
    name TEXT NOT NULL DEFAULT '',
    quantity INTEGER NOT NULL DEFAULT 0,
    payload_json TEXT NOT NULL DEFAULT '{}',
    FOREIGN KEY(order_id) REFERENCES marketplace_orders(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS marketplace_sync_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    products_count INTEGER NOT NULL DEFAULT 0,
    prices_count INTEGER NOT NULL DEFAULT 0,
    stocks_count INTEGER NOT NULL DEFAULT 0,
    orders_count INTEGER NOT NULL DEFAULT 0,
    error_message TEXT NOT NULL DEFAULT '',
    started_at TEXT NOT NULL,
    finished_at TEXT,
    FOREIGN KEY(account_id) REFERENCES marketplace_accounts(id)
);
CREATE TABLE IF NOT EXISTS marketplace_production_links (
    marketplace_product_id INTEGER PRIMARY KEY,
    production_product_name TEXT NOT NULL DEFAULT '',
    production_size TEXT NOT NULL DEFAULT '',
    production_color TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'unmatched',
    route_configured INTEGER NOT NULL DEFAULT 0,
    source TEXT NOT NULL DEFAULT 'auto',
    updated_at TEXT NOT NULL,
    FOREIGN KEY(marketplace_product_id) REFERENCES marketplace_products(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_marketplace_products_account ON marketplace_products(account_id, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_marketplace_production_links_status ON marketplace_production_links(status, production_product_name);
CREATE INDEX IF NOT EXISTS idx_marketplace_stocks_product ON marketplace_stocks(product_id, observed_at DESC);
CREATE INDEX IF NOT EXISTS idx_marketplace_stocks_latest ON marketplace_stocks(product_id, warehouse_type, warehouse_name, id DESC);
CREATE INDEX IF NOT EXISTS idx_marketplace_prices_latest ON marketplace_prices(product_id, id DESC);
CREATE INDEX IF NOT EXISTS idx_marketplace_orders_account ON marketplace_orders(account_id, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_marketplace_sync_runs_account ON marketplace_sync_runs(account_id, started_at DESC);
CREATE TABLE IF NOT EXISTS marketplace_supplies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    marketplace TEXT NOT NULL,
    account_id INTEGER,
    external_supply_id TEXT NOT NULL,
    external_preorder_id TEXT NOT NULL DEFAULT '',
    external_status TEXT NOT NULL DEFAULT '',
    canonical_status TEXT NOT NULL DEFAULT 'EXTERNAL_DRAFT',
    supply_type TEXT NOT NULL DEFAULT '',
    destination_type TEXT NOT NULL DEFAULT '',
    destination_id TEXT NOT NULL DEFAULT '',
    destination_name TEXT NOT NULL DEFAULT '',
    macrolocal_cluster_id TEXT NOT NULL DEFAULT '',
    planned_at TEXT,
    timeslot_from TEXT,
    timeslot_to TEXT,
    created_at_external TEXT,
    updated_at_external TEXT,
    last_synced_at TEXT NOT NULL,
    payload_json TEXT NOT NULL DEFAULT '{}',
    warehouse_shipment_id INTEGER,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(marketplace, account_id, external_supply_id),
    FOREIGN KEY(account_id) REFERENCES marketplace_accounts(id)
);
CREATE TABLE IF NOT EXISTS marketplace_supply_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supply_id INTEGER NOT NULL,
    marketplace_product_id INTEGER,
    external_product_id TEXT NOT NULL DEFAULT '',
    offer_id TEXT NOT NULL DEFAULT '',
    sku TEXT NOT NULL DEFAULT '',
    name TEXT NOT NULL DEFAULT '',
    barcode TEXT NOT NULL DEFAULT '',
    size TEXT NOT NULL DEFAULT '',
    color TEXT NOT NULL DEFAULT '',
    quantity INTEGER NOT NULL DEFAULT 0,
    mapped_status TEXT NOT NULL DEFAULT 'unmatched',
    payload_json TEXT NOT NULL DEFAULT '{}',
    FOREIGN KEY(supply_id) REFERENCES marketplace_supplies(id) ON DELETE CASCADE,
    FOREIGN KEY(marketplace_product_id) REFERENCES marketplace_products(id)
);
CREATE TABLE IF NOT EXISTS warehouse_shipments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    number TEXT NOT NULL UNIQUE,
    source_type TEXT NOT NULL DEFAULT 'marketplace_supply',
    source_id INTEGER,
    marketplace TEXT NOT NULL DEFAULT '',
    external_supply_id TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'WAITING_RESERVATION',
    destination_name TEXT NOT NULL DEFAULT '',
    planned_at TEXT,
    total_quantity INTEGER NOT NULL DEFAULT 0,
    reserved_quantity INTEGER NOT NULL DEFAULT 0,
    picked_quantity INTEGER NOT NULL DEFAULT 0,
    packed_quantity INTEGER NOT NULL DEFAULT 0,
    notes TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(source_type, source_id),
    FOREIGN KEY(source_id) REFERENCES marketplace_supplies(id)
);
CREATE TABLE IF NOT EXISTS warehouse_shipment_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    shipment_id INTEGER NOT NULL,
    marketplace_product_id INTEGER,
    product_key TEXT NOT NULL DEFAULT '',
    name TEXT NOT NULL DEFAULT '',
    article TEXT NOT NULL DEFAULT '',
    barcode TEXT NOT NULL DEFAULT '',
    size TEXT NOT NULL DEFAULT '',
    color TEXT NOT NULL DEFAULT '',
    quantity INTEGER NOT NULL DEFAULT 0,
    reserved_quantity INTEGER NOT NULL DEFAULT 0,
    picked_quantity INTEGER NOT NULL DEFAULT 0,
    packed_quantity INTEGER NOT NULL DEFAULT 0,
    from_location_code TEXT NOT NULL DEFAULT '',
    mapping_status TEXT NOT NULL DEFAULT 'unmatched',
    FOREIGN KEY(shipment_id) REFERENCES warehouse_shipments(id) ON DELETE CASCADE,
    FOREIGN KEY(marketplace_product_id) REFERENCES marketplace_products(id)
);
-- Allocation is intentionally a separate row: one marketplace position may
-- need to be picked from several address cells.
CREATE TABLE IF NOT EXISTS warehouse_shipment_allocations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    shipment_item_id INTEGER NOT NULL,
    location_code TEXT NOT NULL,
    product_key_json TEXT NOT NULL DEFAULT '{}',
    quantity INTEGER NOT NULL DEFAULT 0,
    reserved_quantity INTEGER NOT NULL DEFAULT 0,
    picked_quantity INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(shipment_item_id, location_code),
    FOREIGN KEY(shipment_item_id) REFERENCES warehouse_shipment_items(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS warehouse_shipment_pick_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    shipment_id INTEGER NOT NULL,
    allocation_id INTEGER NOT NULL,
    request_key TEXT NOT NULL UNIQUE,
    quantity INTEGER NOT NULL,
    employee_id INTEGER,
    created_at TEXT NOT NULL,
    FOREIGN KEY(shipment_id) REFERENCES warehouse_shipments(id) ON DELETE CASCADE,
    FOREIGN KEY(allocation_id) REFERENCES warehouse_shipment_allocations(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS marketplace_sync_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    marketplace TEXT NOT NULL,
    event_type TEXT NOT NULL,
    severity TEXT NOT NULL DEFAULT 'info',
    external_id TEXT NOT NULL DEFAULT '',
    message TEXT NOT NULL,
    payload_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_marketplace_supplies_status ON marketplace_supplies(marketplace, canonical_status, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_marketplace_supply_items_supply ON marketplace_supply_items(supply_id);
CREATE INDEX IF NOT EXISTS idx_warehouse_shipments_status ON warehouse_shipments(status, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_warehouse_shipment_allocations_item ON warehouse_shipment_allocations(shipment_item_id, location_code);
CREATE INDEX IF NOT EXISTS idx_marketplace_sync_events_created ON marketplace_sync_events(created_at DESC);
"""


class MarketplaceError(RuntimeError):
    def __init__(self, message: str, *, code: str = "marketplace_error"):
        super().__init__(message)
        self.code = code


def ensure_schema(conn: sqlite3.Connection | None = None) -> None:
    owned = conn is None
    connection = conn or get_db_connection()
    try:
        if connection.row_factory is None:
            connection.row_factory = sqlite3.Row
        connection.executescript(SCHEMA_SQL)
        link_columns = {
            row[1] for row in connection.execute(
                "PRAGMA table_info(marketplace_production_links)"
            ).fetchall()
        }
        if "route_configured" not in link_columns:
            connection.execute(
                "ALTER TABLE marketplace_production_links "
                "ADD COLUMN route_configured INTEGER NOT NULL DEFAULT 0"
            )
        connection.commit()
    finally:
        if owned:
            connection.close()


def _json(value) -> str:
    return json.dumps(value if value is not None else {}, ensure_ascii=False, separators=(",", ":"))


def _now() -> str:
    return local_now().isoformat(timespec="seconds")


def _number(value) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(str(value).replace(",", "."))
    except (TypeError, ValueError):
        return None


def _int(value, default: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _text(value) -> str:
    return "" if value is None else str(value).strip()


MARKETPLACE_SUPPLY_STATUSES = (
    "EXTERNAL_DRAFT", "PLANNED", "WAITING_RESERVATION", "SHORTAGE",
    "READY_TO_PICK", "PICKING", "PICKED", "PACKING", "DOCUMENTS_REQUIRED",
    "READY_TO_HANDOVER", "HANDED_OVER", "ACCEPTING", "ACCEPTED",
    "PARTIALLY_ACCEPTED", "SHIPPED_FROM_PRODUCTION", "CANCELLED", "SYNC_ERROR",
)

# Only these Ozon states still require preparation by the seller. The Ozon
# list endpoint also returns transferred, accepted, completed and cancelled
# history; those rows must not become new warehouse work.
OZON_ACTIONABLE_SUPPLY_STATES = frozenset({"DATA_FILLING", "READY_TO_SUPPLY"})


def supply_is_actionable(marketplace: str, external_status: object) -> bool:
    if _text(marketplace).lower() != "ozon":
        return True
    return _text(external_status).upper() in OZON_ACTIONABLE_SUPPLY_STATES


def canonical_supply_status(marketplace: str, external_status: object) -> str:
    """Map a marketplace status to the internal, read-only warehouse state."""
    status = _text(external_status).lower().replace("-", "_").replace(" ", "_")
    if status in {"data_filling", "ready_to_supply"}:
        return "PLANNED"
    if any(token in status for token in ("cancel", "reject", "declin")):
        return "CANCELLED"
    if any(token in status for token in ("accept", "received", "delivered", "complete")):
        return "ACCEPTED"
    if any(token in status for token in ("handover", "handed", "transit", "shipped")):
        return "HANDED_OVER"
    if any(token in status for token in ("pack", "package")):
        return "PACKING"
    if any(token in status for token in ("pick", "assembly")):
        return "READY_TO_PICK"
    if any(token in status for token in ("plan", "ready", "created", "new")):
        return "PLANNED"
    if not status:
        return "EXTERNAL_DRAFT"
    return "EXTERNAL_DRAFT"


def _sync_event(conn: sqlite3.Connection, marketplace: str, event_type: str, message: str,
                *, severity: str = "info", external_id: str = "", payload: object = None) -> None:
    conn.execute(
        "INSERT INTO marketplace_sync_events (marketplace,event_type,severity,external_id,message,payload_json,created_at) VALUES (?,?,?,?,?,?,?)",
        (_text(marketplace), _text(event_type), _text(severity) or "info", _text(external_id), _text(message), _json(payload), _now()),
    )


def upsert_marketplace_supply(conn: sqlite3.Connection, payload: dict, *, marketplace: str,
                              account_id: int | None = None) -> int:
    """Persist an external supply without sending any mutation to a marketplace."""
    external_id = _text(payload.get("id") or payload.get("supply_id") or payload.get("supplyId") or payload.get("number"))
    if not external_id:
        raise MarketplaceError("У поставки нет внешнего идентификатора.", code="supply_id_missing")
    now = _now()
    external_status = _text(payload.get("status") or payload.get("state"))
    canonical = canonical_supply_status(marketplace, external_status)
    # The marketplace is the source of truth for its external state, but while
    # an actionable supply is being processed the employee must see the local
    # warehouse state rather than have it reset to "Запланирована" on every
    # read-only sync.
    existing = conn.execute(
        """SELECT s.warehouse_shipment_id,ws.status AS warehouse_status
             FROM marketplace_supplies s
        LEFT JOIN warehouse_shipments ws ON ws.id=s.warehouse_shipment_id
            WHERE s.marketplace=? AND s.account_id IS ? AND s.external_supply_id=?""",
        (_text(marketplace), account_id, external_id),
    ).fetchone()
    if existing and supply_is_actionable(marketplace, external_status):
        warehouse_status = _text(existing["warehouse_status"])
        if warehouse_status in {
            "WAITING_RESERVATION", "SHORTAGE", "READY_TO_PICK", "PICKING",
            "PICKED", "PACKING", "READY_TO_HANDOVER", "SHIPPED",
        }:
            canonical = "SHIPPED_FROM_PRODUCTION" if warehouse_status == "SHIPPED" else warehouse_status
    destination = payload.get("destination") if isinstance(payload.get("destination"), dict) else {}
    timeslot = payload.get("timeslot") if isinstance(payload.get("timeslot"), dict) else {}
    conn.execute(
        """INSERT INTO marketplace_supplies
           (marketplace,account_id,external_supply_id,external_preorder_id,external_status,canonical_status,
            supply_type,destination_type,destination_id,destination_name,macrolocal_cluster_id,planned_at,
            timeslot_from,timeslot_to,created_at_external,updated_at_external,last_synced_at,payload_json,created_at,updated_at)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
           ON CONFLICT(marketplace,account_id,external_supply_id) DO UPDATE SET
            external_preorder_id=excluded.external_preorder_id, external_status=excluded.external_status,
            canonical_status=excluded.canonical_status, supply_type=excluded.supply_type,
            destination_type=excluded.destination_type, destination_id=excluded.destination_id,
            destination_name=excluded.destination_name, macrolocal_cluster_id=excluded.macrolocal_cluster_id,
            planned_at=excluded.planned_at, timeslot_from=excluded.timeslot_from, timeslot_to=excluded.timeslot_to,
            created_at_external=excluded.created_at_external, updated_at_external=excluded.updated_at_external,
            last_synced_at=excluded.last_synced_at, payload_json=excluded.payload_json, updated_at=excluded.updated_at""",
        (
            _text(marketplace), account_id, external_id,
            _text(payload.get("preorder_id") or payload.get("preorderId")), external_status, canonical,
            _text(payload.get("type") or payload.get("supply_type")), _text(destination.get("type")),
            _text(destination.get("id")), _text(destination.get("name") or payload.get("destination_name")),
            _text(payload.get("macrolocal_cluster_id") or payload.get("macro_local_cluster_id")),
            _text(payload.get("planned_at") or payload.get("shipment_date")),
            _text(timeslot.get("from") or timeslot.get("start")), _text(timeslot.get("to") or timeslot.get("end")),
            _text(payload.get("created_at")), _text(payload.get("updated_at")), now, _json(payload), now, now,
        ),
    )
    row = conn.execute(
        "SELECT id FROM marketplace_supplies WHERE marketplace=? AND account_id IS ? AND external_supply_id=?",
        (_text(marketplace), account_id, external_id),
    ).fetchone()
    supply_id = int(row[0])
    conn.execute("DELETE FROM marketplace_supply_items WHERE supply_id=?", (supply_id,))
    items = payload.get("items") or payload.get("products") or []
    if isinstance(items, dict):
        items = items.get("items") or items.get("products") or []
    if not isinstance(items, list):
        items = []
    for item in items:
        if not isinstance(item, dict):
            continue
        offer_id = _text(item.get("offer_id") or item.get("offerId") or item.get("article"))
        sku = _text(item.get("sku") or item.get("fbo_sku") or item.get("fbs_sku"))
        external_product_id = _text(item.get("product_id") or item.get("id") or item.get("external_product_id"))
        product = None
        if account_id is not None:
            product = conn.execute(
                "SELECT id,barcode,size,color,name FROM marketplace_products WHERE account_id=? AND (external_product_id=? OR offer_id=? OR sku=?) ORDER BY id DESC LIMIT 1",
                (account_id, external_product_id, offer_id, sku),
            ).fetchone()
        quantity = max(0, _int(item.get("quantity") or item.get("count") or item.get("qty")))
        conn.execute(
            "INSERT INTO marketplace_supply_items (supply_id,marketplace_product_id,external_product_id,offer_id,sku,name,barcode,size,color,quantity,mapped_status,payload_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (supply_id, product[0] if product else None, external_product_id, offer_id, sku,
             _text(item.get("name") or item.get("title") or (product[4] if product else "")),
             _text(item.get("barcode") or (product[1] if product else "")),
             _text(item.get("size") or (product[2] if product else "")),
             _text(item.get("color") or (product[3] if product else "")), quantity,
             "matched" if product else "unmatched", _json(item)),
        )
    if any(_text(item.get("offer_id") or item.get("sku") or item.get("product_id")) and not conn.execute("SELECT 1 FROM marketplace_supply_items WHERE supply_id=? AND mapped_status='unmatched' LIMIT 1", (supply_id,)).fetchone() for item in items if isinstance(item, dict)):
        pass
    if external_status and canonical == "EXTERNAL_DRAFT" and external_status.lower() not in {"draft", "new"}:
        _sync_event(conn, marketplace, "unknown_supply_status", f"Неизвестный статус поставки: {external_status}", severity="warning", external_id=external_id, payload=payload)
    return supply_id


def project_ozon_supplies_from_postgres(rows: list[dict]) -> dict:
    """Project PostgreSQL Ozon supplies into the local WMS operational model."""

    conn = get_db_connection()
    ensure_schema(conn)
    account_name = os.getenv("OZON_ACCOUNT_NAME", "Основной Ozon").strip() or "Основной Ozon"
    account_id = _account(conn, "ozon", account_name, os.getenv("OZON_CLIENT_ID", "").strip())
    projected = 0
    try:
        for payload in rows:
            if not isinstance(payload, dict):
                continue
            upsert_marketplace_supply(conn, payload, marketplace="ozon", account_id=account_id)
            projected += 1
        _sync_event(
            conn,
            "ozon",
            "supplies_projected",
            f"Поставки FBO обновлены из PostgreSQL: {projected}.",
            payload={"count": projected, "source": "postgresql"},
        )
        conn.commit()
        return {"ok": True, "projected": projected}
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _supply_rows(conn: sqlite3.Connection, *, marketplace: str = "", status: str = "", search: str = "", limit: int = 100,
                 active_only: bool = False) -> list[dict]:
    clauses, args = [], []
    if marketplace and marketplace != "all":
        clauses.append("s.marketplace=?"); args.append(marketplace)
    if status:
        clauses.append("s.canonical_status=?"); args.append(status)
    if search:
        term = f"%{search.lower()}%"
        clauses.append("(lower(s.external_supply_id) LIKE ? OR lower(s.destination_name) LIKE ? OR lower(s.external_status) LIKE ?)")
        args.extend([term, term, term])
    if active_only:
        placeholders = ",".join("?" for _ in OZON_ACTIONABLE_SUPPLY_STATES)
        clauses.append(f"(s.marketplace<>'ozon' OR upper(s.external_status) IN ({placeholders}))")
        args.extend(sorted(OZON_ACTIONABLE_SUPPLY_STATES))
    where = " WHERE " + " AND ".join(clauses) if clauses else ""
    args.append(max(1, min(500, int(limit or 100))))
    rows = conn.execute(f"""SELECT s.id,s.marketplace,s.external_supply_id,s.external_preorder_id,s.external_status,
            s.canonical_status,s.supply_type,s.destination_name,s.macrolocal_cluster_id,s.planned_at,
            s.timeslot_from,s.timeslot_to,s.last_synced_at,s.warehouse_shipment_id,ws.number AS warehouse_shipment_number,ws.status AS warehouse_shipment_status,s.updated_at,
            COUNT(i.id) AS item_count, COALESCE(SUM(i.quantity),0) AS total_quantity,
            SUM(CASE WHEN i.mapped_status='unmatched' THEN 1 ELSE 0 END) AS unmatched_count
        FROM marketplace_supplies s LEFT JOIN marketplace_supply_items i ON i.supply_id=s.id
        LEFT JOIN warehouse_shipments ws ON ws.id=s.warehouse_shipment_id
        {where} GROUP BY s.id ORDER BY s.updated_at DESC LIMIT ?""", args).fetchall()
    result = [dict(row) for row in rows]
    for row in result:
        row["is_actionable"] = supply_is_actionable(row.get("marketplace", ""), row.get("external_status", ""))
    return result


def marketplace_supplies(*, marketplace: str = "", status: str = "", search: str = "", limit: int = 100) -> dict:
    conn = get_db_connection(); ensure_schema(conn)
    rows = _supply_rows(conn, marketplace=marketplace, status=status, search=search, limit=limit)
    counts = {key: 0 for key in MARKETPLACE_SUPPLY_STATUSES}
    for row in conn.execute("SELECT canonical_status,COUNT(*) AS count FROM marketplace_supplies GROUP BY canonical_status"):
        counts[row[0]] = row[1]
    conn.close()
    return {"ok": True, "supplies": rows, "counts": counts, "statuses": list(MARKETPLACE_SUPPLY_STATUSES)}


def marketplace_supply_detail(supply_id: int) -> dict | None:
    conn = get_db_connection(); ensure_schema(conn)
    row = conn.execute("SELECT * FROM marketplace_supplies WHERE id=?", (int(supply_id),)).fetchone()
    if row is None:
        conn.close(); return None
    items = [dict(item) for item in conn.execute("SELECT * FROM marketplace_supply_items WHERE supply_id=? ORDER BY id", (int(supply_id),))]
    shipment = None
    if row["warehouse_shipment_id"]:
        shipment = conn.execute("SELECT * FROM warehouse_shipments WHERE id=?", (row["warehouse_shipment_id"],)).fetchone()
        shipment = dict(shipment) if shipment else None
    result = dict(row); result["items"] = items; result["warehouse_shipment"] = shipment
    conn.close(); return result


def create_internal_shipment_for_supply(supply_id: int) -> dict:
    """Create the internal picking document; reservation is a separate WMS step."""
    conn = get_db_connection(); ensure_schema(conn)
    supply = conn.execute("SELECT * FROM marketplace_supplies WHERE id=?", (int(supply_id),)).fetchone()
    if supply is None:
        conn.close(); return {"ok": False, "message": "Поставка не найдена."}
    existing = conn.execute("SELECT id,number,status FROM warehouse_shipments WHERE source_type='marketplace_supply' AND source_id=?", (int(supply_id),)).fetchone()
    if existing:
        conn.close(); return {"ok": True, "shipment": dict(existing), "created": False}
    if not supply_is_actionable(supply["marketplace"], supply["external_status"]):
        conn.close()
        return {
            "ok": False,
            "code": "supply_not_actionable",
            "message": "Задание складу можно создать только для актуальной поставки Ozon.",
        }
    unmatched = conn.execute("SELECT COUNT(*) FROM marketplace_supply_items WHERE supply_id=? AND mapped_status='unmatched'", (int(supply_id),)).fetchone()[0]
    if unmatched:
        _sync_event(conn, supply["marketplace"], "mapping_required", "Поставка не передана на склад: есть не сопоставленные товары.", severity="critical", external_id=supply["external_supply_id"])
        conn.commit(); conn.close()
        return {"ok": False, "code": "mapping_required", "message": "Сначала сопоставьте все товары поставки с номенклатурой производства."}
    item_count = conn.execute(
        "SELECT COUNT(*) FROM marketplace_supply_items WHERE supply_id=?",
        (int(supply_id),),
    ).fetchone()[0]
    if not item_count:
        conn.close()
        return {"ok": False, "code": "empty_supply", "message": "Ozon ещё не передал состав этой поставки."}
    now = _now()
    number = f"MP-{int(supply_id):06d}"
    items = conn.execute("SELECT * FROM marketplace_supply_items WHERE supply_id=? ORDER BY id", (int(supply_id),)).fetchall()
    total = sum(max(0, int(item["quantity"] or 0)) for item in items)
    cursor = conn.execute("INSERT INTO warehouse_shipments (number,source_id,marketplace,external_supply_id,status,destination_name,planned_at,total_quantity,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
                          (number, int(supply_id), supply["marketplace"], supply["external_supply_id"], "WAITING_RESERVATION", supply["destination_name"], supply["planned_at"], total, now, now))
    shipment_id = cursor.lastrowid
    for item in items:
        conn.execute("INSERT INTO warehouse_shipment_items (shipment_id,marketplace_product_id,product_key,name,article,barcode,size,color,quantity,mapping_status) VALUES (?,?,?,?,?,?,?,?,?,?)",
                      (shipment_id, item["marketplace_product_id"], item["offer_id"] or item["sku"] or item["external_product_id"], item["name"], item["offer_id"], item["barcode"], item["size"], item["color"], item["quantity"], item["mapped_status"]))
    conn.execute("UPDATE marketplace_supplies SET warehouse_shipment_id=?,canonical_status='WAITING_RESERVATION',updated_at=? WHERE id=?", (shipment_id, now, int(supply_id)))
    conn.commit(); conn.close()
    return {"ok": True, "created": True, "shipment": {"id": shipment_id, "number": number, "status": "WAITING_RESERVATION", "total_quantity": total}}


def warehouse_shipment_tasks(*, limit: int = 100) -> list[dict]:
    """Return employee-facing marketplace shipment tasks by operational status.

    Old historical marketplace rows are deliberately not turned into new work:
    only an active Ozon supply, an already started task, or a completed local
    task appears here. Empty legacy WB tasks are hidden as well.
    """
    conn = get_db_connection(); ensure_schema(conn)
    rows = conn.execute(
        """SELECT s.id,s.number,s.marketplace,s.external_supply_id,s.status,s.destination_name,
                  s.total_quantity,s.reserved_quantity,s.picked_quantity,s.packed_quantity,
                  s.planned_at,s.created_at,s.updated_at,COUNT(i.id) AS item_count,ms.external_status
             FROM warehouse_shipments s
        LEFT JOIN warehouse_shipment_items i ON i.shipment_id=s.id
        LEFT JOIN marketplace_supplies ms ON ms.id=s.source_id
            WHERE s.status NOT IN ('CANCELLED')
              AND (s.total_quantity > 0 OR s.status IN ('SHIPPED','HANDED_OVER','ACCEPTED'))
              AND (
                    s.marketplace <> 'ozon'
                    OR upper(COALESCE(ms.external_status,'')) IN ('DATA_FILLING','READY_TO_SUPPLY')
                    OR s.status IN ('READY_TO_PICK','PICKING','PICKED','PACKING','READY_TO_HANDOVER','SHIPPED','HANDED_OVER','ACCEPTED')
              )
         GROUP BY s.id
         ORDER BY s.updated_at DESC
            LIMIT ?""",
        (max(1, min(500, int(limit or 100))),),
    ).fetchall()
    result = [dict(row) for row in rows]
    conn.close()
    return result


def _shipment_item_product_key(conn: sqlite3.Connection, item: sqlite3.Row) -> dict:
    """Build WMS identity by the marketplace article, not display text.

    Names and colours can be edited by a marketplace, while the seller article
    identifies the physical variant.  Prefer it over a stale product id from a
    historic supply snapshot and use the id only as a fallback.
    """
    article = _text(item["article"]) or _text(item["product_key"])
    link = conn.execute(
        """SELECT l.production_product_name,l.production_size,l.production_color,l.status
             FROM marketplace_products p
             JOIN marketplace_production_links l ON l.marketplace_product_id=p.id
            WHERE (?<>'' AND (p.offer_id=? OR p.sku=? OR p.external_product_id=?)) OR p.id=?
         ORDER BY CASE
             WHEN p.offer_id=? THEN 0
             WHEN p.sku=? THEN 1
             WHEN p.external_product_id=? THEN 2
             WHEN p.id=? THEN 3
             ELSE 4 END
            LIMIT 1""",
        (
            article, article, article, article, item["marketplace_product_id"],
            article, article, article, item["marketplace_product_id"],
        ),
    ).fetchone()
    product_name = _text(link["production_product_name"] if link else "") or _text(item["name"])
    size = _text(link["production_size"] if link else "") or _text(item["size"])
    color = _text(link["production_color"] if link else "") or _text(item["color"])
    if not product_name or not size or not color:
        raise MarketplaceError(
            f"Для позиции «{_text(item['name']) or _text(item['article'])}» не заполнены наименование, размер или цвет.",
            code="shipment_product_identity_missing",
        )
    return {
        "item_type": "finished", "product_name": product_name,
        "product_size": size, "product_color": color,
        "stage_name": "Готово", "ready_for_position": "Склад",
    }


def _refresh_shipment_counters(conn: sqlite3.Connection, shipment_id: int, *, status: str | None = None) -> None:
    now = _now()
    totals = conn.execute(
        """SELECT COALESCE(SUM(reserved_quantity),0),COALESCE(SUM(picked_quantity),0)
             FROM warehouse_shipment_items WHERE shipment_id=?""",
        (shipment_id,),
    ).fetchone()
    if status is None:
        current = conn.execute("SELECT status FROM warehouse_shipments WHERE id=?", (shipment_id,)).fetchone()
        status = current[0] if current else "WAITING_RESERVATION"
    conn.execute(
        """UPDATE warehouse_shipments
              SET reserved_quantity=?,picked_quantity=?,status=?,updated_at=? WHERE id=?""",
        (int(totals[0] or 0), int(totals[1] or 0), status, now, shipment_id),
    )


def _reserve_shipment_positions(items: list[tuple[int, dict, int, str]]) -> list[tuple[int, str, dict, int]]:
    """Reserve unbound address stock in one Postgres transaction.

    SQLite stores the task document; Postgres owns physical stock.  A caller
    writes allocations to SQLite only after this commit, and retries are safe
    because it requests only the still-unreserved quantity.
    """
    from wms.connection import get_pg_connection
    from wms.models import ProductKey

    conn = get_pg_connection()
    allocations: list[tuple[int, str, dict, int]] = []
    try:
        with conn.cursor() as cur:
            for item_id, key_data, needed, article in items:
                if needed <= 0:
                    continue
                # WMS stock itself keeps a production key, not the marketplace
                # article. Resolve each physical row through the same metadata
                # adapter that powers the warehouse-map product card, then use
                # the seller article/SKU as the only business selector.
                cur.execute(
                    """SELECT ws.id,ws.quantity,ws.reserved_quantity,l.code,
                              ws.item_type,ws.product_name,ws.product_size,ws.product_color,
                              ws.stage_name,ws.ready_for_position
                         FROM warehouse_stock ws
                         JOIN wms_locations l ON l.id=ws.location_id
                        WHERE ws.item_state='SELLABLE' AND ws.unit='шт' AND l.status='active'
                          AND ws.quantity > ws.reserved_quantity
                     ORDER BY l.pick_priority,l.route_order,l.code,ws.id""",
                )
                candidates = cur.fetchall()
                keys = [
                    {
                        "item_type": row[4], "product_name": row[5],
                        "product_size": row[6], "product_color": row[7],
                        "stage_name": row[8], "ready_for_position": row[9],
                    }
                    for row in candidates
                ]
                metadata = marketplace_metadata_for_wms_product_keys(keys) if keys else []
                article_key = _text(article).casefold()
                matching_ids = [
                    int(row[0]) for row, product in zip(candidates, metadata)
                    if product and article_key in {
                        _text(product.get("offer_id")).casefold(),
                        _text(product.get("sku")).casefold(),
                        _text(product.get("external_product_id")).casefold(),
                    }
                ]
                if not matching_ids:
                    continue
                placeholders = ",".join("%s" for _ in matching_ids)
                cur.execute(
                    f"""SELECT ws.id,ws.quantity,ws.reserved_quantity,l.code,
                               ws.item_type,ws.product_name,ws.product_size,ws.product_color,
                               ws.stage_name,ws.ready_for_position
                          FROM warehouse_stock ws
                          JOIN wms_locations l ON l.id=ws.location_id
                         WHERE ws.id IN ({placeholders})
                           AND ws.item_state='SELLABLE' AND ws.unit='шт' AND l.status='active'
                           AND ws.quantity > ws.reserved_quantity
                      ORDER BY l.pick_priority,l.route_order,l.code,ws.id FOR UPDATE""",
                    matching_ids,
                )
                remaining = int(needed)
                for row in cur.fetchall():
                    if remaining <= 0:
                        break
                    available = max(0, int(row[1]) - int(row[2]))
                    take = min(remaining, available)
                    if not take:
                        continue
                    cur.execute(
                        "UPDATE warehouse_stock SET reserved_quantity=reserved_quantity+%s,updated_at=now() WHERE id=%s",
                        (take, int(row[0])),
                    )
                    # A product can have been accepted at a different internal
                    # route step than the one used by the marketplace link.
                    # The physical cell is still a valid source when the item,
                    # variant and state match. Preserve its exact WMS key for
                    # the later scan and atomic pick.
                    actual_key = ProductKey(
                        item_type=str(row[4]), product_name=str(row[5]),
                        product_size=str(row[6]), product_color=str(row[7]),
                        stage_name=str(row[8]), ready_for_position=str(row[9]),
                    )
                    allocations.append((item_id, str(row[3]), actual_key.to_dict(), take))
                    remaining -= take
        conn.commit()
        return allocations
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def warehouse_shipment_task_detail(shipment_number: str) -> dict | None:
    conn = get_db_connection(); ensure_schema(conn)
    shipment = conn.execute("SELECT * FROM warehouse_shipments WHERE number=?", (_text(shipment_number),)).fetchone()
    if shipment is None:
        conn.close(); return None
    result = dict(shipment)
    items = []
    for row in conn.execute("SELECT * FROM warehouse_shipment_items WHERE shipment_id=? ORDER BY id", (shipment["id"],)):
        item = dict(row)
        item["allocations"] = [dict(value) for value in conn.execute(
            "SELECT * FROM warehouse_shipment_allocations WHERE shipment_item_id=? ORDER BY location_code,id", (row["id"],)
        )]
        items.append(item)
    result["items"] = items
    result["can_start"] = result["status"] in {"WAITING_RESERVATION", "SHORTAGE"}
    result["can_confirm"] = bool(items) and all(int(item["picked_quantity"] or 0) >= int(item["quantity"] or 0) for item in items)
    conn.close()
    return result


def start_warehouse_shipment_task(shipment_number: str) -> dict:
    """Reserve locations and make a marketplace shipment available for picking."""
    conn = get_db_connection(); ensure_schema(conn)
    try:
        shipment = conn.execute("SELECT * FROM warehouse_shipments WHERE number=?", (_text(shipment_number),)).fetchone()
        if shipment is None:
            return {"ok": False, "message": "Задание на отгрузку не найдено."}
        if shipment["status"] in {"SHIPPED", "HANDED_OVER", "ACCEPTED", "CANCELLED"}:
            return {"ok": False, "message": "Это задание уже завершено и недоступно для комплектации."}
        items_to_reserve = []
        for item in conn.execute("SELECT * FROM warehouse_shipment_items WHERE shipment_id=? ORDER BY id", (shipment["id"],)):
            missing = max(0, int(item["quantity"] or 0) - int(item["reserved_quantity"] or 0))
            if missing:
                items_to_reserve.append((
                    int(item["id"]), _shipment_item_product_key(conn, item), missing,
                    _text(item["article"]) or _text(item["product_key"]),
                ))
        allocations = _reserve_shipment_positions(items_to_reserve) if items_to_reserve else []
        now = _now()
        for item_id, location_code, product_key, quantity in allocations:
            conn.execute(
                """INSERT INTO warehouse_shipment_allocations
                   (shipment_item_id,location_code,product_key_json,quantity,reserved_quantity,picked_quantity,created_at,updated_at)
                   VALUES (?,?,?,?,?,?,?,?)
                   ON CONFLICT(shipment_item_id,location_code) DO UPDATE SET
                     quantity=warehouse_shipment_allocations.quantity+excluded.quantity,
                     reserved_quantity=warehouse_shipment_allocations.reserved_quantity+excluded.reserved_quantity,
                     updated_at=excluded.updated_at""",
                (item_id, location_code, _json(product_key), quantity, quantity, 0, now, now),
            )
            conn.execute(
                "UPDATE warehouse_shipment_items SET reserved_quantity=reserved_quantity+?,from_location_code=COALESCE(NULLIF(from_location_code,''),?) WHERE id=?",
                (quantity, location_code, item_id),
            )
        complete = conn.execute(
            "SELECT COUNT(*) FROM warehouse_shipment_items WHERE shipment_id=? AND reserved_quantity < quantity",
            (shipment["id"],),
        ).fetchone()[0] == 0
        _refresh_shipment_counters(conn, int(shipment["id"]), status="READY_TO_PICK" if complete else "SHORTAGE")
        conn.commit()
        detail = warehouse_shipment_task_detail(_text(shipment_number))
        message = (
            "Ячейки зарезервированы." if complete
            else ("Часть позиций зарезервирована; по остальным не хватает товара." if allocations
                  else "По артикулу поставки не найден адресный остаток для резервирования.")
        )
        return {"ok": True, "shipment": detail, "message": message}
    except MarketplaceError as error:
        conn.rollback(); return {"ok": False, "code": error.code, "message": str(error)}
    except Exception as error:
        conn.rollback(); return {"ok": False, "message": f"Не удалось подготовить отгрузку: {error}"}
    finally:
        conn.close()


def pick_warehouse_shipment_allocation(shipment_number: str, allocation_id: int, quantity: int, *, employee_id: int, location_code: str, request_key: str = "") -> dict:
    """Consume an already reserved line after the employee scans its cell."""
    from wms import operations as wms_operations
    from wms.models import ProductKey
    conn = get_db_connection(); ensure_schema(conn)
    try:
        row = conn.execute(
            """SELECT a.*,i.shipment_id,s.number,s.status FROM warehouse_shipment_allocations a
                 JOIN warehouse_shipment_items i ON i.id=a.shipment_item_id
                 JOIN warehouse_shipments s ON s.id=i.shipment_id
                WHERE a.id=? AND s.number=?""",
            (int(allocation_id), _text(shipment_number)),
        ).fetchone()
        if row is None:
            return {"ok": False, "message": "Позиция отгрузки не найдена."}
        if _text(row["status"]) in {"SHIPPED", "HANDED_OVER", "ACCEPTED", "CANCELLED"}:
            return {"ok": False, "message": "Отгрузка уже завершена."}
        if _text(location_code).upper() != _text(row["location_code"]).upper():
            return {"ok": False, "message": f"Сначала отсканируйте ячейку {row['location_code']}."}
        quantity = int(quantity)
        remaining = max(0, int(row["reserved_quantity"] or 0) - int(row["picked_quantity"] or 0))
        if quantity <= 0 or quantity > remaining:
            return {"ok": False, "message": f"Для этой позиции осталось отобрать {remaining} шт."}
        request_key = _text(request_key) or f"marketplace-pick:{row['shipment_id']}:{row['id']}:{uuid.uuid4().hex}"
        key_data = json.loads(row["product_key_json"] or "{}")
        operation = wms_operations.pick_reserved_for_shipment(
            ProductKey.from_dict(key_data), quantity,
            from_location_code=row["location_code"], shipment_id=int(row["shipment_id"]),
            employee_id=int(employee_id), request_key=request_key, reason=f"Комплектация поставки {row['number']}",
        )
        if not operation.ok:
            return {"ok": False, "message": operation.reason or "Не удалось отобрать товар из ячейки."}
        now = _now()
        event = conn.execute(
            "INSERT OR IGNORE INTO warehouse_shipment_pick_events (shipment_id,allocation_id,request_key,quantity,employee_id,created_at) VALUES (?,?,?,?,?,?)",
            (row["shipment_id"], row["id"], request_key, quantity, employee_id, now),
        )
        if event.rowcount:
            conn.execute("UPDATE warehouse_shipment_allocations SET picked_quantity=picked_quantity+?,updated_at=? WHERE id=?", (quantity, now, row["id"]))
            conn.execute("UPDATE warehouse_shipment_items SET picked_quantity=picked_quantity+? WHERE id=?", (quantity, row["shipment_item_id"]))
        all_picked = conn.execute(
            "SELECT COUNT(*) FROM warehouse_shipment_items WHERE shipment_id=? AND picked_quantity < quantity",
            (row["shipment_id"],),
        ).fetchone()[0] == 0
        _refresh_shipment_counters(conn, int(row["shipment_id"]), status="PICKED" if all_picked else "PICKING")
        conn.commit()
        return {"ok": True, "shipment": warehouse_shipment_task_detail(_text(shipment_number)), "message": "Позиция отобрана."}
    except (ValueError, json.JSONDecodeError) as error:
        conn.rollback(); return {"ok": False, "message": f"Некорректные данные позиции: {error}"}
    except Exception as error:
        conn.rollback(); return {"ok": False, "message": f"Не удалось выполнить подбор: {error}"}
    finally:
        conn.close()


def confirm_warehouse_shipment(shipment_number: str, *, employee_id: int) -> dict:
    """Mark a fully picked document as shipped from production."""
    conn = get_db_connection(); ensure_schema(conn)
    try:
        shipment = conn.execute("SELECT * FROM warehouse_shipments WHERE number=?", (_text(shipment_number),)).fetchone()
        if shipment is None:
            return {"ok": False, "message": "Задание на отгрузку не найдено."}
        if shipment["status"] == "SHIPPED":
            return {"ok": True, "shipment": warehouse_shipment_task_detail(_text(shipment_number)), "message": "Отгрузка уже подтверждена."}
        outstanding = conn.execute(
            "SELECT COUNT(*) FROM warehouse_shipment_items WHERE shipment_id=? AND picked_quantity < quantity",
            (shipment["id"],),
        ).fetchone()[0]
        if outstanding:
            return {"ok": False, "message": "Нельзя подтвердить отгрузку: собраны не все позиции."}
        now = _now()
        conn.execute(
            "UPDATE warehouse_shipments SET status='SHIPPED',packed_quantity=picked_quantity,updated_at=? WHERE id=?",
            (now, shipment["id"]),
        )
        if shipment["source_id"]:
            conn.execute(
                "UPDATE marketplace_supplies SET canonical_status='SHIPPED_FROM_PRODUCTION',updated_at=? WHERE id=?",
                (now, shipment["source_id"]),
            )
        _sync_event(conn, shipment["marketplace"], "shipment_confirmed", f"Отгрузка {shipment['number']} подтверждена сотрудником {employee_id}.", external_id=shipment["external_supply_id"])
        conn.commit()
        return {"ok": True, "shipment": warehouse_shipment_task_detail(_text(shipment_number)), "message": "Отгрузка подтверждена и передана в маркетплейсы."}
    except Exception as error:
        conn.rollback(); return {"ok": False, "message": f"Не удалось подтвердить отгрузку: {error}"}
    finally:
        conn.close()


def product_group_for(*values: object) -> tuple[str, str]:
    """Return a stable product group from the article/name/variant text.

    Ozon exposes product variants as separate rows.  Grouping therefore uses
    both the seller article (offer id/SKU) and the human-readable name, while
    ignoring size and colour differences.  Explicit product words win over
    the size fallback so a renamed article remains in the expected family.
    """

    text = " ".join(_text(value) for value in values if _text(value)).lower().replace("ё", "е")
    sizes = [int(value) for value in re.findall(r"(?<!\d)(?:8[6-9]|9\d|1[0-7]\d|18\d)(?!\d)", text)]

    if "костюм" in text:
        if "классическ" in text and "трикотаж" in text:
            return "suits-classic-knitted", "Костюм классический трикотажный"
        if "трикотаж" in text and "детск" in text:
            return "suits-knitted-children", "Костюм трикотажный детский"
        if "детск" in text:
            return "suits-children", "Костюм детский"
        return "suits", "Костюмы"
    if "кардиган" in text:
        has_child = any(token in text for token in ("детск", "дет.", "kids", "child"))
        has_teen = any(token in text for token in ("подрост", "подр.", "teen", "junior"))
        if has_child and not has_teen:
            return "cardigans-children", "Кардиганы детские"
        if has_teen and not has_child:
            return "cardigans-teens", "Кардиганы подростковые"
        if sizes and max(sizes) > 128 and min(sizes) >= 134:
            return "cardigans-teens", "Кардиганы подростковые"
        if sizes and max(sizes) <= 128:
            return "cardigans-children", "Кардиганы детские"
        return "cardigans", "Кардиганы"
    if "брюк" in text and "стрел" in text:
        return "trousers-arrows", "Брюки со стрелками"
    if "джог" in text:
        return "trousers-joggers", "Брюки-джоггеры"
    if "ползун" in text:
        return "trousers-pullers", "Брюки-ползунки"
    if "легин" in text:
        return "leggings", "Легинсы"
    if "шорт" in text:
        return "shorts", "Шорты"
    if "футбол" in text:
        return "tshirts", "Футболки"
    if "свитшот" in text:
        return "sweatshirts", "Свитшоты"
    if "бомбер" in text:
        has_child = any(token in text for token in ("детск", "дет.", "kids", "child"))
        has_teen = any(token in text for token in ("подрост", "подр.", "teen", "junior"))
        if has_child and not has_teen:
            return "bombers-children", "Бомбер детский"
        if has_teen and not has_child:
            return "bombers-teens", "Бомбер подростковый"
        if sizes and max(sizes) <= 128:
            return "bombers-children", "Бомбер детский"
        if sizes and min(sizes) >= 134:
            return "bombers-teens", "Бомбер подростковый"
        return "bombers", "Бомберы"
    if "юбк" in text and "шорт" in text:
        return "skirt-shorts", "Юбка-шорты"
    if "юбк" in text and "жакет" in text:
        return "skirts-jackets", "Юбки и жакеты"
    if "жакет" in text:
        return "jackets", "Жакеты"
    if "юбк" in text:
        return "skirts", "Юбки"
    if "брюк" in text:
        return "trousers", "Брюки"

    # Не превращаем техническую связку «название / offer_id / SKU» в имя
    # группы.  У Ozon встречаются карточки, где название равно артикулу
    # (например, «Кбшв-»); раньше в таком случае в интерфейс попадала вся
    # склеенная строка с SKU и каждая позиция становилась отдельной группой.
    name = _text(values[0]) if values else ""
    name_normalized = re.sub(r"[^a-zа-я0-9]+", "", name.lower().replace("ё", "е"))
    other_normalized = {
        re.sub(r"[^a-zа-я0-9]+", "", _text(value).lower().replace("ё", "е"))
        for value in values[1:]
        if _text(value)
    }
    fallback = re.sub(
        r"\b(?:\d{2,3}|черн\w*|син\w*|бел\w*|красн\w*|зелен\w*|сер\w*)\b",
        " ",
        name.lower().replace("ё", "е"),
    )
    fallback = " ".join(fallback.split())
    if fallback and name_normalized and name_normalized not in other_normalized:
        slug = re.sub(r"[^a-zа-я0-9]+", "-", fallback).strip("-")[:48] or "other"
        return f"other-{slug}", fallback.capitalize()
    return "other", "Прочие товары"


# Ozon contains individual selling variants. Production remains route-driven, so
# only a variant whose type, size and colour are supported by an existing route
# may become a factory/WMS product automatically. Everything else stays visible
# in the catalogue with status ``unmatched`` until its route is configured.
PRODUCTION_TARGET_BY_GROUP = {
    "trousers-joggers": "Брюки-джоггеры",
    "trousers-pullers": "Брюки-ползунки",
    "leggings": "Легинсы",
    "shorts": "Шорты",
    "tshirts": "Футболки",
    "sweatshirts": "Свитшоты",
    "cardigans": "Кардиган",
    "cardigans-children": "Кардиган",
    "cardigans-teens": "Кардиган",
    "bombers": "Бомбер",
    "bombers-children": "Бомбер",
    "bombers-teens": "Бомбер",
    "jackets": "Жакет для девочек",
    "skirt-shorts": "Юбка-шорты",
}


def _normalized_value(value: object) -> str:
    return re.sub(r"[^a-zа-я0-9]+", "", _text(value).lower().replace("ё", "е"))


def _production_size(value: object, allowed: list[str]) -> str:
    match = re.search(r"(?<!\d)(\d{2,3})(?!\d)", _text(value))
    candidate = match.group(1) if match else _text(value)
    return candidate if candidate in allowed else ""


def _production_color(value: object, allowed: list[str]) -> str:
    normalized = _normalized_value(value)
    for color in allowed:
        if _normalized_value(color) == normalized:
            return color
    return ""


def production_target_for_marketplace_product(row: dict) -> tuple[str, str, str] | None:
    """Map one marketplace variant to one existing factory route, if safe."""
    from catalog import COMMON_COLORS, PRODUCT_OPTIONS

    group_key, _ = product_group_for(
        row.get("name"), row.get("offer_id"), row.get("sku"), row.get("barcode"), row.get("size"),
    )
    if group_key.startswith("suits"):
        allowed_sizes = sorted(
            {
                str(size)
                for product in ("Брюки со стрелками детские", "Брюки со стрелками подростковые", "Кардиган")
                for size in PRODUCT_OPTIONS.get(product, {}).get("sizes", [])
            },
            key=lambda value: int(value),
        )
        allowed_colors = list(dict.fromkeys([
            *COMMON_COLORS,
            *(
                color
                for product in ("Брюки со стрелками детские", "Брюки со стрелками подростковые", "Кардиган")
                for color in PRODUCT_OPTIONS.get(product, {}).get("colors", [])
            ),
        ]))
        size = _production_size(row.get("size"), allowed_sizes)
        color = _production_color(row.get("color"), allowed_colors)
        if not size or not color:
            return None
        return "Костюм: брюки + кардиган", size, color
    if group_key == "trousers-arrows":
        raw_size = _production_size(row.get("size"), [str(size) for size in range(80, 170)])
        if raw_size and int(raw_size) <= 128:
            product_name = "Брюки со стрелками детские"
        elif raw_size and int(raw_size) >= 134:
            product_name = "Брюки со стрелками подростковые"
        else:
            return None
    else:
        product_name = PRODUCTION_TARGET_BY_GROUP.get(group_key, "")
    options = PRODUCT_OPTIONS.get(product_name)
    if not options:
        return None
    size = _production_size(row.get("size"), list(options.get("sizes") or []))
    color = _production_color(row.get("color"), list(options.get("colors") or []))
    if not size or not color:
        return None
    return product_name, size, color


def sync_production_links(conn: sqlite3.Connection, account_id: int) -> dict[str, int]:
    """Refresh the unified Ozon, production and WMS product catalogue.

    Every Ozon variant receives a stable internal product identity.  Supported
    factory products point to their real route identity; catalogue-only and
    historical products remain usable by WMS without pretending that a
    production route exists for them.
    """
    rows = conn.execute(
        "SELECT id,name,offer_id,sku,barcode,size,color FROM marketplace_products WHERE account_id=?",
        (account_id,),
    ).fetchall()
    linked = 0
    route_linked = 0
    catalog_only = 0
    now = _now()
    for source_row in rows:
        row = dict(source_row)
        target = production_target_for_marketplace_product(row)
        if target:
            product_name, size, color = target
            route_configured = 1
            source = "auto_route"
            route_linked += 1
        else:
            group_key, group_name = product_group_for(
                row.get("name"), row.get("offer_id"), row.get("sku"),
                row.get("barcode"), row.get("size"),
            )
            product_name = (
                _text(row.get("name"))
                if group_key == "other"
                else _text(group_name)
            ) or _text(row.get("offer_id") or row.get("sku")) or "Товар Ozon"
            size = _text(row.get("size")) or _production_size(
                row.get("offer_id"), [str(value) for value in range(40, 200)]
            ) or "Не указан"
            color = _text(row.get("color")) or "Не указан"
            route_configured = 0
            source = "ozon_catalog"
            catalog_only += 1
        status = "linked"
        linked += 1
        conn.execute(
            """INSERT INTO marketplace_production_links
               (marketplace_product_id,production_product_name,production_size,production_color,
                status,route_configured,source,updated_at)
               VALUES (?,?,?,?,?,?,?,?)
               ON CONFLICT(marketplace_product_id) DO UPDATE SET
                 production_product_name=excluded.production_product_name,
                 production_size=excluded.production_size,
                 production_color=excluded.production_color,
                 status=excluded.status,
                 route_configured=excluded.route_configured,
                 source=excluded.source,
                 updated_at=excluded.updated_at""",
            (row["id"], product_name, size, color, status, route_configured, source, now),
        )
    return {
        "linked": linked,
        "route_linked": route_linked,
        "catalog_only": catalog_only,
        "unmatched": 0,
    }


def _normalized_marketplace_barcode(value: object) -> str:
    barcode = "".join(character for character in _text(value) if ord(character) >= 32).strip()
    if re.match(r"^\][A-Za-z][0-9]", barcode):
        barcode = barcode[3:].strip()
    return barcode


def _marketplace_payload_barcodes(payload_json: object) -> set[str]:
    """Collect primary and alternate barcodes retained in marketplace JSON."""
    if isinstance(payload_json, str):
        try:
            payload_json = json.loads(payload_json or "{}")
        except (TypeError, ValueError):
            return set()
    found: set[str] = set()

    def visit(value: object, barcode_context: bool = False) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                visit(child, barcode_context or "barcode" in str(key).casefold())
            return
        if isinstance(value, list):
            for child in value:
                visit(child, barcode_context)
            return
        if barcode_context:
            normalized = _normalized_marketplace_barcode(value)
            if normalized:
                found.add(normalized)

    visit(payload_json)
    return found


def resolve_production_product_by_barcode(barcode: str) -> dict | None:
    """Resolve an Ozon barcode to a linked internal product key for WMS scans."""
    if os.getenv("MARKETPLACE_PHASE1A_ENABLED", "0").strip() == "1":
        from marketplace_pg import MarketplacePGRepository
        from marketplace_phase1a import account_key

        return MarketplacePGRepository().resolve_production_product_by_barcode(account_key(), barcode)
    value = _normalized_marketplace_barcode(barcode)
    if not value:
        return None
    conn = get_db_connection()
    try:
        ensure_schema(conn)
        account_name = os.getenv("OZON_ACCOUNT_NAME", "Основной Ozon").strip() or "Основной Ozon"
        account_id = _account(conn, "ozon", account_name, os.getenv("OZON_CLIENT_ID", "").strip())
        sync_production_links(conn, account_id)
        row = conn.execute(
            """SELECT l.production_product_name,l.production_size,l.production_color,p.payload_json,p.barcode
                 FROM marketplace_products p
                 JOIN marketplace_production_links l ON l.marketplace_product_id=p.id
                 WHERE p.account_id=? AND p.barcode=? AND l.status='linked'
                 LIMIT 1""",
            (account_id, value),
        ).fetchone()
        if not row:
            linked_rows = conn.execute(
                """SELECT l.production_product_name,l.production_size,l.production_color,p.payload_json,p.barcode
                     FROM marketplace_products p
                     JOIN marketplace_production_links l ON l.marketplace_product_id=p.id
                     WHERE p.account_id=? AND l.status='linked'""",
                (account_id,),
            ).fetchall()
            row = next(
                (
                    candidate for candidate in linked_rows
                    if value == _normalized_marketplace_barcode(candidate[4])
                    or value in _marketplace_payload_barcodes(candidate[3])
                ),
                None,
            )
        conn.commit()
        if not row:
            return None
        return {
            "item_type": "finished",
            "product_name": row[0],
            "product_size": row[1],
            "product_color": row[2],
            "stage_name": "Упаковано",
            "ready_for_position": "Склад",
        }
    finally:
        conn.close()


def _find_nested_text(value, keys: tuple[str, ...]) -> str:
    if isinstance(value, dict):
        for key in keys:
            if value.get(key) not in (None, "") and not isinstance(value.get(key), (dict, list)):
                return _text(value[key])
        for child in value.values():
            found = _find_nested_text(child, keys)
            if found:
                return found
    elif isinstance(value, list):
        for child in value:
            found = _find_nested_text(child, keys)
            if found:
                return found
    return ""


# Ozon keeps the value of the clothing colour in a common characteristic and
# uses several size characteristics depending on the category.  We keep the
# IDs here rather than parsing an article like ``БДШВ-1/104``: the catalogue is
# the source of truth and an article is not guaranteed to contain a size.
OZON_COLOR_ATTRIBUTE_IDS = {10096}
OZON_SIZE_ATTRIBUTE_IDS = (4295, 9533, 4508)


def _product_identity(row: dict) -> tuple[str, str]:
    return (_text(row.get("product_id") or row.get("id")), _text(row.get("offer_id")))


def _attribute_value(row: dict, attribute_ids: set[int] | tuple[int, ...]) -> str:
    wanted = set(attribute_ids)
    for attribute in row.get("attributes") or []:
        if not isinstance(attribute, dict) or _int(attribute.get("id"), -1) not in wanted:
            continue
        for value in attribute.get("values") or []:
            if isinstance(value, dict) and _text(value.get("value")):
                return _text(value["value"])
    return ""


def _enrich_catalog_products(products: list[dict], details: list[dict], attributes: list[dict]) -> list[dict]:
    """Merge Ozon list, detailed-card and characteristic responses by product."""
    details_by_id = {_product_identity(row)[0]: row for row in details if _product_identity(row)[0]}
    attributes_by_id = {_product_identity(row)[0]: row for row in attributes if _product_identity(row)[0]}
    enriched: list[dict] = []
    for product in products:
        product_id, _ = _product_identity(product)
        detail = details_by_id.get(product_id, {})
        attribute_row = attributes_by_id.get(product_id, {})
        row = {**product, **detail}
        # ``/v3/product/info/list`` calls the identifier ``id``. Preserve the
        # original ``product_id`` so subsequent code has one stable key.
        if product_id:
            row["product_id"] = product_id
        detail_barcodes = detail.get("barcodes") if isinstance(detail.get("barcodes"), list) else []
        attribute_barcodes = attribute_row.get("barcodes") if isinstance(attribute_row.get("barcodes"), list) else []
        if not row.get("barcode"):
            row["barcode"] = _text(detail.get("barcode") or (detail_barcodes[0] if detail_barcodes else "") or attribute_row.get("barcode") or (attribute_barcodes[0] if attribute_barcodes else ""))
        if not row.get("color"):
            row["color"] = _attribute_value(attribute_row, OZON_COLOR_ATTRIBUTE_IDS)
        if not row.get("size"):
            row["size"] = _attribute_value(attribute_row, OZON_SIZE_ATTRIBUTE_IDS)
        enriched.append(row)
    return enriched


class OzonClient:
    base_url = "https://api-seller.ozon.ru"

    def __init__(self, client_id: str, api_key: str, *, timeout: int = 25):
        self.client_id = client_id.strip()
        self.api_key = api_key.strip()
        self.timeout = timeout
        if not self.client_id or not self.api_key:
            raise MarketplaceError(
                "Не настроены OZON_CLIENT_ID и OZON_API_KEY.",
                code="not_configured",
            )

    def post_readonly(self, path: str, payload: dict) -> dict:
        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
        request = Request(
            url,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Client-Id": self.client_id,
                "Api-Key": self.api_key,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                raw = response.read(8 * 1024 * 1024)
        except HTTPError as error:
            detail = error.read(2048).decode("utf-8", "replace")
            raise MarketplaceError(
                f"Ozon API {path} HTTP {error.code}: {detail[:500]}",
                code="api_error",
            ) from error
        except URLError as error:
            raise MarketplaceError(f"Ozon API недоступен: {error.reason}", code="network_error") from error
        try:
            data = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise MarketplaceError("Ozon API вернул некорректный JSON.", code="invalid_response") from error
        if not isinstance(data, dict):
            raise MarketplaceError("Ozon API вернул неожиданный формат ответа.", code="invalid_response")
        return data

    @staticmethod
    def _response_nodes(response: dict):
        stack = [response]
        while stack:
            node = stack.pop(0)
            if not isinstance(node, dict):
                continue
            yield node
            for key in ("result", "data"):
                child = node.get(key)
                if isinstance(child, dict):
                    stack.append(child)

    @classmethod
    def _response_items(cls, response: dict) -> list[dict]:
        for node in cls._response_nodes(response):
            for key in ("items", "products", "postings"):
                value = node.get(key)
                if isinstance(value, list):
                    return [item for item in value if isinstance(item, dict)]
        return []

    @classmethod
    def _response_cursor(cls, response: dict) -> str:
        for node in cls._response_nodes(response):
            value = _text(node.get("cursor") or node.get("last_id"))
            if value:
                return value
        return ""

    def _paged(self, path: str, *, limit: int = 100, max_pages: int = 100) -> list[dict]:
        rows: list[dict] = []
        cursor = ""
        for _ in range(max_pages):
            payload = {"filter": {"visibility": "ALL"}, "limit": limit}
            if cursor:
                payload["cursor"] = cursor
                payload["last_id"] = cursor
            response = self.post_readonly(path, payload)
            items = self._response_items(response)
            rows.extend(items)
            next_cursor = self._response_cursor(response)
            if not next_cursor or next_cursor == cursor or len(items) < limit:
                break
            cursor = next_cursor
        return rows

    def _paged_with_fallback(self, paths: tuple[str, ...]) -> list[dict]:
        last_error: MarketplaceError | None = None
        for path in paths:
            try:
                return self._paged(path)
            except MarketplaceError as error:
                last_error = error
        assert last_error is not None
        raise last_error

    def products(self) -> list[dict]:
        return self._paged_with_fallback(("/v3/product/list", "/v2/product/list"))

    def product_details(self, product_ids: list[str]) -> list[dict]:
        """Read detailed product cards in Ozon's safe batch size of 100."""
        rows: list[dict] = []
        ids = [value for value in dict.fromkeys(_text(item) for item in product_ids) if value]
        for offset in range(0, len(ids), 100):
            response = self.post_readonly("/v3/product/info/list", {"product_id": ids[offset:offset + 100]})
            rows.extend(self._response_items(response))
        return rows

    def product_attributes(self) -> list[dict]:
        """Read all visible product characteristics, including colour/size."""
        rows: list[dict] = []
        last_id = ""
        # The Ozon endpoint returns a non-JSON validation response for a
        # larger page.  Keep the documented working page size and paginate.
        page_size = 100
        for _ in range(20):
            payload = {"filter": {"visibility": "ALL"}, "limit": page_size}
            if last_id:
                payload["last_id"] = last_id
            response = self.post_readonly("/v4/product/info/attributes", payload)
            result = response.get("result")
            items = [item for item in result if isinstance(item, dict)] if isinstance(result, list) else self._response_items(response)
            rows.extend(items)
            next_last_id = _text(response.get("last_id") or response.get("cursor"))
            if not next_last_id or next_last_id == last_id or len(items) < page_size:
                break
            last_id = next_last_id
        return rows

    def prices(self) -> list[dict]:
        return self._paged_with_fallback(("/v5/product/info/prices", "/v4/product/info/prices"))

    def stocks(self) -> list[dict]:
        return self._paged_with_fallback(("/v4/product/info/stocks", "/v3/product/info/stocks"))

    def warehouse_stocks(self) -> list[dict]:
        """Return FBO balances split by the actual Ozon warehouse."""
        rows: list[dict] = []
        limit = 100
        offset = 0
        for page_index in range(200):
            if page_index:
                time.sleep(1.1)
            response = None
            for attempt in range(4):
                try:
                    response = self.post_readonly(
                        "/v2/analytics/stock_on_warehouses",
                        {"limit": limit, "offset": offset, "warehouse_type": "ALL"},
                    )
                    break
                except MarketplaceError as error:
                    if "HTTP 429" not in str(error) or attempt == 3:
                        if rows:
                            return rows
                        raise
                    time.sleep(2.0 * (attempt + 1))
            if response is None:
                break
            result = response.get("result") if isinstance(response.get("result"), dict) else {}
            page = result.get("rows") if isinstance(result.get("rows"), list) else []
            page = [item for item in page if isinstance(item, dict)]
            rows.extend(page)
            if len(page) < limit:
                break
            offset += limit
        return rows

    def fbs_postings(self) -> list[dict]:
        now = datetime.now(timezone.utc)
        response = self.post_readonly(
            "/v3/posting/fbs/list",
            {
                "dir": "ASC",
                "filter": {
                    "since": (now - timedelta(days=30)).isoformat().replace("+00:00", "Z"),
                    "to": now.isoformat().replace("+00:00", "Z"),
                },
                "limit": 100,
                "with": {"analytics_data": True, "financial_data": True},
            },
        )
        return self._response_items(response)


def _account(conn: sqlite3.Connection, marketplace: str, account_name: str, seller_id: str = "") -> int:
    now = _now()
    conn.execute(
        """INSERT INTO marketplace_accounts (marketplace, account_name, seller_id, updated_at, created_at)
           VALUES (?, ?, ?, ?, ?)
           ON CONFLICT(marketplace, account_name) DO UPDATE SET seller_id=excluded.seller_id, updated_at=excluded.updated_at""",
        (marketplace, account_name, seller_id, now, now),
    )
    row = conn.execute(
        "SELECT id FROM marketplace_accounts WHERE marketplace=? AND account_name=?",
        (marketplace, account_name),
    ).fetchone()
    return int(row[0])


def _product(conn: sqlite3.Connection, account_id: int, row: dict) -> int:
    offer_id = _text(row.get("offer_id") or row.get("offerId"))
    sku = _text(row.get("sku") or row.get("fbo_sku") or row.get("fbs_sku"))
    external_id = _text(row.get("id") or row.get("product_id") or offer_id or sku)
    if not sku:
        sku = external_id
    name = _text(row.get("name") or row.get("title") or row.get("offer_id") or sku)
    barcodes = row.get("barcodes") if isinstance(row.get("barcodes"), list) else []
    barcode = _text(row.get("barcode") or (barcodes[0] if barcodes else ""))
    size = _find_nested_text(row, ("size", "Размер", "размер"))
    color = _find_nested_text(row, ("color", "Цвет", "цвет"))
    now = _now()
    conn.execute(
        """INSERT INTO marketplace_products
           (account_id, external_product_id, offer_id, sku, barcode, name, size, color, payload_json, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
           ON CONFLICT(account_id, external_product_id, offer_id) DO UPDATE SET
             sku=excluded.sku, barcode=excluded.barcode, name=excluded.name,
             size=excluded.size, color=excluded.color, payload_json=excluded.payload_json,
             updated_at=excluded.updated_at""",
        (account_id, external_id, offer_id, sku, barcode, name, size, color, _json(row), now),
    )
    item = conn.execute(
        "SELECT id FROM marketplace_products WHERE account_id=? AND external_product_id=? AND offer_id=?",
        (account_id, external_id, offer_id),
    ).fetchone()
    return int(item[0])


def _price_values(row: dict) -> tuple[float | None, float | None, float | None, str]:
    price = row.get("price") if isinstance(row.get("price"), dict) else row
    marketing = row.get("marketing_actions") if isinstance(row.get("marketing_actions"), dict) else {}
    return (
        _number(price.get("price") or price.get("current_price")),
        _number(price.get("old_price") or price.get("oldPrice")),
        _number(price.get("marketing_price") or marketing.get("value")),
        _text(price.get("currency_code") or price.get("currency") or "RUB"),
    )


def _stock_rows(row: dict) -> list[dict]:
    stocks = row.get("stocks")
    if not isinstance(stocks, list):
        stocks = [row]
    return [stock for stock in stocks if isinstance(stock, dict)] or [row]


def sync_ozon() -> dict:
    from marketplace_extended import ensure_schema as ensure_extended_schema, sync_extended

    conn = get_db_connection()
    ensure_schema(conn)
    ensure_extended_schema(conn)
    account_name = os.getenv("OZON_ACCOUNT_NAME", "Основной Ozon").strip() or "Основной Ozon"
    existing_account = conn.execute(
        "SELECT id FROM marketplace_accounts WHERE marketplace='ozon' ORDER BY id LIMIT 1"
    ).fetchone()
    account_id = int(existing_account[0]) if existing_account else _account(
        conn, "ozon", account_name, os.getenv("OZON_CLIENT_ID", "").strip()
    )
    sync_production_links(conn, account_id)
    conn.commit()
    started = _now()
    run = conn.execute(
        "INSERT INTO marketplace_sync_runs (account_id, status, started_at) VALUES (?, 'running', ?)",
        (account_id, started),
    )
    run_id = run.lastrowid
    conn.commit()
    try:
        client = OzonClient(os.getenv("OZON_CLIENT_ID", ""), os.getenv("OZON_API_KEY", ""))
        products = client.products()
        product_ids = [_product_identity(item)[0] for item in products]
        details = client.product_details(product_ids)
        attributes = client.product_attributes()
        products = _enrich_catalog_products(products, details, attributes)
        prices = client.prices()
        stocks = client.stocks()
        try:
            warehouse_stocks = client.warehouse_stocks()
        except MarketplaceError:
            warehouse_stocks = []
        try:
            postings = client.fbs_postings()
        except MarketplaceError:
            postings = []
        product_ids: dict[tuple[str, str], int] = {}
        for item in products:
            product_ids[(_text(item.get("id") or item.get("product_id")), _text(item.get("offer_id")))] = _product(conn, account_id, item)
        link_summary = sync_production_links(conn, account_id)
        for item in prices:
            key = (_text(item.get("id") or item.get("product_id")), _text(item.get("offer_id")))
            pid = product_ids.get(key)
            if pid is None:
                pid = _product(conn, account_id, item)
                product_ids[key] = pid
            current, old, marketing, currency = _price_values(item)
            conn.execute(
                "INSERT INTO marketplace_prices (product_id,current_price,old_price,marketing_price,currency,payload_json,observed_at) VALUES (?,?,?,?,?,?,?)",
                (pid, current, old, marketing, currency, _json(item), _now()),
            )
        for item in stocks:
            key = (_text(item.get("id") or item.get("product_id")), _text(item.get("offer_id")))
            pid = product_ids.get(key)
            if pid is None:
                pid = _product(conn, account_id, item)
                product_ids[key] = pid
            for stock in _stock_rows(item):
                stock_qty = _int(stock.get("present") or stock.get("stock") or stock.get("available"))
                reserved = _int(stock.get("reserved"))
                conn.execute(
                    "INSERT INTO marketplace_stocks (product_id,warehouse_type,warehouse_name,stock,reserved,available,payload_json,observed_at) VALUES (?,?,?,?,?,?,?,?)",
                    (pid, _text(stock.get("type") or stock.get("warehouse_type")), _text(stock.get("warehouse_name") or stock.get("warehouse_name")), stock_qty, reserved, max(0, stock_qty - reserved), _json(stock), _now()),
                )
        product_identity_rows = conn.execute(
            "SELECT id,sku,offer_id FROM marketplace_products WHERE account_id=?",
            (account_id,),
        ).fetchall()
        product_by_identity = {}
        for product_row in product_identity_rows:
            for identity in (product_row["sku"], product_row["offer_id"]):
                if _text(identity):
                    product_by_identity[_text(identity)] = int(product_row["id"])
        for stock in warehouse_stocks:
            pid = product_by_identity.get(_text(stock.get("sku"))) or product_by_identity.get(_text(stock.get("item_code")))
            warehouse_name = _text(stock.get("warehouse_name"))
            if pid is None or not warehouse_name:
                continue
            available = max(0, _int(stock.get("free_to_sell_amount")))
            reserved = max(0, _int(stock.get("reserved_amount")))
            conn.execute(
                "INSERT INTO marketplace_stocks (product_id,warehouse_type,warehouse_name,stock,reserved,available,payload_json,observed_at) VALUES (?,?,?,?,?,?,?,?)",
                (pid, "ozon_warehouse", warehouse_name, available + reserved, reserved, available, _json(stock), _now()),
            )
        for posting in postings:
            external_id = _text(posting.get("order_id") or posting.get("posting_number") or posting.get("order_number"))
            if not external_id:
                continue
            conn.execute(
                """INSERT INTO marketplace_orders (account_id,external_order_id,posting_number,warehouse_type,status,shipment_date,payload_json,updated_at)
                   VALUES (?,?,?,?,?,?,?,?) ON CONFLICT(account_id,external_order_id) DO UPDATE SET
                   posting_number=excluded.posting_number, status=excluded.status, shipment_date=excluded.shipment_date,
                   payload_json=excluded.payload_json, updated_at=excluded.updated_at""",
                (account_id, external_id, _text(posting.get("posting_number")), "FBS", _text(posting.get("status")), _text(posting.get("shipment_date") or posting.get("shipment_date")), _json(posting), _now()),
            )
            order_id = conn.execute("SELECT id FROM marketplace_orders WHERE account_id=? AND external_order_id=?", (account_id, external_id)).fetchone()[0]
            conn.execute("DELETE FROM marketplace_order_items WHERE order_id=?", (order_id,))
            for item in posting.get("products") or []:
                conn.execute(
                    "INSERT INTO marketplace_order_items (order_id,external_product_id,offer_id,sku,name,quantity,payload_json) VALUES (?,?,?,?,?,?,?)",
                    (order_id, _text(item.get("product_id")), _text(item.get("offer_id")), _text(item.get("sku")), _text(item.get("name")), _int(item.get("quantity")), _json(item)),
                )
        extended = sync_extended(conn, account_id)
        total_orders = conn.execute("SELECT COUNT(*) FROM marketplace_orders WHERE account_id=?", (account_id,)).fetchone()[0]
        finished = _now()
        conn.execute("UPDATE marketplace_sync_runs SET status='success', products_count=?, prices_count=?, stocks_count=?, orders_count=?, finished_at=? WHERE id=?", (len(products), len(prices), len(stocks), total_orders, finished, run_id))
        conn.execute("UPDATE marketplace_accounts SET last_sync_at=?, last_error='', updated_at=? WHERE id=?", (finished, finished, account_id))
        conn.commit()
        return {"ok": True, "message": "Ozon синхронизирован.", "products": len(products), "prices": len(prices), "stocks": len(stocks), "orders": total_orders, "extended": extended, "production_links": link_summary}
    except MarketplaceError as error:
        message = str(error)
        conn.execute("UPDATE marketplace_sync_runs SET status='error', error_message=?, finished_at=? WHERE id=?", (message, _now(), run_id))
        conn.execute("UPDATE marketplace_accounts SET last_error=?, updated_at=? WHERE id=?", (message, _now(), account_id))
        conn.commit()
        return {"ok": False, "code": error.code, "message": message}
    except Exception as error:
        conn.rollback()
        message = f"Ошибка синхронизации: {error}"
        conn.execute("UPDATE marketplace_sync_runs SET status='error', error_message=?, finished_at=? WHERE id=?", (message[:500], _now(), run_id))
        conn.execute("UPDATE marketplace_accounts SET last_error=?, updated_at=? WHERE id=?", (message[:500], _now(), account_id))
        conn.commit()
        return {"ok": False, "code": "sync_error", "message": "Ошибка синхронизации маркетплейса. Подробности сохранены в журнале."}
    finally:
        conn.close()


def _marketplace_product_image(payload_json: object) -> str:
    """Return the first usable product image saved by Ozon or Wildberries."""
    try:
        payload = json.loads(str(payload_json or "{}"))
    except (TypeError, ValueError, json.JSONDecodeError):
        return ""
    if not isinstance(payload, dict):
        return ""
    for field in ("primary_image", "images", "color_image", "images360"):
        value = payload.get(field)
        candidates = value if isinstance(value, list) else [value]
        for candidate in candidates:
            if isinstance(candidate, str) and candidate.startswith("https://"):
                return candidate

    # Wildberries cards keep image variants inside ``photos``.  Prefer the
    # medium portrait image: it is sharp enough for product cards without
    # downloading the full-size original on every warehouse screen.
    photos = payload.get("photos")
    if isinstance(photos, list):
        for photo in photos:
            if not isinstance(photo, dict):
                continue
            for field in ("c516x688", "big", "square", "c246x328", "tm"):
                candidate = photo.get(field)
                if isinstance(candidate, str) and candidate.startswith("https://"):
                    return candidate
    return ""


def dashboard(*, read_only: bool = False) -> dict:
    from marketplace_extended import dashboard_extension, ensure_schema as ensure_extended_schema

    conn = get_db_connection(timeout=2 if read_only else 30)
    if not read_only:
        ensure_schema(conn)
        ensure_extended_schema(conn)
    conn.row_factory = sqlite3.Row
    account_name = os.getenv("OZON_ACCOUNT_NAME", "Основной Ozon").strip() or "Основной Ozon"
    if read_only:
        account_row = conn.execute(
            "SELECT id FROM marketplace_accounts WHERE marketplace='ozon' ORDER BY id LIMIT 1"
        ).fetchone()
        account_id = int(account_row[0]) if account_row else 0
    else:
        account_id = _account(conn, "ozon", account_name, os.getenv("OZON_CLIENT_ID", "").strip())
    rows = conn.execute("SELECT id,marketplace,account_name,seller_id,enabled,last_sync_at,last_error FROM marketplace_accounts ORDER BY marketplace,id").fetchall()
    products = conn.execute("SELECT COUNT(*) FROM marketplace_products WHERE account_id=?", (account_id,)).fetchone()[0]
    stocks = conn.execute("SELECT COUNT(*) FROM marketplace_stocks WHERE product_id IN (SELECT id FROM marketplace_products WHERE account_id=?)", (account_id,)).fetchone()[0]
    orders = conn.execute("SELECT COUNT(*) FROM marketplace_orders WHERE account_id=? AND status NOT IN ('cancelled','delivered')", (account_id,)).fetchone()[0]
    product_rows = conn.execute(
        """SELECT p.id,p.external_product_id,p.name,p.offer_id,p.sku,p.barcode,p.size,p.color,p.payload_json,
                  (SELECT current_price FROM marketplace_prices WHERE product_id=p.id ORDER BY id DESC LIMIT 1) AS current_price,
                  (SELECT old_price FROM marketplace_prices WHERE product_id=p.id ORDER BY id DESC LIMIT 1) AS old_price,
                  (SELECT SUM(available) FROM marketplace_stocks WHERE product_id=p.id AND LOWER(warehouse_type) IN ('fbo','fbs') AND id IN (SELECT MAX(id) FROM marketplace_stocks GROUP BY product_id,warehouse_type,warehouse_name)) AS available,
                  p.updated_at
           FROM marketplace_products p WHERE p.account_id=? ORDER BY p.updated_at DESC""",
        (account_id,),
    ).fetchall()
    warehouse_stock_rows = conn.execute(
        """SELECT s.product_id,LOWER(s.warehouse_type) AS warehouse_type,s.warehouse_name,SUM(s.available) AS available
             FROM marketplace_stocks s
            WHERE s.product_id IN (SELECT id FROM marketplace_products WHERE account_id=?)
              AND LOWER(s.warehouse_type) IN ('ozon_warehouse','fbs')
              AND s.id IN (SELECT MAX(id) FROM marketplace_stocks GROUP BY product_id,warehouse_type,warehouse_name)
            GROUP BY s.product_id,LOWER(s.warehouse_type),s.warehouse_name""",
        (account_id,),
    ).fetchall()
    stock_by_product: dict[int, dict[str, int]] = {}
    for stock_row in warehouse_stock_rows:
        warehouse_key = (
            f"ozon:{_text(stock_row['warehouse_name'])}"
            if stock_row["warehouse_type"] == "ozon_warehouse"
            else "fbs"
        )
        stock_by_product.setdefault(int(stock_row["product_id"]), {})[warehouse_key] = int(stock_row["available"] or 0)
    production_link_rows = conn.execute(
        """SELECT marketplace_product_id,production_product_name,production_size,production_color,
                  route_configured
             FROM marketplace_production_links
            WHERE marketplace_product_id IN (SELECT id FROM marketplace_products WHERE account_id=?)
              AND status='linked'""",
        (account_id,),
    ).fetchall()
    wms_finished_stock: dict[tuple[str, str, str], int] = {}
    wms_finished_rows: list[dict[str, object]] = []
    wms_stock_available = True
    try:
        from wms.connection import get_pg_connection
        from wms.repository import get_stock_rows

        wms_conn = get_pg_connection()
        for stock_row in get_stock_rows(wms_conn):
            key = stock_row.product_key
            if key.item_type != "finished" or stock_row.item_state != "SELLABLE":
                continue
            identity = (key.product_name, key.product_size, key.product_color)
            available_quantity = max(
                0, int(stock_row.quantity or 0) - int(stock_row.reserved_quantity or 0),
            )
            wms_finished_stock[identity] = wms_finished_stock.get(identity, 0) + available_quantity
            wms_finished_rows.append({"name": key.product_name, "available": available_quantity})
        wms_conn.rollback()
    except Exception:
        wms_stock_available = False
    production_stock_by_product = {}
    for row in production_link_rows:
        identity = (
            _text(row["production_product_name"]),
            _text(row["production_size"]),
            _text(row["production_color"]),
        )
        production_stock_by_product[int(row["marketplace_product_id"])] = {
            "available": wms_finished_stock.get(identity, 0),
            "key": "|".join(identity),
        }
    warehouse_names = [
        _text(row[0]) for row in conn.execute(
            """SELECT s.warehouse_name
                 FROM marketplace_stocks s
                WHERE LOWER(s.warehouse_type)='ozon_warehouse'
                  AND s.product_id IN (SELECT id FROM marketplace_products WHERE account_id=?)
                  AND s.id IN (SELECT MAX(id) FROM marketplace_stocks GROUP BY product_id,warehouse_type,warehouse_name)
             GROUP BY s.warehouse_name ORDER BY s.warehouse_name""",
            (account_id,),
        ).fetchall() if _text(row[0])
    ]
    warehouse_options = [
        {"key": f"ozon:{name}", "name": name} for name in warehouse_names
    ]
    if any("fbs" in stocks for stocks in stock_by_product.values()):
        warehouse_options.append({"key": "fbs", "name": "FBS — собственный склад"})
    if not warehouse_options:
        warehouse_options = [
            {"key": "fbo", "name": "FBO — склады Ozon"},
            {"key": "fbs", "name": "FBS — собственный склад"},
        ]
    product_history: dict[str, dict[str, dict[str, object]]] = {}

    def history_day(identity: str, day: str) -> dict[str, object] | None:
        identity = _text(identity)
        day = _text(day)[:10]
        if not identity or not day:
            return None
        return product_history.setdefault(identity, {}).setdefault(
            day, {"date": day, "orders": set(), "units": 0, "returns": 0, "accruals": 0.0},
        )

    for history_row in conn.execute(
        """SELECT oi.external_product_id,oi.offer_id,oi.sku,oi.quantity,o.posting_number,
                  substr(CASE WHEN trim(o.shipment_date)<>'' THEN o.shipment_date ELSE o.updated_at END,1,10) AS day
             FROM marketplace_order_items oi
             JOIN marketplace_orders o ON o.id=oi.order_id
            WHERE o.account_id=?""",
        (account_id,),
    ):
        for identity in {history_row["external_product_id"], history_row["offer_id"], history_row["sku"]}:
            bucket = history_day(identity, history_row["day"])
            if bucket is not None:
                bucket["orders"].add(_text(history_row["posting_number"]))
                bucket["units"] += int(history_row["quantity"] or 0)
    for history_row in conn.execute(
        """SELECT offer_id,sku,quantity,substr(returned_at,1,10) AS day
             FROM marketplace_returns WHERE account_id=? AND trim(returned_at)<>''""",
        (account_id,),
    ):
        for identity in {history_row["offer_id"], history_row["sku"]}:
            bucket = history_day(identity, history_row["day"])
            if bucket is not None:
                bucket["returns"] += max(1, int(history_row["quantity"] or 0))
    for history_row in conn.execute(
        """SELECT sku,amount,accrual_date AS day
             FROM marketplace_finance_accruals WHERE account_id=? AND trim(sku)<>''""",
        (account_id,),
    ):
        bucket = history_day(history_row["sku"], history_row["day"])
        if bucket is not None:
            bucket["accruals"] += float(history_row["amount"] or 0)
    products_payload = []
    groups = {}
    for row in product_rows:
        item = dict(row)
        item["image_url"] = _marketplace_product_image(item.pop("payload_json", ""))
        group_key, group_name = product_group_for(
            item.get("name"), item.get("offer_id"), item.get("sku"), item.get("barcode"),
        )
        item["group_key"] = group_key
        item["group_name"] = group_name
        item["warehouse_stocks"] = stock_by_product.get(int(item["id"]), {})
        direct_stock_rows = [
            row for row in wms_finished_rows
            if (_text(item.get("offer_id")) and _text(item.get("offer_id")).casefold() in _text(row.get("name")).casefold())
            or (_text(item.get("sku")) and _text(item.get("sku")).casefold() in _text(row.get("name")).casefold())
        ]
        if direct_stock_rows:
            production_stock = {
                "available": sum(int(row.get("available") or 0) for row in direct_stock_rows),
                "key": f"ozon|{_text(item.get('offer_id') or item.get('sku'))}",
            }
        else:
            production_stock = production_stock_by_product.get(int(item["id"]), {})
        item["production_available"] = int(production_stock.get("available", 0))
        item["production_linked"] = bool(production_stock)
        item["production_stock_available"] = wms_stock_available
        merged_history: dict[str, dict[str, object]] = {}
        for identity in {item.get("external_product_id"), item.get("offer_id"), item.get("sku")}:
            for day, source in product_history.get(_text(identity), {}).items():
                target = merged_history.setdefault(
                    day, {"date": day, "orders": set(), "units": 0, "returns": 0, "accruals": 0.0},
                )
                target["orders"].update(source["orders"])
                target["units"] = max(int(target["units"]), int(source["units"]))
                target["returns"] = max(int(target["returns"]), int(source["returns"]))
                target["accruals"] = source["accruals"] if abs(float(source["accruals"])) > abs(float(target["accruals"])) else target["accruals"]
        item["history"] = [
            {**entry, "orders": len({value for value in entry["orders"] if value})}
            for entry in sorted(merged_history.values(), key=lambda value: str(value["date"]))
        ]
        products_payload.append(item)
        group = groups.setdefault(
            group_key,
            {
                "key": group_key,
                "name": group_name,
                "products": 0,
                "articles": set(),
                "available": 0,
                "production_available": 0,
                "production_keys": set(),
                "production_linked_products": 0,
                "production_stock_available": wms_stock_available,
                "prices": [],
            },
        )
        if not group.get("image_url") and item.get("image_url"):
            group["image_url"] = item["image_url"]
        group["products"] += 1
        article = _text(item.get("offer_id") or item.get("sku"))
        if article:
            group["articles"].add(article)
        group["available"] += int(item.get("available") or 0)
        production_key = _text(production_stock.get("key"))
        if production_key and production_key not in group["production_keys"]:
            group["production_keys"].add(production_key)
            group["production_available"] += int(item.get("production_available") or 0)
        if item["production_linked"]:
            group["production_linked_products"] += 1
        if item.get("current_price") is not None:
            group["prices"].append(float(item["current_price"]))
    group_payload = []
    for group in groups.values():
        prices = group.pop("prices")
        group.pop("production_keys", None)
        group["articles"] = len(group.pop("articles"))
        group["price_min"] = min(prices) if prices else None
        group["price_max"] = max(prices) if prices else None
        group_payload.append(group)
    group_payload.sort(key=lambda item: (item["name"].lower(), item["key"]))
    order_rows = [dict(row) for row in conn.execute(
        "SELECT id,external_order_id,posting_number,warehouse_type,status,shipment_date,payload_json,updated_at FROM marketplace_orders WHERE account_id=? ORDER BY updated_at DESC",
        (account_id,),
    ).fetchall()]
    for order in order_rows:
        try:
            order_payload = json.loads(order.pop("payload_json", "{}") or "{}")
        except (TypeError, ValueError):
            order_payload = {}
        analytics_data = order_payload.get("analytics_data") if isinstance(order_payload.get("analytics_data"), dict) else {}
        delivery_method = order_payload.get("delivery_method") if isinstance(order_payload.get("delivery_method"), dict) else {}
        order["warehouse_name"] = _text(
            order_payload.get("warehouse_name")
            or analytics_data.get("warehouse_name")
            or delivery_method.get("warehouse_name")
            or delivery_method.get("warehouse")
            or order.get("warehouse_type")
        ) or "Склад не указан"
        lines = []
        for line_row in conn.execute(
            "SELECT external_product_id,offer_id,sku,name,quantity,payload_json FROM marketplace_order_items WHERE order_id=? ORDER BY id",
            (order["id"],),
        ).fetchall():
            line = dict(line_row)
            try:
                line_payload = json.loads(line.pop("payload_json", "{}") or "{}")
            except (TypeError, ValueError):
                line_payload = {}
            price = line_payload.get("price")
            price_payload = price if isinstance(price, dict) else {}
            price = price_payload.get("amount") or price_payload.get("value") or price_payload.get("price") if price_payload else price
            try:
                line["price"] = float(price) if price is not None and str(price).strip() else None
            except (TypeError, ValueError):
                line["price"] = None
            line["currency"] = _text(
                line_payload.get("currency_code") or line_payload.get("currency")
                or price_payload.get("currency_code") or price_payload.get("currency") or "RUB"
            )
            line["amount"] = float(line["quantity"] or 0) * line["price"] if line["price"] is not None else None
            lines.append(line)
        priced_lines = [line for line in lines if line.get("price") is not None]
        order["items"] = lines
        order["item_count"] = len(lines)
        order["quantity"] = sum(float(line.get("quantity") or 0) for line in lines)
        order["amount"] = sum(float(line.get("amount") or 0) for line in priced_lines)
        order["amount_available"] = bool(lines) and len(priced_lines) == len(lines)
        order["amount_partial"] = bool(priced_lines) and len(priced_lines) != len(lines)
    recent = conn.execute("SELECT id,status,products_count,prices_count,stocks_count,orders_count,error_message,started_at,finished_at FROM marketplace_sync_runs WHERE account_id=? ORDER BY id DESC LIMIT 5", (account_id,)).fetchall()
    configured = bool(os.getenv("OZON_CLIENT_ID", "").strip() and os.getenv("OZON_API_KEY", "").strip())
    wildberries_configured = bool(os.getenv("WB_API_TOKEN", "").strip())
    supply_rows = _supply_rows(conn, limit=20, active_only=True)
    supply_counts = {key: 0 for key in MARKETPLACE_SUPPLY_STATUSES}
    for status_row in conn.execute("SELECT canonical_status,COUNT(*) AS count FROM marketplace_supplies GROUP BY canonical_status"):
        supply_counts[status_row[0]] = int(status_row[1])
    warehouse_shipments = [dict(row) for row in conn.execute("SELECT id,number,marketplace,external_supply_id,status,destination_name,total_quantity,reserved_quantity,picked_quantity,packed_quantity,planned_at,updated_at FROM warehouse_shipments ORDER BY updated_at DESC LIMIT 20")]
    sync_events = [dict(row) for row in conn.execute("SELECT id,marketplace,event_type,severity,external_id,message,created_at FROM marketplace_sync_events ORDER BY id DESC LIMIT 20")]
    extended = dashboard_extension(conn, account_id, ensure_schema_first=not read_only)
    conn.close()
    try:
        from wildberries import dashboard as wildberries_dashboard
        wildberries_payload = wildberries_dashboard(read_only=read_only)
    except Exception as error:
        wildberries_payload = {"ok": False, "configured": wildberries_configured, "error": str(error)}
    return {
        "ok": True,
        "configured": configured,
        "read_only": True,
        "connectors": [
            {"marketplace": "ozon", "configured": configured, "read_only": True},
            {"marketplace": "wildberries", "configured": wildberries_configured, "read_only": True},
        ],
        "accounts": [dict(row) for row in rows],
        "summary": {"products": products, "stock_rows": stocks, "open_orders": orders, "supplies": len(supply_rows), "warehouse_shipments": len(warehouse_shipments)},
        "product_groups": group_payload,
        "products_rows": products_payload,
        "warehouses": warehouse_options,
        "orders_rows": order_rows,
        "sync_runs": [dict(row) for row in recent],
        "supplies": supply_rows,
        "supply_counts": supply_counts,
        "warehouse_shipments": warehouse_shipments,
        "sync_events": sync_events,
        "analytics": extended,
        "wildberries": wildberries_payload,
    }


def dashboard_supplement() -> dict:
    """Return only SQLite/WB fields appended to the PostgreSQL dashboard."""

    ensure_schema()
    conn = get_db_connection(timeout=2)
    conn.row_factory = sqlite3.Row
    try:
        supplies = _supply_rows(conn, limit=20, active_only=True)
        supply_counts = {key: 0 for key in MARKETPLACE_SUPPLY_STATUSES}
        for row in conn.execute(
            "SELECT canonical_status,COUNT(*) AS count FROM marketplace_supplies GROUP BY canonical_status"
        ):
            supply_counts[row[0]] = int(row[1])
        warehouse_shipments = [dict(row) for row in conn.execute(
            """SELECT id,number,marketplace,external_supply_id,status,destination_name,
                      total_quantity,reserved_quantity,picked_quantity,packed_quantity,
                      planned_at,updated_at
                 FROM warehouse_shipments ORDER BY updated_at DESC LIMIT 20"""
        )]
        sync_events = [dict(row) for row in conn.execute(
            """SELECT id,marketplace,event_type,severity,external_id,message,created_at
                 FROM marketplace_sync_events ORDER BY id DESC LIMIT 20"""
        )]
    finally:
        conn.close()

    ozon_configured = bool(os.getenv("OZON_CLIENT_ID", "").strip() and os.getenv("OZON_API_KEY", "").strip())
    wildberries_configured = bool(os.getenv("WB_API_TOKEN", "").strip())
    try:
        from wildberries import dashboard as wildberries_dashboard
        wildberries_payload = wildberries_dashboard(read_only=True)
    except Exception as error:
        wildberries_payload = {"ok": False, "configured": wildberries_configured, "error": str(error)}
    return {
        "connectors": [
            {"marketplace": "ozon", "configured": ozon_configured, "read_only": True},
            {"marketplace": "wildberries", "configured": wildberries_configured, "read_only": True},
        ],
        "wildberries": wildberries_payload,
        "supplies": supplies,
        "supply_counts": supply_counts,
        "warehouse_shipments": warehouse_shipments,
        "sync_events": sync_events,
    }


def warehouse_catalog() -> dict:
    """Return the full, read-only Ozon catalogue for warehouse staff.

    This deliberately exposes only identification data required to identify a
    physical item while receiving, placing or issuing it.  It never calls Ozon
    and never returns marketplace credentials, orders, prices, or diagnostics.
    """
    conn = get_db_connection()
    ensure_schema(conn)
    account_name = os.getenv("OZON_ACCOUNT_NAME", "Основной Ozon").strip() or "Основной Ozon"
    account_id = _account(conn, "ozon", account_name, os.getenv("OZON_CLIENT_ID", "").strip())
    account = conn.execute(
        "SELECT account_name,last_sync_at FROM marketplace_accounts WHERE id=?",
        (account_id,),
    ).fetchone()
    sync_production_links(conn, account_id)
    rows = conn.execute(
        """SELECT p.id,p.name,p.offer_id,p.sku,p.barcode,p.size,p.color,p.updated_at,
                  COALESCE(l.status,'unmatched') AS production_status,
                  COALESCE(l.route_configured,0) AS route_configured,
                  COALESCE(l.production_product_name,'') AS production_product_name,
                  COALESCE(l.production_size,'') AS production_size,
                  COALESCE(l.production_color,'') AS production_color
             FROM marketplace_products p
             LEFT JOIN marketplace_production_links l ON l.marketplace_product_id=p.id
             WHERE p.account_id=?
             ORDER BY p.name COLLATE NOCASE, p.offer_id COLLATE NOCASE, p.size, p.color, p.id""",
        (account_id,),
    ).fetchall()
    product_payload = []
    for row in rows:
        item = dict(row)
        group_key, group_name = product_group_for(
            item.get("name"), item.get("offer_id"), item.get("sku"), item.get("barcode"), item.get("size"),
        )
        item["group_key"] = group_key
        item["group_name"] = group_name
        product_payload.append(item)
    conn.close()
    return {
        "ok": True,
        "marketplace": "ozon",
        "account_name": account["account_name"] if account else account_name,
        "last_sync_at": account["last_sync_at"] if account else None,
        "products": product_payload,
    }


def _catalog_identity(*values: object) -> tuple[str, str, str]:
    """Normalise a factory identity without changing the source values.

    Marketplace titles are user-facing and may differ in punctuation or case.
    The warehouse, however, owns the canonical ``name / size / colour`` key.
    Keeping this normalisation in one place makes the read-only catalogue
    projection predictable for both Ozon and Wildberries.
    """

    normalized = [
        " ".join(_text(value).casefold().replace("ё", "е").split())
        for value in values
    ]
    return (
        normalized[0] if len(normalized) > 0 else "",
        normalized[1] if len(normalized) > 1 else "",
        normalized[2] if len(normalized) > 2 else "",
    )


def marketplace_catalog_reconciliation(
    ozon_products: list[dict] | None,
    wildberries_products: list[dict] | None,
) -> dict:
    """Project marketplace cards, production routes and physical cells together.

    This is deliberately a read-only view.  A marketplace card is never
    invented for a warehouse row: unmatched factory stock stays visible with
    an explicit ``no Ozon/WB card`` status.  Conversely, a marketplace card
    without a supported factory route is shown as ``route_missing`` instead of
    receiving a made-up warehouse balance.
    """

    wms_by_identity: dict[tuple[str, str, str], dict] = {}
    warehouse_available = True
    try:
        from wms.connection import get_pg_connection
        from wms.repository import get_stock_rows, list_locations

        wms_conn = get_pg_connection()
        try:
            location_codes = {int(location.id): _text(location.code) for location in list_locations(wms_conn)}
            for stock_row in get_stock_rows(wms_conn):
                product_key = stock_row.product_key
                if product_key.item_type != "finished" or stock_row.item_state != "SELLABLE":
                    continue
                identity = _catalog_identity(
                    product_key.product_name,
                    product_key.product_size,
                    product_key.product_color,
                )
                if not all(identity):
                    continue
                entry = wms_by_identity.setdefault(identity, {
                    "production_name": _text(product_key.product_name),
                    "size": _text(product_key.product_size),
                    "color": _text(product_key.product_color),
                    "quantity": 0,
                    "reserved_quantity": 0,
                    "available_quantity": 0,
                    "locations": [],
                })
                quantity = max(0, int(stock_row.quantity or 0))
                reserved = max(0, int(stock_row.reserved_quantity or 0))
                available = max(0, quantity - reserved)
                entry["quantity"] += quantity
                entry["reserved_quantity"] += reserved
                entry["available_quantity"] += available
                entry["locations"].append({
                    "code": location_codes.get(int(stock_row.location_id or 0), "Не размещён"),
                    "quantity": quantity,
                    "reserved_quantity": reserved,
                    "available_quantity": available,
                })
            wms_conn.rollback()
        finally:
            wms_conn.close()
    except Exception:
        # A temporary WMS outage must not hide the marketplace catalogue or be
        # presented as a physical zero balance.
        warehouse_available = False
        wms_by_identity = {}

    marketplace_items: list[dict] = []
    by_identity: dict[tuple[str, str, str], list[dict]] = {}
    for marketplace, source_rows in (
        ("ozon", ozon_products or []),
        ("wildberries", wildberries_products or []),
    ):
        for source in source_rows:
            if not isinstance(source, dict):
                continue
            target = production_target_for_marketplace_product(source)
            production_name, size, color = target if target else ("", "", "")
            identity = _catalog_identity(production_name, size, color) if target else None
            stock = wms_by_identity.get(identity) if identity else None
            item = {
                "marketplace": marketplace,
                "id": _text(source.get("id") or source.get("external_product_id") or source.get("sku") or source.get("offer_id")),
                "article": _text(source.get("offer_id") or source.get("sku") or source.get("external_product_id")),
                "sku": _text(source.get("sku")),
                "name": _text(source.get("name")) or "Без названия",
                "size": _text(source.get("size")),
                "color": _text(source.get("color")),
                "production_name": production_name,
                "production_size": size,
                "production_color": color,
                "route_configured": bool(target),
                "warehouse_found": bool(stock),
                "warehouse_quantity": int(stock["quantity"]) if stock else 0,
                "warehouse_reserved_quantity": int(stock["reserved_quantity"]) if stock else 0,
                "warehouse_available_quantity": int(stock["available_quantity"]) if stock else 0,
                "locations": list(stock["locations"]) if stock else [],
                "status": "ready" if target and stock else ("route_missing" if not target else "not_in_warehouse"),
            }
            marketplace_items.append(item)
            if identity:
                by_identity.setdefault(identity, []).append(item)

    production_items: list[dict] = []
    for identity, stock in wms_by_identity.items():
        linked_cards = by_identity.get(identity, [])
        ozon_cards = [item for item in linked_cards if item["marketplace"] == "ozon"]
        wildberries_cards = [item for item in linked_cards if item["marketplace"] == "wildberries"]
        production_items.append({
            **stock,
            "ozon_cards": [{"article": item["article"], "name": item["name"]} for item in ozon_cards],
            "wildberries_cards": [{"article": item["article"], "name": item["name"]} for item in wildberries_cards],
            "visible_on_ozon": bool(ozon_cards),
            "visible_on_wildberries": bool(wildberries_cards),
        })

    marketplace_items.sort(key=lambda item: (item["marketplace"], item["name"].casefold(), item["article"]))
    production_items.sort(key=lambda item: (item["production_name"].casefold(), item["size"], item["color"]))

    def provider_summary(provider: str) -> dict:
        rows = [item for item in marketplace_items if item["marketplace"] == provider]
        return {
            "products": len(rows),
            "route_configured": sum(1 for item in rows if item["route_configured"]),
            "route_missing": sum(1 for item in rows if not item["route_configured"]),
            "warehouse_found": sum(1 for item in rows if item["warehouse_found"]),
            "not_in_warehouse": sum(1 for item in rows if item["route_configured"] and not item["warehouse_found"]),
        }

    return {
        "ok": True,
        "warehouse_available": warehouse_available,
        "marketplace_items": marketplace_items,
        "production_items": production_items,
        "summary": {
            "ozon": provider_summary("ozon"),
            "wildberries": provider_summary("wildberries"),
            "production": {
                "finished_identities": len(production_items),
                "visible_on_ozon": sum(1 for item in production_items if item["visible_on_ozon"]),
                "visible_on_wildberries": sum(1 for item in production_items if item["visible_on_wildberries"]),
                "without_marketplace_card": sum(
                    1 for item in production_items
                    if not item["visible_on_ozon"] and not item["visible_on_wildberries"]
                ),
            },
        },
    }


def marketplace_metadata_for_wms_product_keys(product_keys: list[dict]) -> list[dict | None]:
    """Resolve WMS finished-goods identities to their marketplace cards.

    PostgreSQL is authoritative for the current Ozon catalogue.  Wildberries
    still uses the shared legacy projection, so it remains a fallback for an
    otherwise unresolved physical product instead of disappearing from the
    warehouse screen when Phase 1A is enabled.
    """
    if os.getenv("MARKETPLACE_PHASE1A_ENABLED", "0").strip() == "1":
        from marketplace_pg import MarketplacePGRepository
        from marketplace_phase1a import account_key

        ozon_rows = MarketplacePGRepository().marketplace_metadata_for_wms_product_keys(
            account_key(), product_keys,
        )
        fallback_rows = _legacy_marketplace_metadata_for_wms_product_keys(product_keys)
        return [ozon or fallback for ozon, fallback in zip(ozon_rows, fallback_rows)]
    conn = get_db_connection()
    ensure_schema(conn)
    rows = conn.execute(
        """SELECT p.id,p.name,p.offer_id,p.sku,p.barcode,p.size,p.color,p.payload_json,
                  COALESCE(l.status,'unmatched') AS production_status,
                  COALESCE(l.route_configured,0) AS route_configured,
                  COALESCE(l.production_product_name,'') AS production_product_name,
                  COALESCE(l.production_size,'') AS production_size,
                  COALESCE(l.production_color,'') AS production_color
             FROM marketplace_products p
             LEFT JOIN marketplace_production_links l ON l.marketplace_product_id=p.id
            ORDER BY p.updated_at DESC,p.id DESC"""
    ).fetchall()
    products = []
    for source in rows:
        product = dict(source)
        payload_json = product.pop("payload_json", "")
        product["image_url"] = _marketplace_product_image(payload_json)
        product["barcodes"] = sorted(_marketplace_payload_barcodes(payload_json))
        group_key, group_name = product_group_for(
            product.get("name"), product.get("offer_id"), product.get("sku"), product.get("barcode"),
        )
        product["group_key"] = group_key
        product["group_name"] = group_name
        products.append(product)
    resolved: list[dict | None] = []
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
        if linked:
            alternate_barcodes = set(linked.get("barcodes") or [])
            primary_barcode = _normalized_marketplace_barcode(linked.get("barcode"))
            if primary_barcode:
                alternate_barcodes.add(primary_barcode)
            resolved.append({
                key: linked.get(key)
                for key in (
                    "id", "external_product_id", "name", "group_name", "offer_id",
                    "sku", "barcode", "size", "color", "image_url",
                    "route_configured", "production_product_name",
                    "production_size", "production_color",
                )
            } | {"barcodes": sorted(alternate_barcodes)})
        else:
            resolved.append(None)
    conn.close()
    return resolved


def _legacy_marketplace_metadata_for_wms_product_keys(product_keys: list[dict]) -> list[dict | None]:
    """Resolve a WMS identity against retained Ozon/WB cards without PG mode.

    The helper is intentionally only a fallback: a fresh Ozon projection from
    PostgreSQL always wins, while a matching Wildberries card can still be
    shown to warehouse staff.
    """

    conn = get_db_connection()
    ensure_schema(conn)
    rows = conn.execute(
        """SELECT p.id,p.external_product_id,p.name,p.offer_id,p.sku,p.barcode,p.size,p.color,p.payload_json,
                  a.marketplace,
                  COALESCE(l.status,'unmatched') AS production_status,
                  COALESCE(l.route_configured,0) AS route_configured,
                  COALESCE(l.production_product_name,'') AS production_product_name,
                  COALESCE(l.production_size,'') AS production_size,
                  COALESCE(l.production_color,'') AS production_color
             FROM marketplace_products p
             JOIN marketplace_accounts a ON a.id=p.account_id
             LEFT JOIN marketplace_production_links l ON l.marketplace_product_id=p.id
            ORDER BY CASE a.marketplace WHEN 'wildberries' THEN 0 ELSE 1 END,p.updated_at DESC,p.id DESC"""
    ).fetchall()
    products = []
    for source in rows:
        product = dict(source)
        payload_json = product.pop("payload_json", "")
        product["image_url"] = _marketplace_product_image(payload_json)
        product["barcodes"] = sorted(_marketplace_payload_barcodes(payload_json))
        products.append(product)

    resolved: list[dict | None] = []
    for product_key in product_keys:
        if _text(product_key.get("item_type")) != "finished":
            resolved.append(None)
            continue
        wms_name, wms_size, wms_color = _catalog_identity(
            product_key.get("product_name"),
            product_key.get("product_size"),
            product_key.get("product_color"),
        )
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
                and _catalog_identity(
                    product.get("production_product_name"),
                    product.get("production_size"),
                    product.get("production_color"),
                ) == (wms_name, wms_size, wms_color)
            ),
            None,
        )
        if linked is None:
            resolved.append(None)
            continue
        alternate_barcodes = set(linked.get("barcodes") or [])
        primary_barcode = _normalized_marketplace_barcode(linked.get("barcode"))
        if primary_barcode:
            alternate_barcodes.add(primary_barcode)
        resolved.append({
            key: linked.get(key)
            for key in (
                "id", "marketplace", "external_product_id", "name", "offer_id", "sku", "barcode",
                "size", "color", "image_url", "route_configured", "production_product_name",
                "production_size", "production_color",
            )
        } | {"barcodes": sorted(alternate_barcodes)})
    conn.close()
    return resolved


def sync_for_admin() -> dict:
    try:
        from wildberries import sync_wildberries
        wildberries = sync_wildberries()
    except Exception as error:
        wildberries = {"ok": False, "message": str(error)}
    if os.getenv("MARKETPLACE_PHASE1A_ENABLED", "0").strip() == "1":
        from marketplace_phase1a import start_phase1a_sync

        ozon = start_phase1a_sync()
    else:
        ozon = sync_ozon()
    return {
        "ok": bool(ozon.get("ok")) and bool(wildberries.get("ok")),
        "message": "Ozon и Wildberries синхронизированы." if ozon.get("ok") and wildberries.get("ok") else "Синхронизация завершена с ошибками.",
        "ozon": ozon,
        "wildberries": wildberries,
    }
