#!/usr/bin/env python3
"""Conservative read-only load smoke for the production web entry points."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics
import time
from urllib.parse import urlparse
from urllib.request import Request, urlopen


def percentile(values: list[float], percent: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    index = max(0, min(len(ordered) - 1, round((len(ordered) - 1) * percent)))
    return ordered[index]


def request_once(url: str) -> tuple[int, float, int]:
    started = time.perf_counter()
    request = Request(url, headers={"User-Agent": "sewing-readonly-load-smoke/1", "Connection": "close"})
    try:
        with urlopen(request, timeout=10) as response:
            body = response.read()
            return int(response.status), (time.perf_counter() - started) * 1000, len(body)
    except Exception:
        return 0, (time.perf_counter() - started) * 1000, 0


def run(base_url: str, *, requests: int, concurrency: int) -> dict[str, float | int]:
    base = base_url.rstrip("/")
    urls = [f"{base}/health" if index % 2 == 0 else f"{base}/app" for index in range(requests)]
    results = []
    started = time.perf_counter()
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(request_once, url) for url in urls]
        for future in as_completed(futures):
            results.append(future.result())
    elapsed = max(0.001, time.perf_counter() - started)
    durations = [duration for _, duration, _ in results]
    failures = sum(status != 200 for status, _, _ in results)
    return {
        "requests": len(results),
        "failures": failures,
        "rps": round(len(results) / elapsed, 2),
        "p50_ms": round(statistics.median(durations), 2) if durations else 0,
        "p95_ms": round(percentile(durations, 0.95), 2),
        "max_ms": round(max(durations, default=0), 2),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("base_url")
    parser.add_argument("--requests", type=int, default=60)
    parser.add_argument("--concurrency", type=int, default=6)
    parser.add_argument("--maximum-p95-ms", type=float, default=1500)
    arguments = parser.parse_args()
    parsed = urlparse(arguments.base_url)
    if parsed.scheme != "https" and parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise SystemExit("Load smoke requires HTTPS outside loopback.")
    requests = max(1, min(500, arguments.requests))
    concurrency = max(1, min(20, arguments.concurrency))
    result = run(arguments.base_url, requests=requests, concurrency=concurrency)
    print(
        "Read-only load smoke: "
        f"requests={result['requests']} failures={result['failures']} rps={result['rps']} "
        f"p50_ms={result['p50_ms']} p95_ms={result['p95_ms']} max_ms={result['max_ms']}"
    )
    return 0 if result["failures"] == 0 and result["p95_ms"] <= arguments.maximum_p95_ms else 1


if __name__ == "__main__":
    raise SystemExit(main())
