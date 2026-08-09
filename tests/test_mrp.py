from __future__ import annotations

from decimal import Decimal
import unittest

from wms.mrp import calculate_material_plan, component_key


class MaterialRequirementsPlanningTests(unittest.TestCase):
    def test_bom_explosion_aggregates_demand_scrap_and_available_stock(self):
        demands = [
            {"product_master_id": 10, "quantity": 100},
            {"product_master_id": 10, "quantity": 20},
        ]
        bom = [{
            "product_master_id": 10,
            "component_type": "material",
            "component_article": "FAB-BEIGE",
            "component_name": "Футер",
            "unit": "м",
            "quantity_per": "1.5",
            "scrap_percent": "10",
        }]
        available = [{
            "component_type": "material",
            "component_article": "fab-beige",
            "component_name": "Другое название не разрывает связь",
            "unit": "М",
            "available_quantity": "150",
        }]

        plan = calculate_material_plan(demands, bom, available)

        self.assertEqual(plan["status"], "shortage")
        self.assertEqual(plan["shortage_count"], 1)
        self.assertEqual(plan["lines"][0]["required_quantity"], Decimal("198.000000"))
        self.assertEqual(plan["lines"][0]["available_quantity"], Decimal("150.000000"))
        self.assertEqual(plan["lines"][0]["shortage_quantity"], Decimal("48.000000"))

    def test_article_is_authoritative_component_identity(self):
        first = component_key({
            "component_type": "semifinished", "component_article": "CUT-1",
            "component_name": "Крой старое имя", "component_size": "98",
            "component_color": "бежевый", "unit": "шт",
        })
        second = component_key({
            "component_type": "semifinished", "component_article": "cut-1",
            "component_name": "Крой новое имя", "component_size": "110",
            "component_color": "синий", "unit": "ШТ",
        })
        self.assertEqual(first, second)

    def test_plan_is_incomplete_when_product_has_no_active_bom(self):
        plan = calculate_material_plan(
            [{"product_master_id": 77, "quantity": 5}],
            [],
            [],
        )
        self.assertEqual(plan["status"], "incomplete")
        self.assertEqual(plan["missing_bom_product_ids"], [77])
        self.assertEqual(plan["component_count"], 0)

    def test_invalid_quantities_and_scrap_are_rejected(self):
        base_line = {
            "product_master_id": 1, "component_type": "material",
            "component_name": "Ткань", "unit": "м", "quantity_per": 1,
        }
        with self.assertRaisesRegex(ValueError, "positive"):
            calculate_material_plan([{"product_master_id": 1, "quantity": 0}], [base_line], [])
        with self.assertRaisesRegex(ValueError, "exceed"):
            calculate_material_plan(
                [{"product_master_id": 1, "quantity": 1}],
                [{**base_line, "scrap_percent": 101}],
                [],
            )


if __name__ == "__main__":
    unittest.main()
