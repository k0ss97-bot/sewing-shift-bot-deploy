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
    source TEXT NOT NULL DEFAULT 'auto',
    updated_at TEXT NOT NULL,
    FOREIGN KEY(marketplace_product_id) REFERENCES marketplace_products(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_marketplace_products_account ON marketplace_products(account_id, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_marketplace_production_links_status ON marketplace_production_links(status, production_product_name);
CREATE INDEX IF NOT EXISTS idx_marketplace_stocks_product ON marketplace_stocks(product_id, observed_at DESC);
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
    "PARTIALLY_ACCEPTED", "CANCELLED", "SYNC_ERROR",
)


def canonical_supply_status(marketplace: str, external_status: object) -> str:
    """Map a marketplace status to the internal, read-only warehouse state."""
    status = _text(external_status).lower().replace("-", "_").replace(" ", "_")
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


def _supply_rows(conn: sqlite3.Connection, *, marketplace: str = "", status: str = "", search: str = "", limit: int = 100) -> list[dict]:
    clauses, args = [], []
    if marketplace and marketplace != "all":
        clauses.append("s.marketplace=?"); args.append(marketplace)
    if status:
        clauses.append("s.canonical_status=?"); args.append(status)
    if search:
        term = f"%{search.lower()}%"
        clauses.append("(lower(s.external_supply_id) LIKE ? OR lower(s.destination_name) LIKE ? OR lower(s.external_status) LIKE ?)")
        args.extend([term, term, term])
    where = " WHERE " + " AND ".join(clauses) if clauses else ""
    args.append(max(1, min(500, int(limit or 100))))
    rows = conn.execute(f"""SELECT s.id,s.marketplace,s.external_supply_id,s.external_preorder_id,s.external_status,
            s.canonical_status,s.supply_type,s.destination_name,s.macrolocal_cluster_id,s.planned_at,
            s.timeslot_from,s.timeslot_to,s.last_synced_at,s.warehouse_shipment_id,s.updated_at,
            COUNT(i.id) AS item_count, COALESCE(SUM(i.quantity),0) AS total_quantity,
            SUM(CASE WHEN i.mapped_status='unmatched' THEN 1 ELSE 0 END) AS unmatched_count
        FROM marketplace_supplies s LEFT JOIN marketplace_supply_items i ON i.supply_id=s.id
        {where} GROUP BY s.id ORDER BY s.updated_at DESC LIMIT ?""", args).fetchall()
    return [dict(row) for row in rows]


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
    unmatched = conn.execute("SELECT COUNT(*) FROM marketplace_supply_items WHERE supply_id=? AND mapped_status='unmatched'", (int(supply_id),)).fetchone()[0]
    if unmatched:
        _sync_event(conn, supply["marketplace"], "mapping_required", "Поставка не передана на склад: есть не сопоставленные товары.", severity="critical", external_id=supply["external_supply_id"])
        conn.commit(); conn.close()
        return {"ok": False, "code": "mapping_required", "message": "Сначала сопоставьте все товары поставки с номенклатурой производства."}
    existing = conn.execute("SELECT id,number,status FROM warehouse_shipments WHERE source_type='marketplace_supply' AND source_id=?", (int(supply_id),)).fetchone()
    if existing:
        conn.close(); return {"ok": True, "shipment": dict(existing), "created": False}
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


def product_group_for(*values: object) -> tuple[str, str]:
    """Return a stable product group from the article/name/variant text.

    Ozon exposes product variants as separate rows.  Grouping therefore uses
    both the seller article (offer id/SKU) and the human-readable name, while
    ignoring size and colour differences.  Explicit product words win over
    the size fallback so a renamed article remains in the expected family.
    """

    text = " ".join(_text(value) for value in values if _text(value)).lower().replace("ё", "е")
    sizes = [int(value) for value in re.findall(r"(?<!\d)(?:8[6-9]|9\d|1[0-7]\d|18\d)(?!\d)", text)]

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
    from catalog import PRODUCT_OPTIONS

    group_key, _ = product_group_for(
        row.get("name"), row.get("offer_id"), row.get("sku"), row.get("barcode"), row.get("size"),
    )
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
    """Refresh deterministic Ozon-to-production links without touching stock."""
    rows = conn.execute(
        "SELECT id,name,offer_id,sku,barcode,size,color FROM marketplace_products WHERE account_id=?",
        (account_id,),
    ).fetchall()
    linked = 0
    unmatched = 0
    now = _now()
    for source_row in rows:
        row = dict(source_row)
        target = production_target_for_marketplace_product(row)
        if target:
            product_name, size, color = target
            status = "linked"
            linked += 1
        else:
            product_name = size = color = ""
            status = "unmatched"
            unmatched += 1
        conn.execute(
            """INSERT INTO marketplace_production_links
               (marketplace_product_id,production_product_name,production_size,production_color,status,source,updated_at)
               VALUES (?,?,?,?,?,'auto',?)
               ON CONFLICT(marketplace_product_id) DO UPDATE SET
                 production_product_name=excluded.production_product_name,
                 production_size=excluded.production_size,
                 production_color=excluded.production_color,
                 status=excluded.status,
                 source=excluded.source,
                 updated_at=excluded.updated_at""",
            (row["id"], product_name, size, color, status, now),
        )
    return {"linked": linked, "unmatched": unmatched}


def resolve_production_product_by_barcode(barcode: str) -> dict | None:
    """Resolve an Ozon barcode to a linked internal product key for WMS scans."""
    value = _text(barcode)
    if not value:
        return None
    conn = get_db_connection()
    try:
        ensure_schema(conn)
        account_name = os.getenv("OZON_ACCOUNT_NAME", "Основной Ozon").strip() or "Основной Ozon"
        account_id = _account(conn, "ozon", account_name, os.getenv("OZON_CLIENT_ID", "").strip())
        sync_production_links(conn, account_id)
        row = conn.execute(
            """SELECT l.production_product_name,l.production_size,l.production_color
                 FROM marketplace_products p
                 JOIN marketplace_production_links l ON l.marketplace_product_id=p.id
                 WHERE p.account_id=? AND p.barcode=? AND l.status='linked'
                 LIMIT 1""",
            (account_id, value),
        ).fetchone()
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

    def _paged(self, path: str, *, limit: int = 1000, max_pages: int = 20) -> list[dict]:
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
                "limit": 1000,
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
    conn = get_db_connection()
    ensure_schema(conn)
    account_name = os.getenv("OZON_ACCOUNT_NAME", "Основной Ozon").strip() or "Основной Ozon"
    account_id = _account(conn, "ozon", account_name, os.getenv("OZON_CLIENT_ID", "").strip())
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
        finished = _now()
        conn.execute("UPDATE marketplace_sync_runs SET status='success', products_count=?, prices_count=?, stocks_count=?, orders_count=?, finished_at=? WHERE id=?", (len(products), len(prices), len(stocks), len(postings), finished, run_id))
        conn.execute("UPDATE marketplace_accounts SET last_sync_at=?, last_error='', updated_at=? WHERE id=?", (finished, finished, account_id))
        conn.commit()
        return {"ok": True, "message": "Ozon синхронизирован.", "products": len(products), "prices": len(prices), "stocks": len(stocks), "orders": len(postings), "production_links": link_summary}
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


def dashboard() -> dict:
    conn = get_db_connection()
    ensure_schema(conn)
    account_name = os.getenv("OZON_ACCOUNT_NAME", "Основной Ozon").strip() or "Основной Ozon"
    account_id = _account(conn, "ozon", account_name, os.getenv("OZON_CLIENT_ID", "").strip())
    rows = conn.execute("SELECT id,marketplace,account_name,seller_id,enabled,last_sync_at,last_error FROM marketplace_accounts ORDER BY marketplace,id").fetchall()
    products = conn.execute("SELECT COUNT(*) FROM marketplace_products WHERE account_id=?", (account_id,)).fetchone()[0]
    stocks = conn.execute("SELECT COUNT(*) FROM marketplace_stocks WHERE product_id IN (SELECT id FROM marketplace_products WHERE account_id=?)", (account_id,)).fetchone()[0]
    orders = conn.execute("SELECT COUNT(*) FROM marketplace_orders WHERE account_id=? AND status NOT IN ('cancelled','delivered')", (account_id,)).fetchone()[0]
    product_rows = conn.execute(
        """SELECT p.id,p.name,p.offer_id,p.sku,p.barcode,p.size,p.color,
                  (SELECT current_price FROM marketplace_prices WHERE product_id=p.id ORDER BY id DESC LIMIT 1) AS current_price,
                  (SELECT old_price FROM marketplace_prices WHERE product_id=p.id ORDER BY id DESC LIMIT 1) AS old_price,
                  (SELECT SUM(available) FROM marketplace_stocks WHERE product_id=p.id AND id IN (SELECT MAX(id) FROM marketplace_stocks GROUP BY product_id,warehouse_type,warehouse_name)) AS available,
                  p.updated_at
           FROM marketplace_products p WHERE p.account_id=? ORDER BY p.updated_at DESC LIMIT 100""",
        (account_id,),
    ).fetchall()
    products_payload = []
    groups = {}
    for row in product_rows:
        item = dict(row)
        group_key, group_name = product_group_for(
            item.get("name"), item.get("offer_id"), item.get("sku"), item.get("barcode"),
        )
        item["group_key"] = group_key
        item["group_name"] = group_name
        products_payload.append(item)
        group = groups.setdefault(
            group_key,
            {
                "key": group_key,
                "name": group_name,
                "products": 0,
                "articles": set(),
                "available": 0,
                "prices": [],
            },
        )
        group["products"] += 1
        article = _text(item.get("offer_id") or item.get("sku"))
        if article:
            group["articles"].add(article)
        group["available"] += int(item.get("available") or 0)
        if item.get("current_price") is not None:
            group["prices"].append(float(item["current_price"]))
    group_payload = []
    for group in groups.values():
        prices = group.pop("prices")
        group["articles"] = len(group.pop("articles"))
        group["price_min"] = min(prices) if prices else None
        group["price_max"] = max(prices) if prices else None
        group_payload.append(group)
    group_payload.sort(key=lambda item: (item["name"].lower(), item["key"]))
    order_rows = conn.execute(
        "SELECT id,external_order_id,posting_number,status,shipment_date,updated_at FROM marketplace_orders WHERE account_id=? ORDER BY updated_at DESC LIMIT 100",
        (account_id,),
    ).fetchall()
    recent = conn.execute("SELECT id,status,products_count,prices_count,stocks_count,orders_count,error_message,started_at,finished_at FROM marketplace_sync_runs WHERE account_id=? ORDER BY id DESC LIMIT 5", (account_id,)).fetchall()
    configured = bool(os.getenv("OZON_CLIENT_ID", "").strip() and os.getenv("OZON_API_KEY", "").strip())
    wildberries_configured = bool(os.getenv("WB_API_TOKEN", "").strip())
    supply_rows = _supply_rows(conn, limit=20)
    supply_counts = {key: 0 for key in MARKETPLACE_SUPPLY_STATUSES}
    for status_row in conn.execute("SELECT canonical_status,COUNT(*) AS count FROM marketplace_supplies GROUP BY canonical_status"):
        supply_counts[status_row[0]] = int(status_row[1])
    warehouse_shipments = [dict(row) for row in conn.execute("SELECT id,number,marketplace,external_supply_id,status,destination_name,total_quantity,reserved_quantity,picked_quantity,packed_quantity,planned_at,updated_at FROM warehouse_shipments ORDER BY updated_at DESC LIMIT 20")]
    sync_events = [dict(row) for row in conn.execute("SELECT id,marketplace,event_type,severity,external_id,message,created_at FROM marketplace_sync_events ORDER BY id DESC LIMIT 20")]
    conn.close()
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
        "orders_rows": [dict(row) for row in order_rows],
        "sync_runs": [dict(row) for row in recent],
        "supplies": supply_rows,
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


def sync_for_admin() -> dict:
    return sync_ozon()
