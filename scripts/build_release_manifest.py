#!/usr/bin/env python3
"""Build non-secret release metadata for deployment and incident recovery."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FEATURE_FLAGS = {
    "marketplace_phase1a": ("MARKETPLACE_PHASE1A_ENABLED", False),
    "warehouse_auto_receipt": ("WMS_AUTO_RECEIPT_ENABLED", True),
    "warehouse_ui_v2": ("WAREHOUSE_UI_V2", True),
}
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")


def _git(*arguments: str) -> str:
    process = subprocess.run(
        ["git", *arguments],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return process.stdout.strip()


def _release_identity() -> dict[str, object]:
    try:
        return {
            "commit": _git("rev-parse", "HEAD"),
            "branch": _git("branch", "--show-current") or "detached",
            "dirty": bool(_git("status", "--porcelain")),
        }
    except (FileNotFoundError, subprocess.CalledProcessError):
        commit_file = PROJECT_ROOT / "COMMIT"
        if not commit_file.is_file():
            raise RuntimeError("release identity is unavailable: no Git checkout or COMMIT file")
        commit = commit_file.read_text(encoding="utf-8").strip()
        if COMMIT_PATTERN.fullmatch(commit) is None:
            raise RuntimeError("release COMMIT file must contain a full lowercase Git commit SHA")
        return {"commit": commit, "branch": "release", "dirty": False}


def _enabled(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _test_report(path: Path | None) -> dict | None:
    if path is None:
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    allowed = {"discovered", "executed", "passed", "failed", "skipped", "skip_gate"}
    return {key: payload[key] for key in allowed if key in payload}


def _material(path: Path) -> dict[str, object]:
    return {
        "path": path.relative_to(PROJECT_ROOT).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": _sha256(path),
    }


def _sbom(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("bomFormat") != "CycloneDX" or payload.get("specVersion") != "1.5":
        raise ValueError("release SBOM must be CycloneDX 1.5 JSON")
    components = payload.get("components")
    if not isinstance(components, list) or not components:
        raise ValueError("release SBOM does not contain components")
    return {
        "filename": path.name,
        "format": "CycloneDX",
        "spec_version": "1.5",
        "components": len(components),
        "bytes": path.stat().st_size,
        "sha256": _sha256(path),
    }


def _provenance() -> dict[str, str] | None:
    allowed = {
        "repository": "GITHUB_REPOSITORY",
        "workflow": "GITHUB_WORKFLOW",
        "run_id": "GITHUB_RUN_ID",
        "run_attempt": "GITHUB_RUN_ATTEMPT",
        "event": "GITHUB_EVENT_NAME",
        "ref": "GITHUB_REF",
        "sha": "GITHUB_SHA",
    }
    values = {label: os.environ[name] for label, name in allowed.items() if os.environ.get(name)}
    return values or None


def build_manifest(*, sbom_path: Path, test_report_path: Path | None = None) -> dict:
    migrations = []
    for path in sorted((PROJECT_ROOT / "wms_migrations").glob("*.sql")):
        migrations.append({"filename": path.name, "sha256": _sha256(path)})
    frontend = {}
    for name in ("shell.html", "app.css", "app.js"):
        path = PROJECT_ROOT / "assets" / "app" / name
        frontend[name] = {"bytes": path.stat().st_size, "sha256": _sha256(path)}
    materials = [
        _material(PROJECT_ROOT / "requirements.txt"),
        _material(PROJECT_ROOT / ".github" / "workflows" / "quality.yml"),
    ]
    release_inputs = {
        "materials": materials,
        "migrations": migrations,
        "frontend": frontend,
    }
    release_inputs_sha256 = hashlib.sha256(
        json.dumps(release_inputs, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return {
        "schema_version": 2,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git": _release_identity(),
        "runtime": {"python": platform.python_version()},
        "provenance": _provenance(),
        "release_inputs_sha256": release_inputs_sha256,
        "materials": materials,
        "sbom": _sbom(sbom_path),
        "feature_flags": {
            label: _enabled(environment_name, default)
            for label, (environment_name, default) in FEATURE_FLAGS.items()
        },
        "migrations": migrations,
        "frontend": frontend,
        "tests": _test_report(test_report_path),
    }


def write_manifest(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--sbom", type=Path, required=True)
    parser.add_argument("--test-report", type=Path)
    arguments = parser.parse_args()
    payload = build_manifest(sbom_path=arguments.sbom, test_report_path=arguments.test_report)
    write_manifest(arguments.output, payload)
    print(
        f"Release manifest: {arguments.output} commit={payload['git']['commit'][:12]} "
        f"migrations={len(payload['migrations'])} dirty={payload['git']['dirty']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
