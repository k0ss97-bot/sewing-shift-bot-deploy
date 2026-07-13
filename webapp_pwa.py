"""Self-contained PWA resources for the ``Шагаем вместе`` web application.

The module has no framework or third-party dependencies.  ``miniapp_server`` can
serve an exact resource path with a single ``send_pwa_resource`` call and can add
the metadata/registration markup with ``inject_pwa_markup``.

Only the static application shell is cached.  API requests, non-GET requests,
authenticated requests, query strings, and network responses containing user
state are never written to Cache Storage.
"""

from __future__ import annotations

import binascii
import hashlib
import json
import math
import struct
import zlib
from dataclasses import dataclass
from functools import lru_cache
from types import MappingProxyType
from typing import Mapping
from urllib.parse import urlsplit


APP_NAME = "Шагаем вместе"
APP_SHORT_NAME = "Шагаем вместе"
APP_DESCRIPTION = "Рабочее приложение швейного производства"
APP_START_URL = "/app"
APP_SCOPE = "/"

THEME_COLOR = "#c36f55"
BACKGROUND_COLOR = "#fffaf3"

MANIFEST_PATH = "/manifest.webmanifest"
SERVICE_WORKER_PATH = "/service-worker.js"
BROWSERCONFIG_PATH = "/browserconfig.xml"
ICON_SVG_PATH = "/pwa/icon.svg"
MASK_ICON_SVG_PATH = "/pwa/safari-pinned-tab.svg"
ICON_32_PATH = "/pwa/icon-32.png"
APPLE_TOUCH_ICON_PATH = "/pwa/apple-touch-icon-180.png"
ICON_192_PATH = "/pwa/icon-192.png"
ICON_512_PATH = "/pwa/icon-512.png"
MS_TILE_ICON_PATH = "/pwa/mstile-150x150.png"

_ICON_BACKGROUND = (195, 111, 85)
_ICON_BACKGROUND_DARK = (169, 86, 64)
_ICON_FOREGROUND = (255, 250, 243)
_ICON_SAGE = (111, 128, 95)


@dataclass(frozen=True, slots=True)
class PWAResource:
    """An immutable HTTP representation ready for ``BaseHTTPRequestHandler``."""

    path: str
    body: bytes
    content_type: str
    cache_control: str
    etag: str
    extra_headers: tuple[tuple[str, str], ...] = ()

    @property
    def content(self) -> bytes:
        """Compatibility alias for servers that name response bytes ``content``."""

        return self.body

    def response_headers(self) -> dict[str, str]:
        headers = {
            "Content-Type": self.content_type,
            "Content-Length": str(len(self.body)),
            "Cache-Control": self.cache_control,
            "ETag": self.etag,
            "X-Content-Type-Options": "nosniff",
            "Cross-Origin-Resource-Policy": "same-origin",
            "Referrer-Policy": "no-referrer",
        }
        headers.update(self.extra_headers)
        return headers


def _json_bytes(payload: object) -> bytes:
    return json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8") + b"\n"


def build_manifest() -> dict[str, object]:
    """Return a fresh, JSON-serializable web app manifest."""

    return {
        "id": APP_START_URL,
        "name": APP_NAME,
        "short_name": APP_SHORT_NAME,
        "description": APP_DESCRIPTION,
        "lang": "ru",
        "dir": "ltr",
        "start_url": APP_START_URL,
        "scope": APP_SCOPE,
        "display": "standalone",
        "background_color": BACKGROUND_COLOR,
        "theme_color": THEME_COLOR,
        "categories": ["business", "productivity"],
        "prefer_related_applications": False,
        "icons": [
            {
                "src": ICON_SVG_PATH,
                "sizes": "any",
                "type": "image/svg+xml",
                "purpose": "any maskable",
            },
            {
                "src": ICON_192_PATH,
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "any maskable",
            },
            {
                "src": ICON_512_PATH,
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "any maskable",
            },
        ],
    }


APP_ICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <rect width="512" height="512" fill="#c36f55"/>
  <path d="M118 348h87v-72h87v-71h66" fill="none" stroke="#a95640" stroke-opacity=".34" stroke-width="48" stroke-linecap="round" stroke-linejoin="round" transform="translate(4 7)"/>
  <path d="M118 348h87v-72h87v-71h66" fill="none" stroke="#fffaf3" stroke-width="40" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="118" cy="348" r="14" fill="#6f805f"/>
  <circle cx="205" cy="276" r="14" fill="#6f805f"/>
  <circle cx="292" cy="205" r="14" fill="#6f805f"/>
  <path d="m352 211 48-48" fill="none" stroke="#6f805f" stroke-width="18" stroke-linecap="round"/>
  <circle cx="400" cy="163" r="18" fill="#fffaf3"/>
  <circle cx="400" cy="163" r="7" fill="#c36f55"/>
