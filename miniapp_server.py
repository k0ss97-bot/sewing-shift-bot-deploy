import hashlib
import hmac
import json
import logging
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qsl, urlparse

from database import (
    add_edit_log,
    close_shift,
    create_shift,
    ensure_admin_employee,
    get_employee_by_telegram_id,
    get_open_shift_for_today,
    get_shift_for_today,
)
from miniapp_auth import parse_auth_token


AUTH_MAX_AGE_SECONDS = 7 * 24 * 60 * 60


def get_admin_ids():
    admin_ids = []
    raw_admin_ids = os.getenv("ADMIN_IDS", "").replace("ADMIN_IDS=", "")

    for raw_admin_id in raw_admin_ids.split(","):
        raw_admin_id = raw_admin_id.strip()

        if not raw_admin_id:
            continue

        try:
            admin_ids.append(int(raw_admin_id))
        except ValueError:
            logging.warning("Invalid ADMIN_IDS item ignored: %s", raw_admin_id)

    return admin_ids


def is_admin(telegram_id: int):
    return telegram_id in get_admin_ids()


def get_employee_for_access(telegram_id: int):
    if is_admin(telegram_id):
        return ensure_admin_employee(telegram_id)

    return get_employee_by_telegram_id(telegram_id)


def format_minutes(total_minutes: int | None):
    if total_minutes is None:
        return ""

    hours = total_minutes // 60
    minutes = total_minutes % 60
    return f"{hours}:{minutes:02d}"


