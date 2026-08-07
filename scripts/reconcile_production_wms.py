#!/usr/bin/env python3
"""Run the production SQLite → PostgreSQL WMS reconciliation job."""

from __future__ import annotations

import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from database import init_db
from production_wms_reconciliation import run_production_wms_reconciliation


def main() -> int:
    init_db()
    report = run_production_wms_reconciliation()
    print(
        json.dumps(
            {
                "ok": report.get("ok", False),
                "status": report.get("status", "unknown"),
                "run_id": report.get("run_id"),
                "issue_count": report.get("issue_count", 0),
                "summary": report.get("summary", {}),
                "checked_at": report.get("checked_at", ""),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0 if report.get("status") != "unavailable" else 1


if __name__ == "__main__":
    raise SystemExit(main())

