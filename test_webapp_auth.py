import importlib
import http.client
import hashlib
import hmac
import json
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from urllib.parse import urlencode


PROJECT_DIR = Path(__file__).resolve().parent


class WebAppAuthTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.old_db_dir = os.environ.get("DB_DIR")
        os.environ["DB_DIR"] = self.temp_dir.name
        sys.path.insert(0, str(PROJECT_DIR))
        for module_name in ["database", "webapp_auth"]:
            sys.modules.pop(module_name, None)
        self.database = importlib.import_module("database")
        self.database.init_db()
        self.auth = importlib.import_module("webapp_auth")
        self.auth.init_web_auth()

    def tearDown(self):
        if self.old_db_dir is None:
            os.environ.pop("DB_DIR", None)
        else:
            os.environ["DB_DIR"] = self.old_db_dir
        for module_name in ["database", "webapp_auth"]:
            sys.modules.pop(module_name, None)
        if str(PROJECT_DIR) in sys.path:
            sys.path.remove(str(PROJECT_DIR))
        self.temp_dir.cleanup()

    def test_account_login_session_csrf_and_logout(self):
        account = self.auth.upsert_web_account("worker.test", 22001, "strong-demo-password")
        self.assertEqual(account["username"], "worker.test")
        self.assertIsNone(self.auth.authenticate_web_credentials("worker.test", "wrong-password"))

        authenticated = self.auth.authenticate_web_credentials("WORKER.TEST", "strong-demo-password")
        self.assertEqual(authenticated["telegram_id"], 22001)
        session = self.auth.create_web_session(authenticated, "127.0.0.1", "unit-test")

        self.assertIsNone(
            self.auth.get_web_session(session["session_token"], "wrong-csrf", require_csrf=True)
        )
        restored = self.auth.get_web_session(
            session["session_token"], session["csrf_token"], require_csrf=True
        )
        self.assertEqual(restored["telegram_id"], 22001)
        self.assertEqual(restored["csrf_token"], session["csrf_token"])

        cookie = self.auth.build_session_cookie(session["session_token"], secure=True, max_age=60)
        self.assertIn("HttpOnly", cookie)
        self.assertIn("SameSite=Strict", cookie)
        self.assertIn("Secure", cookie)
        self.assertEqual(self.auth.session_token_from_cookie(cookie), session["session_token"])

        self.assertTrue(self.auth.revoke_web_session(session["session_token"]))
        self.assertIsNone(self.auth.get_web_session(session["session_token"]))

    def test_updating_password_revokes_existing_sessions(self):
        first = self.auth.upsert_web_account("admin.test", 99001, "first-demo-password")
        authenticated = self.auth.authenticate_web_credentials("admin.test", "first-demo-password")
        session = self.auth.create_web_session(authenticated)

        updated = self.auth.upsert_web_account("admin.test", 99001, "second-demo-password")
        self.assertEqual(first["id"], updated["id"])
        self.assertIsNone(self.auth.get_web_session(session["session_token"]))
        self.assertIsNone(self.auth.authenticate_web_credentials("admin.test", "first-demo-password"))
        self.assertIsNotNone(self.auth.authenticate_web_credentials("admin.test", "second-demo-password"))

    def test_rejects_weak_account_credentials(self):
        with self.assertRaises(ValueError):
            self.auth.upsert_web_account("x", 1, "strong-demo-password")
        with self.assertRaises(ValueError):
            self.auth.upsert_web_account("valid-user", 1, "short")


