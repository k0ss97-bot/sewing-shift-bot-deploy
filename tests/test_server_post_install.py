from __future__ import annotations

from pathlib import Path
import re
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "deploy" / "post-install-new-server.sh"


class ServerPostInstallTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = SCRIPT.read_text(encoding="utf-8")

    def test_script_is_fail_fast_and_contains_no_secret_assignments(self):
        self.assertIn("set -eu", self.text)
        self.assertNotRegex(self.text, re.compile(r"(?i)(token|password|secret|api[_-]?key)=[^\n]+"))
        self.assertNotIn("/var/lib/sewing-web/bot.db", self.text)
        self.assertNotIn("pg_restore", self.text)

    def test_script_installs_required_runtime_and_uses_separate_accounts(self):
        self.assertIn("DPkg::Lock::Timeout=300", self.text)
        for package in ("caddy", "postgresql-16", "python3-venv", "rsync", "sqlite3", "ufw"):
            self.assertIn(package, self.text)
        for account in ("deploy", "team-messenger", "sewing-monitor"):
            self.assertIn(f"ensure_system_user {account} ", self.text)

    def test_postgres_and_firewall_are_not_public(self):
        self.assertIn("listen_addresses = '127.0.0.1,::1'", self.text)
        self.assertIn("ufw default deny incoming", self.text)
        self.assertIn('ufw allow "$SSH_PORT/tcp"', self.text)
        self.assertIn("ufw allow 80/tcp", self.text)
        self.assertIn("ufw allow 443/tcp", self.text)
        self.assertNotRegex(self.text, re.compile(r"ufw allow (?:5432|3000|3100)"))

    def test_password_login_is_disabled_after_provider_key_install(self):
        self.assertIn("PubkeyAuthentication yes", self.text)
        self.assertIn("PasswordAuthentication no", self.text)
        self.assertIn("PermitRootLogin prohibit-password", self.text)
        self.assertIn("sshd -t", self.text)

    def test_app_services_are_not_started_before_restore(self):
        self.assertNotIn("systemctl start sewing-web", self.text)
        self.assertNotIn("systemctl start team-messenger", self.text)
        self.assertIn("systemctl disable --now caddy", self.text)


if __name__ == "__main__":
    unittest.main()
