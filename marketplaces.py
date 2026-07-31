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
CREATE INDEX IF NOT EXISTS idx_marketplace_products_account ON marketplace_products(account_id, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_marketplace_stocks_product ON marketplace_stocks(product_id, observed_at DESC);
CREATE INDEX IF NOT EXISTS idx_marketplace_orders_account ON marketplace_orders(account_id, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_marketplace_sync_runs_account ON marketplace_sync_runs(account_id, started_at DESC);
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
        prices = client.prices()
        stocks = client.stocks()
        try:
            postings = client.fbs_postings()
        except MarketplaceError:
            postings = []
        product_ids: dict[tuple[str, str], int] = {}
        for item in products:
            product_ids[(_text(item.get("id") or item.get("product_id")), _text(item.get("offer_id")))] = _product(conn, account_id, item)
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
        return {"ok": True, "message": "Ozon синхронизирован.", "products": len(products), "prices": len(prices), "stocks": len(stocks), "orders": len(postings)}
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
        "summary": {"products": products, "stock_rows": stocks, "open_orders": orders},
        "product_groups": group_payload,
        "products_rows": products_payload,
        "orders_rows": [dict(row) for row in order_rows],
        "sync_runs": [dict(row) for row in recent],
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
    rows = conn.execute(
        """SELECT p.id,p.name,p.offer_id,p.sku,p.barcode,p.size,p.color,p.updated_at
             FROM marketplace_products p
             WHERE p.account_id=?
             ORDER BY p.name COLLATE NOCASE, p.offer_id COLLATE NOCASE, p.size, p.color, p.id""",
        (account_id,),
    ).fetchall()
    conn.close()
    return {
        "ok": True,
        "marketplace": "ozon",
        "account_name": account["account_name"] if account else account_name,
        "last_sync_at": account["last_sync_at"] if account else None,
        "products": [dict(row) for row in rows],
    }


def sync_for_admin() -> dict:
    return sync_ozon()
