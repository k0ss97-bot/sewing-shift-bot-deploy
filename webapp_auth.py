"""Standalone web authentication for the shared miniapp/webapp backend."""

from __future__ import annotations

import argparse
import getpass
import hashlib
import hmac
import os
import re
import secrets
import sqlite3
import time
from http.cookies import SimpleCookie

from database import DB_NAME, local_now


COOKIE_NAME = "sewing_web_session"
SECURE_COOKIE_NAME = "__Host-sewing_web_session"
PASSWORD_ITERATIONS = 310_000
MIN_PASSWORD_LENGTH = 10
MAX_PASSWORD_LENGTH = 128
MAX_FAILED_ATTEMPTS = 5
LOCK_SECONDS = 5 * 60
MIN_SESSION_LIFETIME_SECONDS = 15 * 60
MAX_SESSION_LIFETIME_SECONDS = 30 * 24 * 60 * 60
DEFAULT_SESSION_TTL_SECONDS = MAX_SESSION_LIFETIME_SECONDS
DEFAULT_SESSION_IDLE_SECONDS = MAX_SESSION_LIFETIME_SECONDS


class WebRegistrationError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def _now_text() -> str:
    return local_now().isoformat(timespec="seconds")


def _session_ttl_seconds() -> int:
    try:
        configured = int(os.getenv("WEBAPP_SESSION_TTL_SECONDS", DEFAULT_SESSION_TTL_SECONDS))
    except (TypeError, ValueError):
        configured = DEFAULT_SESSION_TTL_SECONDS
    return max(MIN_SESSION_LIFETIME_SECONDS, min(configured, MAX_SESSION_LIFETIME_SECONDS))


def _session_idle_seconds() -> int:
    try:
        configured = int(os.getenv("WEBAPP_SESSION_IDLE_SECONDS", DEFAULT_SESSION_IDLE_SECONDS))
    except (TypeError, ValueError):
        configured = DEFAULT_SESSION_IDLE_SECONDS
    return max(MIN_SESSION_LIFETIME_SECONDS, min(configured, _session_ttl_seconds()))


def _normalize_username(username: str) -> str:
    username = str(username or "").strip().casefold()
    if not 3 <= len(username) <= 64:
        return ""
    if any(not (char.isalnum() or char in "._@-") for char in username):
        return ""
    return username


def _normalize_email(email: str) -> str:
    value = str(email or "").strip().casefold()
    if not value or len(value) > 254 or value.count("@") != 1:
        return ""
    local_part, domain = value.rsplit("@", 1)
    if not local_part or len(local_part) > 64 or local_part.startswith(".") or local_part.endswith("."):
        return ""
    if ".." in local_part or re.search(r"\s", local_part):
        return ""
    try:
        ascii_domain = domain.encode("idna").decode("ascii")
    except UnicodeError:
        return ""
    labels = ascii_domain.split(".")
    if len(labels) < 2 or any(
        not label
        or len(label) > 63
        or label.startswith("-")
        or label.endswith("-")
        or not re.fullmatch(r"[a-z0-9-]+", label)
        for label in labels
    ):
        return ""
    return f"{local_part}@{ascii_domain}"


def _normalize_phone(phone: str) -> str:
    value = str(phone or "").strip()
    if not value or not re.fullmatch(r"[+\d\s().-]+", value):
        return ""
    digits = re.sub(r"\D", "", value)
    if len(digits) == 10:
        digits = f"7{digits}"
    elif len(digits) == 11 and digits.startswith("8"):
        digits = f"7{digits[1:]}"
    if not 10 <= len(digits) <= 15:
        return ""
    return f"+{digits}"


def _normalize_full_name(full_name: str) -> str:
    value = " ".join(str(full_name or "").strip().split())
    parts = value.split()
    if not 5 <= len(value) <= 120 or not 2 <= len(parts) <= 5:
        return ""
    if any(
        not any(char.isalpha() for char in part)
        or any(not (char.isalpha() or char in "-'’") for char in part)
        for part in parts
    ):
        return ""
    return value


