"""Versioned Mini App assets loaded from independently reviewable source files."""

from __future__ import annotations

import hashlib
from pathlib import Path


_ASSET_DIR = Path(__file__).resolve().parent / "assets" / "app"
_SHELL_TEMPLATE = (_ASSET_DIR / "shell.html").read_text(encoding="utf-8")
MINIAPP_CSS = (_ASSET_DIR / "app.css").read_text(encoding="utf-8")
MINIAPP_JS = (_ASSET_DIR / "app.js").read_text(encoding="utf-8")

MINIAPP_CSS_PATH = f"/assets/app-{hashlib.sha256(MINIAPP_CSS.encode('utf-8')).hexdigest()[:16]}.css"
MINIAPP_JS_PATH = f"/assets/app-{hashlib.sha256(MINIAPP_JS.encode('utf-8')).hexdigest()[:16]}.js"
MINIAPP_SHELL_HTML = (
    _SHELL_TEMPLATE
    .replace("{{MINIAPP_CSS_PATH}}", MINIAPP_CSS_PATH)
    .replace("{{MINIAPP_JS_PATH}}", MINIAPP_JS_PATH)
)

# Compatibility contract for tests and narrow tools that inspect the historical
# combined document. The HTTP server uses MINIAPP_SHELL_HTML and never serves
# this combined value.
MINIAPP_HTML = (
    MINIAPP_SHELL_HTML
    .replace(
        f'<link rel="stylesheet" href="{MINIAPP_CSS_PATH}">',
        f"<style>{MINIAPP_CSS}</style>",
        1,
    )
    .replace(
        f'<script src="{MINIAPP_JS_PATH}" defer></script>',
        f"<script>{MINIAPP_JS}</script>",
        1,
    )
)
