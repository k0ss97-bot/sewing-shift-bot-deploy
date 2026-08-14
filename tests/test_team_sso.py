import base64
import json
import os
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

from webapp_auth import TEAM_SSO_AUDIENCE, TEAM_SSO_TOKEN_SECONDS, create_team_sso_url


class TeamSsoTests(unittest.TestCase):
    def test_signed_url_contains_short_lived_employee_ticket(self):
        with patch.dict(os.environ, {
            "TEAM_SSO_SECRET": "s" * 48,
            "TEAM_SSO_CALLBACK_URL": "https://team.example.test/api/sso/callback",
        }, clear=False):
            url = create_team_sso_url(12345, now_epoch=1_900_000_000)

        parsed = urlparse(url)
        token = parse_qs(parsed.query)["token"][0]
        payload_part, signature_part = token.split(".", 1)
        payload = json.loads(base64.urlsafe_b64decode(payload_part + "=" * (-len(payload_part) % 4)))
        self.assertEqual("https", parsed.scheme)
        self.assertEqual("team.example.test", parsed.netloc)
        self.assertEqual(12345, payload["sub"])
        self.assertEqual(TEAM_SSO_AUDIENCE, payload["aud"])
        self.assertEqual(TEAM_SSO_TOKEN_SECONDS, payload["exp"] - payload["iat"])
        self.assertTrue(signature_part)

    def test_requires_dedicated_strong_secret(self):
        with patch.dict(os.environ, {"TEAM_SSO_SECRET": "short"}, clear=False):
            with self.assertRaises(RuntimeError):
                create_team_sso_url(1)


if __name__ == "__main__":
    unittest.main()
