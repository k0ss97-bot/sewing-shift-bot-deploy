#!/usr/bin/env python3
"""Compile project Python sources without writing bytecode into the checkout."""

from __future__ import annotations

import py_compile
import sys
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_DIRECTORIES = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".tox",
    ".venv",
    ".vendor",
    ".web-demo-data",
    "__pycache__",
    "build",
    "dist",
    "venv",
}


def python_sources() -> list[Path]:
    sources = []

    for path in PROJECT_ROOT.rglob("*.py"):
        relative_path = path.relative_to(PROJECT_ROOT)
        if any(part in EXCLUDED_DIRECTORIES for part in relative_path.parts):
            continue
        sources.append(path)

    return sorted(sources)


def main() -> int:
    sources = python_sources()
    if not sources:
        print("Compile audit failed: no Python sources found.", file=sys.stderr)
        return 1

    failures = []

    with tempfile.TemporaryDirectory(prefix="sewing-python-compile-") as cache_dir:
        cache_root = Path(cache_dir)

        for source in sources:
            relative_path = source.relative_to(PROJECT_ROOT)
            bytecode_path = (cache_root / relative_path).with_suffix(".pyc")
            bytecode_path.parent.mkdir(parents=True, exist_ok=True)

            try:
                py_compile.compile(
                    str(source),
                    cfile=str(bytecode_path),
                    dfile=str(relative_path),
                    doraise=True,
                )
            except (OSError, py_compile.PyCompileError) as error:
                failures.append(f"{relative_path}: {error}")

    if failures:
        print("Compile audit failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print(f"Compile audit passed: {len(sources)} Python files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
