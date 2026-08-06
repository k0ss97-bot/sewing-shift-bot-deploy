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
            "catalog_reconciliation": {
                "ok": True,
                "warehouse_available": True,
                "marketplace_items": [{"marketplace": "ozon", "article": "SKU-1"}],
            },
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
        self.assertEqual(metrics["recommendations"]["value"], len(result["risks"]))
        self.assertTrue(result["catalog_reconciliation"]["ok"])
        self.assertEqual(result["catalog_reconciliation"]["marketplace_items"][0]["article"], "SKU-1")

    def test_production_freshness_requires_observation_timestamp(self):
        dashboard = {
            "ok": True,
            "configured": True,
            "accounts": [{"marketplace": "ozon", "last_sync_at": "2026-08-05T05:00:00Z"}],
            "wildberries": {"ok": True, "configured": False},
        }

        def build(production):
            return analytics_overview(
                {"start_date": "2026-08-05", "end_date": "2026-08-05"},
                dashboard_reader=lambda: dashboard,
                data_quality_reader=lambda: {"ok": True, "enabled": False},
                production_reader=lambda _start, _end: production,
                current=datetime(2026, 8, 5, 5, 10, tzinfo=timezone.utc),
            )

        unverified = build({"plan": 12, "fact": 10, "active_quantity": 2, "fpy": 100})
        verified = build({
            "plan": 12,
            "fact": 10,
            "active_quantity": 2,
            "fpy": 100,
            "updated_at": "2026-08-05T05:09:00Z",
        })

        unverified_metrics = {row["code"]: row for row in unverified["metrics"]}
        verified_metrics = {row["code"]: row for row in verified["metrics"]}
        self.assertEqual(unverified_metrics["production_plan"]["status"], "unknown")
        self.assertEqual(verified_metrics["production_plan"]["status"], "fresh")
        self.assertEqual(
            verified_metrics["production_plan"]["meta"]["max_source_updated_at"],
            "2026-08-05T05:09:00Z",
        )

    def test_recommendations_metric_counts_actionable_risks(self):
        dashboard = {
            "ok": True,
            "configured": True,
            "accounts": [{"marketplace": "ozon", "last_sync_at": "2026-08-05T05:00:00Z"}],
            "wildberries": {
                "ok": True,
                "configured": True,
                "accounts": [{"marketplace": "wildberries", "last_sync_at": "2026-08-05T05:00:00Z"}],
                "analytics": {
                    "capability_rows": [
                        {"capability": "catalog", "status": "fresh", "checked_at": "2026-08-05T05:09:00Z"},
                        {"capability": "stocks", "status": "permission_required", "checked_at": "2026-08-05T05:09:00Z"},
                    ],
                },
                "products_rows": [{"available": 7}],
                "summary": {"products": 1},
            },
        }
        result = analytics_overview(
            {"start_date": "2026-08-05", "end_date": "2026-08-05"},
            dashboard_reader=lambda: dashboard,
            data_quality_reader=lambda: {"ok": True, "enabled": False},
            production_reader=lambda _start, _end: {"updated_at": "2026-08-05T05:09:00Z"},
            current=datetime(2026, 8, 5, 5, 10, tzinfo=timezone.utc),
        )

        metrics = {row["code"]: row for row in result["metrics"]}
        self.assertGreater(len(result["risks"]), 0)
        self.assertEqual(metrics["recommendations"]["value"], len(result["risks"]))
        self.assertNotEqual(metrics["recommendations"]["status"], "unavailable")
