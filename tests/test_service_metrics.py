from __future__ import annotations

import threading
import unittest

from service_metrics import ServiceMetrics, route_label


class ServiceMetricsTests(unittest.TestCase):
    def test_red_snapshot_has_latency_error_rate_payload_and_bounded_routes(self):
        metrics = ServiceMetrics(sample_limit=10)
        metrics.observe_request(
            method="GET", path="/api/items/123?secret=no", status=200,
            duration_ms=10, request_bytes=5, response_bytes=100,
        )
        metrics.observe_request(
            method="GET", path="/api/items/456", status=503,
            duration_ms=100, request_bytes=0, response_bytes=50,
        )
        snapshot = metrics.snapshot()
        self.assertEqual(snapshot["requests"], 2)
        self.assertEqual(snapshot["errors"], 1)
        self.assertEqual(snapshot["error_rate"], 0.5)
        self.assertEqual(snapshot["latency_ms"], {"samples": 2, "p50": 10.0, "p95": 100.0, "p99": 100.0})
        self.assertEqual(snapshot["payload_bytes"], {"request": 5, "response": 150})
        self.assertEqual(snapshot["routes"][0]["route"], "GET /api/items/:id")
        self.assertNotIn("secret", str(snapshot))

    def test_frontend_metrics_are_validated_and_report_p75(self):
        metrics = ServiceMetrics()
        metrics.observe_rum({"lcp_ms": 1000, "inp_ms": 80, "cls": 0.02, "long_task_ms": 30})
        metrics.observe_rum({"lcp_ms": 3000, "inp_ms": "bad", "cls": -1})
        frontend = metrics.snapshot()["frontend"]
        self.assertEqual(frontend["lcp_ms"], {"samples": 2, "p75": 3000.0})
        self.assertEqual(frontend["inp_ms"], {"samples": 1, "p75": 80.0})
        self.assertEqual(frontend["cls"], {"samples": 1, "p75": 0.02})

    def test_concurrent_observation_is_lossless(self):
        metrics = ServiceMetrics(sample_limit=2000)
        threads = [
            threading.Thread(
                target=lambda: [
                    metrics.observe_request(method="POST", path="/api/work", status=200, duration_ms=1)
                    for _ in range(100)
                ]
            )
            for _ in range(10)
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=2)
        self.assertEqual(metrics.snapshot()["requests"], 1000)

    def test_thumbnail_route_does_not_create_unbounded_digest_labels(self):
        self.assertEqual(
            route_label("/assets/product-thumbnails/abcdef1234567890.webp?source=x"),
            "/assets/product-thumbnails/:digest.webp",
        )


if __name__ == "__main__":
    unittest.main()
