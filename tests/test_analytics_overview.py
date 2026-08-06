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

    def test_marketplace_units_money_stock_value_and_regions_are_separate(self):
        observed_at = "2026-08-05T05:09:00Z"
        dashboard = {
            "ok": True,
            "configured": True,
            "source": "postgresql",
            "accounts": [{"marketplace": "ozon", "last_sync_at": observed_at}],
            "products_rows": [
                {"available": 4, "current_price": 500},
                {"available": 2, "current_price": 750},
            ],
            "analytics": {
                "sales_daily": [
                    {"date": "2026-08-05", "orders": 3, "units": 5, "amount": 3250, "unpriced_lines": 0},
                ],
                "sales_by_region_daily": [
                    {"date": "2026-08-05", "region": "Москва", "orders": 2, "units": 3, "amount": 1750},
                    {"date": "2026-08-05", "region": "Урал", "orders": 1, "units": 2, "amount": 1500},
                ],
            },
            "wildberries": {"ok": True, "configured": False},
        }
        datasets = [
            {"dataset": name, "status": "success", "freshness": "fresh", "finished_at": observed_at}
            for name in ("catalog", "prices", "stocks", "orders")
        ]
        result = analytics_overview(
            {"start_date": "2026-08-05", "end_date": "2026-08-05"},
            dashboard_reader=lambda: dashboard,
            data_quality_reader=lambda: {
                "ok": True,
                "enabled": True,
                "state": "fresh",
                "datasets": datasets,
                "totals": {"products": 2, "stock_available": 6},
            },
            production_reader=lambda _start, _end: {"updated_at": observed_at},
            current=datetime(2026, 8, 5, 5, 10, tzinfo=timezone.utc),
        )

        provider = next(row for row in result["providers"] if row["marketplace"] == "ozon")
        metrics = {row["code"]: row for row in result["metrics"]}
        self.assertEqual(provider["orders"], 3)
        self.assertEqual(provider["sales_units"], "5")
        self.assertEqual(provider["gross_sales"], "3250.00")
        self.assertEqual(provider["stock_available"], "6")
        self.assertEqual(provider["stock_retail_value"], "3500.00")
        self.assertEqual(metrics["sales_units"]["value"], "5")
        self.assertEqual(metrics["gross_sales"]["value"], "3250.00")
        self.assertEqual(metrics["stock_retail_value"]["value"], "3500.00")
        self.assertEqual(metrics["geo"]["value"], 2)
        self.assertEqual([row["region"] for row in result["geography"]["rows"]], ["Москва", "Урал"])
        self.assertEqual(result["series"]["sales"][0]["ozon_units"], "5")
        self.assertEqual(result["series"]["sales"][0]["ozon_amount"], "3250.00")
