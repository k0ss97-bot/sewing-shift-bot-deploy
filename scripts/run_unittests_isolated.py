#!/usr/bin/env python3
"""Run unittest discovery from an empty directory with a disposable DB_DIR."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="sewing-unittest-") as temporary_dir:
        isolated_root = Path(temporary_dir).resolve()
        working_directory = isolated_root / "cwd"
        database_directory = isolated_root / "database"
        working_directory.mkdir()
        database_directory.mkdir()

        environment = os.environ.copy()
        environment["DB_DIR"] = str(database_directory)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        environment.pop("SHARED_DIR", None)

        existing_python_path = environment.get("PYTHONPATH", "")
        environment["PYTHONPATH"] = os.pathsep.join(
            part for part in (str(PROJECT_ROOT), existing_python_path) if part
        )

        command = [
            sys.executable,
            "-m",
            "unittest",
            "discover",
            "-s",
            str(PROJECT_ROOT),
            "-t",
            str(PROJECT_ROOT),
            "-p",
            "test*.py",
            "-v",
        ]
        completed = subprocess.run(
            command,
            cwd=working_directory,
            env=environment,
            check=False,
        )
        return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