</svg>
"""

SAFARI_MASK_ICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <path d="M118 328h67v-72h87v-71h66l43-43a27 27 0 1 1 19 19l-48 48a27 27 0 0 1-19 8h-29v66a25 25 0 0 1-25 25h-62v47a25 25 0 0 1-25 25h-74a26 26 0 1 1 0-52Z"/>
</svg>
"""


def _png_chunk(kind: bytes, payload: bytes) -> bytes:
    checksum = binascii.crc32(kind)
    checksum = binascii.crc32(payload, checksum) & 0xFFFFFFFF
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", checksum)


def _segment_distance(
    x: float,
    y: float,
    start: tuple[float, float],
    end: tuple[float, float],
) -> float:
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    denominator = dx * dx + dy * dy
    if denominator == 0:
        return math.hypot(x - start[0], y - start[1])
    position = ((x - start[0]) * dx + (y - start[1]) * dy) / denominator
    position = max(0.0, min(1.0, position))
    return math.hypot(x - (start[0] + position * dx), y - (start[1] + position * dy))


def _coverage(distance: float, radius: float, antialias: float) -> float:
    return max(0.0, min(1.0, (radius + antialias - distance) / (2.0 * antialias)))


def _paint_segment(
    pixels: bytearray,
    size: int,
    start: tuple[float, float],
    end: tuple[float, float],
    radius: float,
    color: tuple[int, int, int],
    opacity: float = 1.0,
) -> None:
    antialias = 0.85 / size
    padding = radius + antialias
    first_column = max(0, math.floor((min(start[0], end[0]) - padding) * size))
    final_column = min(size, math.ceil((max(start[0], end[0]) + padding) * size))
    first_row = max(0, math.floor((min(start[1], end[1]) - padding) * size))
    final_row = min(size, math.ceil((max(start[1], end[1]) + padding) * size))

    for row_index in range(first_row, final_row):
        y = (row_index + 0.5) / size
        for column_index in range(first_column, final_column):
            x = (column_index + 0.5) / size
            coverage = opacity * _coverage(
                _segment_distance(x, y, start, end),
                radius,
                antialias,
            )
            if coverage <= 0:
                continue
            pixel_index = (row_index * size + column_index) * 4
            for channel in range(3):
                current = pixels[pixel_index + channel]
                pixels[pixel_index + channel] = round(
                    current + (color[channel] - current) * coverage
                )


@lru_cache(maxsize=8)
def render_icon_png(size: int) -> bytes:
    """Render the vector mark as a deterministic, dependency-free RGBA PNG."""

    if size < 16 or size > 1024:
        raise ValueError("icon size must be between 16 and 1024 pixels")

    points = (
        (118 / 512, 348 / 512),
        (205 / 512, 348 / 512),
        (205 / 512, 276 / 512),
        (292 / 512, 276 / 512),
        (292 / 512, 205 / 512),
        (358 / 512, 205 / 512),
    )
    step_segments = tuple(zip(points, points[1:]))
    needle_start = (352 / 512, 211 / 512)
    needle_end = (400 / 512, 163 / 512)
    pixel = bytes((*_ICON_BACKGROUND, 255))
    pixels = bytearray(pixel * size * size)

    shadow_offset = (4 / 512, 7 / 512)
    for start, end in step_segments:
        _paint_segment(
            pixels,
            size,
            (start[0] + shadow_offset[0], start[1] + shadow_offset[1]),
            (end[0] + shadow_offset[0], end[1] + shadow_offset[1]),
            24 / 512,
            _ICON_BACKGROUND_DARK,
            0.34,
        )

    for start, end in step_segments:
        _paint_segment(pixels, size, start, end, 20 / 512, _ICON_FOREGROUND)

    for center in (points[0], points[2], points[4]):
        _paint_segment(pixels, size, center, center, 14 / 512, _ICON_SAGE)

    _paint_segment(
        pixels,
        size,
        needle_start,
        needle_end,
        9 / 512,
        _ICON_SAGE,
    )
    _paint_segment(
        pixels,
        size,
        needle_end,
        needle_end,
        18 / 512,
        _ICON_FOREGROUND,
    )
    _paint_segment(
        pixels,
        size,
        needle_end,
        needle_end,
        7 / 512,
        _ICON_BACKGROUND,
    )

    raw_rows = bytearray()
    stride = size * 4
    for row_index in range(size):
        raw_rows.append(0)  # PNG filter type: None
        row_start = row_index * stride
        raw_rows.extend(pixels[row_start:row_start + stride])

    header = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    return b"".join(
        (
            b"\x89PNG\r\n\x1a\n",
            _png_chunk(b"IHDR", header),
            _png_chunk(b"IDAT", zlib.compress(bytes(raw_rows), level=9)),
            _png_chunk(b"IEND", b""),
        )
    )


