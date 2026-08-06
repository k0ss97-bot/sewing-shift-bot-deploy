from datetime import datetime, timezone
import unittest

from miniapp_server import finished_goods_plan_quantity
from wms import repository


class _Cursor:
    def __init__(self, rows):
        self.rows = rows
        self.sql = ""
        self.params = ()

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def execute(self, sql, params):
        self.sql = sql
        self.params = params

    def fetchall(self):
        return self.rows


class _Connection:
    def __init__(self, rows):
        self.cursor_value = _Cursor(rows)

    def cursor(self):
        return self.cursor_value


class ProductionAnalyticsTests(unittest.TestCase):
    def test_plan_counts_finished_task_items_once_not_route_operations(self):
        rows = [
            (1, "Костюм", "active", "2026-08-06T09:00:00", None, "98", "бежевый", 12, 10),
            (1, "Костюм", "active", "2026-08-06T09:00:00", None, "104", "бежевый", 8, 8),
            (2, "Отмена", "cancelled", "2026-08-06T10:00:00", None, "98", "чёрный", 100, 0),
            (3, "Старое", "active", "2026-08-01T10:00:00", None, "98", "чёрный", 50, 0),
        ]

        self.assertEqual(finished_goods_plan_quantity(rows, "2026-08-06", "2026-08-06"), 20)

    def test_fact_query_requires_finished_production_receipt_in_receive_zone(self):
        first = datetime(2026, 8, 6, 5, 0, tzinfo=timezone.utc)
        second = datetime(2026, 8, 6, 6, 0, tzinfo=timezone.utc)
        conn = _Connection([
            {
                "receipt_date": "2026-08-06", "product_name": "Костюм",
                "product_size": "98", "product_color": "бежевый",
                "location_code": "RECEIVE-01", "quantity": 2,
                "occurred_at": first, "id": 1,
            },
            {
                "receipt_date": "2026-08-06", "product_name": "Костюм",
                "product_size": "104", "product_color": "бежевый",
                "location_code": "RECEIVE-01", "quantity": 3,
                "occurred_at": second, "id": 2,
            },
        ])

        result = repository.finished_production_receipts(
            conn, start_date="2026-08-06", end_date="2026-08-06"
        )

        self.assertEqual(result["quantity"], 5)
        self.assertEqual(result["daily"], [{"date": "2026-08-06", "quantity": 5}])
        self.assertEqual(result["updated_at"], second.isoformat())
        sql = conn.cursor_value.sql
        self.assertIn("movement.movement_type = 'production_receipt'", sql)
        self.assertIn("movement.source_type = 'production'", sql)
        self.assertIn("movement.product_key->>'item_type' = 'finished'", sql)
        self.assertIn("zone.code = 'RECEIVE'", sql)


if __name__ == "__main__":
    unittest.main()
