"""Server-only Web Push delivery helpers."""

from __future__ import annotations

import base64
import json
import os
from dataclasses import dataclass


DEFAULT_SUBJECT = "mailto:notifications@shagaemfabrika.ru"


@dataclass(frozen=True)
class WebPushSettings:
    public_key: str
    private_key: str
    subject: str

    @property
    def configured(self) -> bool:
        return bool(self.public_key and self.private_key and self.subject)


class WebPushDeliveryError(RuntimeError):
    def __init__(self, message: str, *, invalid_subscription: bool = False):
        super().__init__(message)
        self.invalid_subscription = invalid_subscription


def _is_valid_public_key(value: str) -> bool:
    try:
        padded = value + "=" * (-len(value) % 4)
        decoded = base64.urlsafe_b64decode(padded.encode("ascii"))
    except (UnicodeEncodeError, ValueError):
        return False
    return len(decoded) == 65 and decoded[:1] == b"\x04"


def get_web_push_settings() -> WebPushSettings:
    public_key = os.getenv("WEB_PUSH_VAPID_PUBLIC_KEY", "").strip()
    private_key = os.getenv("WEB_PUSH_VAPID_PRIVATE_KEY", "").strip()
    subject = os.getenv("WEB_PUSH_VAPID_SUBJECT", DEFAULT_SUBJECT).strip()
    if public_key and not _is_valid_public_key(public_key):
        public_key = ""
    if not subject.startswith(("mailto:", "https://")):
        subject = ""
    return WebPushSettings(public_key, private_key, subject)


def sender_is_available() -> bool:
    try:
        import pywebpush  # noqa: F401
    except ImportError:
        return False
    return True


def web_push_is_ready() -> bool:
    return get_web_push_settings().configured and sender_is_available()


def get_public_web_push_config() -> dict[str, object]:
    settings = get_web_push_settings()
    ready = settings.configured and sender_is_available()
    return {"configured": ready, "public_key": settings.public_key if ready else ""}


def send_web_push(
    subscription: dict,
    *,
    title: str,
    message: str,
    notification_id: int,
) -> None:
    settings = get_web_push_settings()
    if not settings.configured:
        raise WebPushDeliveryError("Web Push is not configured")
    try:
        from pywebpush import WebPushException, webpush
    except ImportError as error:
        raise WebPushDeliveryError("Web Push sender is not installed") from error

    payload = json.dumps(
        {
            "title": str(title or "Критичное уведомление")[:160],
            "body": str(message or "Проверьте приложение.")[:1000],
            "url": "/app",
            "tag": f"critical-{int(notification_id)}",
        },
        ensure_ascii=False,
    )
    try:
        webpush(
            subscription_info={
                "endpoint": subscription["endpoint"],
                "keys": {
                    "p256dh": subscription["p256dh"],
                    "auth": subscription["auth"],
                },
            },
            data=payload,
            vapid_private_key=settings.private_key,
            vapid_claims={"sub": settings.subject},
            ttl=60 * 60 * 12,
        )
    except WebPushException as error:
        response = getattr(error, "response", None)
        status_code = getattr(response, "status_code", None)
        invalid = status_code in {404, 410}
        detail = f"Web Push gateway rejected delivery ({status_code or 'unknown'})"
        raise WebPushDeliveryError(detail, invalid_subscription=invalid) from error
    except (KeyError, TypeError, ValueError) as error:
        raise WebPushDeliveryError(
            "Web Push subscription is invalid", invalid_subscription=True
        ) from error
