from __future__ import annotations

import io
import json
import sqlite3
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

from wildberries import WildberriesAPIError, WildberriesClient, _now, _persisted_retry_remaining


class FakeResponse:
    def __init__(self, payload, *, status=200, headers=None):
        self.payload = json.dumps(payload).encode()
        self.status = status
        self.headers = headers or {}

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self, _limit=-1):
        return self.payload


def http_error(status: int, payload: dict, headers=None) -> HTTPError:
    return HTTPError(
        "https://example.invalid",
        status,
        "error",
        headers or {},
        io.BytesIO(json.dumps(payload).encode()),
    )


class WildberriesClientTests(unittest.TestCase):
    def client(self, **kwargs):
        return WildberriesClient(
            "seller-token",
            client_secret=kwargs.pop("client_secret", ""),
            sleep=lambda _seconds: None,
            monotonic=lambda: 0.0,
            max_attempts=kwargs.pop("max_attempts", 1),
            **kwargs,
        )

    @patch("wildberries.urlopen")
    def test_request_sends_bearer_and_client_secret(self, mocked_urlopen):
        mocked_urlopen.return_value = FakeResponse({"ok": True})
        client = self.client(client_secret="service-secret")

        self.assertEqual(client.request("https://example.invalid", scope="catalog"), {"ok": True})

        request = mocked_urlopen.call_args.args[0]
        self.assertEqual(request.get_header("Authorization"), "Bearer seller-token")
        self.assertEqual(request.get_header("X-client-secret"), "service-secret")
        self.assertEqual(request.get_header("User-agent"), "ShagaemVmeste/1.0")

    @patch("wildberries.urlopen")
    def test_403_is_forbidden_with_safe_wb_diagnostics(self, mocked_urlopen):
        mocked_urlopen.side_effect = http_error(
            403,
            {
                "title": "forbidden",
                "detail": "base token without secret is not allowed",
                "code": "base token without secret is not allowed for this path",
                "requestId": "request-403",
                "unsafe": "must not be retained",
            },
        )

        with self.assertRaises(WildberriesAPIError) as caught:
            self.client().request("https://example.invalid", scope="stocks")

        self.assertEqual(caught.exception.code, "forbidden")
        self.assertEqual(caught.exception.http_status, 403)
        self.assertEqual(caught.exception.request_id, "request-403")
        self.assertNotIn("unsafe", caught.exception.safe_response)
        self.assertIn("X-Client-Secret", str(caught.exception))

    @patch("wildberries.urlopen")
    def test_http_codes_are_not_collapsed_to_permission_required(self, mocked_urlopen):
        cases = {
            401: "invalid_token",
            402: "payment_required",
            404: "endpoint_or_resource_not_found",
            503: "wb_unavailable",
        }
        for status, expected_code in cases.items():
            mocked_urlopen.side_effect = http_error(status, {"requestId": f"request-{status}"})
            with self.subTest(status=status):
                with self.assertRaises(WildberriesAPIError) as caught:
                    self.client().request("https://example.invalid", scope="catalog")
                self.assertEqual(caught.exception.code, expected_code)

    def test_fbs_stocks_uses_chrt_ids_for_each_warehouse(self):
        client = self.client()
        calls = []

        def request(url, payload=None, *, method=None, scope="generic"):
            calls.append((url, payload, method, scope))
            if url.endswith("/api/v3/warehouses"):
                return [{"id": 10, "name": "Склад 10"}, {"id": 20, "name": "Склад 20"}]
            return {"stocks": [{"chrtId": payload["chrtIds"][0], "amount": 7}]}

        client.request = request
        rows = client.fbs_stocks([111, 222])

        self.assertEqual([call[1] for call in calls[1:]], [{"chrtIds": [111, 222]}, {"chrtIds": [111, 222]}])
        self.assertEqual([row["warehouseId"] for row in rows], [10, 20])
        self.assertEqual([row["warehouseName"] for row in rows], ["Склад 10", "Склад 20"])

    def test_persisted_rate_limit_is_scoped_to_one_capability(self):
        connection = sqlite3.connect(":memory:")
        connection.execute(
            """CREATE TABLE marketplace_wb_capabilities (
                   account_id INTEGER, capability TEXT, status TEXT,
                   retry_after_seconds REAL, checked_at TEXT
               )"""
        )
        connection.execute(
            "INSERT INTO marketplace_wb_capabilities VALUES (1,'finance','rate_limited',600,?)",
            (_now(),),
        )

        self.assertGreater(_persisted_retry_remaining(connection, 1, "finance"), 0)
        self.assertEqual(_persisted_retry_remaining(connection, 1, "catalog"), 0)


if __name__ == "__main__":
    unittest.main()
