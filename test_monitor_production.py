import importlib
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch


PROJECT_DIR = Path(__file__).resolve().parent


class ProductionMonitorTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.old_db_dir = os.environ.get("DB_DIR")
        self.old_cwd = os.getcwd()
        os.environ["DB_DIR"] = self.temp_dir.name
        os.chdir(self.temp_dir.name)
        sys.path.insert(0, str(PROJECT_DIR))
        for module_name in ["database", "web_push", "scripts.monitor_production"]:
            sys.modules.pop(module_name, None)
        self.database = importlib.import_module("database")
        self.database.init_db()
        self.monitor = importlib.import_module("scripts.monitor_production")

    def tearDown(self):
        if self.old_db_dir is None:
            os.environ.pop("DB_DIR", None)
        else:
            os.environ["DB_DIR"] = self.old_db_dir
        os.chdir(self.old_cwd)
        if str(PROJECT_DIR) in sys.path:
            sys.path.remove(str(PROJECT_DIR))
        for module_name in ["database", "web_push", "scripts.monitor_production"]:
            sys.modules.pop(module_name, None)
        self.temp_dir.cleanup()

    def test_critical_web_push_is_sent_once_per_subscription(self):
        self.database.create_employee(6201, "Тест Монитор", "Швея")
        admin = self.database.get_employee_by_telegram_id(6201)
        self.database.update_employee_status(admin[0], "active")
        self.assertTrue(self.database.update_employee_role(admin[0], "admin")["ok"])
        self.database.upsert_web_push_subscription(
            admin[0],
            {
                "endpoint": "https://push.example.test/monitor-6201",
                "keys": {"p256dh": "synthetic-p256dh", "auth": "synthetic-auth"},
            },
            "Synthetic Monitor Test",
        )
        self.database.create_or_refresh_operational_notification(
            "synthetic-monitor-alert",
            "Критично: тест",
            "Изолированная проверка доставки.",
            severity="critical",
        )

        with patch.object(self.monitor, "web_push_is_ready", return_value=True), patch.object(
            self.monitor, "send_web_push"
        ) as sender:
            first = self.monitor.deliver_open_web_push_notifications()
            second = self.monitor.deliver_open_web_push_notifications()

        self.assertEqual(first, {"sent": 1, "failed": 0, "skipped": 0})
        self.assertEqual(second, {"sent": 0, "failed": 0, "skipped": 1})
        sender.assert_called_once()

    def test_fresh_clean_reconciliation_resolves_alert(self):
        now = datetime(2026, 8, 7, 9, 0, tzinfo=timezone.utc)
        self.database.create_or_refresh_operational_notification(
            "production-wms-reconciliation",
            "Старая ошибка",
            "Уже устранена",
            severity="critical",
        )
        with patch.object(
            self.monitor,
            "get_latest_production_wms_reconciliation",
            return_value={
                "status": "ok",
                "issue_count": 0,
                "finished_at": "2026-08-07T08:55:00+00:00",
            },
        ):
            self.assertTrue(self.monitor.check_production_wms_reconciliation(now))
        self.assertFalse(any(
            row["event_key"] == "production-wms-reconciliation"
            for row in self.database.get_open_critical_notifications()
        ))

    def test_reconciliation_issue_creates_critical_alert(self):
        now = datetime(2026, 8, 7, 9, 0, tzinfo=timezone.utc)
        with patch.object(
            self.monitor,
            "get_latest_production_wms_reconciliation",
            return_value={
                "status": "warning",
                "issue_count": 2,
                "finished_at": "2026-08-07T08:59:00+00:00",
            },
        ):
            self.assertFalse(self.monitor.check_production_wms_reconciliation(now))
        notification = next(
            row for row in self.database.get_open_critical_notifications()
            if row["event_key"] == "production-wms-reconciliation"
        )
        self.assertEqual(notification["severity"], "critical")
        self.assertIn("2", notification["message"])

    def test_admin_can_acknowledge_open_critical_notification_once(self):
        self.database.create_employee(6202, "Администратор Уведомлений", "Администратор")
        employee = self.database.get_employee_by_telegram_id(6202)
        self.database.update_employee_status(employee[0], "active")
        notification_id = self.database.create_or_refresh_operational_notification(
            "acknowledge-test",
            "Проверка подтверждения",
            "Изолированное уведомление.",
            severity="critical",
        )
        self.assertTrue(self.database.acknowledge_critical_notification(notification_id, employee[0]))
        self.assertFalse(self.database.acknowledge_critical_notification(notification_id, employee[0]))
        self.assertFalse(any(
            row["event_key"] == "acknowledge-test"
            for row in self.database.get_open_critical_notifications()
        ))

    def test_resource_thresholds_create_and_resolve_notifications(self):
        self.assertFalse(self.monitor.check_disk_health(91.2))
        self.assertFalse(self.monitor.check_memory_health((81.0, 4.0)))
        notifications = {
            row["event_key"]: row for row in self.database.get_open_critical_notifications()
        }
        self.assertEqual(notifications["resource-disk"]["severity"], "critical")
        self.assertEqual(notifications["resource-memory"]["severity"], "warning")
        self.assertEqual(notifications["resource-swap"]["severity"], "warning")

        self.assertTrue(self.monitor.check_disk_health(79.9))
        self.assertTrue(self.monitor.check_memory_health((79.0, 0.0)))
        event_keys = {
            row["event_key"] for row in self.database.get_open_critical_notifications()
        }
        self.assertNotIn("resource-disk", event_keys)
        self.assertNotIn("resource-memory", event_keys)
        self.assertNotIn("resource-swap", event_keys)

    def test_stopped_service_and_oom_are_critical(self):
        self.assertFalse(self.monitor.check_services_health({
            "sewing-web.service": False,
            "sewing-web-monitor.timer": True,
        }))
        self.assertFalse(self.monitor.check_oom_health(True))
        notifications = {
            row["event_key"]: row for row in self.database.get_open_critical_notifications()
        }
        self.assertEqual(notifications["service-stopped"]["severity"], "critical")
        self.assertIn("sewing-web.service", notifications["service-stopped"]["message"])
        self.assertEqual(notifications["resource-oom"]["severity"], "critical")

    def test_stale_outbox_and_marketplace_dataset_are_reported(self):
        now = datetime(2026, 8, 7, 9, 0, tzinfo=timezone.utc)
        with patch.object(
            self.monitor,
            "get_pending_wms_receipt_outbox",
            return_value=[{"id": 7, "created_at": "2026-08-07T08:00:00+00:00"}],
        ):
            self.assertFalse(self.monitor.check_outbox_health(now))
        self.assertFalse(self.monitor.check_marketplace_snapshot_health({
            "phase1a": {
                "enabled": True,
                "datasets": [
                    {"dataset": "stocks", "freshness": "stale"},
                    {"dataset": "orders", "freshness": "fresh"},
                ],
            }
        }))
        notifications = {
            row["event_key"]: row for row in self.database.get_open_critical_notifications()
        }
        self.assertEqual(notifications["wms-outbox-stuck"]["severity"], "critical")
        self.assertIn("stocks", notifications["marketplace-snapshot-stale"]["message"])

    def test_postgres_health_rolls_back_successful_and_failed_checks(self):
        class Cursor:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def execute(self, _sql):
                return None

            def fetchone(self):
                return (1,)

        class Connection:
            def __init__(self, fail=False):
                self.fail = fail
                self.rollbacks = 0

            def cursor(self):
                if self.fail:
                    raise RuntimeError("synthetic outage")
                return Cursor()

            def rollback(self):
                self.rollbacks += 1

        healthy = Connection()
        self.assertTrue(self.monitor.check_postgres_health(healthy))
        self.assertEqual(healthy.rollbacks, 1)

        failed = Connection(fail=True)
        self.assertFalse(self.monitor.check_postgres_health(failed))
        self.assertEqual(failed.rollbacks, 1)
        notification = next(
            row for row in self.database.get_open_critical_notifications()
            if row["event_key"] == "postgres-unavailable"
        )
        self.assertNotIn("synthetic outage", notification["message"])


if __name__ == "__main__":
    unittest.main()