@unittest.skipUnless(os.getenv("RUN_HTTP_TESTS") == "1", "HTTP binding is an opt-in integration test")
class WebAppHttpTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.old_db_dir = os.environ.get("DB_DIR")
        os.environ["DB_DIR"] = self.temp_dir.name
        sys.path.insert(0, str(PROJECT_DIR))
        for module_name in ["database", "webapp_auth", "miniapp_server"]:
            sys.modules.pop(module_name, None)
        self.database = importlib.import_module("database")
        self.database.init_db()
        self.database.create_employee(23001, "Веб Сотрудник", "Швея")
        employee = self.database.get_employee_by_telegram_id(23001)
        self.database.update_employee_status(employee[0], "active")
        self.database.create_employee(23002, "Telegram Сотрудник", "Упаковщик")
        telegram_employee = self.database.get_employee_by_telegram_id(23002)
        self.database.update_employee_status(telegram_employee[0], "active")
        self.auth = importlib.import_module("webapp_auth")
        self.auth.upsert_web_account("web-worker", 23001, "web-worker-password")
        self.server_module = importlib.import_module("miniapp_server")
        self.server = self.server_module.start_miniapp_server("test-secret", "127.0.0.1", 0, debug=False)
        self.port = self.server.server_address[1]
        self.origin = f"http://127.0.0.1:{self.port}"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        if self.old_db_dir is None:
            os.environ.pop("DB_DIR", None)
        else:
            os.environ["DB_DIR"] = self.old_db_dir
        for module_name in ["database", "webapp_auth", "miniapp_server"]:
            sys.modules.pop(module_name, None)
        if str(PROJECT_DIR) in sys.path:
            sys.path.remove(str(PROJECT_DIR))
        self.temp_dir.cleanup()

    def request(self, method, path, payload=None, headers=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        body = json.dumps(payload or {}) if payload is not None else None
        request_headers = dict(headers or {})
        if body is not None:
            request_headers["Content-Type"] = "application/json"
        connection.request(method, path, body=body, headers=request_headers)
        response = connection.getresponse()
        response_body = response.read()
        result = json.loads(response_body.decode("utf-8")) if response_body else {}
        response_headers = dict(response.getheaders())
        connection.close()
        return response.status, result, response_headers

    def telegram_init_data(self, telegram_id, auth_date=None):
        values = {
            "auth_date": str(int(auth_date if auth_date is not None else time.time())),
            "user": json.dumps({"id": telegram_id}, ensure_ascii=False, separators=(",", ":")),
        }
        check_string = "\n".join(f"{key}={value}" for key, value in sorted(values.items()))
        secret = hmac.new(b"WebAppData", b"test-secret", hashlib.sha256).digest()
        values["hash"] = hmac.new(secret, check_string.encode("utf-8"), hashlib.sha256).hexdigest()
        return urlencode(values)

    def test_telegram_init_data_rejects_tampering_expiry_and_future(self):
        valid = self.telegram_init_data(23002)
        self.assertEqual(self.server_module.parse_telegram_init_data(valid, "test-secret")["id"], 23002)
        self.assertIsNone(self.server_module.parse_telegram_init_data(valid.replace("23002", "23003"), "test-secret"))
        expired = self.telegram_init_data(23002, time.time() - self.server_module.AUTH_MAX_AGE_SECONDS - 5)
        self.assertIsNone(self.server_module.parse_telegram_init_data(expired, "test-secret"))
        future = self.telegram_init_data(23002, time.time() + 120)
        self.assertIsNone(self.server_module.parse_telegram_init_data(future, "test-secret"))

    def test_public_debug_and_insecure_production_start_are_refused(self):
        self.assertIsNone(
            self.server_module.start_miniapp_server("test-secret", "0.0.0.0", 0, debug=True)
        )
        previous_env = os.environ.get("WEBAPP_ENV")
        previous_secure = os.environ.get("WEBAPP_COOKIE_SECURE")
        previous_origin = os.environ.get("WEBAPP_PUBLIC_ORIGIN")
        try:
            os.environ["WEBAPP_ENV"] = "production"
            os.environ["WEBAPP_COOKIE_SECURE"] = "0"
            os.environ["WEBAPP_PUBLIC_ORIGIN"] = "http://example.test"
            self.assertIsNone(
                self.server_module.start_miniapp_server("test-secret", "127.0.0.1", 0, debug=False)
            )
        finally:
            for name, value in {
                "WEBAPP_ENV": previous_env,
                "WEBAPP_COOKIE_SECURE": previous_secure,
                "WEBAPP_PUBLIC_ORIGIN": previous_origin,
            }.items():
                if value is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = value

    def test_web_cookie_and_csrf_protect_api(self):
        status, _, _ = self.request(
            "POST", "/api/web/login", {"username": "web-worker", "password": "web-worker-password"}
        )
        self.assertEqual(status, 403)

        status, _, _ = self.request(
            "POST",
            "/api/web/login",
            {"username": "web-worker", "password": "wrong-password"},
            {"Origin": self.origin},
        )
        self.assertEqual(status, 401)

        status, login, headers = self.request(
            "POST",
            "/api/web/login",
            {"username": "web-worker", "password": "web-worker-password"},
            {"Origin": self.origin},
        )
        self.assertEqual(status, 200)
        cookie = headers["Set-Cookie"].split(";", 1)[0]
        csrf = login["csrf_token"]

        status, _, _ = self.request(
            "POST", "/api/app/state", {}, {"Cookie": cookie, "Origin": self.origin}
        )
        self.assertEqual(status, 401)

        status, app_state, _ = self.request(
            "POST",
            "/api/app/state",
            {},
            {"Cookie": cookie, "X-CSRF-Token": csrf, "Origin": self.origin},
        )
        self.assertEqual(status, 200)
        self.assertEqual(app_state["employee"]["telegram_id"], 23001)

        status, telegram_state, _ = self.request(
            "POST",
            "/api/app/state",
            {"initData": self.telegram_init_data(23002)},
            {"Cookie": cookie, "X-CSRF-Token": csrf, "Origin": self.origin},
        )
        self.assertEqual(status, 200)
        self.assertEqual(telegram_state["employee"]["telegram_id"], 23002)

        status, _, _ = self.request(
            "POST",
            "/api/app/state",
            {},
            {"Cookie": cookie, "X-CSRF-Token": csrf, "Origin": "https://invalid.example"},
        )
        self.assertEqual(status, 403)

        status, restored, _ = self.request("GET", "/api/web/session", headers={"Cookie": cookie})
        self.assertEqual(status, 200)
        self.assertEqual(restored["csrf_token"], csrf)

        status, _, _ = self.request(
            "POST",
            "/api/web/logout",
            {},
            {"Cookie": cookie, "X-CSRF-Token": "wrong", "Origin": self.origin},
        )
        self.assertEqual(status, 403)
        status, _, _ = self.request("GET", "/api/web/session", headers={"Cookie": cookie})
        self.assertEqual(status, 200)

        status, _, clear_headers = self.request(
            "POST",
            "/api/web/logout",
            {},
            {"Cookie": cookie, "X-CSRF-Token": csrf, "Origin": self.origin},
        )
        self.assertEqual(status, 200)
        self.assertIn("Max-Age=0", clear_headers["Set-Cookie"])


if __name__ == "__main__":
    unittest.main()
