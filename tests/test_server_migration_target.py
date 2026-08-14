from __future__ import annotations

import unittest

from scripts.check_server_migration_target import (
    GIB,
    REQUIRED_SERVICES,
    REQUIRED_TIMERS,
    evaluate_snapshot,
)


class ServerMigrationTargetTests(unittest.TestCase):
    def _snapshot(self):
        return {
            "cpu_count": 8,
            "memory_bytes": 16 * GIB,
            "disk_total_bytes": 160 * GIB,
            "disk_free_bytes": 130 * GIB,
            "os_id": "ubuntu",
            "os_version": "24.04",
            "ntp_synchronized": "yes",
            "commands": {
                "python3": "Python 3.12.3",
                "psql": "psql (PostgreSQL) 16.14",
                "caddy": "2.6.2",
            },
            "release_commits": {"sewing": "84e6842deadbeef", "messenger": "f397523deadbeef"},
            "data_paths": {"sewing": True, "messenger": True},
            "services": {unit: {"active": "active", "enabled": "enabled"} for unit in REQUIRED_SERVICES},
            "timers": {unit: {"active": "active", "enabled": "enabled"} for unit in REQUIRED_TIMERS},
            "health": {"sewing": 200, "messenger": 200},
            "postgres_listeners": ["LISTEN 0 200 127.0.0.1:5432 0.0.0.0:*"],
            "tcp_listeners": [
                "LISTEN 0 4096 0.0.0.0:22 0.0.0.0:*",
                "LISTEN 0 4096 *:80 *:*",
                "LISTEN 0 4096 *:443 *:*",
                "LISTEN 0 200 127.0.0.1:5432 0.0.0.0:*",
            ],
            "optional": {
                "hermes_timer": {"active": "active", "enabled": "enabled"},
                "hermes_service": {"active": "inactive", "enabled": "disabled"},
                "n8n_service": {"active": "inactive", "enabled": ""},
            },
        }

    def test_running_target_passes_with_expected_commits(self):
        report = evaluate_snapshot(
            self._snapshot(),
            phase="running",
            expected_sewing_commit="84e6842",
            expected_messenger_commit="f397523",
        )
        self.assertTrue(report["ready"])
        self.assertTrue(any("n8n" in warning for warning in report["warnings"]))

    def test_capacity_and_platform_are_fail_closed(self):
        snapshot = self._snapshot()
        snapshot.update({
            "cpu_count": 2,
            "memory_bytes": 4 * GIB,
            "disk_total_bytes": 60 * GIB,
            "disk_free_bytes": 20 * GIB,
            "os_version": "22.04",
            "ntp_synchronized": "no",
        })
        report = evaluate_snapshot(snapshot, phase="bootstrap")
        self.assertFalse(report["ready"])
        self.assertGreaterEqual(len(report["errors"]), 6)

    def test_wrong_release_and_missing_service_block_running(self):
        snapshot = self._snapshot()
        snapshot["release_commits"]["sewing"] = "badc0de"
        snapshot["services"]["sewing-web.service"]["active"] = "failed"
        report = evaluate_snapshot(
            snapshot,
            phase="running",
            expected_sewing_commit="84e6842",
            expected_messenger_commit="f397523",
        )
        self.assertFalse(report["ready"])
        self.assertTrue(any("commit" in error for error in report["errors"]))
        self.assertTrue(any("sewing-web.service" in error for error in report["errors"]))

    def test_public_postgres_listener_blocks_cutover(self):
        snapshot = self._snapshot()
        snapshot["postgres_listeners"] = ["LISTEN 0 200 0.0.0.0:5432 0.0.0.0:*"]
        report = evaluate_snapshot(snapshot, phase="bootstrap")
        self.assertFalse(report["ready"])
        self.assertTrue(any("PostgreSQL" in error for error in report["errors"]))

    def test_unexpected_public_service_port_blocks_cutover(self):
        snapshot = self._snapshot()
        snapshot["tcp_listeners"].append("LISTEN 0 20 0.0.0.0:25 0.0.0.0:*")
        report = evaluate_snapshot(snapshot, phase="bootstrap")
        self.assertFalse(report["ready"])
        self.assertTrue(any("25" in error for error in report["errors"]))

    def test_failed_hermes_is_only_required_when_selected(self):
        snapshot = self._snapshot()
        snapshot["optional"]["hermes_service"]["active"] = "failed"
        optional_report = evaluate_snapshot(snapshot, phase="bootstrap")
        required_report = evaluate_snapshot(snapshot, phase="bootstrap", include_hermes=True)
        self.assertTrue(optional_report["ready"])
        self.assertFalse(required_report["ready"])


if __name__ == "__main__":
    unittest.main()