def _validated_password(password: str) -> str:
    value = str(password or "")
    if len(value) < MIN_PASSWORD_LENGTH:
        raise WebRegistrationError(
            "weak_password",
            f"Пароль должен содержать не менее {MIN_PASSWORD_LENGTH} символов.",
        )
    if len(value) > MAX_PASSWORD_LENGTH:
        raise WebRegistrationError(
            "password_too_long",
            f"Пароль должен содержать не более {MAX_PASSWORD_LENGTH} символов.",
        )
    return value


def _hash_secret(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _client_fingerprint(value: str) -> str:
    value = str(value or "").strip()
    return _hash_secret(value) if value else ""


def _password_hash(password: str, salt_hex: str, iterations: int = PASSWORD_ITERATIONS) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt_hex),
        int(iterations),
    ).hex()


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_NAME, timeout=30)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 30000")
    return conn


def init_web_auth() -> None:
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS web_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER NOT NULL,
            username TEXT NOT NULL COLLATE NOCASE UNIQUE,
            password_salt TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            password_iterations INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            failed_attempts INTEGER NOT NULL DEFAULT 0,
            locked_until INTEGER,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            last_login_at TEXT
        )
        """
    )
    cursor.execute("PRAGMA table_info(web_accounts)")
    account_columns = {column[1] for column in cursor.fetchall()}
    for column_name, definition in {
        "email": "TEXT",
        "phone": "TEXT",
        "full_name": "TEXT",
    }.items():
        if column_name not in account_columns:
            cursor.execute(f"ALTER TABLE web_accounts ADD COLUMN {column_name} {definition}")
    cursor.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_web_accounts_email
        ON web_accounts (email COLLATE NOCASE)
        WHERE email IS NOT NULL AND email != ''
        """
    )
    cursor.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_web_accounts_phone
        ON web_accounts (phone)
        WHERE phone IS NOT NULL AND phone != ''
        """
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_web_accounts_telegram_status ON web_accounts (telegram_id, status)"
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS web_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            token_hash TEXT NOT NULL UNIQUE,
            csrf_token TEXT NOT NULL,
            created_at INTEGER NOT NULL,
            expires_at INTEGER NOT NULL,
            last_seen_at INTEGER NOT NULL,
            revoked_at INTEGER,
            ip_hash TEXT NOT NULL DEFAULT '',
            user_agent_hash TEXT NOT NULL DEFAULT '',
            FOREIGN KEY (account_id) REFERENCES web_accounts(id) ON DELETE CASCADE
        )
        """
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_web_sessions_expiry ON web_sessions (expires_at, revoked_at)"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_web_sessions_account ON web_sessions (account_id, revoked_at)"
    )
    cursor.execute(
        "DELETE FROM web_sessions WHERE expires_at < ? OR revoked_at IS NOT NULL",
        (int(time.time()) - 24 * 60 * 60,),
    )
    conn.commit()
    conn.close()


