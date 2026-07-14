"""Run the standalone web application without starting the Telegram bot."""

from __future__ import annotations

import logging
import os
import secrets
import signal
import threading
from dataclasses import dataclass


@dataclass(frozen=True)
class RuntimeSettings:
    host: str
    port: int
    secret: str
    debug: bool
    production: bool


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
    secret = str(values.get("WEBAPP_SERVER_SECRET") or values.get("BOT_TOKEN") or "").strip()
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
    from database import init_db
    from miniapp_server import start_miniapp_server

    init_db()
    server = start_miniapp_server(
        settings.secret,
        settings.host,
        settings.port,
        settings.debug,
    )
    if server is None:
        raise RuntimeError("Standalone web server failed to start.")

    stop_event = threading.Event()

    def request_stop(signum, frame):
        del signum, frame
        stop_event.set()

    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)
    logging.info("Standalone web application is ready on %s:%s", settings.host, settings.port)
    try:
        stop_event.wait()
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
