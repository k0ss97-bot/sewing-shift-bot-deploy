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
from http.cookies import SimpleCookie
from pathlib import Path
from urllib.parse import urlencode


PROJECT_DIR = Path(__file__).resolve().parent


class WebAppAuthTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.old_db_dir = os.environ.get("DB_DIR")
        self.old_session_ttl = os.environ.pop("WEBAPP_SESSION_TTL_SECONDS", None)
        self.old_session_idle = os.environ.pop("WEBAPP_SESSION_IDLE_SECONDS", None)
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
        if self.old_session_ttl is not None:
            os.environ["WEBAPP_SESSION_TTL_SECONDS"] = self.old_session_ttl
        else:
            os.environ.pop("WEBAPP_SESSION_TTL_SECONDS", None)
        if self.old_session_idle is not None:
            os.environ["WEBAPP_SESSION_IDLE_SECONDS"] = self.old_session_idle
        else:
            os.environ.pop("WEBAPP_SESSION_IDLE_SECONDS", None)
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
        self.assertIn("Max-Age=60", cookie)
        self.assertIn("SameSite=Strict", cookie)
        self.assertIn("Secure", cookie)
        self.assertEqual(self.auth.session_token_from_cookie(cookie), session["session_token"])

        self.assertTrue(self.auth.revoke_web_session(session["session_token"]))
        self.assertIsNone(self.auth.get_web_session(session["session_token"]))

    def test_session_defaults_are_30_days_and_upper_bounds_are_enforced(self):
        expected = 30 * 24 * 60 * 60
        self.assertEqual(self.auth.DEFAULT_SESSION_TTL_SECONDS, expected)
        self.assertEqual(self.auth.DEFAULT_SESSION_IDLE_SECONDS, expected)
        self.assertEqual(self.auth.MAX_SESSION_LIFETIME_SECONDS, expected)
        self.assertEqual(self.auth._session_ttl_seconds(), expected)
        self.assertEqual(self.auth._session_idle_seconds(), expected)

        os.environ["WEBAPP_SESSION_TTL_SECONDS"] = str(90 * 24 * 60 * 60)
        os.environ["WEBAPP_SESSION_IDLE_SECONDS"] = str(90 * 24 * 60 * 60)
        self.assertEqual(self.auth._session_ttl_seconds(), expected)
        self.assertEqual(self.auth._session_idle_seconds(), expected)

        os.environ.pop("WEBAPP_SESSION_TTL_SECONDS")
        os.environ.pop("WEBAPP_SESSION_IDLE_SECONDS")
        account = self.auth.upsert_web_account("month.session", 22002, "month-session-password")
        authenticated = self.auth.authenticate_web_credentials(
            account["username"], "month-session-password"
        )
        before = int(time.time())
        session = self.auth.create_web_session(authenticated)
        after = int(time.time())
        self.assertGreaterEqual(session["expires_at"], before + expected)
        self.assertLessEqual(session["expires_at"], after + expected)

        cookie = self.auth.build_session_cookie(
            session["session_token"], secure=True, max_age=self.auth._session_ttl_seconds()
        )
        parsed_cookie = SimpleCookie()
        parsed_cookie.load(cookie)
        morsel = parsed_cookie[self.auth.SECURE_COOKIE_NAME]
        self.assertEqual(morsel["max-age"], str(expected))
        self.assertEqual(morsel["path"], "/")
        self.assertTrue(morsel["httponly"])
        self.assertTrue(morsel["secure"])
        self.assertEqual(morsel["samesite"], "Strict")

    def test_updating_password_revokes_existing_sessions(self):
        first = self.auth.upsert_web_account("admin.test", 99001, "first-demo-password")
        authenticated = self.auth.authenticate_web_credentials("admin.test", "first-demo-password")
        session = self.auth.create_web_session(authenticated)

        updated = self.auth.upsert_web_account("admin.test", 99001, "second-demo-password")
        self.assertEqual(first["id"], updated["id"])
        self.assertIsNone(self.auth.get_web_session(session["session_token"]))
        self.assertIsNone(self.auth.authenticate_web_credentials("admin.test", "first-demo-password"))
        self.assertIsNotNone(self.auth.authenticate_web_credentials("admin.test", "second-demo-password"))

    def test_revoking_employee_sessions_closes_every_device(self):
        account = self.auth.upsert_web_account("worker.devices", 99002, "worker-device-password")
        authenticated = self.auth.authenticate_web_credentials("worker.devices", "worker-device-password")
        first_session = self.auth.create_web_session(authenticated, "127.0.0.1", "first-device")
        second_session = self.auth.create_web_session(authenticated, "127.0.0.2", "second-device")

        self.assertEqual(self.auth.revoke_web_sessions_for_telegram_id(account["telegram_id"]), 2)
        self.assertIsNone(self.auth.get_web_session(first_session["session_token"]))
        self.assertIsNone(self.auth.get_web_session(second_session["session_token"]))

    def test_employee_can_change_password_and_existing_sessions_are_revoked(self):
        account = self.auth.upsert_web_account("worker.password", 99003, "first-worker-password")
        authenticated = self.auth.authenticate_web_credentials("worker.password", "first-worker-password")
        session = self.auth.create_web_session(authenticated)

        rejected = self.auth.change_web_password(account["id"], "wrong-password", "second-worker-password")
        self.assertFalse(rejected["ok"])
        self.assertIsNotNone(self.auth.get_web_session(session["session_token"]))

        changed = self.auth.change_web_password(account["id"], "first-worker-password", "second-worker-password")
        self.assertTrue(changed["ok"])
        self.assertIsNone(self.auth.get_web_session(session["session_token"]))
        self.assertIsNone(self.auth.authenticate_web_credentials("worker.password", "first-worker-password"))
        self.assertIsNotNone(self.auth.authenticate_web_credentials("worker.password", "second-worker-password"))

    def test_database_roles_are_atomic_and_preserve_last_admin(self):
        self.database.create_employee(99101, "Первый Администратор", "Швея")
        first = self.database.get_employee_by_telegram_id(99101)
        promoted = self.database.update_employee_role(first[0], "admin")
        self.assertTrue(promoted["ok"])
        self.assertEqual(promoted["employee"][3], "Администратор")
        self.assertEqual(promoted["employee"][4], "admin")
        self.assertEqual(promoted["employee"][5], "active")

        blocked = self.database.update_employee_role(first[0], "employee", "Швея")
        self.assertFalse(blocked["ok"])
        self.assertEqual(blocked["code"], "last_admin")
        blocked_status = self.database.update_employee_access_status(first[0], "inactive")
        self.assertFalse(blocked_status["ok"])
        self.assertEqual(blocked_status["code"], "last_admin")

        self.database.create_employee(99102, "Второй Администратор", "Упаковщик")
        second = self.database.get_employee_by_telegram_id(99102)
        self.assertTrue(self.database.update_employee_role(second[0], "admin")["ok"])
        demoted = self.database.update_employee_role(first[0], "employee", "Раскройщик")
        self.assertTrue(demoted["ok"])
        self.assertEqual(demoted["employee"][3], "Раскройщик")
        self.assertEqual(demoted["employee"][4], "employee")

        accounts = self.database.get_all_user_accounts()
        self.assertEqual({row[5] for row in accounts}, {"admin", "employee"})

    def test_rejects_weak_account_credentials(self):
        with self.assertRaises(ValueError):
            self.auth.upsert_web_account("x", 1, "strong-demo-password")
        with self.assertRaises(ValueError):
            self.auth.upsert_web_account("valid-user", 1, "short")

    def test_registration_creates_pending_employee_and_supports_email_or_phone_login(self):
        registration = self.auth.register_web_account(
            " Worker.Test@Example.RU ",
            "8 (999) 123-45-67",
            "Иванова Наталья Сергеевна",
            "registration-password",
        )

        self.assertEqual(registration["email"], "worker.test@example.ru")
        self.assertEqual(registration["phone"], "+79991234567")
        self.assertEqual(registration["status"], "pending")
        self.assertLess(registration["telegram_id"], 0)
        employee = self.database.get_employee_by_telegram_id(registration["telegram_id"])
        self.assertEqual(employee[2], "Иванова Наталья Сергеевна")
        self.assertIsNone(employee[3])
        self.assertEqual(employee[4], "employee")
        self.assertEqual(employee[5], "pending")

        by_email = self.auth.authenticate_web_credentials(
            "WORKER.TEST@EXAMPLE.RU", "registration-password"
        )
        by_phone = self.auth.authenticate_web_credentials(
            "+7 999 123-45-67", "registration-password"
        )
        self.assertEqual(by_email["telegram_id"], registration["telegram_id"])
        self.assertEqual(by_phone["telegram_id"], registration["telegram_id"])

        with self.assertRaises(self.auth.WebRegistrationError) as duplicate_email:
            self.auth.register_web_account(
                "worker.test@example.ru",
                "+7 999 765-43-21",
                "Петров Иван Сергеевич",
                "registration-password",
            )
        self.assertEqual(duplicate_email.exception.code, "email_exists")

        with self.assertRaises(self.auth.WebRegistrationError) as duplicate_phone:
            self.auth.register_web_account(
                "second.worker@example.ru",
                "8 999 123 45 67",
                "Петров Иван Сергеевич",
                "registration-password",
            )
        self.assertEqual(duplicate_phone.exception.code, "phone_exists")