def upsert_web_account(username: str, telegram_id: int, password: str, active: bool = True) -> dict:
    normalized_username = _normalize_username(username)
    password = str(password or "")
    if not normalized_username:
        raise ValueError("Логин должен содержать от 3 до 64 букв, цифр или символов . _ @ -")
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"Пароль должен содержать не менее {MIN_PASSWORD_LENGTH} символов.")
    if len(password) > MAX_PASSWORD_LENGTH:
        raise ValueError(f"Пароль должен содержать не более {MAX_PASSWORD_LENGTH} символов.")
    try:
        telegram_id = int(telegram_id)
    except (TypeError, ValueError) as error:
        raise ValueError("Некорректный идентификатор пользователя.") from error

    init_web_auth()
    salt_hex = secrets.token_hex(16)
    password_digest = _password_hash(password, salt_hex)
    now_text = _now_text()
    status = "active" if active else "disabled"
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO web_accounts (
            telegram_id, username, password_salt, password_hash,
            password_iterations, status, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(username) DO UPDATE SET
            telegram_id = excluded.telegram_id,
            password_salt = excluded.password_salt,
            password_hash = excluded.password_hash,
            password_iterations = excluded.password_iterations,
            status = excluded.status,
            failed_attempts = 0,
            locked_until = NULL,
            updated_at = excluded.updated_at
        """,
        (
            telegram_id,
            normalized_username,
            salt_hex,
            password_digest,
            PASSWORD_ITERATIONS,
            status,
            now_text,
            now_text,
        ),
    )
    account_id = cursor.execute(
        "SELECT id FROM web_accounts WHERE username = ? COLLATE NOCASE",
        (normalized_username,),
    ).fetchone()[0]
    cursor.execute(
        "UPDATE web_sessions SET revoked_at = ? WHERE account_id = ? AND revoked_at IS NULL",
        (int(time.time()), account_id),
    )
    conn.commit()
    conn.close()
    return {"id": account_id, "telegram_id": telegram_id, "username": normalized_username, "status": status}


def register_web_account(email: str, phone: str, full_name: str, password: str) -> dict:
    normalized_email = _normalize_email(email)
    normalized_phone = _normalize_phone(phone)
    normalized_full_name = _normalize_full_name(full_name)
    if not normalized_email:
        raise WebRegistrationError("invalid_email", "Введите корректный адрес электронной почты.")
    if not normalized_phone:
        raise WebRegistrationError("invalid_phone", "Введите корректный номер телефона.")
    if not normalized_full_name:
        raise WebRegistrationError("invalid_full_name", "Введите фамилию и имя полностью.")
    password = _validated_password(password)

    init_web_auth()
    salt_hex = secrets.token_hex(16)
    password_digest = _password_hash(password, salt_hex)
    now_text = _now_text()
    conn = _connect()
    cursor = conn.cursor()
    try:
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.execute("BEGIN IMMEDIATE")
        if cursor.execute(
            "SELECT 1 FROM web_accounts WHERE email = ? COLLATE NOCASE OR username = ? COLLATE NOCASE",
            (normalized_email, normalized_email),
        ).fetchone():
            raise WebRegistrationError("email_exists", "Пользователь с такой почтой уже зарегистрирован.")
        if cursor.execute(
            "SELECT 1 FROM web_accounts WHERE phone = ? OR username = ? COLLATE NOCASE",
            (normalized_phone, normalized_phone),
        ).fetchone():
            raise WebRegistrationError("phone_exists", "Пользователь с таким телефоном уже зарегистрирован.")

        minimum_telegram_id = cursor.execute(
            "SELECT COALESCE(MIN(telegram_id), 0) FROM employees WHERE telegram_id < 0"
        ).fetchone()[0]
        telegram_id = min(-1, int(minimum_telegram_id or 0) - 1)
        cursor.execute(
            """
            INSERT INTO employees (
                telegram_id, full_name, position, role, status, registered_at
            )
            VALUES (?, ?, NULL, 'employee', 'pending', ?)
            """,
            (telegram_id, normalized_full_name, now_text),
        )
        employee_id = cursor.lastrowid
        cursor.execute(
            """
            INSERT INTO web_accounts (
                telegram_id, username, email, phone, full_name,
                password_salt, password_hash, password_iterations,
                status, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'active', ?, ?)
            """,
            (
                telegram_id,
                normalized_email,
                normalized_email,
                normalized_phone,
                normalized_full_name,
                salt_hex,
                password_digest,
                PASSWORD_ITERATIONS,
                now_text,
                now_text,
            ),
        )
        account_id = cursor.lastrowid
        conn.commit()
    except WebRegistrationError:
        conn.rollback()
        raise
    except sqlite3.IntegrityError as error:
        conn.rollback()
        raise WebRegistrationError(
            "registration_conflict",
            "Почта или телефон уже используются другим пользователем.",
        ) from error
    finally:
        conn.close()

    return {
        "id": account_id,
        "employee_id": employee_id,
        "telegram_id": telegram_id,
        "username": normalized_email,
        "email": normalized_email,
        "phone": normalized_phone,
        "full_name": normalized_full_name,
        "status": "pending",
    }


def get_web_account_profiles_by_telegram_ids(telegram_ids) -> dict[int, dict]:
    normalized_ids = sorted({int(value) for value in telegram_ids})
    if not normalized_ids:
        return {}
    init_web_auth()
    placeholders = ",".join("?" for _ in normalized_ids)
    conn = _connect()
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        f"""
        SELECT telegram_id, email, phone, full_name
        FROM web_accounts
        WHERE telegram_id IN ({placeholders})
        ORDER BY id ASC
        """,
        normalized_ids,
    ).fetchall()
    conn.close()
    return {
        int(row["telegram_id"]): {
            "email": row["email"] or "",
            "phone": row["phone"] or "",
            "full_name": row["full_name"] or "",
        }
        for row in rows
    }


def authenticate_web_credentials(username: str, password: str) -> dict | None:
    raw_username = str(username or "").strip()
    normalized_username = _normalize_username(raw_username)
    normalized_email = _normalize_email(raw_username)
    normalized_phone = _normalize_phone(raw_username)
    password = str(password or "")
    password_to_check = password if len(password) <= MAX_PASSWORD_LENGTH else password[:MAX_PASSWORD_LENGTH]
    init_web_auth()
    conn = _connect()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    account = cursor.execute(
        """
        SELECT * FROM web_accounts
        WHERE username = ? COLLATE NOCASE
           OR email = ? COLLATE NOCASE
           OR phone = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (normalized_username, normalized_email, normalized_phone),
    ).fetchone()

    # Keep unknown-user attempts computationally comparable to known-user attempts.
    if account is None:
        _password_hash(password_to_check, "0" * 32)
        conn.close()
        return None

    now_epoch = int(time.time())
    if account["status"] != "active" or int(account["locked_until"] or 0) > now_epoch:
        conn.close()
        return None

    expected = _password_hash(password_to_check, account["password_salt"], account["password_iterations"])
    if not hmac.compare_digest(expected, account["password_hash"]):
        failed_attempts = int(account["failed_attempts"] or 0) + 1
        locked_until = now_epoch + LOCK_SECONDS if failed_attempts >= MAX_FAILED_ATTEMPTS else None
        cursor.execute(
            "UPDATE web_accounts SET failed_attempts = ?, locked_until = ?, updated_at = ? WHERE id = ?",
            (failed_attempts, locked_until, _now_text(), account["id"]),
        )
        conn.commit()
        conn.close()
        return None

    cursor.execute(
        """
        UPDATE web_accounts
        SET failed_attempts = 0, locked_until = NULL, last_login_at = ?, updated_at = ?
        WHERE id = ?
        """,
        (_now_text(), _now_text(), account["id"]),
    )
    conn.commit()
    result = {
        "id": account["id"],
        "telegram_id": account["telegram_id"],
        "username": account["username"],
        "email": account["email"] or "",
        "phone": account["phone"] or "",
        "full_name": account["full_name"] or "",
    }
    conn.close()
    return result


