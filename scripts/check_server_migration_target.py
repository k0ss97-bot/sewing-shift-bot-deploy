#!/usr/bin/env python3
"""Fail-closed readiness check for a replacement production server.

The checker intentionally does not read environment files, database contents,
tokens, employee data, uploads, or backup artifacts.  It only inspects host
capacity, installed command versions, release identifiers, service state,
loopback health endpoints, and the PostgreSQL listen address.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from typing import Any, Mapping
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


GIB = 1024**3
MIN_CPU = 4
MIN_MEMORY_BYTES = 8 * GIB
MIN_DISK_BYTES = 120 * GIB
MIN_FREE_DISK_BYTES = 80 * GIB

REQUIRED_SERVICES = (
    "caddy.service",
    "postgresql@16-main.service",
    "sewing-web.service",
    "team-messenger.service",
)

REQUIRED_TIMERS = (
    "sewing-marketplaces-sync.timer",
    "sewing-production-wms-reconcile.timer",
    "sewing-web-backup.timer",
    "sewing-web-healthcheck.timer",
    "sewing-web-monitor.timer",
    "sewing-wms-backup.timer",
    "team-messenger-backup.timer",
    "team-messenger-sync.timer",
)

ALLOWED_PUBLIC_TCP_PORTS = {22, 80, 443}


def _run(*arguments: str) -> str:
    try:
        completed = subprocess.run(
            arguments,
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    if completed.returncode != 0:
        return ""
    return completed.stdout.strip()


def _read_first_line(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8").splitlines()[0].strip()
    except (OSError, IndexError, UnicodeError):
        return ""


def _memory_bytes() -> int:
    try:
        for line in Path("/proc/meminfo").read_text(encoding="utf-8").splitlines():
            if line.startswith("MemTotal:"):
                return int(line.split()[1]) * 1024
    except (OSError, ValueError, IndexError):
        pass
    return 0


def _os_release() -> dict[str, str]:
    result: dict[str, str] = {}
    try:
        lines = Path("/etc/os-release").read_text(encoding="utf-8").splitlines()
    except OSError:
        return result
    for line in lines:
        if "=" not in line or line.startswith("#"):
            continue
        key, value = line.split("=", 1)
        result[key] = value.strip().strip('"')
    return result


def _http_status(url: str) -> int:
    try:
        with urlopen(url, timeout=5) as response:
            response.read(1)
            return int(response.status)
    except HTTPError as error:
        return int(error.code)
    except (URLError, OSError, ValueError):
        return 0


def _service_state(unit: str) -> dict[str, str]:
    def query(action: str) -> str:
        try:
            completed = subprocess.run(
                ["systemctl", action, unit],
                check=False,
                capture_output=True,
                text=True,
                timeout=10,
            )
        except (OSError, subprocess.TimeoutExpired):
            return ""
        # systemctl intentionally returns a non-zero status for useful states
        # such as inactive, disabled and failed. Preserve the safe state name.
        return completed.stdout.strip()

    return {
        "active": query("is-active"),
        "enabled": query("is-enabled"),
    }


def _release_commit(current_path: Path) -> str:
    commit = _read_first_line(current_path / "COMMIT")
    if commit:
        return commit
    try:
        target_name = current_path.resolve(strict=True).name
    except OSError:
        return ""
    match = re.search(r"(?:^|[-_])([0-9a-f]{7,40})(?:$|[-_])", target_name)
    return match.group(1) if match else ""


def collect_snapshot() -> dict[str, Any]:
    disk = shutil.disk_usage("/")
    os_release = _os_release()
    services = {unit: _service_state(unit) for unit in REQUIRED_SERVICES}
    timers = {unit: _service_state(unit) for unit in REQUIRED_TIMERS}
    tcp_listeners = _run("ss", "-ltnH").splitlines()
    postgres_listeners = [line for line in tcp_listeners if re.search(r":5432\s", line)]
    return {
        "cpu_count": int(os.cpu_count() or 0),
        "memory_bytes": _memory_bytes(),
        "disk_total_bytes": int(disk.total),
        "disk_free_bytes": int(disk.free),
        "os_id": os_release.get("ID", ""),
        "os_version": os_release.get("VERSION_ID", ""),
        "ntp_synchronized": _run("timedatectl", "show", "-p", "NTPSynchronized", "--value"),
        "commands": {
            "python3": _run("python3", "--version"),
            "psql": _run("psql", "--version"),
            "caddy": _run("caddy", "version"),
        },
        "release_commits": {
            "sewing": _release_commit(Path("/opt/sewing-web/current")),
            "messenger": _release_commit(Path("/opt/shagaem-team-messenger")),
        },
        "data_paths": {
            "sewing": Path("/var/lib/sewing-web").is_dir(),
            "messenger": Path("/var/lib/shagaem-team-messenger").is_dir(),
        },
        "services": services,
        "timers": timers,
        "health": {
            "sewing": _http_status("http://127.0.0.1:3000/health"),
            "messenger": _http_status("http://127.0.0.1:3100/health"),
        },
        "postgres_listeners": postgres_listeners,
        "tcp_listeners": tcp_listeners,
        "optional": {
            "hermes_timer": _service_state("hermes-daily-report.timer"),
            "hermes_service": _service_state("hermes-daily-report.service"),
            "n8n_service": _service_state("n8n.service"),
        },
    }


def _commit_matches(actual: str, expected: str) -> bool:
    if not actual or not expected:
        return False
    return actual == expected or actual.startswith(expected) or expected.startswith(actual)


def _unexpected_public_ports(listeners: list[str]) -> list[int]:
    unexpected: set[int] = set()
    for listener in listeners:
        fields = str(listener).split()
        if len(fields) < 4:
            continue
        local = fields[3]
        try:
            host, port_text = local.rsplit(":", 1)
            port = int(port_text)
        except (ValueError, IndexError):
            continue
        host = host.strip("[]")
        if host.startswith("127.") or host in {"::1", "localhost"}:
            continue
        if port not in ALLOWED_PUBLIC_TCP_PORTS:
            unexpected.add(port)
    return sorted(unexpected)


def evaluate_snapshot(
    snapshot: Mapping[str, Any],
    *,
    phase: str,
    expected_sewing_commit: str = "",
    expected_messenger_commit: str = "",
    include_hermes: bool = False,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    if int(snapshot.get("cpu_count") or 0) < MIN_CPU:
        errors.append(f"Нужно не менее {MIN_CPU} vCPU")
    if int(snapshot.get("memory_bytes") or 0) < MIN_MEMORY_BYTES:
        errors.append("Нужно не менее 8 GiB RAM")
    if int(snapshot.get("disk_total_bytes") or 0) < MIN_DISK_BYTES:
        errors.append("Нужен диск не менее 120 GiB")
    if int(snapshot.get("disk_free_bytes") or 0) < MIN_FREE_DISK_BYTES:
        errors.append("Перед восстановлением нужно не менее 80 GiB свободного места")
    if snapshot.get("os_id") != "ubuntu" or not str(snapshot.get("os_version") or "").startswith("24.04"):
        errors.append("Поддерживаемая целевая ОС: Ubuntu 24.04 LTS")
    if str(snapshot.get("ntp_synchronized") or "").lower() != "yes":
        errors.append("Синхронизация времени NTP не подтверждена")

    commands = snapshot.get("commands") or {}
    if not str(commands.get("python3") or "").startswith("Python 3.12"):
        errors.append("Не найден Python 3.12")
    if "PostgreSQL) 16" not in str(commands.get("psql") or ""):
        errors.append("Не найден PostgreSQL client 16")
    if not commands.get("caddy"):
        errors.append("Не найден Caddy")

    if phase in {"restored", "running"}:
        data_paths = snapshot.get("data_paths") or {}
        if data_paths.get("sewing") is not True:
            errors.append("Не подготовлен /var/lib/sewing-web")
        if data_paths.get("messenger") is not True:
            errors.append("Не подготовлен /var/lib/shagaem-team-messenger")
        commits = snapshot.get("release_commits") or {}
        if not _commit_matches(str(commits.get("sewing") or ""), expected_sewing_commit):
            errors.append("Не совпадает commit производственного сайта")
        if not _commit_matches(str(commits.get("messenger") or ""), expected_messenger_commit):
            errors.append("Не совпадает commit мессенджера")

    if phase == "running":
        services = snapshot.get("services") or {}
        for unit in REQUIRED_SERVICES:
            if (services.get(unit) or {}).get("active") != "active":
                errors.append(f"Сервис не active: {unit}")
        timers = snapshot.get("timers") or {}
        for unit in REQUIRED_TIMERS:
            state = timers.get(unit) or {}
            if state.get("active") != "active" or state.get("enabled") not in {"enabled", "enabled-runtime"}:
                errors.append(f"Таймер не active/enabled: {unit}")
        health = snapshot.get("health") or {}
        if health.get("sewing") != 200:
            errors.append("Основной health не вернул HTTP 200")
        if health.get("messenger") != 200:
            errors.append("Messenger health не вернул HTTP 200")

    for listener in snapshot.get("postgres_listeners") or []:
        if re.search(r"(?:0\.0\.0\.0|\[::\]|\*):5432\b", str(listener)):
            errors.append("PostgreSQL слушает публичный интерфейс")
            break

    unexpected_ports = _unexpected_public_ports(list(snapshot.get("tcp_listeners") or []))
    if unexpected_ports:
        errors.append(
            "На публичных интерфейсах есть лишние TCP-порты: "
            + ", ".join(str(port) for port in unexpected_ports)
        )

    optional = snapshot.get("optional") or {}
    if include_hermes:
        hermes_timer = optional.get("hermes_timer") or {}
        hermes_service = optional.get("hermes_service") or {}
        if hermes_timer.get("active") != "active" or hermes_timer.get("enabled") not in {"enabled", "enabled-runtime"}:
            errors.append("Hermes timer не active/enabled")
        if hermes_service.get("active") == "failed":
            errors.append("Hermes service находится в failed")
    elif (optional.get("hermes_service") or {}).get("active") == "failed":
        warnings.append("Hermes service находится в failed и не включён в обязательный gate")
    if (optional.get("n8n_service") or {}).get("active") != "active":
        warnings.append("n8n пока не установлен или не запущен; это не блокирует перенос текущих сервисов")

    return {
        "ready": not errors,
        "phase": phase,
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("bootstrap", "restored", "running"), default="bootstrap")
    parser.add_argument("--expected-sewing-commit", default="")
    parser.add_argument("--expected-messenger-commit", default="")
    parser.add_argument("--include-hermes", action="store_true")
    parser.add_argument("--output", choices=("text", "json"), default="text")
    arguments = parser.parse_args()

    if arguments.phase != "bootstrap" and (
        not arguments.expected_sewing_commit or not arguments.expected_messenger_commit
    ):
        parser.error("restored/running require both expected commit arguments")

    snapshot = collect_snapshot()
    report = evaluate_snapshot(
        snapshot,
        phase=arguments.phase,
        expected_sewing_commit=arguments.expected_sewing_commit,
        expected_messenger_commit=arguments.expected_messenger_commit,
        include_hermes=arguments.include_hermes,
    )
    payload = {"snapshot": snapshot, "report": report}
    if arguments.output == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"Migration target: {'READY' if report['ready'] else 'BLOCKED'} ({arguments.phase})")
        for item in report["errors"]:
            print(f"ERROR: {item}")
        for item in report["warnings"]:
            print(f"WARNING: {item}")
    return 0 if report["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
