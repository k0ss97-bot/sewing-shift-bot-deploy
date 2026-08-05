from datetime import datetime, timezone
import unittest

from analytics_overview import analytics_overview


class AnalyticsOverviewTests(unittest.TestCase):
    def test_uses_positive_finance_accruals_for_sales_before_withholdings(self):
        dashboard = {
            "ok": True,
            "configured": True,
            "accounts": [{"marketplace": "ozon", "last_sync_at": "2026-08-05T05:00:00Z"}],
            "analytics": {
                "finance_daily": [
                    {"date": "2026-08-04", "revenue": 1250, "net": 1010},
                    {"date": "2026-08-05", "revenue": 750, "net": 580},
                ],
            },
            "wildberries": {"ok": True, "configured": False},
        }

        result = analytics_overview(
            {"start_date": "2026-08-04", "end_date": "2026-08-05"},
            dashboard_reader=lambda: dashboard,
            data_quality_reader=lambda: {"ok": True, "enabled": False},
            production_reader=lambda _start, _end: {},
            current=datetime(2026, 8, 5, 5, 10, tzinfo=timezone.utc),
        )

        metrics = {row["code"]: row for row in result["metrics"]}
        provider = next(row for row in result["providers"] if row["marketplace"] == "ozon")
        self.assertTrue(result["ok"])
        self.assertEqual(provider["recognized_sales"], "2000.00")
        self.assertEqual(provider["net_payout"], "1590.00")
        self.assertEqual(metrics["recognized_sales"]["value"], "2000.00")
        self.assertEqual(metrics["net_payout"]["value"], "1590.00")

