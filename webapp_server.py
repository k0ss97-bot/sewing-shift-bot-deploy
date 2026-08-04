"""Run the standalone web application without starting the Telegram bot."""

from __future__ import annotations

import logging
import os
import secrets
import signal
import subprocess
import sys
import threading
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RuntimeSettings:
    host: str
    port: int
    secret: str
    debug: bool
    production: bool


BOT_ENABLE_MARKER = "bot.enabled"


def start_shared_bot_process(
    environ: dict[str, str] | None = None,
    *,
    popen_factory=subprocess.Popen,
    working_directory: str | Path | None = None,
):
    values = dict(os.environ if environ is None else environ)
    db_dir = str(values.get("DB_DIR") or "").strip()
    if not db_dir:
        return None

    marker = Path(db_dir) / BOT_ENABLE_MARKER
    if not marker.is_file():
        return None

    if not str(values.get("BOT_TOKEN") or "").strip():
        raise RuntimeError("BOT_TOKEN is required when shared bot polling is enabled.")

    project_dir = Path(working_directory or Path(__file__).resolve().parent)
    child_environment = dict(values)
    child_environment["MINIAPP_ENABLED"] = "0"
    child_environment["LOGS_DIR"] = str(Path(db_dir) / "logs")
    process = popen_factory(
        [sys.executable, str(project_dir / "main.py")],
        cwd=str(project_dir),
        env=child_environment,
    )
    logging.info("Telegram bot started as shared database process (pid=%s)", process.pid)
    return process


def stop_shared_bot_process(process) -> None:
    if process is None or process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=15)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def load_runtime_settings(environ: dict[str, str] | None = None) -> RuntimeSettings:
    values = os.environ if environ is None else environ
    host = str(values.get("MINIAPP_HOST") or "127.0.0.1").strip()
    raw_port = values.get("PORT") or values.get("MINIAPP_PORT") or "3000"
    try:
        port = int(raw_port)
    except (TypeError, ValueError) as error:
        raise RuntimeError("MINIAPP_PORT must be an integer.") from error
    if not 1 <= port <= 65535:
        raise RuntimeError("MINIAPP_PORT must be between 1 and 65535.")

    production = str(values.get("WEBAPP_ENV") or "").strip().lower() == "production"
    debug = str(values.get("MINIAPP_DEBUG") or "0").strip() == "1"
    secret = str(values.get("WEBAPP_SERVER_SECRET") or "").strip()
    if production and len(secret) < 32:
        raise RuntimeError("WEBAPP_SERVER_SECRET must contain at least 32 characters in production.")
    if production and debug:
        raise RuntimeError("MINIAPP_DEBUG is not allowed in production.")
    if not secret:
        secret = secrets.token_urlsafe(32)

    return RuntimeSettings(host=host, port=port, secret=secret, debug=debug, production=production)


def main() -> None:
    from dotenv import load_dotenv

    load_dotenv(".env")
    settings = load_runtime_settings()
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s %(levelname)s %(message)s",
    )

    # Import after loading the environment because database.py resolves DB_DIR
    # when the module is imported.
    from database import (
        apply_kurasova_brownie_contour_migration,
        apply_ready_cut_confirmation_migration,
        init_db,
    )
    from miniapp_server import start_miniapp_server

    init_db()
    if str(os.getenv("MARKETPLACE_PHASE1A_ENABLED") or "").strip().lower() in {"1", "true", "yes", "on"}:
        try:
            from wms.migrate import migrate_all

            applied = migrate_all()
            if applied:
                logging.info("Applied PostgreSQL migrations at startup: %s", ", ".join(applied))
        except Exception:
            # The web application and local production/WMS workflows must
            # remain available during a temporary PostgreSQL outage. The
            # marketplace screen will expose its own unavailable state.
            logging.exception("PostgreSQL startup migrations were not applied")
    if not apply_kurasova_brownie_contour_migration():
        logging.warning("Requested Kurasova contour reset was not applied; matching active tasks were not found or are no longer safe to reset")
    ready_cut_migration = apply_ready_cut_confirmation_migration()
    if ready_cut_migration is None:
        logging.warning("Ready-cut confirmation migration failed; early preparation tasks were not changed")
    elif ready_cut_migration.get("cancelled_ids"):
        logging.info(
            "Cancelled %s untouched early preparation tasks; they will be recreated after ready-cut confirmation",
            len(ready_cut_migration["cancelled_ids"]),
        )
    server = start_miniapp_server(
        settings.secret,
        settings.host,
        settings.port,
        settings.debug,
    )
    if server is None:
        raise RuntimeError("Standalone web server failed to start.")

    if str(os.getenv("MARKETPLACE_PHASE1A_ENABLED") or "").strip().lower() in {"1", "true", "yes", "on"}:
        def refresh_ozon_supplies() -> None:
            try:
                from marketplace_phase1a import run_phase1a_sync

                result = run_phase1a_sync(datasets=["supplies"], trigger_kind="startup")
                logging.info(
                    "Ozon FBO supply startup refresh: status=%s ok=%s",
                    result.get("status") or result.get("code") or "unknown",
                    bool(result.get("ok")),
                )
            except Exception:
                logging.exception("Ozon FBO supply startup refresh failed")

        threading.Thread(
            target=refresh_ozon_supplies,
            name="ozon-fbo-supply-startup-refresh",
            daemon=True,
        ).start()

    bot_process = None
    logging.info("Telegram bot integration is disabled; running standalone web application only")
    stop_event = threading.Event()

    def request_stop(signum, frame):
        del signum, frame
        stop_event.set()

    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)
    logging.info("Standalone web application is ready on %s:%s", settings.host, settings.port)
    try:
        while not stop_event.wait(5):
            if bot_process is not None and bot_process.poll() is not None:
                raise RuntimeError(
                    f"Telegram bot process stopped unexpectedly with code {bot_process.returncode}."
                )
    finally:
        stop_shared_bot_process(bot_process)
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