@unittest.skipUnless(os.getenv("RUN_HTTP_TESTS") == "1", "HTTP binding is an opt-in integration test")
class WebAppHttpTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.old_db_dir = os.environ.get("DB_DIR")
        self.old_admin_ids = os.environ.get("ADMIN_IDS")
        self.old_session_ttl = os.environ.pop("WEBAPP_SESSION_TTL_SECONDS", None)
        self.old_session_idle = os.environ.pop("WEBAPP_SESSION_IDLE_SECONDS", None)
        os.environ["DB_DIR"] = self.temp_dir.name
        os.environ.pop("ADMIN_IDS", None)
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
        if self.old_admin_ids is None:
            os.environ.pop("ADMIN_IDS", None)
        else:
            os.environ["ADMIN_IDS"] = self.old_admin_ids
        if self.old_session_ttl is not None:
            os.environ["WEBAPP_SESSION_TTL_SECONDS"] = self.old_session_ttl
        else:
            os.environ.pop("WEBAPP_SESSION_TTL_SECONDS", None)
        if self.old_session_idle is not None:
            os.environ["WEBAPP_SESSION_IDLE_SECONDS"] = self.old_session_idle
        else:
            os.environ.pop("WEBAPP_SESSION_IDLE_SECONDS", None)
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
        response_headers = dict(response.getheaders())
        if response_headers.get("Content-Type", "").startswith("application/json"):
            result = json.loads(response_body.decode("utf-8")) if response_body else {}
        else:
            result = response_body
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
        set_cookie = headers["Set-Cookie"]
        parsed_cookie = SimpleCookie()
        parsed_cookie.load(set_cookie)
        session_morsel = parsed_cookie.get(self.auth.COOKIE_NAME) or parsed_cookie.get(
            self.auth.SECURE_COOKIE_NAME
        )
        self.assertIsNotNone(session_morsel)
        cookie_max_age = int(session_morsel["max-age"])
        self.assertGreaterEqual(cookie_max_age, self.auth.DEFAULT_SESSION_TTL_SECONDS - 1)
        self.assertLessEqual(cookie_max_age, self.auth.DEFAULT_SESSION_TTL_SECONDS)
        cookie = set_cookie.split(";", 1)[0]
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
        self.assertEqual(telegram_state["employee"]["telegram_id"], 23001)

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

        status, repeated_logout, repeated_clear_headers = self.request(
            "POST",
            "/api/web/logout",
            {},
            {"Cookie": cookie, "X-CSRF-Token": csrf, "Origin": self.origin},
        )
        self.assertEqual(status, 200)
        self.assertTrue(repeated_logout["ok"])
        self.assertIn("Max-Age=0", repeated_clear_headers["Set-Cookie"])

    def test_registration_waits_for_admin_approval_then_allows_phone_login(self):
        payload = {
            "full_name": "Сидорова Мария Петровна",
            "email": "new.worker@example.ru",
            "phone": "+7 921 555-44-33",
            "password": "new-worker-password",
        }
        status, result, _ = self.request("POST", "/api/web/register", payload)
        self.assertEqual(status, 403)
        self.assertEqual(result["code"], "invalid_origin")

        status, result, _ = self.request(
            "POST", "/api/web/register", payload, {"Origin": self.origin}
        )
        self.assertEqual(status, 201)
        self.assertTrue(result["ok"])
        self.assertEqual(result["status"], "pending")

        status, result, _ = self.request(
            "POST",
            "/api/web/login",
            {"username": "new.worker@example.ru", "password": "new-worker-password"},
            {"Origin": self.origin},
        )
        self.assertEqual(status, 403)
        self.assertEqual(result["code"], "account_pending")

        account = self.auth.authenticate_web_credentials(
            "new.worker@example.ru", "new-worker-password"
        )
        employee = self.database.get_employee_by_telegram_id(account["telegram_id"])
        self.database.update_employee_position(employee[0], "Швея")
        self.database.update_employee_status(employee[0], "active")

        status, result, headers = self.request(
            "POST",
            "/api/web/login",
            {"username": "8 (921) 555-44-33", "password": "new-worker-password"},
            {"Origin": self.origin},
        )
        self.assertEqual(status, 200)
        self.assertTrue(result["ok"])
        self.assertIn("Set-Cookie", headers)

    def test_database_admin_role_grants_web_admin_access(self):
        self.database.create_employee(23003, "Веб Администратор", "Швея")
        employee = self.database.get_employee_by_telegram_id(23003)
        self.assertTrue(self.database.update_employee_role(employee[0], "admin")["ok"])
        self.auth.upsert_web_account("web-admin", 23003, "web-admin-password")

        status, login, headers = self.request(
            "POST",
            "/api/web/login",
            {"username": "web-admin", "password": "web-admin-password"},
            {"Origin": self.origin},
        )
        self.assertEqual(status, 200)
        cookie = headers["Set-Cookie"].split(";", 1)[0]
        request_headers = {
            "Cookie": cookie,
            "X-CSRF-Token": login["csrf_token"],
            "Origin": self.origin,
        }

        status, app_state, _ = self.request("POST", "/api/app/state", {}, request_headers)
        self.assertEqual(status, 200)
        self.assertTrue(app_state["is_admin"])
        self.assertTrue(app_state["features"]["can_admin"])
        self.assertEqual(app_state["employee"]["position"], "Администратор")

        status, dashboard, _ = self.request("POST", "/api/admin/dashboard", {}, request_headers)
        self.assertEqual(status, 200)
        self.assertTrue(dashboard["ok"])
        self.assertTrue(any(row["role"] == "admin" for row in dashboard["user_accounts"]))

        task = self.database.create_production_task(
            "Шорты",
            ["80"],
            ["Бежевый"],
            employee[0],
            attachment={
                "file_name": "раскрой.pdf",
                "mime_type": "application/pdf",
                "content_base64": "ZmlsZQ==",
            },
        )
        status, content, file_headers = self.request(
            "GET",
            f"/api/production/task-attachment?task_id={task['id']}&mode=open",
            headers={"Cookie": cookie},
        )
        self.assertEqual(status, 200)
        self.assertEqual(content, b"file")
        self.assertTrue(file_headers["Content-Disposition"].startswith("inline;"))
        status, content, file_headers = self.request(
            "GET",
            f"/api/production/task-attachment?task_id={task['id']}&mode=download",
            headers={"Cookie": cookie},
        )
        self.assertEqual(status, 200)
        self.assertEqual(content, b"file")
        self.assertTrue(file_headers["Content-Disposition"].startswith("attachment;"))

        status, demotion, _ = self.request(
            "POST",
            "/api/admin/employee/role",
            {"employee_id": employee[0], "role": "employee", "position": "Швея"},
            request_headers,
        )
        self.assertEqual(status, 200)
        self.assertFalse(demotion["ok"])
        self.assertIn("собственного аккаунта", demotion["message"])

    def test_admin_can_delete_unused_employee_and_web_access(self):
        self.database.create_employee(23003, "Веб Администратор", "Швея")
        admin = self.database.get_employee_by_telegram_id(23003)
        self.assertTrue(self.database.update_employee_role(admin[0], "admin")["ok"])
        self.auth.upsert_web_account("delete-admin", 23003, "delete-admin-password")

        status, login, headers = self.request(
            "POST",
            "/api/web/login",
            {"username": "delete-admin", "password": "delete-admin-password"},
            {"Origin": self.origin},
        )
        self.assertEqual(status, 200)
        admin_headers = {
            "Cookie": headers["Set-Cookie"].split(";", 1)[0],
            "X-CSRF-Token": login["csrf_token"],
            "Origin": self.origin,
        }

        self.database.create_employee(23004, "Удаляемый Сотрудник", "Упаковщик")
        target = self.database.get_employee_by_telegram_id(23004)
        self.database.update_employee_status(target[0], "active")
        self.auth.upsert_web_account("delete-worker", 23004, "delete-worker-password")
        signed_in_target = self.auth.authenticate_web_credentials("delete-worker", "delete-worker-password")
        target_session = self.auth.create_web_session(signed_in_target)

        status, result, _ = self.request(
            "POST",
            "/api/admin/employee/delete",
            {"employee_id": target[0]},
            admin_headers,
        )
        self.assertEqual(status, 200)
        self.assertTrue(result["ok"], result)
        self.assertIsNone(self.database.get_employee_by_telegram_id(23004))
        self.assertIsNone(self.auth.authenticate_web_credentials("delete-worker", "delete-worker-password"))
        self.assertIsNone(self.auth.get_web_session(target_session["session_token"]))

    def test_admin_cannot_delete_employee_with_production_history(self):
        self.database.create_employee(23003, "Веб Администратор", "Швея")
        admin = self.database.get_employee_by_telegram_id(23003)
        self.assertTrue(self.database.update_employee_role(admin[0], "admin")["ok"])
        self.auth.upsert_web_account("history-admin", 23003, "history-admin-password")
        status, login, headers = self.request(
            "POST",
            "/api/web/login",
            {"username": "history-admin", "password": "history-admin-password"},
            {"Origin": self.origin},
        )
        self.assertEqual(status, 200)
        admin_headers = {
            "Cookie": headers["Set-Cookie"].split(";", 1)[0],
            "X-CSRF-Token": login["csrf_token"],
            "Origin": self.origin,
        }

        self.database.create_employee(23004, "Сотрудник с историей", "Упаковщик")
        target = self.database.get_employee_by_telegram_id(23004)
        self.database.update_employee_status(target[0], "active")
        self.database.create_shift(target[0])

        status, result, _ = self.request(
            "POST",
            "/api/admin/employee/delete",
            {"employee_id": target[0]},
            admin_headers,
        )
        self.assertEqual(status, 200)
        self.assertFalse(result["ok"])
        self.assertIn("сохранить отчёты", result["message"])
        self.assertIsNotNone(self.database.get_employee_by_telegram_id(23004))

    def test_disabled_employee_session_is_revoked_on_restore(self):
        status, login, headers = self.request(
            "POST",
            "/api/web/login",
            {"username": "web-worker", "password": "web-worker-password"},
            {"Origin": self.origin},
        )
        self.assertEqual(status, 200)
        cookie = headers["Set-Cookie"].split(";", 1)[0]
        session_token = cookie.split("=", 1)[1]

        employee = self.database.get_employee_by_telegram_id(23001)
        self.assertTrue(self.database.update_employee_access_status(employee[0], "inactive")["ok"])

        status, result, restore_headers = self.request(
            "GET", "/api/web/session", headers={"Cookie": cookie}
        )
        self.assertEqual(status, 401)
        self.assertEqual(result["code"], "account_disabled")
        self.assertIn("Max-Age=0", restore_headers["Set-Cookie"])
        self.assertIsNone(self.auth.get_web_session(session_token))

    def test_web_password_endpoint_requires_current_password_and_logs_out(self):
        status, login, headers = self.request(
            "POST",
            "/api/web/login",
            {"username": "web-worker", "password": "web-worker-password"},
            {"Origin": self.origin},
        )
        self.assertEqual(status, 200)
        cookie = headers["Set-Cookie"].split(";", 1)[0]
        request_headers = {
            "Cookie": cookie,
            "X-CSRF-Token": login["csrf_token"],
            "Origin": self.origin,
        }

        status, rejected, _ = self.request(
            "POST",
            "/api/web/password",
            {"current_password": "wrong-password", "new_password": "new-web-worker-password"},
            request_headers,
        )
        self.assertEqual(status, 400)
        self.assertEqual(rejected["code"], "invalid_current_password")

        status, changed, changed_headers = self.request(
            "POST",
            "/api/web/password",
            {"current_password": "web-worker-password", "new_password": "new-web-worker-password"},
            request_headers,
        )
        self.assertEqual(status, 200)
        self.assertTrue(changed["ok"])
        self.assertIn("Max-Age=0", changed_headers["Set-Cookie"])

        status, _, _ = self.request("GET", "/api/web/session", headers={"Cookie": cookie})
        self.assertEqual(status, 401)
        status, _, _ = self.request(
            "POST",
            "/api/web/login",
            {"username": "web-worker", "password": "new-web-worker-password"},
            {"Origin": self.origin},
        )
        self.assertEqual(status, 200)

    def test_rejected_origin_consumes_request_body_on_keep_alive_connection(self):
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        body = json.dumps({"email": "blocked@example.ru", "password": "blocked-password"})
        connection.request(
            "POST",
            "/api/web/register",
            body=body,
            headers={
                "Content-Type": "application/json",
                "Origin": "https://invalid.example",
            },
        )
        rejected = connection.getresponse()
        rejected.read()
        self.assertEqual(rejected.status, 403)

        connection.request("GET", "/health")
        health = connection.getresponse()
        health_payload = json.loads(health.read().decode("utf-8"))
        connection.close()
        self.assertEqual(health.status, 200)
        self.assertEqual(health_payload, {"ok": True})


if __name__ == "__main__":
    unittest.main()
