"""Standalone web authentication for the shared miniapp/webapp backend."""

from __future__ import annotations

import argparse
import base64
import getpass
import hashlib
import hmac
import json
import os
import re
import secrets
import sqlite3
import struct
import threading
import time
from http.cookies import SimpleCookie
from urllib.parse import quote, urlencode, urlparse

from database import DB_NAME, get_db_connection, local_now


COOKIE_NAME = "sewing_web_session"
SECURE_COOKIE_NAME = "__Host-sewing_web_session"
PASSWORD_ITERATIONS = 600_000
MIN_PASSWORD_LENGTH = 10
MAX_PASSWORD_LENGTH = 128
MAX_FAILED_ATTEMPTS = 5
LOCK_SECONDS = 5 * 60
MFA_CHALLENGE_SECONDS = 5 * 60
MFA_MAX_FAILED_ATTEMPTS = 5
MFA_RECOVERY_CODE_COUNT = 10
MIN_SESSION_LIFETIME_SECONDS = 15 * 60
MAX_SESSION_LIFETIME_SECONDS = 30 * 24 * 60 * 60
DEFAULT_SESSION_TTL_SECONDS = 12 * 60 * 60
DEFAULT_SESSION_IDLE_SECONDS = 45 * 60
_WEB_AUTH_INIT_LOCK = threading.Lock()
_WEB_AUTH_INITIALIZED_DB = ""
TEAM_SSO_AUDIENCE = "shagaem-team-messenger"
TEAM_SSO_TOKEN_SECONDS = 90


