#!/usr/bin/env python3
"""Offline smoke audit for the miniapp using a disposable SQLite database."""

from __future__ import annotations

import importlib
import json
import logging
import os
import re
import sys
import tempfile
from html.parser import HTMLParser
from http.cookies import SimpleCookie
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SMOKE_TELEGRAM_ID = 990_000_001
ALLOWED_REMOTE_RESOURCE_HOSTS = {"telegram.org"}
RESOURCE_ATTRIBUTES = {
    "audio": ("src",),
    "iframe": ("src",),
    "img": ("src",),
    "link": ("href",),
    "script": ("src",),
    "source": ("src", "srcset"),
    "video": ("poster", "src"),
}
ISOLATED_MODULES = (
    "database",
    "catalog",
    "route_maps",
    "webapp_auth",
    "webapp_pwa",
    "miniapp_server",
)
CSS_URL_PATTERN = re.compile(r"url\(\s*(['\"]?)([^'\")]+)\1\s*\)", re.IGNORECASE)


class SmokeFailure(RuntimeError):
    """Raised when a required web smoke assertion fails."""


class ResourceCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.resources: list[str] = []
        self.tags: set[str] = set()
        self.inline_script_count = 0
        self.inline_style_count = 0
        self.inline_style_chunks: list[str] = []
        self._style_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        self.tags.add(tag)
        attributes = {name.lower(): value for name, value in attrs}

        if tag == "script" and not attributes.get("src"):
            self.inline_script_count += 1
        if tag == "style":
            self.inline_style_count += 1
            self._style_depth += 1

        for attribute_name in RESOURCE_ATTRIBUTES.get(tag, ()):
            value = attributes.get(attribute_name)
            if not value:
                continue
            if attribute_name == "srcset":
                self.resources.extend(
                    candidate.strip().split()[0]
                    for candidate in value.split(",")
                    if candidate.strip()
                )
            else:
                self.resources.append(value.strip())

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "style" and self._style_depth:
            self._style_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._style_depth:
            self.inline_style_chunks.append(data)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SmokeFailure(message)


def http_request(
    url: str,
    *,
    method: str = "GET",
    payload: dict | None = None,
    headers: dict[str, str] | None = None,
) -> tuple[int, object, bytes]:
    body = None
    request_headers = {"Connection": "close", **(headers or {})}

    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        request_headers["Content-Type"] = "application/json"

    request = Request(url, data=body, headers=request_headers, method=method)

    try:
        with urlopen(request, timeout=5) as response:
            return response.status, response.headers, response.read()
    except HTTPError as error:
        return error.code, error.headers, error.read()


def parse_json_response(status: int, headers: object, body: bytes) -> dict:
    content_type = headers.get_content_type()
    require(content_type == "application/json", f"Expected JSON response, got {content_type}.")

    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise SmokeFailure(f"Invalid JSON response for HTTP {status}: {error}") from error

    require(isinstance(payload, dict), f"Expected JSON object for HTTP {status}.")
    return payload


def audit_html_resources(base_url: str, html_text: str) -> tuple[int, int]:
    collector = ResourceCollector()
    collector.feed(html_text)
    collector.close()

    require({"html", "head", "body"}.issubset(collector.tags), "Miniapp HTML is missing document structure.")
    require(collector.inline_style_count > 0, "Miniapp HTML has no inline stylesheet.")
    require(collector.inline_script_count > 0, "Miniapp HTML has no inline application script.")

    inline_css = "\n".join(collector.inline_style_chunks)
    collector.resources.extend(match.group(2).strip() for match in CSS_URL_PATTERN.finditer(inline_css))

    base_host = urlparse(base_url).netloc
    local_count = 0
    remote_count = 0
    failures = []

    for resource in sorted(set(collector.resources)):
        if not resource or resource.startswith(("#", "data:", "blob:")):
            continue

        resource_url = urljoin(f"{base_url}/", resource)
        parsed_resource = urlparse(resource_url)

        if parsed_resource.netloc == base_host:
            status, _, body = http_request(resource_url)
            if status != 200:
                failures.append(f"Local web resource returned HTTP {status}: {resource}")
                continue
            if not body:
                failures.append(f"Local web resource is empty: {resource}")
                continue
            local_count += 1
            continue

        if parsed_resource.scheme != "https":
            failures.append(f"Remote resource is not HTTPS: {resource}")
            continue
        if parsed_resource.hostname not in ALLOWED_REMOTE_RESOURCE_HOSTS:
            failures.append(f"Remote resource host is not allow-listed: {resource}")
            continue
        remote_count += 1

    if failures:
        details = "\n".join(f"- {failure}" for failure in failures)
        raise SmokeFailure(f"Web resource audit failed:\n{details}")

    return local_count, remote_count


