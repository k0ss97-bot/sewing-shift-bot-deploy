import unittest

from webapp_server import load_runtime_settings


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


if __name__ == "__main__":
    unittest.main()
