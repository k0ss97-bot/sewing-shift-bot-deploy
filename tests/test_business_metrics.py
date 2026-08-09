from __future__ import annotations

from decimal import Decimal
import unittest

from business_metrics import calculate_inventory_turnover, calculate_unit_economics, moving_average_forecast


class BusinessMetricsTests(unittest.TestCase):
    def test_unit_economics_calculates_contribution_after_all_variable_costs(self):
        result = calculate_unit_economics({
            "quantity":10,"revenue":10000,"unit_cost":500,"marketplace_fees":1000,
            "logistics_cost":500,"returns_cost":100,"other_variable_cost":100,
        })
        self.assertEqual(result["cogs"], Decimal("5000.00"))
        self.assertEqual(result["contribution_margin"], Decimal("3300.00"))
        self.assertEqual(result["margin_percent"], Decimal("33.000000"))

    def test_missing_cost_is_not_silently_treated_as_zero(self):
        result = calculate_unit_economics({"quantity":10,"revenue":10000,"unit_cost":None})
        self.assertEqual(result["status"], "unavailable")
        self.assertIsNone(result["cogs"])
        self.assertIsNone(result["contribution_margin"])

    def test_inventory_turnover_and_days_on_hand(self):
        result = calculate_inventory_turnover(period_cogs=120000, average_inventory_cost=30000, period_days=365)
        self.assertEqual(result["turnover"], Decimal("4.000000"))
        self.assertEqual(result["days_on_hand"], Decimal("91.250000"))

    def test_zero_inventory_does_not_create_infinite_turnover(self):
        result = calculate_inventory_turnover(period_cogs=100, average_inventory_cost=0)
        self.assertEqual(result["status"], "unavailable")
        self.assertIsNone(result["turnover"])

    def test_forecast_is_labelled_and_warns_on_short_history(self):
        result = moving_average_forecast([{"units":2},{"units":4},{"units":6}], horizon_days=2, window_days=7)
        self.assertEqual(result["status"], "partial")
        self.assertEqual(result["method"], "moving_average")
        self.assertEqual(result["forecast_units"], [Decimal("4.000000"), Decimal("4.000000")])
        self.assertTrue(result["warnings"])


if __name__ == "__main__":
    unittest.main()
