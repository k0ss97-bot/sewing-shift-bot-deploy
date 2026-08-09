from __future__ import annotations

import unittest
from pathlib import Path

from planning_api import calculate_planning_model


class PlanningApiTests(unittest.TestCase):
    def test_admin_http_and_frontend_contracts_are_wired(self):
        root = Path(__file__).resolve().parents[1]
        server = (root / "miniapp_server.py").read_text(encoding="utf-8")
        frontend = (root / "assets" / "app" / "app.js").read_text(encoding="utf-8")

        self.assertIn('"/api/admin/planning/overview"', server)
        self.assertIn('"/api/admin/planning/calculate"', server)
        self.assertIn("get_admin_planning_overview", server)
        self.assertIn("calculate_admin_planning", server)
        for module in ("mrp", "capacity", "oee", "unit_economics", "forecast", "slotting"):
            self.assertIn(f'["{module}"', frontend)
        self.assertIn('data-admin-action="planning-calculate"', frontend)
        self.assertIn('event.target.id === "planningModuleSelect"', frontend)

    def test_mrp_capacity_and_oee_are_exposed_as_json_safe_results(self):
        mrp = calculate_planning_model({
            "module": "mrp",
            "demands": [{"product_master_id": 1, "quantity": 10}],
            "bom_lines": [{
                "product_master_id": 1, "component_type": "material",
                "component_article": "FAB-1", "component_name": "Ткань",
                "unit": "м", "quantity_per": "1.5", "scrap_percent": 0,
            }],
            "available_rows": [{
                "component_type": "material", "component_article": "FAB-1",
                "component_name": "Ткань", "unit": "м", "available_quantity": 20,
            }],
        })
        self.assertTrue(mrp["ok"])
        self.assertEqual(mrp["result"]["status"], "ready")
        self.assertEqual(mrp["result"]["lines"][0]["required_quantity"], 15)

        capacity = calculate_planning_model({
            "module": "capacity",
            "jobs": [{"job_key": "J1", "operation_code": "SEW", "quantity": 5, "standard_minutes_per_unit": 4}],
            "resources": [{"resource_id": 3, "name": "Швея", "capacity_minutes": 30, "skills": {"SEW": 1}}],
        })
        self.assertEqual(capacity["result"]["status"], "ready")
        self.assertEqual(capacity["result"]["assignments"][0]["assigned_quantity"], 5)

        oee = calculate_planning_model({"module": "oee", "inputs": {
            "planned_production_minutes": 480, "unplanned_downtime_minutes": 60,
            "total_units": 100, "good_units": 95, "ideal_cycle_minutes": 4,
        }})
        self.assertEqual(oee["result"]["oee"], 0.791667)

    def test_finance_forecast_and_wms_plans_are_available(self):
        economics = calculate_planning_model({"module": "unit_economics", "inputs": {
            "quantity": 10, "revenue": 10000, "unit_cost": 500,
            "marketplace_fees": 1000, "logistics_cost": 500,
        }})
        self.assertEqual(economics["result"]["contribution_margin"], 3500)

        forecast = calculate_planning_model({
            "module": "forecast", "history": [{"units": 2}, {"units": 4}, {"units": 6}],
            "horizon_days": 2, "window_days": 3,
        })
        self.assertEqual(forecast["result"]["forecast_units"], [4, 4])

        slotting = calculate_planning_model({
            "module": "slotting",
            "products": [{"article": "B", "pick_count": 1, "picked_units": 5}, {"article": "A", "pick_count": 2, "picked_units": 2}],
        })
        self.assertEqual([row["article"] for row in slotting["result"]["rows"]], ["A", "B"])

    def test_unknown_module_and_invalid_inputs_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "Выберите"):
            calculate_planning_model({"module": "unknown"})
        with self.assertRaises(ValueError):
            calculate_planning_model({"module": "forecast", "history": [], "horizon_days": 0})


if __name__ == "__main__":
    unittest.main()
