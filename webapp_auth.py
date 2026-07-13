"""Standalone web authentication for the shared miniapp/webapp backend."""

from __future__ import annotations

import argparse
import getpass
import hashlib
import hmac
import os
import secrets
import sqlite3
import time
from http.cookies import SimpleCookie

from database import DB_NAME, local_now


COOKIE_NAME = "sewing_web_session"
SECURE_COOKIE_NAME = "__Host-sewing_web_session"
PASSWORD_ITERATIONS = 310_000
MIN_PASSWORD_LENGTH = 10
MAX_FAILED_ATTEMPTS = 5
LOCK_SECONDS = 5 * 60
DEFAULT_SESSION_TTL_SECONDS = 12 * 60 * 60
DEFAULT_SESSION_IDLE_SECONDS = 2 * 60 * 60


def _now_text() -> str:
    return local_now().isoformat(timespec="seconds")


def _session_ttl_seconds() -> int:
    try:
        configured = int(os.getenv("WEBAPP_SESSION_TTL_SECONDS", DEFAULT_SESSION_TTL_SECONDS))
    except (TypeError, ValueError):
        configured = DEFAULT_SESSION_TTL_SECONDS
    return max(15 * 60, min(configured, 30 * 24 * 60 * 60))


def _session_idle_seconds() -> int:
    try:
        configured = int(os.getenv("WEBAPP_SESSION_IDLE_SECONDS", DEFAULT_SESSION_IDLE_SECONDS))
    except (TypeError, ValueError):
        configured = DEFAULT_SESSION_IDLE_SECONDS
    return max(15 * 60, min(configured, _session_ttl_seconds()))


def _normalize_username(username: str) -> str:
    username = str(username or "").strip().casefold()
    if not 3 <= len(username) <= 64:
        return ""
    if any(not (char.isalnum() or char in "._@-") for char in username):
        return ""
    return username


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


def init_web_auth() -> None:
    conn = sqlite3.connect(DB_NAME)
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
    try:
        telegram_id = int(telegram_id)
    except (TypeError, ValueError) as error:
        raise ValueError("Некорректный идентификатор пользователя.") from error

    init_web_auth()
    salt_hex = secrets.token_hex(16)
    password_digest = _password_hash(password, salt_hex)
    now_text = _now_text()
    status = "active" if active else "disabled"
    conn = sqlite3.connect(DB_NAME)
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


def authenticate_web_credentials(username: str, password: str) -> dict | None:
    normalized_username = _normalize_username(username)
    password = str(password or "")
    init_web_auth()
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    account = cursor.execute(
        "SELECT * FROM web_accounts WHERE username = ? COLLATE NOCASE",
        (normalized_username,),
    ).fetchone()

    # Keep unknown-user attempts computationally comparable to known-user attempts.
    if account is None:
        _password_hash(password, "0" * 32)
        conn.close()
        return None

    now_epoch = int(time.time())
    if account["status"] != "active" or int(account["locked_until"] or 0) > now_epoch:
        conn.close()
        return None

    expected = _password_hash(password, account["password_salt"], account["password_iterations"])
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
    result = {"id": account["id"], "telegram_id": account["telegram_id"], "username": account["username"]}
    conn.close()
    return result


def create_web_session(account: dict, ip_address: str = "", user_agent: str = "") -> dict:
    init_web_auth()
    session_token = secrets.token_urlsafe(32)
    csrf_token = secrets.token_urlsafe(24)
    now_epoch = int(time.time())
    expires_at = now_epoch + _session_ttl_seconds()
    conn = sqlite3.connect(DB_NAME)
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
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    row = cursor.execute(
        """
        SELECT
            s.id AS session_id, s.csrf_token, s.expires_at, s.last_seen_at,
            a.id AS account_id, a.telegram_id, a.username, a.status
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
        "expires_at": int(row["expires_at"]),
        "csrf_token": new_csrf_token or row["csrf_token"],
    }


def revoke_web_session(session_token: str) -> bool:
    if not session_token:
        return False
    init_web_auth()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE web_sessions SET revoked_at = ? WHERE token_hash = ? AND revoked_at IS NULL",
        (int(time.time()), _hash_secret(session_token)),
    )
    changed = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return changed


def session_token_from_cookie(cookie_header: str) -> str:
    try:
        cookie = SimpleCookie()
        cookie.load(str(cookie_header or ""))
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
