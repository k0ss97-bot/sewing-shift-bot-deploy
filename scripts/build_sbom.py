#!/usr/bin/env python3
"""Build a deterministic CycloneDX SBOM from the pinned Python requirements."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from urllib.parse import quote
import uuid


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REQUIREMENT_PATTERN = re.compile(
    r"^(?P<name>[A-Za-z0-9_.-]+)(?:\[(?P<extras>[A-Za-z0-9_,.-]+)\])?==(?P<version>[^\s;]+)$"
)


def _git(*arguments: str) -> str:
    process = subprocess.run(
        ["git", *arguments],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return process.stdout.strip()


def _timestamp() -> str:
    raw_epoch = os.environ.get("SOURCE_DATE_EPOCH")
    epoch = int(raw_epoch) if raw_epoch else int(_git("show", "-s", "--format=%ct", "HEAD"))
    return datetime.fromtimestamp(epoch, tz=timezone.utc).isoformat().replace("+00:00", "Z")


def _requirements(path: Path) -> list[dict[str, object]]:
    components: list[dict[str, object]] = []
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        match = REQUIREMENT_PATTERN.fullmatch(line)
        if match is None:
            raise ValueError(
                f"{path.name}:{line_number}: dependency must use one exact == version: {line!r}"
            )
        name = match.group("name")
        normalized = re.sub(r"[-_.]+", "-", name).lower()
        version = match.group("version")
        component: dict[str, object] = {
            "type": "library",
            "bom-ref": f"pkg:pypi/{quote(normalized)}@{quote(version)}",
            "name": name,
            "version": version,
            "purl": f"pkg:pypi/{quote(normalized)}@{quote(version)}",
        }
        extras = match.group("extras")
        if extras:
            component["properties"] = [
                {"name": "sewing:python:extras", "value": ",".join(sorted(extras.split(",")))}
            ]
        components.append(component)
    if not components:
        raise ValueError(f"{path.name}: no dependencies found")
    return sorted(components, key=lambda item: str(item["purl"]))


def build_sbom(requirements_path: Path | None = None) -> dict[str, object]:
    requirements = requirements_path or PROJECT_ROOT / "requirements.txt"
    requirements_digest = hashlib.sha256(requirements.read_bytes()).hexdigest()
    commit = _git("rev-parse", "HEAD")
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "serialNumber": f"urn:uuid:{uuid.uuid5(uuid.NAMESPACE_URL, requirements_digest)}",
        "version": 1,
        "metadata": {
            "timestamp": _timestamp(),
            "component": {
                "type": "application",
                "bom-ref": f"git:{commit}",
                "name": "sewing-shift-bot",
                "version": commit,
            },
            "properties": [
                {"name": "sewing:requirements:sha256", "value": requirements_digest}
            ],
        },
        "components": _requirements(requirements),
    }


def write_sbom(path: Path, payload: dict[str, object]) -> None:
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
    parser.add_argument("--requirements", type=Path, default=PROJECT_ROOT / "requirements.txt")
    arguments = parser.parse_args()
    payload = build_sbom(arguments.requirements)
    write_sbom(arguments.output, payload)
    print(f"CycloneDX SBOM: {arguments.output} components={len(payload['components'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