MANIFEST_WEBMANIFEST = _json_bytes(build_manifest())
PWA_MANIFEST = MANIFEST_WEBMANIFEST

_ICON_PNGS = MappingProxyType(
    {
        32: render_icon_png(32),
        150: render_icon_png(150),
        180: render_icon_png(180),
        192: render_icon_png(192),
        512: render_icon_png(512),
    }
)


def _asset_revision() -> str:
    digest = hashlib.sha256(MANIFEST_WEBMANIFEST)
    digest.update(APP_ICON_SVG.encode("utf-8"))
    digest.update(SAFARI_MASK_ICON_SVG.encode("utf-8"))
    for size, body in _ICON_PNGS.items():
        digest.update(str(size).encode("ascii"))
        digest.update(body)
    return digest.hexdigest()[:16]


PWA_ASSET_REVISION = _asset_revision()
PWA_CACHE_PREFIX = "shagaem-vmeste-app-shell-"

_SERVICE_WORKER_TEMPLATE = """"use strict";

const CACHE_PREFIX = __CACHE_PREFIX__;
const CACHE_NAME = CACHE_PREFIX + __CACHE_REVISION__;
const APP_SHELL_CACHE_KEY = __APP_SHELL_CACHE_KEY__;
const APP_SHELL_PATHS = new Set(__APP_SHELL_PATHS__);
const PRECACHE_PATHS = Object.freeze(__PRECACHE_PATHS__);
const STATIC_PATHS = new Set(__STATIC_PATHS__);
const PERSONAL_QUERY_KEYS = new Set([
  "auth", "authtoken", "debug_tg_id", "hash", "initdata", "telegram_id",
  "tgwebappdata", "token"
]);

function isPersonalPath(pathname) {
  return pathname === "/api" || pathname.startsWith("/api/");
}

function hasPersonalQuery(url) {
  for (const key of url.searchParams.keys()) {
    if (PERSONAL_QUERY_KEYS.has(key.toLowerCase())) return true;
  }
  return false;
}

async function fetchForPrecache(path) {
  // This exact URL is a public shell. Credentials and query data are omitted.
  const request = new Request(path, {
    method: "GET",
    credentials: "omit",
    cache: "reload",
    redirect: "error"
  });
  const response = await fetch(request);
  if (!response.ok || response.type !== "basic") {
    throw new Error(`PWA precache failed for ${path}: ${response.status}`);
  }
  return [new Request(path, {credentials: "omit"}), response];
}

self.addEventListener("install", (event) => {
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE_NAME);
    const entries = await Promise.all(PRECACHE_PATHS.map(fetchForPrecache));
    await Promise.all(entries.map(([request, response]) => cache.put(request, response)));
    await self.skipWaiting();
  })());
});

self.addEventListener("activate", (event) => {
  event.waitUntil((async () => {
    const cacheNames = await caches.keys();
    await Promise.all(cacheNames
      .filter((name) => name.startsWith(CACHE_PREFIX) && name !== CACHE_NAME)
      .map((name) => caches.delete(name)));
    if (self.registration.navigationPreload) {
      try {
        await self.registration.navigationPreload.enable();
      } catch (_error) {
        // Navigation still works on browsers without preload support.
      }
    }
    await self.clients.claim();
  })());
});

async function networkFirstNavigation(event) {
  try {
    const preloaded = await event.preloadResponse;
    const response = preloaded || await fetch(event.request);
    if (response.status < 500) return response;
  } catch (_error) {
    // Fall through to the credential-free shell cached at install time.
  }
  const cache = await caches.open(CACHE_NAME);
  return await cache.match(APP_SHELL_CACHE_KEY) || Response.error();
}

async function cacheFirstStatic(request, pathname) {
  const cache = await caches.open(CACHE_NAME);
  const cached = await cache.match(pathname);
  // A miss goes to the network but is deliberately not written to Cache Storage.
  return cached || fetch(request);
}

self.addEventListener("fetch", (event) => {
  const request = event.request;
  if (request.method !== "GET") return;

  const url = new URL(request.url);
  if (url.origin !== self.location.origin || isPersonalPath(url.pathname)) return;
  if (request.headers.has("authorization")) return;

  if (request.mode === "navigate" && APP_SHELL_PATHS.has(url.pathname)) {
    // The live response may be personalized, so it is returned but never cached.
    event.respondWith(networkFirstNavigation(event));
    return;
  }

  if (url.search || hasPersonalQuery(url) || !STATIC_PATHS.has(url.pathname)) return;
  event.respondWith(cacheFirstStatic(request, url.pathname));
});

self.addEventListener("message", (event) => {
  if (event.data && event.data.type === "SKIP_WAITING") self.skipWaiting();
});
"""


