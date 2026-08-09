from __future__ import annotations

import threading
import time
import unittest
from pathlib import Path

from http_lifecycle import HTTP_ACCEPT_QUEUE_SIZE, RequestDrainState


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class HttpServerLifecycleTests(unittest.TestCase):
    def test_drain_state_rejects_new_requests_and_waits_for_active_work(self):
        state = RequestDrainState()
        self.assertTrue(state.try_start())
        self.assertEqual(state.active, 1)
        state.begin_draining()
        self.assertTrue(state.draining)
        self.assertFalse(state.try_start())

        completed = threading.Event()

        def finish_request():
            time.sleep(0.03)
            state.finish()
            completed.set()

        worker = threading.Thread(target=finish_request)
        worker.start()
        self.assertTrue(state.wait_until_idle(0.5))
        worker.join()
        self.assertTrue(completed.is_set())
        self.assertEqual(state.active, 0)

    def test_drain_wait_is_bounded_and_counter_cannot_underflow(self):
        state = RequestDrainState()
        self.assertTrue(state.try_start())
        state.begin_draining()
        started = time.monotonic()
        self.assertFalse(state.wait_until_idle(0.02))
        self.assertLess(time.monotonic() - started, 0.2)
        state.finish()
        with self.assertRaisesRegex(RuntimeError, "underflow"):
            state.finish()

    def test_server_has_an_explicit_bounded_accept_queue(self):
        self.assertGreaterEqual(HTTP_ACCEPT_QUEUE_SIZE, 32)
        source = (PROJECT_ROOT / "miniapp_server.py").read_text(encoding="utf-8")
        self.assertIn("request_queue_size = HTTP_ACCEPT_QUEUE_SIZE", source)


if __name__ == "__main__":
    unittest.main()
