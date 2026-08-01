"""Extended read-only Ozon import: orders, returns, ratings and accruals."""

from __future__ import annotations

import json
import os
import time
from datetime import date, datetime, timedelta, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS marketplace_actions (
    account_id INTEGER NOT NULL,
    external_id TEXT NOT NULL,
    title TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT '',
    payload_json TEXT NOT NULL DEFAULT '{}',
    updated_at TEXT NOT NULL,
    PRIMARY KEY (account_id, external_id)
);
CREATE TABLE IF NOT EXISTS marketplace_returns (
    account_id INTEGER NOT NULL,
    external_id TEXT NOT NULL,
    scheme TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT '',
    posting_number TEXT NOT NULL DEFAULT '',
    product_id TEXT NOT NULL DEFAULT '',
    offer_id TEXT NOT NULL DEFAULT '',
    sku TEXT NOT NULL DEFAULT '',
    product_name TEXT NOT NULL DEFAULT '',
    quantity INTEGER NOT NULL DEFAULT 0,
    amount REAL NOT NULL DEFAULT 0,
    returned_at TEXT NOT NULL DEFAULT '',
    payload_json TEXT NOT NULL DEFAULT '{}',
    updated_at TEXT NOT NULL,
    PRIMARY KEY (account_id, external_id)
);
CREATE TABLE IF NOT EXISTS marketplace_ratings (
    account_id INTEGER NOT NULL,
    observed_date TEXT NOT NULL,
    rating REAL,
    payload_json TEXT NOT NULL DEFAULT '{}',
    updated_at TEXT NOT NULL,
    PRIMARY KEY (account_id, observed_date)
);
CREATE TABLE IF NOT EXISTS marketplace_finance_accruals (
    account_id INTEGER NOT NULL,
    accrual_date TEXT NOT NULL,
    external_id TEXT NOT NULL,
    accrual_type TEXT NOT NULL DEFAULT '',
    posting_number TEXT NOT NULL DEFAULT '',
    sku TEXT NOT NULL DEFAULT '',
    amount REAL NOT NULL DEFAULT 0,
    currency TEXT NOT NULL DEFAULT 'RUB',
    payload_json TEXT NOT NULL DEFAULT '{}',
    updated_at TEXT NOT NULL,
    PRIMARY KEY (account_id, accrual_date, external_id)
);
CREATE TABLE IF NOT EXISTS marketplace_extended_sync_state (
    account_id INTEGER NOT NULL,
    resource TEXT NOT NULL,
    cursor_value TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL,
    PRIMARY KEY (account_id, resource)
);
CREATE INDEX IF NOT EXISTS idx_marketplace_returns_date ON marketplace_returns(account_id, returned_at);
CREATE INDEX IF NOT EXISTS idx_marketplace_finance_date ON marketplace_finance_accruals(account_id, accrual_date);
CREATE INDEX IF NOT EXISTS idx_marketplace_finance_posting ON marketplace_finance_accruals(account_id, posting_number);
"""


def ensure_schema(conn) -> None:
    conn.executescript(SCHEMA_SQL)


def _text(value) -> str:
    return "" if value is None else str(value).strip()


def _number(value) -> float:
    try:
        return float(str(value or 0).replace(",", "."))
    except (TypeError, ValueError):
        return 0.0


def _integer(value) -> int:
    try:
        return int(float(value or 0))
    except (TypeError, ValueError):
        return 0


def _json(value) -> str:
    return json.dumps(value if value is not None else {}, ensure_ascii=False, separators=(",", ":"))


def _now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _first(row: dict, *keys, default=""):
    for key in keys:
        value = row.get(key)
        if value not in (None, ""):
            return value
    return default


def _nodes(payload: dict):
    queue = [payload]
    while queue:
        node = queue.pop(0)
        if not isinstance(node, dict):
            continue
        yield node
        for key in ("result", "data"):
            if isinstance(node.get(key), dict):
                queue.append(node[key])


def _items(payload: dict, *names) -> list[dict]:
    if isinstance(payload, dict) and isinstance(payload.get("result"), list):
        return [item for item in payload["result"] if isinstance(item, dict)]
    for node in _nodes(payload):
        for name in names:
            value = node.get(name)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    return []


def _cursor(payload: dict) -> str:
    for node in _nodes(payload):
        value = _text(node.get("cursor") or node.get("last_id"))
        if value:
            return value
    return ""


class OzonReadOnly:
    base_url = "https://api-seller.ozon.ru"

    def __init__(self):
        self.client_id = os.getenv("OZON_CLIENT_ID", "").strip()
        self.api_key = os.getenv("OZON_API_KEY", "").strip()
        if not self.client_id or not self.api_key:
            raise RuntimeError("Ozon API credentials are not configured")

    def request(self, path: str, payload: dict | None = None, *, method: str = "POST") -> dict:
        body = None if method == "GET" else _json(payload or {}).encode("utf-8")
        for attempt in range(5):
            request = Request(
                self.base_url + path,
                data=body,
                method=method,
                headers={
                    "Client-Id": self.client_id,
                    "Api-Key": self.api_key,
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "User-Agent": "sewing-web-readonly/2.0",
                },
            )
            try:
                with urlopen(request, timeout=45) as response:
                    raw = response.read(16 * 1024 * 1024)
                data = json.loads(raw.decode("utf-8")) if raw else {}
                if not isinstance(data, dict):
                    raise RuntimeError(f"Ozon API {path}: unexpected response")
                return data
            except HTTPError as error:
                detail = error.read(4096).decode("utf-8", "replace")
                if error.code == 429 and attempt < 4:
                    time.sleep(2 ** attempt)
                    continue
                raise RuntimeError(f"Ozon API {path} HTTP {error.code}: {detail[:700]}") from error
            except URLError as error:
                if attempt < 2:
                    time.sleep(2 ** attempt)
                    continue
                raise RuntimeError(f"Ozon API {path}: {error.reason}") from error
        raise RuntimeError(f"Ozon API {path}: retry limit reached")

    def actions(self) -> list[dict]:
        return _items(self.request("/v1/actions", method="GET"), "actions", "items")

    def postings(self, scheme: str, history_days: int = 365) -> list[dict]:
        path = "/v3/posting/fbo/list" if scheme == "FBO" else "/v4/posting/fbs/list"
        rows_by_id: dict[str, dict] = {}
        end = datetime.now(timezone.utc)
        start_limit = end - timedelta(days=max(1, history_days))
        while end > start_limit:
            start = max(start_limit, end - timedelta(days=30))
            offset = 0
            previous_signature: tuple[str, ...] | None = None
            while offset < 10000:
                payload = {
                    "dir": "ASC",
                    "filter": {
                        "since": start.isoformat().replace("+00:00", "Z"),
                        "to": end.isoformat().replace("+00:00", "Z"),
                    },
                    "limit": 100,
                    "offset": offset,
                    "with": {"analytics_data": True, "financial_data": True},
                }
                page = _items(self.request(path, payload), "postings", "items")
                signature = tuple(
                    _text(_first(item, "posting_number", "postingNumber", "order_id", "order_number"))
                    for item in page
                )
                if page and signature == previous_signature:
                    break
                previous_signature = signature
                for index, item in enumerate(page):
                    identity = _text(_first(item, "posting_number", "postingNumber", "order_id", "order_number"))
                    if not identity:
                        identity = f"{start.isoformat()}:{offset + index}"
                    rows_by_id[identity] = item
                if len(page) < 100:
                    break
                offset += len(page)
            end = start - timedelta(microseconds=1)
        return list(rows_by_id.values())

    def returns(self, history_days: int = 730) -> list[dict]:
        now = datetime.now(timezone.utc)
        since = now - timedelta(days=max(1, history_days))
        rows: list[dict] = []
        last_id = ""
        for _ in range(100):
            payload = {
                "filter": {"logistic_return_date": {
                    "time_from": since.isoformat().replace("+00:00", "Z"),
                    "time_to": now.isoformat().replace("+00:00", "Z"),
                }},
                "limit": 500,
            }
            if last_id:
                payload["last_id"] = last_id
            response = self.request("/v1/returns/list", payload)
            page = _items(response, "returns", "items")
            rows.extend(page)
            next_id = _cursor(response) or (_text(page[-1].get("id")) if page else "")
            if not response.get("has_next") or not next_id or next_id == last_id:
                break
            last_id = next_id
        return rows

    def rfbs_returns(self) -> list[dict]:
        now = datetime.now(timezone.utc)
        response = self.request("/v2/returns/rfbs/list", {
            "filter": {
                "since": (now - timedelta(days=365)).isoformat().replace("+00:00", "Z"),
                "to": now.isoformat().replace("+00:00", "Z"),
            },
            "limit": 100,
        })
        return _items(response, "returns", "items")

    def rating(self) -> dict:
        return self.request("/v1/rating/summary", {})

    def accrual_day(self, value: date) -> tuple[list[dict], str]:
        response = self.request("/v1/finance/accrual/by-day", {"date": value.isoformat()})
        return _items(response, "accruals", "items"), _cursor(response)

    def posting_accruals(self, posting_numbers: list[str]) -> list[dict]:
        rows: list[dict] = []
        unique = list(dict.fromkeys(number for number in posting_numbers if number))
        for offset in range(0, len(unique), 200):
            response = self.request("/v1/finance/accrual/postings", {"posting_numbers": unique[offset:offset + 200]})
            rows.extend(_items(response, "posting_accruals", "accruals", "items"))
        return rows


def _save_order(conn, account_id: int, scheme: str, row: dict) -> str:
    posting_number = _text(_first(row, "posting_number", "postingNumber"))
    external_id = _text(_first(row, "order_id", "order_number", default=posting_number))
    if not external_id:
        return ""
    status = _text(row.get("status"))
    shipment_date = _text(_first(row, "shipment_date", "in_process_at", "created_at"))
    conn.execute(
        """INSERT INTO marketplace_orders
           (account_id,external_order_id,posting_number,warehouse_type,status,shipment_date,payload_json,updated_at)
           VALUES (?,?,?,?,?,?,?,?) ON CONFLICT(account_id,external_order_id) DO UPDATE SET
           posting_number=excluded.posting_number,warehouse_type=excluded.warehouse_type,status=excluded.status,
           shipment_date=excluded.shipment_date,payload_json=excluded.payload_json,updated_at=excluded.updated_at""",
        (account_id, external_id, posting_number, scheme, status, shipment_date, _json(row), _now()),
    )
    order_id = conn.execute(
        "SELECT id FROM marketplace_orders WHERE account_id=? AND external_order_id=?", (account_id, external_id)
    ).fetchone()[0]
    conn.execute("DELETE FROM marketplace_order_items WHERE order_id=?", (order_id,))
    for item in row.get("products") or []:
        if not isinstance(item, dict):
            continue
        conn.execute(
            "INSERT INTO marketplace_order_items (order_id,external_product_id,offer_id,sku,name,quantity,payload_json) VALUES (?,?,?,?,?,?,?)",
            (order_id, _text(item.get("product_id")), _text(item.get("offer_id")), _text(item.get("sku")),
             _text(item.get("name")), _integer(item.get("quantity")), _json(item)),
        )
    return posting_number


def _rating_value(payload: dict) -> float | None:
    for group in payload.get("groups") or []:
        if not isinstance(group, dict):
            continue
        for item in group.get("items") or []:
            if not isinstance(item, dict):
                continue
            if "оценка товаров" in _text(item.get("name")).lower():
                value = _number(item.get("current_value"))
                return value if 0 <= value <= 5 else None
    candidates = []
    for key, value in payload.items():
        if isinstance(value, (int, float)) and any(token in key.lower() for token in ("rating", "score", "index")):
            candidates.append(float(value))
        elif isinstance(value, dict):
            nested = _rating_value(value)
            if nested is not None:
                candidates.append(nested)
    sensible = [value for value in candidates if 0 <= value <= 5]
    return sensible[0] if sensible else None


def _accrual_identity(row: dict, index: int) -> str:
    explicit = _text(_first(row, "id", "operation_id", "accrual_id"))
    if explicit:
        return explicit
    import hashlib
    return hashlib.sha256((_json(row) + f":{index}").encode()).hexdigest()


def _save_accruals(conn, account_id: int, accrual_date: str, rows: list[dict]) -> None:
    for index, row in enumerate(rows):
        total_amount = row.get("total_amount") if isinstance(row.get("total_amount"), dict) else {}
        posting = row.get("posting") if isinstance(row.get("posting"), dict) else {}
        products = posting.get("products") if isinstance(posting.get("products"), list) else []
        first_product = products[0] if products and isinstance(products[0], dict) else {}
        amount = _number(_first(total_amount, "amount", default=_first(row, "amount", "accrual", "value", "total")))
        accrual_type = _text(_first(row, "accrued_category", "accrual_type", "type", "operation_type", "name"))
        posting_number = _text(_first(posting, "posting_number", "postingNumber", default=_first(row, "posting_number", "postingNumber")))
        conn.execute(
            """INSERT INTO marketplace_finance_accruals
               (account_id,accrual_date,external_id,accrual_type,posting_number,sku,amount,currency,payload_json,updated_at)
               VALUES (?,?,?,?,?,?,?,?,?,?) ON CONFLICT(account_id,accrual_date,external_id) DO UPDATE SET
               accrual_type=excluded.accrual_type,posting_number=excluded.posting_number,sku=excluded.sku,
               amount=excluded.amount,currency=excluded.currency,payload_json=excluded.payload_json,updated_at=excluded.updated_at""",
            (account_id, accrual_date, _accrual_identity(row, index), accrual_type, posting_number,
             _text(_first(first_product, "sku", "product_id", default=_first(row, "sku", "product_id"))),
             amount, _text(total_amount.get("currency") or row.get("currency") or "RUB"), _json(row), _now()),
        )


def sync_extended(conn, account_id: int) -> dict:
    ensure_schema(conn)
    client = OzonReadOnly()
    counts = {"actions": 0, "fbo": 0, "fbs": 0, "returns": 0, "rfbs_returns": 0, "finance": 0, "rating": 0}
    errors = []

    def safely(name, callback, default):
        try:
            return callback()
        except Exception as error:
            errors.append(f"{name}: {error}")
            return default

    actions = safely("actions", client.actions, [])
    for index, row in enumerate(actions):
        external_id = _text(_first(row, "id", "action_id", default=index))
        conn.execute(
            """INSERT INTO marketplace_actions (account_id,external_id,title,status,payload_json,updated_at)
               VALUES (?,?,?,?,?,?) ON CONFLICT(account_id,external_id) DO UPDATE SET
               title=excluded.title,status=excluded.status,payload_json=excluded.payload_json,updated_at=excluded.updated_at""",
            (account_id, external_id, _text(_first(row, "title", "name")), _text(row.get("status")), _json(row), _now()),
        )
    counts["actions"] = len(actions)

    posting_numbers = []
    for scheme in ("FBO", "FBS"):
        rows = safely(scheme.lower(), lambda scheme=scheme: client.postings(scheme), [])
        for row in rows:
            number = _save_order(conn, account_id, scheme, row)
            if number:
                posting_numbers.append(number)
        counts[scheme.lower()] = len(rows)

    returns = safely("returns", client.returns, [])
    rfbs_returns = safely("rfbs_returns", client.rfbs_returns, [])
    for scheme, rows in (("RETURN", returns), ("realFBS", rfbs_returns)):
        for index, row in enumerate(rows):
            external_id = _text(_first(row, "id", "return_id", "posting_number", default=f"{scheme}-{index}"))
            product = row.get("product") if isinstance(row.get("product"), dict) else {}
            logistic = row.get("logistic") if isinstance(row.get("logistic"), dict) else {}
            visual = row.get("visual") if isinstance(row.get("visual"), dict) else {}
            visual_status = visual.get("status") if isinstance(visual.get("status"), dict) else {}
            price = product.get("price") if isinstance(product.get("price"), dict) else {}
            conn.execute(
                """INSERT INTO marketplace_returns
                   (account_id,external_id,scheme,status,posting_number,product_id,offer_id,sku,product_name,
                    quantity,amount,returned_at,payload_json,updated_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(account_id,external_id) DO UPDATE SET
                   scheme=excluded.scheme,status=excluded.status,posting_number=excluded.posting_number,
                   product_id=excluded.product_id,offer_id=excluded.offer_id,sku=excluded.sku,
                   product_name=excluded.product_name,quantity=excluded.quantity,amount=excluded.amount,
                   returned_at=excluded.returned_at,payload_json=excluded.payload_json,updated_at=excluded.updated_at""",
                (account_id, external_id, _text(row.get("schema") or scheme),
                 _text(_first(visual_status, "name", "display_name", default=_first(row, "status", "type"))),
                 _text(row.get("posting_number")), _text(_first(product, "product_id", "id")),
                 _text(product.get("offer_id")), _text(product.get("sku")), _text(product.get("name")),
                 _integer(_first(product, "quantity", "count", default=1)),
                 _number(_first(price, "price", default=_first(product, "amount"))),
                 _text(_first(logistic, "return_date", default=_first(row, "returned_at", "return_date", "logistic_return_date", "created_at"))),
                 _json(row), _now()),
            )
    counts["returns"] = len(returns)
    counts["rfbs_returns"] = len(rfbs_returns)

    rating = safely("rating", client.rating, {})
    if rating:
        today = date.today().isoformat()
        conn.execute(
            """INSERT INTO marketplace_ratings (account_id,observed_date,rating,payload_json,updated_at)
               VALUES (?,?,?,?,?) ON CONFLICT(account_id,observed_date) DO UPDATE SET
               rating=excluded.rating,payload_json=excluded.payload_json,updated_at=excluded.updated_at""",
            (account_id, today, _rating_value(rating), _json(rating), _now()),
        )
        counts["rating"] = 1

    state = conn.execute(
        "SELECT cursor_value FROM marketplace_extended_sync_state WHERE account_id=? AND resource='finance_history'",
        (account_id,),
    ).fetchone()
    current_days = max(1, min(31, int(os.getenv("OZON_FINANCE_CURRENT_DAYS", "31"))))
    history_days = max(1, min(31, int(os.getenv("OZON_FINANCE_HISTORY_BATCH_DAYS", "7"))))
    history_end = date.fromisoformat(state[0]) if state and state[0] else date.today() - timedelta(days=current_days)
    finance_dates = [date.today() - timedelta(days=value) for value in range(current_days)]
    finance_dates.extend(history_end - timedelta(days=value) for value in range(1, history_days + 1))
    for value in dict.fromkeys(finance_dates):
        rows, _ = safely(f"finance {value}", lambda value=value: client.accrual_day(value), ([], ""))
        _save_accruals(conn, account_id, value.isoformat(), rows)
        counts["finance"] += len(rows)
        time.sleep(0.15)
    next_history = history_end - timedelta(days=history_days)
    conn.execute(
        """INSERT INTO marketplace_extended_sync_state (account_id,resource,cursor_value,updated_at)
           VALUES (?,'finance_history',?,?) ON CONFLICT(account_id,resource) DO UPDATE SET
           cursor_value=excluded.cursor_value,updated_at=excluded.updated_at""",
        (account_id, next_history.isoformat(), _now()),
    )

    posting_accruals = safely("posting_accruals", lambda: client.posting_accruals(posting_numbers), [])
    _save_accruals(conn, account_id, date.today().isoformat(), posting_accruals)
    counts["finance"] += len(posting_accruals)
    conn.commit()
    return {"counts": counts, "errors": errors}


def dashboard_extension(conn, account_id: int) -> dict:
    ensure_schema(conn)
    finance_daily = [dict(row) for row in conn.execute(
        """SELECT accrual_date AS date,
                  ROUND(SUM(CASE WHEN amount>0 THEN amount ELSE 0 END),2) AS revenue,
                  ROUND(SUM(amount),2) AS net,
                  COUNT(*) AS records
             FROM marketplace_finance_accruals WHERE account_id=?
             GROUP BY accrual_date ORDER BY accrual_date""", (account_id,)
    )]
    returns_rows = [dict(row) for row in conn.execute(
        """SELECT external_id,scheme,status,posting_number,product_name,offer_id,sku,quantity,amount,returned_at
             FROM marketplace_returns WHERE account_id=? ORDER BY returned_at DESC,updated_at DESC LIMIT 500""", (account_id,)
    )]
    returns_daily = [dict(row) for row in conn.execute(
        """SELECT substr(returned_at,1,10) AS date,COUNT(*) AS records,
                  SUM(CASE WHEN quantity>0 THEN quantity ELSE 1 END) AS quantity
             FROM marketplace_returns WHERE account_id=? AND trim(returned_at)<>''
             GROUP BY substr(returned_at,1,10) ORDER BY date""", (account_id,)
    )]
    actions_rows = [dict(row) for row in conn.execute(
        "SELECT external_id,title,status,updated_at FROM marketplace_actions WHERE account_id=? ORDER BY updated_at DESC",
        (account_id,),
    )]
    rating_row = conn.execute(
        "SELECT observed_date,rating,payload_json FROM marketplace_ratings WHERE account_id=? ORDER BY observed_date DESC LIMIT 1",
        (account_id,),
    ).fetchone()
    rating = None
    rating_payload = {}
    if rating_row:
        rating = rating_row[1]
        try:
            rating_payload = json.loads(rating_row[2] or "{}")
        except json.JSONDecodeError:
            rating_payload = {}
    order_counts = {row[0]: row[1] for row in conn.execute(
        "SELECT warehouse_type,COUNT(*) FROM marketplace_orders WHERE account_id=? GROUP BY warehouse_type", (account_id,)
    )}
    return {
        "finance_daily": finance_daily,
        "returns_rows": returns_rows,
        "returns_daily": returns_daily,
        "actions_rows": actions_rows,
        "rating": rating,
        "rating_payload": rating_payload,
        "order_counts": order_counts,
        "finance_available": bool(finance_daily),
        "returns_available": bool(returns_rows),
        "rating_available": bool(rating_row),
    }
