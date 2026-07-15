import tempfile
import unittest
from pathlib import Path

from webapp_server import load_runtime_settings, start_shared_bot_process


class WebAppServerSettingsTest(unittest.TestCase):
    def test_defaults_to_loopback_and_ephemeral_secret(self):
        settings = load_runtime_settings({})
        self.assertEqual(settings.host, "127.0.0.1")
        self.assertEqual(settings.port, 3000)
        self.assertGreaterEqual(len(settings.secret), 32)
        self.assertFalse(settings.production)
        self.assertFalse(settings.debug)

    def test_production_requires_long_persistent_secret(self):
        with self.assertRaises(RuntimeError):
            load_runtime_settings({"WEBAPP_ENV": "production", "WEBAPP_SERVER_SECRET": "short"})

    def test_production_settings_are_parsed(self):
        settings = load_runtime_settings(
            {
                "WEBAPP_ENV": "production",
                "WEBAPP_SERVER_SECRET": "s" * 32,
                "MINIAPP_HOST": "127.0.0.1",
                "MINIAPP_PORT": "4567",
            }
        )
        self.assertTrue(settings.production)
        self.assertEqual(settings.port, 4567)

    def test_rejects_invalid_port_and_production_debug(self):
        with self.assertRaises(RuntimeError):
            load_runtime_settings({"MINIAPP_PORT": "70000"})
        with self.assertRaises(RuntimeError):
            load_runtime_settings(
                {
                    "WEBAPP_ENV": "production",
                    "WEBAPP_SERVER_SECRET": "s" * 32,
                    "MINIAPP_DEBUG": "1",
                }
            )

    def test_shared_bot_requires_marker_and_uses_site_database_environment(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            calls = []

            class FakeProcess:
                pid = 12345

            def fake_popen(command, **kwargs):
                calls.append((command, kwargs))
                return FakeProcess()

            environment = {
                "DB_DIR": str(root),
                "BOT_TOKEN": "test-token",
            }
            self.assertIsNone(
                start_shared_bot_process(
                    environment,
                    popen_factory=fake_popen,
                    working_directory=root,
                )
            )
            self.assertEqual(calls, [])

            (root / "bot.enabled").touch()
            process = start_shared_bot_process(
                environment,
                popen_factory=fake_popen,
                working_directory=root,
            )
            self.assertEqual(process.pid, 12345)
            command, options = calls[0]
            self.assertEqual(command[-1], str(root / "main.py"))
            self.assertEqual(options["cwd"], str(root))
            self.assertEqual(options["env"]["DB_DIR"], str(root))
            self.assertEqual(options["env"]["MINIAPP_ENABLED"], "0")
            self.assertEqual(options["env"]["LOGS_DIR"], str(root / "logs"))

    def test_shared_bot_marker_requires_token(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "bot.enabled").touch()
            with self.assertRaises(RuntimeError):
                start_shared_bot_process({"DB_DIR": str(root)})


if __name__ == "__main__":
    unittest.main()
