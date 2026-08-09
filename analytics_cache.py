"""Small stampede-protected cache for server-side analytics read models."""

from __future__ import annotations

from collections import OrderedDict
from copy import deepcopy
import threading
import time
from typing import Callable, Generic, Hashable, TypeVar


Key = TypeVar("Key", bound=Hashable)
Value = TypeVar("Value")


class TTLReadModelCache(Generic[Key, Value]):
    def __init__(self, *, ttl_seconds: float, maximum_entries: int = 64) -> None:
        self.ttl_seconds = max(0.1, float(ttl_seconds))
        self.maximum_entries = max(1, int(maximum_entries))
        self._lock = threading.RLock()
        self._values: OrderedDict[Key, tuple[float, Value]] = OrderedDict()
        self._inflight: dict[Key, threading.Event] = {}

    def clear(self) -> None:
        with self._lock:
            self._values.clear()

    def get_or_build(self, key: Key, builder: Callable[[], Value]) -> Value:
        while True:
            now = time.monotonic()
            with self._lock:
                cached = self._values.get(key)
                if cached is not None and cached[0] > now:
                    self._values.move_to_end(key)
                    return deepcopy(cached[1])
                if cached is not None:
                    self._values.pop(key, None)
                event = self._inflight.get(key)
                if event is None:
                    event = threading.Event()
                    self._inflight[key] = event
                    leader = True
                else:
                    leader = False
            if leader:
                break
            # The current builder owns this key. Waiting avoids a request burst
            # executing the same heavy aggregation dozens of times.
            event.wait(timeout=max(1.0, self.ttl_seconds))

        try:
            value = builder()
            with self._lock:
                self._values[key] = (time.monotonic() + self.ttl_seconds, deepcopy(value))
                self._values.move_to_end(key)
                while len(self._values) > self.maximum_entries:
                    self._values.popitem(last=False)
            return value
        finally:
            with self._lock:
                finished = self._inflight.pop(key, None)
                if finished is not None:
                    finished.set()