def run_smoke() -> None:
    previous_cwd = Path.cwd()
    previous_environment = {
        name: os.environ.get(name)
        for name in (
            "ADMIN_IDS",
            "DB_DIR",
            "MINIAPP_ENABLED",
            "SHARED_DIR",
            "WEBAPP_SESSION_IDLE_SECONDS",
            "WEBAPP_SESSION_TTL_SECONDS",
        )
    }
    server = None

    with tempfile.TemporaryDirectory(prefix="sewing-web-smoke-") as temporary_dir:
        isolated_root = Path(temporary_dir).resolve()

        try:
            os.environ["ADMIN_IDS"] = str(SMOKE_TELEGRAM_ID)
            os.environ["DB_DIR"] = str(isolated_root)
            os.environ["MINIAPP_ENABLED"] = "1"
            os.environ.pop("SHARED_DIR", None)
            os.environ.pop("WEBAPP_SESSION_IDLE_SECONDS", None)
            os.environ.pop("WEBAPP_SESSION_TTL_SECONDS", None)
            os.chdir(isolated_root)
            sys.path.insert(0, str(PROJECT_ROOT))

            for module_name in ISOLATED_MODULES:
                sys.modules.pop(module_name, None)

            database = importlib.import_module("database")
            database_path = Path(database.DB_NAME).resolve()
            require(
                database_path.parent == isolated_root,
                f"Database escaped the smoke directory: {database_path}",
            )
            database.init_db()
            admin_employee = database.ensure_admin_employee(SMOKE_TELEGRAM_ID)
            require(admin_employee is not None, "Synthetic smoke administrator was not created.")
            webapp_auth = importlib.import_module("webapp_auth")
            webapp_auth.upsert_web_account(
                "smoke-admin",
                SMOKE_TELEGRAM_ID,
                "smoke-admin-password",
            )

            miniapp_server = importlib.import_module("miniapp_server")
            server = miniapp_server.start_miniapp_server(
                "smoke-test-token",
                "127.0.0.1",
                0,
                debug=True,
            )
            require(server is not None, "Miniapp smoke server did not start.")

            base_url = f"http://127.0.0.1:{server.server_address[1]}"

            status, headers, root_body = http_request(f"{base_url}/")
            require(status == 200, f"GET / returned HTTP {status}.")
            require(headers.get_content_type() == "text/html", "GET / did not return HTML.")
            require(headers.get("Cache-Control") == "no-store", "GET / is missing no-store caching.")
            html_text = root_body.decode("utf-8")
            require(len(html_text) > 1_000, "Miniapp HTML response is unexpectedly small.")
            for registration_marker in (
                'id="webRegisterForm"',
                'id="webFullName"',
                'id="webEmail"',
                'id="webPhone"',
                'id="webRegisterPassword"',
                'id="webPasswordConfirm"',
                'fetch("/api/web/register"',
            ):
                require(
                    registration_marker in html_text,
                    f"Registration interface marker is missing: {registration_marker}",
                )
            for session_restore_marker in (
                'id="connectionView"',
                'id="webConnectionRetry"',
                'window.localStorage.getItem(webIdentityStorageKey)',
                'status: "authenticated"',
                'status: "unauthorized"',
                'status: "network_error"',
                'response.status === 401',
                'const webSessionRetryDelaysMs = [2_000, 5_000, 10_000, 20_000, 30_000]',
                'const actionKey = "web-logout"',
                '"Выход не выполнен"',
            ):
                require(
                    session_restore_marker in html_text,
                    f"Web session recovery marker is missing: {session_restore_marker}",
                )
            for install_marker in (
                'id="pwaInstallDock"',
                'id="pwaInstallButton"',
                'id="pwaInstallSteps"',
                '"beforeinstallprompt"',
                'navigator.standalone === true',
                'Добавить на экран iPhone',
            ):
                require(
                    install_marker in html_text,
                    f"PWA installation interface marker is missing: {install_marker}",
                )
            require(
                "sessionStorage" not in html_text,
                "Web session identity must not depend on ephemeral sessionStorage.",
            )
            local_resources, remote_resources = audit_html_resources(base_url, html_text)

            status, headers, app_body = http_request(f"{base_url}/app")
            require(status == 200, f"GET /app returned HTTP {status}.")
            require(headers.get_content_type() == "text/html", "GET /app did not return HTML.")
            require(app_body == root_body, "GET / and GET /app returned different assets.")

            status, headers, health_body = http_request(f"{base_url}/health")
            health_payload = parse_json_response(status, headers, health_body)
            require(status == 200 and health_payload == {"ok": True}, "Health endpoint failed.")

            status, favicon_headers, favicon_body = http_request(f"{base_url}/favicon.ico")
            require(status == 200, f"Favicon endpoint returned HTTP {status}.")
            require(favicon_headers.get_content_type() == "image/png", "Favicon is not a PNG image.")
            require(favicon_body.startswith(b"\x89PNG\r\n\x1a\n"), "Favicon PNG signature is invalid.")

            status, headers, manifest_body = http_request(f"{base_url}/manifest.webmanifest")
            require(status == 200, f"PWA manifest returned HTTP {status}.")
            manifest = json.loads(manifest_body.decode("utf-8"))
            require(manifest.get("display") == "standalone", "PWA manifest is not standalone.")
            require(manifest.get("start_url") == "/app", "PWA manifest start URL is invalid.")
            require(
                manifest.get("display_override") == ["standalone", "minimal-ui"],
                "PWA manifest display fallback order is invalid.",
            )
            manifest_icons = {
                icon.get("src"): icon
                for icon in manifest.get("icons") or []
                if isinstance(icon, dict)
            }
            for icon_size in (192, 512):
                icon_path = f"/pwa/icon-{icon_size}.png"
                icon = manifest_icons.get(icon_path) or {}
                require(icon.get("sizes") == f"{icon_size}x{icon_size}", f"Manifest {icon_path} size is invalid.")
                require(icon.get("type") == "image/png", f"Manifest {icon_path} type is invalid.")
                status, icon_headers, icon_body = http_request(f"{base_url}{icon_path}")
                require(status == 200, f"PWA icon {icon_path} returned HTTP {status}.")
                require(icon_headers.get_content_type() == "image/png", f"PWA icon {icon_path} is not PNG.")
                require(icon_body.startswith(b"\x89PNG\r\n\x1a\n"), f"PWA icon {icon_path} signature is invalid.")

            status, icon_headers, icon_body = http_request(f"{base_url}/pwa/apple-touch-icon-180.png")
            require(status == 200, f"Apple Touch Icon returned HTTP {status}.")
            require(icon_headers.get_content_type() == "image/png", "Apple Touch Icon is not a PNG image.")
            require(icon_body.startswith(b"\x89PNG\r\n\x1a\n"), "Apple Touch Icon PNG signature is invalid.")

            status, mark_headers, mark_body = http_request(f"{base_url}/brand/mark.svg")
            require(status == 200, f"Brand mark returned HTTP {status}.")
            require(mark_headers.get_content_type() == "image/svg+xml", "Brand mark is not SVG.")
            require(b"brand-main" in mark_body, "Brand mark SVG is incomplete.")

            status, headers, worker_body = http_request(f"{base_url}/service-worker.js")
            require(status == 200, f"Service worker returned HTTP {status}.")
            worker_text = worker_body.decode("utf-8")
            require("isPersonalPath" in worker_text, "Service worker lacks API cache protection.")
            require(
                "url.origin !== self.location.origin || isPersonalPath(url.pathname)" in worker_text,
                "Service worker may intercept personal API responses.",
            )
            require('request.method !== "GET"' in worker_text, "Service worker may cache write requests.")

            status, headers, web_session_body = http_request(f"{base_url}/api/web/session")
            web_session_payload = parse_json_response(status, headers, web_session_body)
            require(status == 401, f"Missing web session returned HTTP {status} instead of 401.")
            require(
                web_session_payload.get("code") == "unauthorized",
                "Missing web session response is not explicitly unauthorized.",
            )

            status, headers, unauthorized_body = http_request(
                f"{base_url}/api/app/state",
                method="POST",
                payload={},
            )
            unauthorized_payload = parse_json_response(status, headers, unauthorized_body)
            require(status == 401, f"Unauthenticated API request returned HTTP {status}.")
            require(unauthorized_payload.get("ok") is False, "Unauthenticated API response is malformed.")

            status, headers, state_body = http_request(
                f"{base_url}/api/app/state",
                method="POST",
                payload={"telegram_id": SMOKE_TELEGRAM_ID},
            )
            state_payload = parse_json_response(status, headers, state_body)
            require(status == 200, f"Debug API smoke request returned HTTP {status}.")
            require(state_payload.get("ok") is True, "Debug API smoke response is not successful.")
            require(state_payload.get("is_admin") is True, "Synthetic smoke administrator was not recognized.")

            status, headers, login_body = http_request(
                f"{base_url}/api/web/login",
                method="POST",
                payload={"username": "smoke-admin", "password": "smoke-admin-password"},
                headers={"Origin": base_url},
            )
            login_payload = parse_json_response(status, headers, login_body)
            require(status == 200 and login_payload.get("ok") is True, "Standalone web login failed.")
            set_cookie = str(headers.get("Set-Cookie") or "")
            parsed_cookie = SimpleCookie()
            parsed_cookie.load(set_cookie)
            session_morsel = parsed_cookie.get(webapp_auth.COOKIE_NAME) or parsed_cookie.get(
                webapp_auth.SECURE_COOKIE_NAME
            )
            require(session_morsel is not None, "Standalone web login did not set a session cookie.")
            cookie_max_age = int(session_morsel["max-age"] or "0")
            require(
                webapp_auth.DEFAULT_SESSION_TTL_SECONDS - 1
                <= cookie_max_age
                <= webapp_auth.DEFAULT_SESSION_TTL_SECONDS,
                "Standalone web session cookie is not valid for the configured 30-day lifetime.",
            )
            session_cookie = set_cookie.split(";", 1)[0]
            require(session_cookie, "Standalone web login did not set a session cookie.")
            require("HttpOnly" in set_cookie, "Session cookie is not HttpOnly.")
            csrf_token = str(login_payload.get("csrf_token") or "")
            require(csrf_token, "Standalone web login did not return CSRF token.")

            status, headers, web_state_body = http_request(
                f"{base_url}/api/app/state",
                method="POST",
                payload={},
                headers={
                    "Cookie": session_cookie,
                    "Origin": base_url,
                    "X-CSRF-Token": csrf_token,
                },
            )
            web_state = parse_json_response(status, headers, web_state_body)
            require(status == 200 and web_state.get("is_admin") is True, "Web session API access failed.")

            status, _, _ = http_request(
                f"{base_url}/api/app/state",
                method="POST",
                payload={},
                headers={
                    "Cookie": session_cookie,
                    "Origin": base_url,
                    "X-CSRF-Token": "invalid",
                },
            )
            require(status == 401, "Invalid CSRF token was not rejected.")

            print(
                "Web smoke passed: HTML, PWA, web session, auth boundary, temporary DB, "
                f"{local_resources} local and {remote_resources} allow-listed remote resources."
            )
        finally:
            if server is not None:
                server.shutdown()
                server.server_close()

            for module_name in ISOLATED_MODULES:
                sys.modules.pop(module_name, None)

            if str(PROJECT_ROOT) in sys.path:
                sys.path.remove(str(PROJECT_ROOT))
            os.chdir(previous_cwd)

            for name, value in previous_environment.items():
                if value is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = value


def main() -> int:
    logging.basicConfig(level=logging.CRITICAL)

    try:
        run_smoke()
    except (OSError, SmokeFailure, UnicodeDecodeError) as error:
        print(f"Web smoke failed: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
