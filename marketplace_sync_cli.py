"""Run the read-only marketplace synchronization outside an HTTP request."""

from datetime import datetime, timedelta
import json
import os

from database import get_db_connection, local_now
from marketplace_phase1a import phase1a_enabled, run_phase1a_sync
from marketplaces import ensure_schema, sync_ozon
from wildberries import sync_wildberries


def _sync_due(marketplace: str, interval_seconds: int) -> bool:
    """Check a connector cadence from persisted run timestamps."""
    interval_seconds = max(300, int(interval_seconds))
    conn = get_db_connection()
    try:
        ensure_schema(conn)
        row = conn.execute(
            """SELECT MAX(COALESCE(r.finished_at,r.started_at))
                 FROM marketplace_sync_runs r
                 JOIN marketplace_accounts a ON a.id=r.account_id
                WHERE a.marketplace=?""",
            (marketplace,),
        ).fetchone()
    finally:
        conn.close()
    if not row or not row[0]:
        return True
    try:
        last_run = datetime.fromisoformat(str(row[0]))
    except (TypeError, ValueError):
        return True
    current_time = datetime.now(last_run.tzinfo) if last_run.tzinfo is not None else local_now()
    return current_time - last_run >= timedelta(seconds=interval_seconds)


def _legacy_sync_due() -> bool:
    """Keep the pre-Phase-1A Ozon fallback on its historical hourly cadence."""
    try:
        interval_seconds = max(300, int(os.getenv("MARKETPLACE_LEGACY_SYNC_INTERVAL_SECONDS", "3600")))
    except (TypeError, ValueError):
        interval_seconds = 3600
    return _sync_due("ozon", interval_seconds)


def _wildberries_sync_due() -> bool:
    try:
        interval_seconds = max(900, int(os.getenv("MARKETPLACE_WB_SYNC_INTERVAL_SECONDS", "1800")))
    except (TypeError, ValueError):
        interval_seconds = 1800
    return _sync_due("wildberries", interval_seconds)


def _ozon_sync() -> dict:
    if phase1a_enabled():
        return run_phase1a_sync()
    if not _legacy_sync_due():
        return {
            "ok": True,
            "status": "not_due",
            "read_only": True,
            "message": "Legacy Ozon sync ещё свежее часовой cadence.",
        }
    return sync_ozon()


def run_sync() -> dict:
    ozon = _ozon_sync()
    if not os.getenv("WB_API_TOKEN", "").strip():
        return ozon
    wildberries = (
        sync_wildberries()
        if _wildberries_sync_due()
        else {
            "ok": True,
            "status": "not_due",
            "read_only": True,
            "message": "Wildberries sync ещё свежее 30-минутной cadence.",
        }
    )
    ok = bool(ozon.get("ok")) and bool(wildberries.get("ok"))
    status = "success" if ok else ("partial" if ozon.get("ok") or wildberries.get("ok") else "error")
    return {
        "ok": ok,
        "status": status,
        "read_only": True,
        "message": "Фоновая синхронизация маркетплейсов завершена." if ok else "Фоновая синхронизация завершена частично.",
        "results": {"ozon": ozon, "wildberries": wildberries},
    }


def cli_exit_code(result: dict) -> int:
    # A partial result is a successfully completed worker invocation whose
    # source-level failures are persisted for data-quality/UI diagnostics.
    return 0 if result.get("ok") or result.get("status") in {"partial", "deferred", "not_due"} else 1


if __name__ == "__main__":
    result = run_sync()
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(cli_exit_code(result))
