from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta
import unittest
from zoneinfo import ZoneInfo

from production_wms_reconciliation import (
    analyse_reconciliation,
    run_production_wms_reconciliation,
)


def outbox_entry(**overrides):
    row = {
        "id": 1,
        "request_key": "production:route-batch:10",
        "route_batch_id": 10,
        "item_type": "finished",
        "product_name": "Футболки",
        "product_size": "116",
        "product_color": "Черный",
        "stage_name": "Упаковано",
        "ready_for_position": "Склад",
        "quantity": 5,
        "status": "sent",
        "attempts": 1,
        "created_at": "2026-08-07T10:00:00+05:00",
        "last_error": "",
    }
    row.update(overrides)
    return row


def movement_entry(**overrides):
    row = {
        "id": 50,
        "request_key": "production:route-batch:10",
        "source_id": 10,
        "product_key": {
            "item_type": "finished",
            "product_name": "Футболки",
            "product_size": "116",
            "product_color": "Черный",
            "stage_name": "Упаковано",
            "ready_for_position": "Склад",
        },
        "quantity": 5,
    }
    row.update(overrides)
    return row


class FakePgCursor:
    def __init__(self, movements, invalid_stock):
        self.movements = movements
        self.invalid_stock = invalid_stock
        self.rows = []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def execute(self, sql, _params=None):
        self.rows = self.movements if "FROM wms_movements" in sql else self.invalid_stock

    def fetchall(self):
        return self.rows


class FakePgConnection:
    def __init__(self, movements, invalid_stock=None):
        self.movements = movements
        self.invalid_stock = invalid_stock or []
        self.rolled_back = False

    def cursor(self):
        return FakePgCursor(self.movements, self.invalid_stock)

    def rollback(self):
        self.rolled_back = True


class ProductionWmsReconciliationTests(unittest.TestCase):
    def test_matching_outbox_and_receipt_are_healthy(self):
        report = analyse_reconciliation(
            outbox_entries=[outbox_entry()],
            packaging_without_outbox=[],
            movements=[movement_entry()],
            negative_sqlite_stock=[],
            invalid_wms_stock=[],
            now=datetime(2026, 8, 7, 12, 0, tzinfo=ZoneInfo("Asia/Yekaterinburg")),
        )
        self.assertTrue(report["ok"])
        self.assertEqual(report["issue_count"], 0)
        self.assertTrue(all(value == 0 for value in report["summary"].values()))

    def test_mismatches_and_stuck_event_are_reported_separately(self):
        now = datetime(2026, 8, 7, 12, 0, tzinfo=ZoneInfo("Asia/Yekaterinburg"))
        report = analyse_reconciliation(
            outbox_entries=[
                outbox_entry(
                    status="failed",
                    attempts=3,
                    created_at=(now - timedelta(hours=2)).isoformat(),
                    last_error="RuntimeError",
                )
            ],
            packaging_without_outbox=[{"route_batch_id": 11}],
            movements=[
                movement_entry(
                    quantity=4,
                    source_id=99,
                    product_key={**movement_entry()["product_key"], "product_color": "Белый"},
                ),
                movement_entry(id=51),
                movement_entry(id=60, request_key="production:route-batch:60", source_id=60),
            ],
            negative_sqlite_stock=[{"id": 2, "quantity": -1}],
            invalid_wms_stock=[{"id": 3, "quantity": 2, "reserved_quantity": 4}],
            now=now,
        )
        self.assertFalse(report["ok"])
        for key in (
            "packaging_without_outbox",
            "receipt_without_outbox",
            "duplicate_request_keys",
            "product_key_mismatch",
            "quantity_mismatch",
            "source_mismatch",
            "invalid_sqlite_stock",
            "invalid_wms_stock",
            "stuck_outbox",
        ):
            self.assertGreater(report["summary"][key], 0, key)

    def test_full_run_journals_report_and_never_commits_postgres(self):
        sqlite_conn = sqlite3.connect(":memory:")
        sqlite_conn.executescript(
            """
            CREATE TABLE wms_receipt_outbox (
                id INTEGER PRIMARY KEY, request_key TEXT, route_batch_id INTEGER,
                item_type TEXT, product_name TEXT, product_size TEXT,
                product_color TEXT, stage_name TEXT, ready_for_position TEXT,
                quantity INTEGER, status TEXT, attempts INTEGER,
                created_at TEXT, last_error TEXT
            );
            CREATE TABLE route_batches (
                id INTEGER PRIMARY KEY, product_name TEXT, product_size TEXT,
                product_color TEXT, good_quantity INTEGER, status TEXT
            );
            CREATE TABLE route_batch_history (
                batch_id INTEGER, operation_name TEXT, completed_at TEXT
            );
            CREATE TABLE warehouse_stock (
                id INTEGER PRIMARY KEY, item_type TEXT, product_name TEXT,
                product_size TEXT, product_color TEXT, stage_name TEXT,
                ready_for_position TEXT, quantity INTEGER
            );
            CREATE TABLE production_wms_reconciliation_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT, status TEXT, issue_count INTEGER,
                summary_json TEXT, details_json TEXT, error TEXT,
                started_at TEXT, finished_at TEXT
            );
            """
        )
        entry = outbox_entry()
        sqlite_conn.execute(
            """
            INSERT INTO wms_receipt_outbox VALUES (
                :id,:request_key,:route_batch_id,:item_type,:product_name,
                :product_size,:product_color,:stage_name,:ready_for_position,
                :quantity,:status,:attempts,:created_at,:last_error
            )
            """,
            entry,
        )
        sqlite_conn.commit()
        pg_conn = FakePgConnection([movement_entry()])

        report = run_production_wms_reconciliation(
            sqlite_conn=sqlite_conn,
            pg_conn=pg_conn,
        )

        self.assertTrue(report["ok"])
        self.assertTrue(pg_conn.rolled_back)
        row = sqlite_conn.execute(
            "SELECT status, issue_count FROM production_wms_reconciliation_runs"
        ).fetchone()
        self.assertEqual(tuple(row), ("ok", 0))


if __name__ == "__main__":
    unittest.main()