def parse_telegram_init_data(init_data: str, bot_token: str):
    if not init_data or not bot_token:
        return None

    parsed_items = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = parsed_items.pop("hash", "")

    if not received_hash:
        return None

    data_check_string = "\n".join(
        f"{key}={value}" for key, value in sorted(parsed_items.items())
    )
    secret_key = hmac.new(
        b"WebAppData",
        bot_token.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(calculated_hash, received_hash):
        return None

    try:
        auth_date = int(parsed_items.get("auth_date", "0"))
    except ValueError:
        return None

    if auth_date <= 0 or time.time() - auth_date > AUTH_MAX_AGE_SECONDS:
        return None

    try:
        return json.loads(parsed_items.get("user", "{}"))
    except json.JSONDecodeError:
        return None


def authenticate_payload(payload: dict, bot_token: str, debug: bool):
    if debug and payload.get("telegram_id"):
        try:
            return {"id": int(payload["telegram_id"])}
        except (TypeError, ValueError):
            return None

    telegram_user = parse_telegram_init_data(payload.get("initData", ""), bot_token)

    if telegram_user:
        return telegram_user

    return parse_auth_token(payload.get("authToken", ""), bot_token)


def shift_to_dict(shift):
    if not shift:
        return None

    return {
        "id": shift[0],
        "date": shift[2],
        "start_time": shift[3],
        "end_time": shift[4],
        "status": shift[5],
    }


def employee_to_dict(employee):
    if not employee:
        return None

    return {
        "id": employee[0],
        "telegram_id": employee[1],
        "full_name": employee[2],
        "position": employee[3],
        "role": employee[4],
        "status": employee[5],
    }


def get_shift_state(telegram_id: int, message: str = ""):
    employee = get_employee_for_access(telegram_id)

    if employee is None:
        return {
            "ok": False,
            "code": "not_registered",
            "message": (
                "Вы не зарегистрированы или ваша запись не перенесена в новую базу. "
                f"Ваш Telegram ID: {telegram_id}. Вернитесь в бот и нажмите /start."
            ),
            "employee": None,
            "shift": None,
        }

    employee_data = employee_to_dict(employee)

    if employee[5] != "active":
        return {
            "ok": False,
            "code": employee[5],
            "message": "Профиль ещё не активен. Дождитесь подтверждения администратора.",
            "employee": employee_data,
            "shift": None,
        }

    open_shift = get_open_shift_for_today(employee[0])
    today_shift = open_shift or get_shift_for_today(employee[0])
    shift_data = shift_to_dict(today_shift)

    if today_shift and today_shift[5] == "closed":
        shift_data["total_minutes_text"] = ""

    return {
        "ok": True,
        "code": "ok",
        "message": message,
        "employee": employee_data,
        "shift": shift_data,
        "has_open_shift": open_shift is not None,
    }


def open_shift_for_telegram(telegram_id: int):
    employee = get_employee_for_access(telegram_id)

    if employee is None or employee[5] != "active":
        return get_shift_state(telegram_id)

    open_shift = get_open_shift_for_today(employee[0])

    if open_shift is not None:
        return get_shift_state(telegram_id, "Смена уже открыта.")

    today_shift = get_shift_for_today(employee[0])

    if today_shift is not None and today_shift[5] == "closed":
        return get_shift_state(telegram_id, "Сегодня смена уже закрыта.")

    shift = create_shift(employee[0])
    add_edit_log(
        telegram_id,
        "employee",
        "Открыл смену из миниаппа",
        "shift",
        shift["id"],
        f"Дата: {shift['shift_date']}, начало: {shift['start_time']}",
    )
    return get_shift_state(telegram_id, "Смена открыта.")


def close_shift_for_telegram(telegram_id: int):
    employee = get_employee_for_access(telegram_id)

    if employee is None or employee[5] != "active":
        return get_shift_state(telegram_id)

    open_shift = get_open_shift_for_today(employee[0])

    if open_shift is None:
        return get_shift_state(telegram_id, "У вас нет открытой смены.")

    result = close_shift(open_shift[0])

    if result is None:
        return get_shift_state(telegram_id, "Не удалось закрыть смену.")

    add_edit_log(
        telegram_id,
        "employee",
        "Закрыл смену из миниаппа",
        "shift",
        open_shift[0],
        f"Окончание: {result['end_time']}, отработано: {format_minutes(result['total_minutes'])}",
    )

    response = get_shift_state(
        telegram_id,
        f"Смена закрыта. Отработано: {format_minutes(result['total_minutes'])}.",
    )

    if response.get("shift"):
        response["shift"]["total_minutes"] = result["total_minutes"]
        response["shift"]["total_minutes_text"] = format_minutes(result["total_minutes"])

    return response


MINIAPP_HTML = """<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Шагаем вместе</title>
  <script src="https://telegram.org/js/telegram-web-app.js"></script>
  <style>
    :root {
      color-scheme: light dark;
      --bg: var(--tg-theme-bg-color, #f4f5f7);
      --text: var(--tg-theme-text-color, #18212f);
      --muted: var(--tg-theme-hint-color, #667085);
      --card: var(--tg-theme-secondary-bg-color, #ffffff);
      --accent: var(--tg-theme-button-color, #2775f6);
      --accent-text: var(--tg-theme-button-text-color, #ffffff);
      --danger: #d92d20;
      --border: rgba(100, 116, 139, 0.22);
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      min-height: 100vh;
      background: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    .page {
      width: min(720px, 100%);
      margin: 0 auto;
      padding: 16px;
    }

    .topbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 16px;
    }

    h1 {
      margin: 0;
      font-size: 22px;
      line-height: 1.2;
      letter-spacing: 0;
    }

    .status {
      padding: 6px 10px;
      border: 1px solid var(--border);
      border-radius: 8px;
      color: var(--muted);
      font-size: 13px;
      white-space: nowrap;
    }

    .card {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 16px;
      margin-bottom: 12px;
    }

    .label {
      margin: 0 0 6px;
      color: var(--muted);
      font-size: 13px;
    }

    .value {
      margin: 0;
      font-size: 18px;
      font-weight: 700;
      line-height: 1.25;
    }

    .grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
      margin-top: 12px;
    }

    button {
      width: 100%;
      min-height: 48px;
      border: 0;
      border-radius: 8px;
      padding: 12px;
      font: inherit;
      font-weight: 700;
      color: var(--accent-text);
      background: var(--accent);
    }

    button.secondary {
      color: var(--text);
      background: transparent;
      border: 1px solid var(--border);
    }

    button.danger {
      background: var(--danger);
    }

    button:disabled {
      opacity: 0.45;
    }

    .message {
      margin-top: 10px;
      color: var(--muted);
      font-size: 14px;
      line-height: 1.35;
    }

    .rows {
      display: grid;
      gap: 10px;
      margin-top: 12px;
    }

    .row {
      display: flex;
      justify-content: space-between;
      gap: 16px;
      padding-top: 10px;
      border-top: 1px solid var(--border);
      color: var(--muted);
      font-size: 14px;
    }

    .row strong {
      color: var(--text);
      text-align: right;
      overflow-wrap: anywhere;
    }

    @media (max-width: 420px) {
      .grid {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body>
  <main class="page">
    <div class="topbar">
      <h1>Шагаем вместе</h1>
      <div class="status" id="connection">Загрузка</div>
    </div>

    <section class="card">
      <p class="label">Сотрудник</p>
      <p class="value" id="employeeName">Проверяем доступ</p>
      <div class="rows">
        <div class="row"><span>Должность</span><strong id="employeePosition">-</strong></div>
        <div class="row"><span>Статус профиля</span><strong id="employeeStatus">-</strong></div>
      </div>
    </section>

    <section class="card">
      <p class="label">Смена</p>
      <p class="value" id="shiftStatus">-</p>
      <div class="rows">
        <div class="row"><span>Дата</span><strong id="shiftDate">-</strong></div>
        <div class="row"><span>Начало</span><strong id="shiftStart">-</strong></div>
        <div class="row"><span>Окончание</span><strong id="shiftEnd">-</strong></div>
        <div class="row"><span>Отработано</span><strong id="shiftTotal">-</strong></div>
      </div>
      <div class="grid">
        <button id="openButton">Открыть смену</button>
        <button id="closeButton" class="danger">Закрыть смену</button>
        <button id="refreshButton" class="secondary">Обновить</button>
      </div>
      <div class="message" id="message"></div>
    </section>
  </main>

  <script>
    const tg = window.Telegram && window.Telegram.WebApp;
    const urlParams = new URLSearchParams(window.location.search);
    const debugTelegramId = urlParams.get("debug_tg_id");
    const authToken = urlParams.get("auth");
    const state = {
      initData: tg ? tg.initData : "",
      loading: false,
    };

    if (tg) {
      tg.ready();
      tg.expand();
    }

    const $ = (id) => document.getElementById(id);

    function setLoading(isLoading) {
      state.loading = isLoading;
      $("connection").textContent = isLoading ? "Обновление" : "Готово";
      $("refreshButton").disabled = isLoading;

      if (isLoading) {
        $("openButton").disabled = true;
        $("closeButton").disabled = true;
      }
    }

    function setText(id, value) {
      $(id).textContent = value || "-";
    }

    function render(data) {
      const employee = data.employee;
      const shift = data.shift;

      setText("employeeName", employee ? employee.full_name : "Нет доступа");
      setText("employeePosition", employee ? employee.position : "-");
      setText("employeeStatus", employee ? employee.status : "-");

      if (!shift) {
        setText("shiftStatus", "Смена не открыта");
        setText("shiftDate", "-");
        setText("shiftStart", "-");
        setText("shiftEnd", "-");
        setText("shiftTotal", "-");
      } else if (shift.status === "open") {
        setText("shiftStatus", "Смена открыта");
        setText("shiftDate", shift.date);
        setText("shiftStart", shift.start_time);
        setText("shiftEnd", "-");
        setText("shiftTotal", "-");
      } else {
        setText("shiftStatus", "Смена закрыта");
        setText("shiftDate", shift.date);
        setText("shiftStart", shift.start_time);
        setText("shiftEnd", shift.end_time);
        setText("shiftTotal", shift.total_minutes_text);
      }

      $("message").textContent = data.message || "";
      $("openButton").disabled = state.loading || !data.ok || data.has_open_shift || (shift && shift.status === "closed");
      $("closeButton").disabled = state.loading || !data.ok || !data.has_open_shift;
    }

    async function request(action) {
      setLoading(true);

      try {
        const response = await fetch(`/api/shift/${action}`, {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({
            initData: state.initData,
            authToken,
            telegram_id: debugTelegramId,
          }),
        });
        const data = await response.json();
        setLoading(false);
        render(data);
      } catch (error) {
        setLoading(false);
        $("connection").textContent = "Ошибка";
        $("message").textContent = "Не удалось связаться с сервером.";
      }
    }

    $("openButton").addEventListener("click", () => request("open"));
    $("closeButton").addEventListener("click", () => request("close"));
    $("refreshButton").addEventListener("click", () => request("status"));

    request("status");
  </script>
</body>
</html>
"""


def make_handler(bot_token: str, debug: bool):
    class MiniAppRequestHandler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def do_GET(self):
            path = urlparse(self.path).path

            if path in {"/", "/app"}:
                self.send_html(MINIAPP_HTML)
                return

            if path == "/health":
                self.send_json({"ok": True})
                return

            self.send_json({"ok": False, "message": "Not found"}, status=404)

        def do_POST(self):
            path = urlparse(self.path).path

            if path not in {"/api/shift/status", "/api/shift/open", "/api/shift/close"}:
                self.send_json({"ok": False, "message": "Not found"}, status=404)
                return

            payload = self.read_json_body()
            user = authenticate_payload(payload, bot_token, debug)

            if not user or not user.get("id"):
                self.send_json(
                    {
                        "ok": False,
                        "code": "unauthorized",
                        "message": "Откройте приложение из Telegram.",
                        "employee": None,
                        "shift": None,
                    },
                    status=401,
                )
                return

            telegram_id = int(user["id"])

            if path.endswith("/open"):
                result = open_shift_for_telegram(telegram_id)
            elif path.endswith("/close"):
                result = close_shift_for_telegram(telegram_id)
            else:
                result = get_shift_state(telegram_id)

            self.send_json(result)

        def read_json_body(self):
            content_length = int(self.headers.get("Content-Length", "0") or "0")
            raw_body = self.rfile.read(content_length) if content_length else b"{}"

            try:
                return json.loads(raw_body.decode("utf-8"))
            except json.JSONDecodeError:
                return {}

        def send_html(self, html_text: str, status: int = 200):
            body = html_text.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def send_json(self, payload: dict, status: int = 200):
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format_string, *args):
            logging.info("Miniapp: " + format_string, *args)

    return MiniAppRequestHandler


class ReusableThreadingHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True


def start_miniapp_server(bot_token: str, host: str, port: int, debug: bool = False):
    if os.getenv("MINIAPP_ENABLED", "1") == "0":
        logging.info("Miniapp server disabled")
        return None

    try:
        server = ReusableThreadingHTTPServer(
            (host, port),
            make_handler(bot_token, debug),
        )
    except OSError:
        logging.exception("Miniapp server failed to bind on %s:%s", host, port)
        return None

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    logging.info("Miniapp server started on %s:%s", host, port)
    return server
