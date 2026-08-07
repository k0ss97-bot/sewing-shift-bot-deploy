#!/usr/bin/env python3
"""Refresh production alerts and deliver critical notifications to admins."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
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
    get_pending_wms_receipt_outbox,
    init_db,
    record_web_push_delivery,
    refresh_operational_notifications,
    resolve_operational_notification,
)
from web_push import WebPushDeliveryError, send_web_push, web_push_is_ready
from production_wms_reconciliation import get_latest_production_wms_reconciliation
from marketplace_phase1a import phase1a_data_quality
from wms.connection import get_pg_connection


BACKUP_MAX_AGE_HOURS = 26
RECONCILIATION_MAX_AGE_MINUTES = 30
OUTBOX_MAX_AGE_MINUTES = 30
DISK_WARNING_PERCENT = 80.0
DISK_CRITICAL_PERCENT = 90.0
MEMORY_WARNING_PERCENT = 80.0
SWAP_WARNING_PERCENT = 1.0


def _notification(
    event_key: str,
    title: str,
    message: str,
    *,
    severity: str = "warning",
) -> None:
    create_or_refresh_operational_notification(
        event_key,
        title,
        message,
        severity=severity,
    )


def disk_usage_percent(path: Path = Path("/")) -> float:
    stats = os.statvfs(path)
    total = int(stats.f_blocks) * int(stats.f_frsize)
    available = int(stats.f_bavail) * int(stats.f_frsize)
    return 0.0 if total <= 0 else (total - available) * 100.0 / total


def check_disk_health(usage_percent: float | None = None) -> bool:
    usage = disk_usage_percent() if usage_percent is None else float(usage_percent)
    if usage < DISK_WARNING_PERCENT:
        resolve_operational_notification("resource-disk")
        return True
    critical = usage >= DISK_CRITICAL_PERCENT
    _notification(
        "resource-disk",
        ("Критично: заканчивается место на диске" if critical else "Внимание: диск заполнен"),
        f"Занято {usage:.1f}% системного диска; пороги {DISK_WARNING_PERCENT:.0f}%/{DISK_CRITICAL_PERCENT:.0f}%.",
        severity="critical" if critical else "warning",
    )
    return False


def read_memory_metrics(path: Path = Path("/proc/meminfo")) -> tuple[float, float]:
    values: dict[str, int] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        key, _separator, raw = line.partition(":")
        try:
            values[key] = int(raw.strip().split()[0])
        except (IndexError, ValueError):
            continue
    total = values.get("MemTotal", 0)
    available = values.get("MemAvailable", 0)
    swap_total = values.get("SwapTotal", 0)
    swap_free = values.get("SwapFree", 0)
    memory = 0.0 if total <= 0 else (total - available) * 100.0 / total
    swap = 0.0 if swap_total <= 0 else (swap_total - swap_free) * 100.0 / swap_total
    return memory, swap


def check_memory_health(metrics: tuple[float, float] | None = None) -> bool:
    memory, swap = metrics if metrics is not None else read_memory_metrics()
    memory_ok = float(memory) < MEMORY_WARNING_PERCENT
    swap_ok = float(swap) < SWAP_WARNING_PERCENT
    if memory_ok:
        resolve_operational_notification("resource-memory")
    else:
        _notification(
            "resource-memory",
            "Внимание: высокая загрузка RAM",
            f"Занято {float(memory):.1f}% RAM; порог {MEMORY_WARNING_PERCENT:.0f}%.",
        )
    if swap_ok:
        resolve_operational_notification("resource-swap")
    else:
        _notification(
            "resource-swap",
            "Внимание: активно используется swap",
            f"Занято {float(swap):.1f}% swap; проверьте устойчивость на следующем цикле.",
        )
    return memory_ok and swap_ok


def monitored_systemd_units() -> list[str]:
    raw = os.getenv(
        "MONITORED_SYSTEMD_UNITS",
        ",".join((
            "sewing-web.service",
            "sewing-web-backup.timer",
            "sewing-wms-backup.timer",
            "sewing-web-monitor.timer",
            "sewing-production-wms-reconcile.timer",
        )),
    )
    return [item.strip() for item in raw.split(",") if item.strip()]


def systemd_unit_is_active(unit: str) -> bool:
    result = subprocess.run(
        ["systemctl", "is-active", "--quiet", unit],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=10,
    )
    return result.returncode == 0


def check_services_health(states: dict[str, bool] | None = None) -> bool:
    states = states or {unit: systemd_unit_is_active(unit) for unit in monitored_systemd_units()}
    stopped = sorted(unit for unit, active in states.items() if not active)
    if not stopped:
        resolve_operational_notification("service-stopped")
        return True
    _notification(
        "service-stopped",
        "Критично: остановлен сервис",
        "Неактивны: " + ", ".join(stopped),
        severity="critical",
    )
    return False


def recent_oom_detected() -> bool:
    try:
        result = subprocess.run(
            [
                "journalctl", "-k", "--since", "-15 minutes", "--no-pager",
                "--grep", "Out of memory|Killed process",
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return result.returncode == 0 and bool(result.stdout.strip())


def check_oom_health(detected: bool | None = None) -> bool:
    detected = recent_oom_detected() if detected is None else bool(detected)
    if not detected:
        resolve_operational_notification("resource-oom")
        return True
    _notification(
        "resource-oom",
        "Критично: обнаружен OOM",
        "В журнале ядра за последние 15 минут есть событие Out Of Memory.",
        severity="critical",
    )
    return False


def check_postgres_health(connection=None) -> bool:
    conn = connection
    try:
        conn = conn or get_pg_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        conn.rollback()
    except Exception as error:
        if conn is not None:
            try:
                conn.rollback()
            except Exception:
                pass
        _notification(
            "postgres-unavailable",
            "Критично: PostgreSQL недоступен",
            f"Контрольный read-only запрос завершился ошибкой {type(error).__name__}.",
            severity="critical",
        )
        return False
    resolve_operational_notification("postgres-unavailable")
    return True


def check_outbox_health(now: datetime | None = None) -> bool:
    now = now or datetime.now(timezone.utc)
    stuck = []
    for row in get_pending_wms_receipt_outbox(limit=200):
        try:
            created = datetime.fromisoformat(str(row.get("created_at") or "").replace("Z", "+00:00"))
            if created.tzinfo is None:
                created = created.replace(tzinfo=timezone.utc)
            age = now - created.astimezone(timezone.utc)
        except ValueError:
            age = timedelta.max
        if age >= timedelta(minutes=OUTBOX_MAX_AGE_MINUTES):
            stuck.append(row)
    if not stuck:
        resolve_operational_notification("wms-outbox-stuck")
        return True
    _notification(
        "wms-outbox-stuck",
        "Критично: зависла очередь WMS",
        f"Событий старше {OUTBOX_MAX_AGE_MINUTES} минут: {len(stuck)}.",
        severity="critical",
    )
    return False


def check_marketplace_snapshot_health(quality: dict | None = None) -> bool:
    quality = quality if quality is not None else phase1a_data_quality()
    phase = quality.get("phase1a") or {}
    if not phase.get("enabled"):
        resolve_operational_notification("marketplace-snapshot-stale")
        return True
    datasets = phase.get("datasets") or []
    stale = [
        str(row.get("dataset") or "unknown")
        for row in datasets
        if row.get("freshness") != "fresh"
    ]
    if not datasets:
        stale.append(str(phase.get("state") or "no_data"))
    if not stale:
        resolve_operational_notification("marketplace-snapshot-stale")
        return True
    _notification(
        "marketplace-snapshot-stale",
        "Внимание: marketplace-снимок устарел",
        "Не прошли SLA: " + ", ".join(sorted(set(stale))),
        severity="warning",
    )
    return False


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


def check_production_wms_reconciliation(now: datetime | None = None) -> bool:
    now = now or datetime.now(timezone.utc)
    report = get_latest_production_wms_reconciliation()
    if report:
        try:
            finished_at = datetime.fromisoformat(str(report.get("finished_at") or "").replace("Z", "+00:00"))
            if finished_at.tzinfo is None:
                finished_at = finished_at.replace(tzinfo=timezone.utc)
            age = now - finished_at.astimezone(timezone.utc)
        except ValueError:
            age = timedelta.max
        if (
            report.get("status") == "ok"
            and age <= timedelta(minutes=RECONCILIATION_MAX_AGE_MINUTES)
        ):
            resolve_operational_notification("production-wms-reconciliation")
            return True
        if report.get("status") == "unavailable":
            detail = "Сверка производства и WMS не может подключиться к PostgreSQL."
        elif int(report.get("issue_count") or 0) > 0:
            detail = f"Сверка производства и WMS обнаружила {int(report.get('issue_count') or 0)} расхождений."
        else:
            detail = f"Сверка производства и WMS старше {RECONCILIATION_MAX_AGE_MINUTES} минут."
    else:
        detail = "Сверка подтверждённых упаковок, outbox и WMS ещё не запускалась."
    create_or_refresh_operational_notification(
        "production-wms-reconciliation",
        "Критично: нарушена сверка производства и WMS",
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
    reconciliation_ok = check_production_wms_reconciliation()
    checks = {
        "disk_ok": check_disk_health(),
        "memory_ok": check_memory_health(),
        "oom_ok": check_oom_health(),
        "services_ok": check_services_health(),
        "postgres_ok": check_postgres_health(),
        "outbox_ok": check_outbox_health(),
        "marketplace_snapshots_ok": check_marketplace_snapshot_health(),
    }
    telegram_delivery = deliver_open_notifications(telegram_token())
    web_push_delivery = deliver_open_web_push_notifications()
    print(
        json.dumps(
            {
                "ok": True,
                "operational_alerts": len(operational),
                "backup_ok": backup_ok,
                "production_wms_reconciliation_ok": reconciliation_ok,
                **checks,
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