def change_web_password(account_id: int, current_password: str, new_password: str) -> dict:
    current_password = str(current_password or "")
    try:
        new_password = _validated_password(new_password)
    except WebRegistrationError as error:
        return {"ok": False, "code": error.code, "message": str(error)}

    init_web_auth()
    conn = _connect()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute("BEGIN IMMEDIATE")
        account = cursor.execute(
            "SELECT * FROM web_accounts WHERE id = ? AND status = 'active'",
            (int(account_id),),
        ).fetchone()
        if account is None:
            conn.rollback()
            return {"ok": False, "code": "account_not_found", "message": "Учётная запись не найдена."}

        expected = _password_hash(
            current_password[:MAX_PASSWORD_LENGTH],
            account["password_salt"],
            account["password_iterations"],
        )
        if not hmac.compare_digest(expected, account["password_hash"]):
            conn.rollback()
            return {"ok": False, "code": "invalid_current_password", "message": "Текущий пароль указан неверно."}
        if hmac.compare_digest(current_password, new_password):
            conn.rollback()
            return {"ok": False, "code": "password_unchanged", "message": "Новый пароль должен отличаться от текущего."}

        salt_hex = secrets.token_hex(16)
        password_digest = _password_hash(new_password, salt_hex)
        now_epoch = int(time.time())
        cursor.execute(
            """
            UPDATE web_accounts
            SET password_salt = ?, password_hash = ?, password_iterations = ?,
                failed_attempts = 0, locked_until = NULL, updated_at = ?
            WHERE id = ?
            """,
            (salt_hex, password_digest, PASSWORD_ITERATIONS, _now_text(), int(account_id)),
        )
        cursor.execute(
            "UPDATE web_sessions SET revoked_at = ? WHERE account_id = ? AND revoked_at IS NULL",
            (now_epoch, int(account_id)),
        )
        conn.commit()
        return {"ok": True, "code": "password_changed", "message": "Пароль изменён. Войдите заново."}
    except sqlite3.Error:
        conn.rollback()
        raise
    finally:
        conn.close()


