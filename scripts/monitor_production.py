#!/usr/bin/env python3
"""Refresh production alerts and deliver critical notifications to admins."""

from __future__ import annotations

import hashlib
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from database import (
    DB_NAME,
    claim_notification_delivery,
    create_or_refresh_operational_notification,
    disable_web_push_subscription,
    finish_notification_delivery,
    get_active_admin_notification_recipients,
    get_active_admin_web_push_subscriptions,
    get_open_critical_notifications,
    init_db,
    record_web_push_delivery,
    refresh_operational_notifications,
    resolve_operational_notification,
)
from web_push import WebPushDeliveryError, send_web_push, web_push_is_ready


BACKUP_MAX_AGE_HOURS = 26


def telegram_token() -> str:
    return (
        os.getenv("NOTIFICATION_TELEGRAM_BOT_TOKEN", "").strip()
        or os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    )


def check_backup_health(now: datetime | None = None) -> bool:
    now = now or datetime.now(timezone.utc)
    backups = sorted(
        (Path(DB_NAME).parent / "backups").glob("webapp_*.db"),
        key=lambda path: path.stat().st_mtime,
    )
    if backups:
        latest_time = datetime.fromtimestamp(backups[-1].stat().st_mtime, timezone.utc)
        if now - latest_time <= timedelta(hours=BACKUP_MAX_AGE_HOURS):
            resolve_operational_notification("backup-overdue")
            return True
        detail = (
            f"Последняя резервная копия создана {latest_time.strftime('%Y-%m-%d %H:%M UTC')} "
            f"— старше {BACKUP_MAX_AGE_HOURS} часов."
        )
    else:
        detail = "В папке резервных копий нет ни одной проверенной SQLite-копии."
    create_or_refresh_operational_notification(
        "backup-overdue",
        "Критично: резервная копия не обновлялась",
        detail,
        severity="critical",
    )
    return False


def telegram_message(notification: dict) -> str:
    title = str(notification.get("title") or "Критичное уведомление")
    message = str(notification.get("message") or "Проверьте приложение.")
    return f"⚠️ {title}\n\n{message}\n\nОткройте «Требует решения» в приложении."


def send_telegram_message(token: str, chat_id: int, text: str) -> None:
    request = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=json.dumps({"chat_id": chat_id, "text": text}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=12) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (OSError, urllib.error.URLError, json.JSONDecodeError) as error:
        raise RuntimeError(f"Telegram delivery failed: {error.__class__.__name__}") from error
    if not isinstance(payload, dict) or not payload.get("ok"):
        raise RuntimeError("Telegram delivery was rejected")


def deliver_open_notifications(token: str) -> dict[str, int]:
    result = {"sent": 0, "failed": 0, "skipped": 0}
    if not token:
        return result
    recipients = get_active_admin_notification_recipients()
    for notification in get_open_critical_notifications():
        if notification.get("severity") != "critical":
            continue
        for employee_id, telegram_id, _full_name in recipients:
            if not claim_notification_delivery(int(notification["id"]), int(employee_id), "telegram"):
                result["skipped"] += 1
                continue
            try:
                send_telegram_message(token, int(telegram_id), telegram_message(notification))
            except RuntimeError as error:
                finish_notification_delivery(
                    int(notification["id"]), int(employee_id), "telegram", sent=False, error=str(error)
                )
                result["failed"] += 1
            else:
                finish_notification_delivery(
                    int(notification["id"]), int(employee_id), "telegram", sent=True
                )
                result["sent"] += 1
    return result


def web_push_channel(subscription: dict) -> str:
    endpoint = str(subscription.get("endpoint") or "")
    digest = hashlib.sha256(endpoint.encode("utf-8")).hexdigest()[:24]
    return f"webpush:{digest}"


def deliver_open_web_push_notifications() -> dict[str, int]:
    result = {"sent": 0, "failed": 0, "skipped": 0}
    if not web_push_is_ready():
        return result
    for notification in get_open_critical_notifications():
        if notification.get("severity") != "critical":
            continue
        for subscription in get_active_admin_web_push_subscriptions():
            employee_id = int(subscription["employee_id"])
            channel = web_push_channel(subscription)
            if not claim_notification_delivery(int(notification["id"]), employee_id, channel):
                result["skipped"] += 1
                continue
            try:
                send_web_push(
                    subscription,
                    title=str(notification.get("title") or "Критичное уведомление"),
                    message=str(notification.get("message") or "Проверьте приложение."),
                    notification_id=int(notification["id"]),
                )
            except WebPushDeliveryError as error:
                finish_notification_delivery(
                    int(notification["id"]), employee_id, channel, sent=False, error=str(error)
                )
                record_web_push_delivery(int(subscription["id"]), sent=False, error=str(error))
                if error.invalid_subscription:
                    disable_web_push_subscription(
                        employee_id, str(subscription["endpoint"]), str(error)
                    )
                result["failed"] += 1
            else:
                finish_notification_delivery(
                    int(notification["id"]), employee_id, channel, sent=True
                )
                record_web_push_delivery(int(subscription["id"]), sent=True)
                result["sent"] += 1
    return result


def main() -> int:
    init_db()
    operational = refresh_operational_notifications()
    backup_ok = check_backup_health()
    telegram_delivery = deliver_open_notifications(telegram_token())
    web_push_delivery = deliver_open_web_push_notifications()
    print(
        json.dumps(
            {
                "ok": True,
                "operational_alerts": len(operational),
                "backup_ok": backup_ok,
                "telegram_configured": bool(telegram_token()),
                "web_push_configured": web_push_is_ready(),
                "delivery": {"telegram": telegram_delivery, "web_push": web_push_delivery},
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"Production monitor failed: {error}", file=sys.stderr)
        raise SystemExit(1)