def _cache_revision(app_shell_revision: str | None) -> str:
    if not app_shell_revision:
        return PWA_ASSET_REVISION
    digest = hashlib.sha256(PWA_ASSET_REVISION.encode("ascii"))
    digest.update(b":")
    digest.update(str(app_shell_revision).encode("utf-8"))
    return digest.hexdigest()[:16]


def app_shell_revision(html: str | bytes) -> str:
    """Create the short revision token expected by ``build_service_worker``."""

    body = html.encode("utf-8") if isinstance(html, str) else bytes(html)
    return hashlib.sha256(body).hexdigest()[:16]


def build_service_worker(app_shell_revision_token: str | None = None) -> str:
    """Build the worker, optionally coupling its cache to the current shell HTML."""

    precache_paths = [
        APP_START_URL,
        MANIFEST_PATH,
        ICON_SVG_PATH,
        ICON_192_PATH,
        ICON_512_PATH,
    ]
    static_paths = [
        MANIFEST_PATH,
        BROWSERCONFIG_PATH,
        ICON_SVG_PATH,
        MASK_ICON_SVG_PATH,
        ICON_32_PATH,
        APPLE_TOUCH_ICON_PATH,
        ICON_192_PATH,
        ICON_512_PATH,
        MS_TILE_ICON_PATH,
    ]
    replacements = {
        "__CACHE_PREFIX__": json.dumps(PWA_CACHE_PREFIX),
        "__CACHE_REVISION__": json.dumps(_cache_revision(app_shell_revision_token)),
        "__APP_SHELL_CACHE_KEY__": json.dumps(APP_START_URL),
        "__APP_SHELL_PATHS__": json.dumps(["/", APP_START_URL]),
        "__PRECACHE_PATHS__": json.dumps(precache_paths),
        "__STATIC_PATHS__": json.dumps(static_paths),
    }
    worker = _SERVICE_WORKER_TEMPLATE
    for placeholder, value in replacements.items():
        worker = worker.replace(placeholder, value)
    return worker


SERVICE_WORKER_JS = build_service_worker()
PWA_SERVICE_WORKER = SERVICE_WORKER_JS

BROWSERCONFIG_XML = f"""<?xml version="1.0" encoding="utf-8"?>
<browserconfig>
  <msapplication>
    <tile>
      <square150x150logo src="{MS_TILE_ICON_PATH}"/>
      <square310x310logo src="{ICON_512_PATH}"/>
      <TileColor>{THEME_COLOR}</TileColor>
    </tile>
  </msapplication>
</browserconfig>
"""

PWA_HEAD_TAGS = f"""<link rel="manifest" href="{MANIFEST_PATH}">
<link rel="icon" href="{ICON_SVG_PATH}" type="image/svg+xml">
<link rel="icon" href="{ICON_32_PATH}" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="{APPLE_TOUCH_ICON_PATH}" sizes="180x180">
<link rel="mask-icon" href="{MASK_ICON_SVG_PATH}" color="{THEME_COLOR}">
<meta name="application-name" content="{APP_NAME}">
<meta name="theme-color" content="{THEME_COLOR}">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="{APP_SHORT_NAME}">
<meta name="msapplication-TileColor" content="{THEME_COLOR}">
<meta name="msapplication-config" content="{BROWSERCONFIG_PATH}">"""