class WebRegistrationError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def _base64url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def create_team_sso_url(telegram_id: int, *, now_epoch: int | None = None) -> str:
    """Create a short-lived signed login URL for the isolated team portal."""
    secret = os.getenv("TEAM_SSO_SECRET", "").encode("utf-8")
    callback_url = os.getenv(
        "TEAM_SSO_CALLBACK_URL",
        "https://team-shagaemfabrika.ru/api/sso/callback",
    ).strip()
    parsed_callback = urlparse(callback_url)
    if len(secret) < 32:
        raise RuntimeError("TEAM_SSO_SECRET must contain at least 32 bytes")
    if parsed_callback.scheme != "https" or not parsed_callback.netloc or parsed_callback.query or parsed_callback.fragment:
        raise RuntimeError("TEAM_SSO_CALLBACK_URL must be an HTTPS URL without query or fragment")
    now_epoch = int(time.time()) if now_epoch is None else int(now_epoch)
    payload = {
        "aud": TEAM_SSO_AUDIENCE,
        "exp": now_epoch + TEAM_SSO_TOKEN_SECONDS,
        "iat": now_epoch,
        "nonce": secrets.token_urlsafe(18),
        "sub": int(telegram_id),
        "v": 1,
    }
    encoded_payload = _base64url_encode(
        json.dumps(payload, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode("utf-8")
    )
    signature = _base64url_encode(hmac.new(secret, encoded_payload.encode("ascii"), hashlib.sha256).digest())
    separator = "&" if parsed_callback.query else "?"
    return f"{callback_url}{separator}{urlencode({'token': f'{encoded_payload}.{signature}'})}"


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


def _mfa_key() -> bytes:
    server_secret = str(os.getenv("WEBAPP_SERVER_SECRET") or "").encode("utf-8")
    if not server_secret:
        # Production startup requires WEBAPP_SERVER_SECRET. This deterministic
        # fallback is limited to isolated tests and local development.
        server_secret = os.path.realpath(DB_NAME).encode("utf-8")
    return hmac.new(server_secret, b"sewing-web-mfa-v1", hashlib.sha256).digest()


def _seal_mfa_secret(secret: str) -> str:
    plaintext = secret.encode("ascii")
    nonce = secrets.token_bytes(16)
    key = _mfa_key()
    stream = b""
    counter = 0
    while len(stream) < len(plaintext):
        stream += hmac.new(
            key, b"enc" + nonce + struct.pack(">I", counter), hashlib.sha256
        ).digest()
        counter += 1
    ciphertext = bytes(left ^ right for left, right in zip(plaintext, stream))
    tag = hmac.new(key, b"tag" + nonce + ciphertext, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(nonce + ciphertext + tag).decode("ascii")


def _open_mfa_secret(ciphertext: str) -> str:
    try:
        payload = base64.urlsafe_b64decode(str(ciphertext or "").encode("ascii"))
    except (ValueError, UnicodeError) as error:
        raise ValueError("Invalid MFA secret ciphertext.") from error
    if len(payload) < 49:
        raise ValueError("Invalid MFA secret ciphertext.")
    nonce, encrypted, supplied_tag = payload[:16], payload[16:-32], payload[-32:]
    key = _mfa_key()
    expected_tag = hmac.new(key, b"tag" + nonce + encrypted, hashlib.sha256).digest()
    if not hmac.compare_digest(supplied_tag, expected_tag):
        raise ValueError("Invalid MFA secret ciphertext.")
    stream = b""
    counter = 0
    while len(stream) < len(encrypted):
        stream += hmac.new(
            key, b"enc" + nonce + struct.pack(">I", counter), hashlib.sha256
        ).digest()
        counter += 1
    return bytes(left ^ right for left, right in zip(encrypted, stream)).decode("ascii")


def _new_totp_secret() -> str:
    return base64.b32encode(secrets.token_bytes(20)).decode("ascii").rstrip("=")


def _totp_code(secret: str, at_time: int | float | None = None) -> str:
    counter = int((time.time() if at_time is None else at_time) // 30)
    padded = secret + "=" * ((8 - len(secret) % 8) % 8)
    key = base64.b32decode(padded, casefold=True)
    digest = hmac.new(key, struct.pack(">Q", counter), hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    binary = struct.unpack(">I", digest[offset:offset + 4])[0] & 0x7FFFFFFF
    return f"{binary % 1_000_000:06d}"


def _matching_totp_counter(secret: str, code: str, now_epoch: int) -> int | None:
    normalized = re.sub(r"\D", "", str(code or ""))
    if len(normalized) != 6:
        return None
    current = now_epoch // 30
    for counter in (current - 1, current, current + 1):
        if hmac.compare_digest(_totp_code(secret, counter * 30), normalized):
            return counter
    return None


def _recovery_hash(code: str) -> str:
    normalized = re.sub(r"[^a-z0-9]", "", str(code or "").casefold())
    return hmac.new(
        _mfa_key(), b"recovery:" + normalized.encode("ascii"), hashlib.sha256
    ).hexdigest()


def _new_recovery_codes() -> list[str]:
    return [
        f"{secrets.token_hex(2)}-{secrets.token_hex(2)}"
        for _ in range(MFA_RECOVERY_CODE_COUNT)
    ]


def init_web_auth() -> None:
    """Initialize the auth schema once per process and database file.

    This function is called from every public auth helper.  Re-running DDL and
    session cleanup for every HTTP request turns otherwise read-only session
    checks into competing writers and can exhaust SQLite's busy timeout.
    """
    global _WEB_AUTH_INITIALIZED_DB

    database_identity = os.path.realpath(DB_NAME)
    if _WEB_AUTH_INITIALIZED_DB == database_identity:
        return

    with _WEB_AUTH_INIT_LOCK:
        if _WEB_AUTH_INITIALIZED_DB == database_identity:
            return

        conn = get_db_connection()
        try:
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
                "mfa_secret_ciphertext": "TEXT",
                "mfa_enabled_at": "TEXT",
                "mfa_recovery_hashes": "TEXT NOT NULL DEFAULT '[]'",
                "mfa_last_counter": "INTEGER NOT NULL DEFAULT -1",
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
            cursor.execute("PRAGMA table_info(web_sessions)")
            session_columns = {column[1] for column in cursor.fetchall()}
            if "mfa_verified" not in session_columns:
                cursor.execute(
                    "ALTER TABLE web_sessions ADD COLUMN mfa_verified INTEGER NOT NULL DEFAULT 0"
                )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS web_mfa_challenges (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id INTEGER NOT NULL,
                    token_hash TEXT NOT NULL UNIQUE,
                    purpose TEXT NOT NULL CHECK (purpose IN ('enroll', 'login')),
                    secret_ciphertext TEXT,
                    created_at INTEGER NOT NULL,
                    expires_at INTEGER NOT NULL,
                    failed_attempts INTEGER NOT NULL DEFAULT 0,
                    consumed_at INTEGER,
                    FOREIGN KEY (account_id) REFERENCES web_accounts(id) ON DELETE CASCADE
                )
                """
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_web_mfa_challenges_expiry ON web_mfa_challenges (expires_at, consumed_at)"
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS web_rate_limits (
                    scope TEXT NOT NULL,
                    key_hash TEXT NOT NULL,
                    window_started INTEGER NOT NULL,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    updated_at INTEGER NOT NULL,
                    PRIMARY KEY (scope, key_hash)
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS web_security_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    outcome TEXT NOT NULL,
                    account_id INTEGER,
                    telegram_id INTEGER,
                    ip_hash TEXT NOT NULL DEFAULT '',
                    details_json TEXT NOT NULL DEFAULT '{}',
                    created_at INTEGER NOT NULL
                )
                """
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_web_security_events_created ON web_security_events (created_at DESC)"
            )
            cursor.execute(
                "DELETE FROM web_sessions WHERE expires_at < ? OR revoked_at IS NOT NULL",
                (int(time.time()) - 24 * 60 * 60,),
            )
            cursor.execute(
                "DELETE FROM web_mfa_challenges WHERE expires_at < ? OR consumed_at IS NOT NULL",
                (int(time.time()) - 24 * 60 * 60,),
            )
            cursor.execute(
                "DELETE FROM web_rate_limits WHERE updated_at < ?",
                (int(time.time()) - 24 * 60 * 60,),
            )
            cursor.execute(
                "DELETE FROM web_security_events WHERE created_at < ?",
                (int(time.time()) - 180 * 24 * 60 * 60,),
            )
            conn.commit()
        finally:
            conn.close()

        _WEB_AUTH_INITIALIZED_DB = database_identity


def rate_limit_check(
    scope: str,
    client_key: str,
    *,
    limit: int,
    window_seconds: int,
    consume: bool = False,
) -> bool:
    """Atomically check a restart-safe rate limit; return True when blocked."""
    init_web_auth()
    scope = re.sub(r"[^a-z0-9_.-]", "", str(scope or "").casefold())[:64]
    key_hash = _hash_secret(f"{scope}:{client_key}")
    limit = max(1, int(limit))
    window_seconds = max(1, int(window_seconds))
    now_epoch = int(time.time())
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("BEGIN IMMEDIATE")
        row = cursor.execute(
            "SELECT window_started, attempts FROM web_rate_limits WHERE scope = ? AND key_hash = ?",
            (scope, key_hash),
        ).fetchone()
        window_started = int(row[0]) if row else now_epoch
        attempts = int(row[1]) if row else 0
        if now_epoch - window_started >= window_seconds:
            window_started = now_epoch
            attempts = 0
        blocked = attempts >= limit
        if consume and not blocked:
            attempts += 1
        cursor.execute(
            """INSERT INTO web_rate_limits (scope, key_hash, window_started, attempts, updated_at)
               VALUES (?, ?, ?, ?, ?)
               ON CONFLICT(scope, key_hash) DO UPDATE SET
                   window_started = excluded.window_started,
                   attempts = excluded.attempts,
                   updated_at = excluded.updated_at""",
            (scope, key_hash, window_started, attempts, now_epoch),
        )
        conn.commit()
        return blocked
    except sqlite3.Error:
        conn.rollback()
        raise
    finally:
        conn.close()


def clear_rate_limit(scope: str, client_key: str) -> None:
    init_web_auth()
    scope = re.sub(r"[^a-z0-9_.-]", "", str(scope or "").casefold())[:64]
    key_hash = _hash_secret(f"{scope}:{client_key}")
    conn = get_db_connection()
    conn.execute("DELETE FROM web_rate_limits WHERE scope = ? AND key_hash = ?", (scope, key_hash))
    conn.commit()
    conn.close()


def record_security_event(
    event_type: str,
    outcome: str,
    *,
    account_id: int | None = None,
    telegram_id: int | None = None,
    ip_address: str = "",
    details: dict | None = None,
) -> None:
    init_web_auth()
    event_type = re.sub(r"[^a-z0-9_.-]", "", str(event_type or "unknown").casefold())[:64] or "unknown"
    outcome = re.sub(r"[^a-z0-9_.-]", "", str(outcome or "unknown").casefold())[:32] or "unknown"
    safe_details = {}
    for key, value in (details or {}).items():
        safe_key = re.sub(r"[^a-z0-9_.-]", "", str(key).casefold())[:40]
        if safe_key:
            safe_details[safe_key] = str(value or "")[:200]
    conn = get_db_connection()
    conn.execute(
        """INSERT INTO web_security_events
               (event_type, outcome, account_id, telegram_id, ip_hash, details_json, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            event_type,
            outcome,
            int(account_id) if account_id is not None else None,
            int(telegram_id) if telegram_id is not None else None,
            _client_fingerprint(ip_address),
            json.dumps(safe_details, ensure_ascii=False, sort_keys=True),
            int(time.time()),
        ),
    )
    conn.commit()
    conn.close()


def recent_security_events(limit: int = 100) -> list[dict]:
    init_web_auth()
    limit = max(1, min(int(limit or 100), 500))
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM web_security_events ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [
        {
            "id": int(row["id"]),
            "event_type": row["event_type"],
            "outcome": row["outcome"],
            "account_id": row["account_id"],
            "telegram_id": row["telegram_id"],
            "ip_hash": row["ip_hash"],
            "details": json.loads(row["details_json"] or "{}"),
            "created_at": int(row["created_at"]),
        }
        for row in rows
    ]


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
    conn = get_db_connection()
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
    conn = get_db_connection()
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
    conn = get_db_connection()
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
    conn = get_db_connection()
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

    now_text = _now_text()
    if int(account["password_iterations"] or 0) < PASSWORD_ITERATIONS:
        # Upgrade legacy PBKDF2 records opportunistically after the password
        # has already been verified. No plaintext password is stored.
        upgraded_salt = secrets.token_hex(16)
        upgraded_hash = _password_hash(password_to_check, upgraded_salt)
        cursor.execute(
            """
            UPDATE web_accounts
            SET password_salt = ?, password_hash = ?, password_iterations = ?,
                failed_attempts = 0, locked_until = NULL, last_login_at = ?, updated_at = ?
            WHERE id = ?
            """,
            (upgraded_salt, upgraded_hash, PASSWORD_ITERATIONS, now_text, now_text, account["id"]),
        )
    else:
        cursor.execute(
            """
            UPDATE web_accounts
            SET failed_attempts = 0, locked_until = NULL, last_login_at = ?, updated_at = ?
            WHERE id = ?
            """,
            (now_text, now_text, account["id"]),
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


def begin_admin_mfa(account: dict) -> dict:
    """Create a short-lived MFA challenge after password verification."""
    init_web_auth()
    now_epoch = int(time.time())
    challenge_token = secrets.token_urlsafe(32)
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute("BEGIN IMMEDIATE")
        row = cursor.execute(
            "SELECT id, username, mfa_secret_ciphertext, mfa_enabled_at FROM web_accounts WHERE id = ? AND status = 'active'",
            (int(account["id"]),),
        ).fetchone()
        if row is None:
            conn.rollback()
            raise ValueError("Account is unavailable.")
        enrollment = not bool(row["mfa_enabled_at"] and row["mfa_secret_ciphertext"])
        secret = _new_totp_secret() if enrollment else ""
        cursor.execute(
            "UPDATE web_mfa_challenges SET consumed_at = ? WHERE account_id = ? AND consumed_at IS NULL",
            (now_epoch, int(row["id"])),
        )
        cursor.execute(
            """INSERT INTO web_mfa_challenges
                   (account_id, token_hash, purpose, secret_ciphertext, created_at, expires_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                int(row["id"]),
                _hash_secret(challenge_token),
                "enroll" if enrollment else "login",
                _seal_mfa_secret(secret) if enrollment else None,
                now_epoch,
                now_epoch + MFA_CHALLENGE_SECONDS,
            ),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
    result = {
        "challenge_token": challenge_token,
        "mfa_enrollment_required": enrollment,
        "expires_at": now_epoch + MFA_CHALLENGE_SECONDS,
    }
    if enrollment:
        label = quote(f"Шагаем вместе:{row['username']}")
        result.update({
            "secret": secret,
            "otpauth_uri": (
                f"otpauth://totp/{label}?secret={secret}"
                f"&issuer={quote('Шагаем вместе')}&digits=6&period=30"
            ),
        })
    return result


def verify_admin_mfa_challenge(challenge_token: str, code: str) -> dict:
    init_web_auth()
    now_epoch = int(time.time())
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute("BEGIN IMMEDIATE")
        row = cursor.execute(
            """SELECT c.*, a.telegram_id, a.username, a.email, a.phone, a.full_name,
                      a.mfa_secret_ciphertext, a.mfa_recovery_hashes, a.mfa_last_counter
                 FROM web_mfa_challenges c
                 JOIN web_accounts a ON a.id = c.account_id
                WHERE c.token_hash = ? AND c.consumed_at IS NULL AND a.status = 'active'""",
            (_hash_secret(str(challenge_token or "")),),
        ).fetchone()
        if row is None or int(row["expires_at"]) <= now_epoch:
            conn.rollback()
            return {
                "ok": False,
                "code": "mfa_challenge_expired",
                "message": "Проверка MFA устарела. Войдите заново.",
            }
        if int(row["failed_attempts"] or 0) >= MFA_MAX_FAILED_ATTEMPTS:
            conn.rollback()
            return {
                "ok": False,
                "code": "mfa_locked",
                "message": "Слишком много попыток. Войдите заново.",
            }

        secret_ciphertext = (
            row["secret_ciphertext"]
            if row["purpose"] == "enroll"
            else row["mfa_secret_ciphertext"]
        )
        secret = _open_mfa_secret(secret_ciphertext)
        matched_counter = _matching_totp_counter(secret, code, now_epoch)
        recovery_hashes = list(json.loads(row["mfa_recovery_hashes"] or "[]"))
        supplied_recovery_hash = _recovery_hash(code)
        recovery_match = (
            row["purpose"] == "login" and supplied_recovery_hash in recovery_hashes
        )
        replayed = (
            matched_counter is not None
            and matched_counter <= int(row["mfa_last_counter"] if row["mfa_last_counter"] is not None else -1)
        )
        if (matched_counter is None and not recovery_match) or replayed:
            failed_attempts = int(row["failed_attempts"] or 0) + 1
            cursor.execute(
                "UPDATE web_mfa_challenges SET failed_attempts = ?, consumed_at = CASE WHEN ? >= ? THEN ? ELSE consumed_at END WHERE id = ?",
                (
                    failed_attempts,
                    failed_attempts,
                    MFA_MAX_FAILED_ATTEMPTS,
                    now_epoch,
                    int(row["id"]),
                ),
            )
            conn.commit()
            return {
                "ok": False,
                "code": "invalid_mfa_code",
                "message": "Неверный или уже использованный код MFA.",
            }

        recovery_codes: list[str] = []
        if row["purpose"] == "enroll":
            recovery_codes = _new_recovery_codes()
            recovery_hashes = [_recovery_hash(value) for value in recovery_codes]
            cursor.execute(
                """UPDATE web_accounts
                      SET mfa_secret_ciphertext = ?, mfa_enabled_at = ?,
                          mfa_recovery_hashes = ?, mfa_last_counter = ?, updated_at = ?
                    WHERE id = ?""",
                (
                    row["secret_ciphertext"],
                    _now_text(),
                    json.dumps(recovery_hashes),
                    int(matched_counter),
                    _now_text(),
                    int(row["account_id"]),
                ),
            )
            cursor.execute(
                "UPDATE web_sessions SET revoked_at = ? WHERE account_id = ? AND revoked_at IS NULL",
                (now_epoch, int(row["account_id"])),
            )
        elif recovery_match:
            recovery_hashes.remove(supplied_recovery_hash)
            cursor.execute(
                "UPDATE web_accounts SET mfa_recovery_hashes = ?, updated_at = ? WHERE id = ?",
                (json.dumps(recovery_hashes), _now_text(), int(row["account_id"])),
            )
        else:
            cursor.execute(
                "UPDATE web_accounts SET mfa_last_counter = ?, updated_at = ? WHERE id = ?",
                (int(matched_counter), _now_text(), int(row["account_id"])),
            )
        cursor.execute(
            "UPDATE web_mfa_challenges SET consumed_at = ? WHERE id = ?",
            (now_epoch, int(row["id"])),
        )
        conn.commit()
        return {
            "ok": True,
            "account": {
                "id": int(row["account_id"]),
                "telegram_id": int(row["telegram_id"]),
                "username": row["username"],
                "email": row["email"] or "",
                "phone": row["phone"] or "",
                "full_name": row["full_name"] or "",
            },
            "recovery_codes": recovery_codes,
            "remaining_recovery_codes": len(recovery_hashes),
        }
    except (sqlite3.Error, ValueError, json.JSONDecodeError):
        conn.rollback()
        raise
    finally:
        conn.close()


def change_web_password(account_id: int, current_password: str, new_password: str) -> dict:
    current_password = str(current_password or "")
    try:
        new_password = _validated_password(new_password)
    except WebRegistrationError as error:
        return {"ok": False, "code": error.code, "message": str(error)}

    init_web_auth()
    conn = get_db_connection()
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


def create_web_session(
    account: dict,
    ip_address: str = "",
    user_agent: str = "",
    *,
    mfa_verified: bool = False,
) -> dict:
    init_web_auth()
    session_token = secrets.token_urlsafe(32)
    csrf_token = secrets.token_urlsafe(24)
    now_epoch = int(time.time())
    expires_at = now_epoch + _session_ttl_seconds()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO web_sessions (
            account_id, token_hash, csrf_token, created_at, expires_at,
            last_seen_at, ip_hash, user_agent_hash, mfa_verified
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            1 if mfa_verified else 0,
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
    conn = get_db_connection()
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
    conn = get_db_connection()
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
    conn = get_db_connection()
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


def reset_admin_mfa(username: str) -> bool:
    """Emergency reset used only from the server CLI after identity checks."""
    normalized_username = _normalize_username(username)
    if not normalized_username:
        return False
    init_web_auth()
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("BEGIN IMMEDIATE")
        row = cursor.execute(
            "SELECT id FROM web_accounts WHERE username = ? COLLATE NOCASE",
            (normalized_username,),
        ).fetchone()
        if row is None:
            conn.rollback()
            return False
        account_id = int(row[0])
        cursor.execute(
            """UPDATE web_accounts
                  SET mfa_secret_ciphertext = NULL, mfa_enabled_at = NULL,
                      mfa_recovery_hashes = '[]', mfa_last_counter = -1,
                      updated_at = ?
                WHERE id = ?""",
            (_now_text(), account_id),
        )
        now_epoch = int(time.time())
        cursor.execute(
            "UPDATE web_sessions SET revoked_at = ? WHERE account_id = ? AND revoked_at IS NULL",
            (now_epoch, account_id),
        )
        cursor.execute(
            "UPDATE web_mfa_challenges SET consumed_at = ? WHERE account_id = ? AND consumed_at IS NULL",
            (now_epoch, account_id),
        )
        conn.commit()
        return True
    except sqlite3.Error:
        conn.rollback()
        raise
    finally:
        conn.close()


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
    reset_parser = subparsers.add_parser(
        "reset-mfa", help="Сбросить MFA и все сессии после проверки личности"
    )
    reset_parser.add_argument("--username", required=True)
    reset_parser.add_argument("--confirm", required=True, choices=["RESET-MFA"])
    args = parser.parse_args()
    if args.command == "reset-mfa":
        if not reset_admin_mfa(args.username):
            raise SystemExit("Аккаунт не найден.")
        print(f"MFA аккаунта {args.username} сброшена; все сессии отозваны.")
        return
    password = getpass.getpass("Пароль: ")
    password_repeat = getpass.getpass("Повторите пароль: ")
    if password != password_repeat:
        raise SystemExit("Пароли не совпадают.")
    account = upsert_web_account(args.username, args.telegram_id, password)
    print(f"Аккаунт {account['username']} настроен.")


if __name__ == "__main__":
    _cli()