def create_web_session(account: dict, ip_address: str = "", user_agent: str = "") -> dict:
    init_web_auth()
    session_token = secrets.token_urlsafe(32)
    csrf_token = secrets.token_urlsafe(24)
    now_epoch = int(time.time())
    expires_at = now_epoch + _session_ttl_seconds()
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO web_sessions (
            account_id, token_hash, csrf_token, created_at, expires_at,
            last_seen_at, ip_hash, user_agent_hash
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            int(account["id"]),
            _hash_secret(session_token),
            csrf_token,
            now_epoch,
            expires_at,
            now_epoch,
            _client_fingerprint(ip_address),
            _client_fingerprint(user_agent),
        ),
    )
    conn.commit()
    conn.close()
    return {
        "session_token": session_token,
        "csrf_token": csrf_token,
        "expires_at": expires_at,
        "telegram_id": int(account["telegram_id"]),
        "username": account["username"],
    }


def get_web_session(
    session_token: str,
    csrf_token: str = "",
    *,
    require_csrf: bool = False,
    rotate_csrf: bool = False,
) -> dict | None:
    session_token = str(session_token or "")
    if not session_token:
        return None
    init_web_auth()
    now_epoch = int(time.time())
    conn = _connect()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    row = cursor.execute(
        """
        SELECT
            s.id AS session_id, s.csrf_token, s.expires_at, s.last_seen_at,
            a.id AS account_id, a.telegram_id, a.username, a.email, a.phone,
            a.full_name, a.status
        FROM web_sessions s
        JOIN web_accounts a ON a.id = s.account_id
        WHERE s.token_hash = ? AND s.revoked_at IS NULL
        """,
        (_hash_secret(session_token),),
    ).fetchone()
    if (
        row is None
        or row["status"] != "active"
        or int(row["expires_at"]) <= now_epoch
        or now_epoch - int(row["last_seen_at"]) > _session_idle_seconds()
    ):
        conn.close()
        return None
    if require_csrf and not hmac.compare_digest(row["csrf_token"], str(csrf_token or "")):
        conn.close()
        return None

    new_csrf_token = ""
    should_touch = now_epoch - int(row["last_seen_at"]) >= 5 * 60
    if rotate_csrf:
        new_csrf_token = secrets.token_urlsafe(24)
        cursor.execute(
            "UPDATE web_sessions SET csrf_token = ?, last_seen_at = ? WHERE id = ?",
            (new_csrf_token, now_epoch, row["session_id"]),
        )
    elif should_touch:
        cursor.execute(
            "UPDATE web_sessions SET last_seen_at = ? WHERE id = ?",
            (now_epoch, row["session_id"]),
        )
    conn.commit()
    conn.close()
    return {
        "session_id": row["session_id"],
        "account_id": row["account_id"],
        "telegram_id": int(row["telegram_id"]),
        "username": row["username"],
        "email": row["email"] or "",
        "phone": row["phone"] or "",
        "full_name": row["full_name"] or "",
        "expires_at": int(row["expires_at"]),
        "csrf_token": new_csrf_token or row["csrf_token"],
    }