PWA_REGISTRATION_JS = f"""(() => {{
  if (!("serviceWorker" in navigator) || !window.isSecureContext) return;
  window.addEventListener("load", () => {{
    navigator.serviceWorker.register({json.dumps(SERVICE_WORKER_PATH)}, {{
      scope: {json.dumps(APP_SCOPE)},
      updateViaCache: "none"
    }}).then((registration) => registration.update()).catch(() => {{}});
  }}, {{once: true}});
}})();"""

PWA_REGISTRATION_TAG = (
    '<script id="pwa-service-worker-registration">\n'
    + PWA_REGISTRATION_JS
    + "\n</script>"
)


def inject_pwa_markup(html: str) -> str:
    """Add metadata and registration without changing visible application UI."""

    result = html
    if f'href="{MANIFEST_PATH}"' not in result:
        head_index = result.lower().rfind("</head>")
        if head_index >= 0:
            result = result[:head_index] + PWA_HEAD_TAGS + "\n" + result[head_index:]
        else:
            result = PWA_HEAD_TAGS + "\n" + result

    if 'id="pwa-service-worker-registration"' not in result:
        body_index = result.lower().rfind("</body>")
        if body_index >= 0:
            result = result[:body_index] + PWA_REGISTRATION_TAG + "\n" + result[body_index:]
        else:
            result = result + "\n" + PWA_REGISTRATION_TAG
    return result


def _resource(
    path: str,
    body: str | bytes,
    content_type: str,
    cache_control: str,
    *extra_headers: tuple[str, str],
) -> PWAResource:
    content = body.encode("utf-8") if isinstance(body, str) else bytes(body)
    etag = '"' + hashlib.sha256(content).hexdigest() + '"'
    return PWAResource(path, content, content_type, cache_control, etag, extra_headers)


_SHORT_CACHE = "public, max-age=300, must-revalidate"
_ICON_CACHE = "public, max-age=604800, stale-while-revalidate=86400"
_SERVICE_WORKER_CACHE = "no-cache, no-store, must-revalidate"

PWA_RESOURCES: Mapping[str, PWAResource] = MappingProxyType(
    {
        MANIFEST_PATH: _resource(
            MANIFEST_PATH,
            MANIFEST_WEBMANIFEST,
            "application/manifest+json; charset=utf-8",
            _SHORT_CACHE,
        ),
        SERVICE_WORKER_PATH: _resource(
            SERVICE_WORKER_PATH,
            SERVICE_WORKER_JS,
            "text/javascript; charset=utf-8",
            _SERVICE_WORKER_CACHE,
            ("Service-Worker-Allowed", APP_SCOPE),
            ("Content-Security-Policy", "default-src 'none'; script-src 'self'; connect-src 'self'"),
            ("Pragma", "no-cache"),
            ("Expires", "0"),
        ),
        BROWSERCONFIG_PATH: _resource(
            BROWSERCONFIG_PATH,
            BROWSERCONFIG_XML,
            "application/xml; charset=utf-8",
            _SHORT_CACHE,
        ),
        ICON_SVG_PATH: _resource(
            ICON_SVG_PATH,
            APP_ICON_SVG,
            "image/svg+xml; charset=utf-8",
            _ICON_CACHE,
        ),
        MASK_ICON_SVG_PATH: _resource(
            MASK_ICON_SVG_PATH,
            SAFARI_MASK_ICON_SVG,
            "image/svg+xml; charset=utf-8",
            _ICON_CACHE,
        ),
        ICON_32_PATH: _resource(
            ICON_32_PATH,
            _ICON_PNGS[32],
            "image/png",
            _ICON_CACHE,
        ),
        APPLE_TOUCH_ICON_PATH: _resource(
            APPLE_TOUCH_ICON_PATH,
            _ICON_PNGS[180],
            "image/png",
            _ICON_CACHE,
        ),
        ICON_192_PATH: _resource(
            ICON_192_PATH,
            _ICON_PNGS[192],
            "image/png",
            _ICON_CACHE,
        ),
        ICON_512_PATH: _resource(
            ICON_512_PATH,
            _ICON_PNGS[512],
            "image/png",
            _ICON_CACHE,
        ),
        MS_TILE_ICON_PATH: _resource(
            MS_TILE_ICON_PATH,
            _ICON_PNGS[150],
            "image/png",
            _ICON_CACHE,
        ),
    }
)

PWA_RESOURCE_PATHS = frozenset(PWA_RESOURCES)


