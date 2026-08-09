"""Bounded in-process RED and Web Vitals metrics without external dependencies."""

from __future__ import annotations

from collections import deque
import math
import re
import threading
import time
from urllib.parse import urlsplit


_ID_SEGMENT = re.compile(r"^(?:\d+|[0-9a-f]{8,})$", re.IGNORECASE)


def route_label(raw_path: str) -> str:
    path = urlsplit(str(raw_path or "/")).path or "/"
    if path.startswith("/assets/product-thumbnails/"):
        return "/assets/product-thumbnails/:digest.webp"
    return "/".join(":id" if _ID_SEGMENT.fullmatch(part) else part for part in path.split("/"))


def _percentile(values: list[float], percentile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, math.ceil(percentile * len(ordered)) - 1))
    return round(ordered[index], 2)


class ServiceMetrics:
    def __init__(self, *, sample_limit: int = 5000, rum_limit: int = 1000) -> None:
        self.started_at = time.time()
        self._lock = threading.Lock()
        self._requests = 0
        self._errors = 0
        self._request_bytes = 0
        self._response_bytes = 0
        self._latencies_ms = deque(maxlen=sample_limit)
        self._routes: dict[str, dict[str, int]] = {}
        self._rum = deque(maxlen=rum_limit)

    def observe_request(
        self,
        *,
        method: str,
        path: str,
        status: int,
        duration_ms: float,
        request_bytes: int = 0,
        response_bytes: int = 0,
    ) -> None:
        label = f"{str(method or 'UNKNOWN').upper()} {route_label(path)}"
        is_error = int(status or 0) >= 500
        with self._lock:
            self._requests += 1
            self._errors += int(is_error)
            self._request_bytes += max(0, int(request_bytes or 0))
            self._response_bytes += max(0, int(response_bytes or 0))
            self._latencies_ms.append(max(0.0, float(duration_ms)))
            route = self._routes.setdefault(label, {"requests": 0, "errors": 0})
            route["requests"] += 1
            route["errors"] += int(is_error)

    def observe_rum(self, payload: dict) -> None:
        allowed = {}
        limits = {"lcp_ms": 120_000, "inp_ms": 120_000, "cls": 100, "long_task_ms": 600_000}
        for key, maximum in limits.items():
            try:
                value = float(payload.get(key, 0) or 0)
            except (TypeError, ValueError):
                continue
            if math.isfinite(value) and 0 <= value <= maximum:
                allowed[key] = value
        if allowed:
            allowed["recorded_at"] = time.time()
            with self._lock:
                self._rum.append(allowed)

    def snapshot(self) -> dict:
        with self._lock:
            latencies = list(self._latencies_ms)
            rum = list(self._rum)
            requests = self._requests
            errors = self._errors
            routes = sorted(
                ({"route": label, **value} for label, value in self._routes.items()),
                key=lambda row: (-row["requests"], row["route"]),
            )[:30]
            request_bytes = self._request_bytes
            response_bytes = self._response_bytes
        rum_summary = {}
        for field in ("lcp_ms", "inp_ms", "cls", "long_task_ms"):
            values = [row[field] for row in rum if field in row]
            rum_summary[field] = {"samples": len(values), "p75": _percentile(values, 0.75)}
        return {
            "uptime_seconds": max(0, int(time.time() - self.started_at)),
            "requests": requests,
            "errors": errors,
            "error_rate": round(errors / requests, 4) if requests else 0.0,
            "latency_ms": {
                "samples": len(latencies),
                "p50": _percentile(latencies, 0.50),
                "p95": _percentile(latencies, 0.95),
                "p99": _percentile(latencies, 0.99),
            },
            "payload_bytes": {"request": request_bytes, "response": response_bytes},
            "routes": routes,
            "frontend": rum_summary,
        }


SERVICE_METRICS = ServiceMetrics()
