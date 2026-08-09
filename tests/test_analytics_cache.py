from __future__ import annotations

import threading
import time
import unittest

from analytics_cache import TTLReadModelCache


class AnalyticsReadModelCacheTests(unittest.TestCase):
    def test_reuses_deep_copied_value_inside_ttl(self):
        cache = TTLReadModelCache(ttl_seconds=10, maximum_entries=2)
        calls = 0

        def build():
            nonlocal calls
            calls += 1
            return {"rows": [{"value": calls}]}

        first = cache.get_or_build("30d", build)
        first["rows"][0]["value"] = 999
        second = cache.get_or_build("30d", build)

        self.assertEqual(calls, 1)
        self.assertEqual(second["rows"][0]["value"], 1)

    def test_concurrent_requests_build_one_read_model(self):
        cache = TTLReadModelCache(ttl_seconds=10)
        calls = 0
        started = threading.Event()
        release = threading.Event()
        results = []

        def build():
            nonlocal calls
            calls += 1
            started.set()
            release.wait(timeout=2)
            return {"ok": True}

        threads = [threading.Thread(target=lambda: results.append(cache.get_or_build("7d", build))) for _ in range(5)]
        for thread in threads:
            thread.start()
        self.assertTrue(started.wait(timeout=1))
        time.sleep(0.05)
        release.set()
        for thread in threads:
            thread.join(timeout=2)

        self.assertEqual(calls, 1)
        self.assertEqual(results, [{"ok": True}] * 5)

    def test_clear_forces_rebuild(self):
        cache = TTLReadModelCache(ttl_seconds=10)
        calls = []
        cache.get_or_build("key", lambda: calls.append(1) or 1)
        cache.clear()
        result = cache.get_or_build("key", lambda: calls.append(2) or 2)
        self.assertEqual(result, 2)
        self.assertEqual(calls, [1, 2])


if __name__ == "__main__":
    unittest.main()
