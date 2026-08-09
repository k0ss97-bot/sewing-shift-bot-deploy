"""Dependency-free request draining primitives for the standalone HTTP server."""

from __future__ import annotations

import threading
import time


HTTP_ACCEPT_QUEUE_SIZE = 64


class RequestDrainState:
    """Track active requests and coordinate a bounded graceful shutdown."""

    def __init__(self):
        self._condition = threading.Condition()
        self._active = 0
        self._draining = False

    def try_start(self) -> bool:
        with self._condition:
            if self._draining:
                return False
            self._active += 1
            return True

    def finish(self) -> None:
        with self._condition:
            if self._active <= 0:
                raise RuntimeError("request drain counter underflow")
            self._active -= 1
            if self._active == 0:
                self._condition.notify_all()

    def begin_draining(self) -> None:
        with self._condition:
            self._draining = True
            if self._active == 0:
                self._condition.notify_all()

    def wait_until_idle(self, timeout_seconds: float) -> bool:
        deadline = time.monotonic() + max(0.0, timeout_seconds)
        with self._condition:
            while self._active:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    return False
                self._condition.wait(remaining)
            return True

    @property
    def active(self) -> int:
        with self._condition:
            return self._active

    @property
    def draining(self) -> bool:
        with self._condition:
            return self._draining