def revoke_web_session(session_token: str) -> bool:
    if not session_token:
        return False
    init_web_auth()
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE web_sessions SET revoked_at = ? WHERE token_hash = ? AND revoked_at IS NULL",
        (int(time.time()), _hash_secret(session_token)),
    )
    changed = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return changed


def revoke_web_sessions_for_telegram_id(telegram_id: int) -> int:
    init_web_auth()
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE web_sessions
        SET revoked_at = ?
        WHERE revoked_at IS NULL
          AND account_id IN (
              SELECT id FROM web_accounts WHERE telegram_id = ?
          )
        """,
        (int(time.time()), int(telegram_id)),
    )
    changed = max(0, cursor.rowcount)
    conn.commit()
    conn.close()
    return changed


def session_token_from_cookie(cookie_header: str, *, secure: bool | None = None) -> str:
    try:
        cookie = SimpleCookie()
        cookie.load(str(cookie_header or ""))
        if secure is True:
            morsel = cookie.get(SECURE_COOKIE_NAME)
        elif secure is False:
            morsel = cookie.get(COOKIE_NAME)
        else:
            morsel = cookie.get(SECURE_COOKIE_NAME) or cookie.get(COOKIE_NAME)
        return morsel.value if morsel else ""
    except (KeyError, ValueError):
        return ""


def build_session_cookie(session_token: str, *, secure: bool, max_age: int | None = None) -> str:
    cookie = SimpleCookie()
    cookie_name = SECURE_COOKIE_NAME if secure else COOKIE_NAME
    cookie[cookie_name] = session_token
    cookie[cookie_name]["path"] = "/"
    cookie[cookie_name]["httponly"] = True
    cookie[cookie_name]["samesite"] = "Strict"
    if secure:
        cookie[cookie_name]["secure"] = True
    if max_age is not None:
        cookie[cookie_name]["max-age"] = str(max_age)
    return cookie.output(header="").strip()


def build_clear_cookie(*, secure: bool) -> str:
    return build_session_cookie("", secure=secure, max_age=0)


def build_clear_cookies() -> tuple[str, str]:
    return (
        build_session_cookie("", secure=True, max_age=0),
        build_session_cookie("", secure=False, max_age=0),
    )


def _cli() -> None:
    parser = argparse.ArgumentParser(description="Управление входом самостоятельного веб-приложения")
    subparsers = parser.add_subparsers(dest="command", required=True)
    create_parser = subparsers.add_parser("set-account", help="Создать или обновить веб-аккаунт")
    create_parser.add_argument("--username", required=True)
    create_parser.add_argument("--telegram-id", required=True, type=int)
    args = parser.parse_args()
    password = getpass.getpass("Пароль: ")
    password_repeat = getpass.getpass("Повторите пароль: ")
    if password != password_repeat:
        raise SystemExit("Пароли не совпадают.")
    account = upsert_web_account(args.username, args.telegram_id, password)
    print(f"Аккаунт {account['username']} настроен.")


if __name__ == "__main__":
    _cli()
