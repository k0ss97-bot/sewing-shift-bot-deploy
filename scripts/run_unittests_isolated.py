#!/usr/bin/env python3
"""Run every unittest from an empty directory with disposable data stores.

The repository historically kept tests both in the project root and in the
``tests/`` namespace directory.  Plain ``unittest discover`` did not recurse
into that namespace and silently omitted a large part of the suite.  This
runner imports every matching module explicitly, de-duplicates compatibility
aliases by test id and prints a machine-readable discovery report.

Production PostgreSQL configuration is never inherited.  DB-backed WMS tests
run only when ``TEST_WMS_DATABASE_URL`` names an explicitly test database;
otherwise they target the conventional loopback ``wms_test`` database and are
cleanly skipped when it is unavailable.
"""

from __future__ import annotations

import ast
import importlib
import os
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEST_WMS_URL = "postgresql://wms:wms@127.0.0.1:5432/wms_test"
CHILD_FLAG = "--isolated-child"


def _test_files() -> list[Path]:
    files = list(PROJECT_ROOT.glob("test*.py"))
    files.extend((PROJECT_ROOT / "tests").glob("test*.py"))
    return sorted(files)


def _module_name(path: Path) -> str:
    relative = path.relative_to(PROJECT_ROOT).with_suffix("")
    return ".".join(relative.parts)


def _declared_test_count(path: Path) -> int:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return sum(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.startswith("test")
        for node in ast.walk(tree)
    )


def _flatten(suite: unittest.TestSuite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from _flatten(item)
        else:
            yield item


def _safe_test_wms_url() -> str:
    value = (os.environ.get("TEST_WMS_DATABASE_URL") or "").strip()
    if not value:
        return DEFAULT_TEST_WMS_URL
    parsed = urlparse(value)
    database_name = parsed.path.rsplit("/", 1)[-1].lower()
    if parsed.scheme not in {"postgres", "postgresql"} or "test" not in database_name:
        raise RuntimeError(
            "TEST_WMS_DATABASE_URL must be a PostgreSQL URL whose database name contains 'test'."
        )
    return value


def _isolated_child() -> int:
    loader = unittest.TestLoader()
    unique_tests: dict[str, unittest.TestCase] = {}
    duplicate_ids: list[str] = []
    import_errors: list[tuple[str, int, str]] = []

    for path in _test_files():
        module_name = _module_name(path)
        try:
            module = importlib.import_module(module_name)
            loaded = loader.loadTestsFromModule(module)
        except Exception as error:  # pragma: no cover - reported as a hard runner failure
            import_errors.append((module_name, _declared_test_count(path), repr(error)))
            continue
        for test in _flatten(loaded):
            test_id = test.id()
            if test_id in unique_tests:
                duplicate_ids.append(test_id)
                continue
            unique_tests[test_id] = test

    suite = unittest.TestSuite(unique_tests.values())
    result = unittest.TextTestRunner(verbosity=2).run(suite)

    skipped = len(result.skipped)
    failed = len(result.failures) + len(result.errors) + len(result.unexpectedSuccesses)
    expected_failures = len(result.expectedFailures)
    executed = result.testsRun - skipped
    passed = executed - failed - expected_failures
    excluded = sum(count for _, count, _ in import_errors)
    discovered = len(unique_tests) + excluded

    print("\nTEST_DISCOVERY_REPORT")
    print(f"files={len(_test_files())}")
    print(f"discovered={discovered}")
    print(f"executed={executed}")
    print(f"passed={passed}")
    print(f"failed={failed}")
    print(f"skipped={skipped}")
    print(f"excluded={excluded}")
    print(f"duplicate_aliases_ignored={len(duplicate_ids)}")

    if result.skipped:
        reasons = Counter(reason for _, reason in result.skipped)
        for reason, count in sorted(reasons.items()):
            print(f"skip_reason[{count}]={reason}")
    for module_name, count, error in import_errors:
        print(f"exclude_reason[{module_name};tests={count}]={error}")

    return 0 if result.wasSuccessful() and not import_errors else 1


def main() -> int:
    if CHILD_FLAG in sys.argv:
        return _isolated_child()

    try:
        test_wms_url = _safe_test_wms_url()
    except RuntimeError as error:
        print(f"Test isolation error: {error}", file=sys.stderr)
        return 2

    with tempfile.TemporaryDirectory(prefix="sewing-unittest-") as temporary_dir:
        isolated_root = Path(temporary_dir).resolve()
        working_directory = isolated_root / "cwd"
        database_directory = isolated_root / "database"
        working_directory.mkdir()
        database_directory.mkdir()

        environment = os.environ.copy()
        environment["DB_DIR"] = str(database_directory)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        environment["RUN_HTTP_TESTS"] = "1"
        environment["WMS_DATABASE_URL"] = test_wms_url
        environment.pop("DATABASE_URL", None)
        environment.pop("MARKETPLACE_DATABASE_URL", None)
        environment.pop("SHARED_DIR", None)

        existing_python_path = environment.get("PYTHONPATH", "")
        environment["PYTHONPATH"] = os.pathsep.join(
            part for part in (str(PROJECT_ROOT), existing_python_path) if part
        )

        completed = subprocess.run(
            [sys.executable, str(Path(__file__).resolve()), CHILD_FLAG],
            cwd=working_directory,
            env=environment,
            check=False,
        )
        return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
