import hashlib
import hmac
import time


AUTH_TOKEN_TTL_SECONDS = 30 * 24 * 60 * 60


def create_auth_token(telegram_id: int, bot_token: str, ttl_seconds: int = AUTH_TOKEN_TTL_SECONDS):
    expires_at = int(time.time()) + ttl_seconds
    payload = f"{telegram_id}:{expires_at}"
    signature = hmac.new(
        bot_token.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    return f"{payload}:{signature}"


def parse_auth_token(auth_token: str, bot_token: str):
    if not auth_token or not bot_token:
        return None

    parts = auth_token.split(":")

    if len(parts) != 3:
        return None

    telegram_id_text, expires_at_text, received_signature = parts

    try:
        telegram_id = int(telegram_id_text)
        expires_at = int(expires_at_text)
    except ValueError:
        return None

    if expires_at < int(time.time()):
        return None

    payload = f"{telegram_id}:{expires_at}"
    expected_signature = hmac.new(
        bot_token.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(expected_signature, received_signature):
        return None

    return {"id": telegram_id}
