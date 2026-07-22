import unittest

from miniapp_assets import MINIAPP_HTML


class WebRegistrationLinkTest(unittest.TestCase):
    def test_direct_registration_link_keeps_the_auth_parameter(self):
        self.assertIn('get("auth") === "register"', MINIAPP_HTML)
        self.assertIn('function requestedWebAuthMode()', MINIAPP_HTML)
        self.assertIn('setWebAuthMode(requestedWebAuthMode(), message);', MINIAPP_HTML)
        self.assertNotIn('if (urlParams.has("auth"))', MINIAPP_HTML)

    def test_manual_auth_tab_switches_keep_the_shareable_link_current(self):
        self.assertIn('function syncWebAuthModeUrl(mode)', MINIAPP_HTML)
        self.assertIn('url.searchParams.set("auth", "register")', MINIAPP_HTML)
        self.assertIn('url.searchParams.delete("auth")', MINIAPP_HTML)


if __name__ == "__main__":
    unittest.main()
