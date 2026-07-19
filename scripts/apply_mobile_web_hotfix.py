#!/usr/bin/env python3
"""Apply the narrow production hotfix for mobile loading and web auth origin."""

from __future__ import annotations

import os
import shutil
from datetime import datetime, timezone
from pathlib import Path


ENV_PATH = Path("/etc/sewing-web/sewing-web.env")
ASSETS_PATH = Path("/opt/sewing-web/current/miniapp_assets.py")
CADDY_PATH = Path("/etc/caddy/Caddyfile")
BACKUP_ROOT = Path("/var/lib/sewing-web/backups")

OLD_TELEGRAM_SCRIPT = '  <script src="https://telegram.org/js/telegram-web-app.js"></script>'
NEW_TELEGRAM_LOADER = r'''  <script>
    (() => {
      const launchUrl = `${window.location.search}&${window.location.hash}`;
      const isTelegramLaunch = /(?:^|[?&#])tgWebApp(?:Data|Version|Platform)=/.test(launchUrl);
      if (isTelegramLaunch) {
        document.write('<script src="https://telegram.org/js/telegram-web-app.js"><\/script>');
      }
    })();
  </script>'''

CADDY_CONFIG = '''{
    servers {
        protocols h1 h2
    }
}

www.shagaemfabrika.ru {
    encode zstd gzip

    header {
        -Server
        Alt-Svc "clear"
        Strict-Transport-Security "max-age=31536000; includeSubDomains"
        X-Content-Type-Options "nosniff"
        Referrer-Policy "same-origin"
    }

    reverse_proxy 127.0.0.1:3000
}

shagaemfabrika.ru {
    redir https://www.shagaemfabrika.ru{uri} permanent
}

sewing.161-104-33-59.sslip.io {
    redir https://www.shagaemfabrika.ru{uri} permanent
}
'''


def atomic_write(path: Path, content: str) -> None:
    stat = path.stat()
    temporary = path.with_name(f".{path.name}.mobile-hotfix.tmp")
    temporary.write_text(content, encoding="utf-8")
    os.chmod(temporary, stat.st_mode)
    os.chown(temporary, stat.st_uid, stat.st_gid)
    os.replace(temporary, path)


def updated_environment(content: str) -> str:
    lines = content.splitlines()
    matches = [index for index, line in enumerate(lines) if line.startswith("WEBAPP_PUBLIC_ORIGIN=")]
    if len(matches) != 1:
        raise RuntimeError("Expected exactly one WEBAPP_PUBLIC_ORIGIN setting")
    lines[matches[0]] = "WEBAPP_PUBLIC_ORIGIN=https://www.shagaemfabrika.ru"
    return "\n".join(lines) + "\n"


def updated_assets(content: str) -> str:
    if NEW_TELEGRAM_LOADER in content:
        return content
    if content.count(OLD_TELEGRAM_SCRIPT) != 1:
        raise RuntimeError("Telegram SDK marker does not match the production file")
    return content.replace(OLD_TELEGRAM_SCRIPT, NEW_TELEGRAM_LOADER)


def main() -> None:
    if os.geteuid() != 0:
        raise SystemExit("Run this hotfix as root")

    environment = updated_environment(ENV_PATH.read_text(encoding="utf-8"))
    assets = updated_assets(ASSETS_PATH.read_text(encoding="utf-8"))

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_dir = BACKUP_ROOT / f"mobile-web-hotfix-{timestamp}"
    backup_dir.mkdir(parents=True, exist_ok=False)
    shutil.copy2(ENV_PATH, backup_dir / ENV_PATH.name)
    shutil.copy2(ASSETS_PATH, backup_dir / ASSETS_PATH.name)
    shutil.copy2(CADDY_PATH, backup_dir / CADDY_PATH.name)

    atomic_write(ENV_PATH, environment)
    atomic_write(ASSETS_PATH, assets)
    atomic_write(CADDY_PATH, CADDY_CONFIG)
    print(f"Hotfix applied; backup: {backup_dir}")


if __name__ == "__main__":
    main()