@lru_cache(maxsize=16)
def _versioned_service_worker_resource(app_shell_revision_token: str) -> PWAResource:
    return _resource(
        SERVICE_WORKER_PATH,
        build_service_worker(app_shell_revision_token),
        "text/javascript; charset=utf-8",
        _SERVICE_WORKER_CACHE,
        ("Service-Worker-Allowed", APP_SCOPE),
        ("Content-Security-Policy", "default-src 'none'; script-src 'self'; connect-src 'self'"),
        ("Pragma", "no-cache"),
        ("Expires", "0"),
    )


def get_pwa_resource(
    path: str,
    *,
    app_shell_revision_token: str | None = None,
) -> PWAResource | None:
    """Return an exact PWA resource; query strings are ignored for route lookup."""

    normalized_path = urlsplit(path).path
    if normalized_path == SERVICE_WORKER_PATH and app_shell_revision_token:
        return _versioned_service_worker_resource(str(app_shell_revision_token))
    return PWA_RESOURCES.get(normalized_path)


def get_pwa_asset(
    path: str,
    *,
    app_shell_revision_token: str | None = None,
) -> PWAResource | None:
    """Alias kept for callers that refer to all public files as assets."""

    return get_pwa_resource(
        path,
        app_shell_revision_token=app_shell_revision_token,
    )


def is_pwa_resource_path(path: str) -> bool:
    return urlsplit(path).path in PWA_RESOURCE_PATHS


def _etag_matches(header_value: str, etag: str) -> bool:
    for candidate in header_value.split(","):
        candidate = candidate.strip()
        if candidate == "*":
            return True
        if candidate.startswith("W/"):
            candidate = candidate[2:].strip()
        if candidate == etag:
            return True
    return False


def send_pwa_resource(
    handler: object,
    path: str | None = None,
    *,
    app_shell_revision_token: str | None = None,
    head_only: bool | None = None,
) -> bool:
    """Serve one resource through a ``BaseHTTPRequestHandler``-like object.

    Returns ``False`` when the path is not owned by this module.  ETag conditional
    requests and HEAD responses are handled here so the server integration stays
    small and consistent.
    """

    requested_path = path if path is not None else str(getattr(handler, "path", ""))
    resource = get_pwa_resource(
        requested_path,
        app_shell_revision_token=app_shell_revision_token,
    )
    if resource is None:
        return False

    request_headers = getattr(handler, "headers", {})
    if_none_match = request_headers.get("If-None-Match", "")
    not_modified = _etag_matches(if_none_match, resource.etag)

    handler.send_response(304 if not_modified else 200)
    headers = resource.response_headers()
    if not_modified:
        headers.pop("Content-Length", None)
    for header_name, header_value in headers.items():
        handler.send_header(header_name, header_value)
    handler.end_headers()

    should_send_body = not not_modified
    if head_only is None:
        should_send_body = should_send_body and getattr(handler, "command", "GET") != "HEAD"
    else:
        should_send_body = should_send_body and not head_only
    if should_send_body:
        handler.wfile.write(resource.body)
    return True


__all__ = [
    "APP_DESCRIPTION",
    "APP_NAME",
    "APP_SCOPE",
    "APP_SHORT_NAME",
    "APP_START_URL",
    "APPLE_TOUCH_ICON_PATH",
    "APP_ICON_SVG",
    "BACKGROUND_COLOR",
    "BROWSERCONFIG_PATH",
    "BROWSERCONFIG_XML",
    "ICON_192_PATH",
    "ICON_512_PATH",
    "ICON_SVG_PATH",
    "MANIFEST_PATH",
    "MANIFEST_WEBMANIFEST",
    "MS_TILE_ICON_PATH",
    "PWA_ASSET_REVISION",
    "PWA_HEAD_TAGS",
    "PWA_MANIFEST",
    "PWA_REGISTRATION_JS",
    "PWA_REGISTRATION_TAG",
    "PWA_RESOURCES",
    "PWA_RESOURCE_PATHS",
    "PWA_SERVICE_WORKER",
    "PWAResource",
    "SERVICE_WORKER_JS",
    "SERVICE_WORKER_PATH",
    "THEME_COLOR",
    "app_shell_revision",
    "build_manifest",
    "build_service_worker",
    "get_pwa_asset",
    "get_pwa_resource",
    "inject_pwa_markup",
    "is_pwa_resource_path",
    "render_icon_png",
    "send_pwa_resource",
]
