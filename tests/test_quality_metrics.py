from __future__ import annotations

from decimal import Decimal
import unittest

from quality_metrics import calculate_oee, can_transition_capa, require_capa_transition


class QualityMetricsTests(unittest.TestCase):
    def test_oee_uses_availability_performance_and_quality(self):
        result = calculate_oee({
            "planned_production_minutes": 480,
            "unplanned_downtime_minutes": 60,
            "total_units": 100,
            "good_units": 95,
            "ideal_cycle_minutes": 4,
        })
        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["availability"], Decimal("0.875000"))
        self.assertEqual(result["performance"], Decimal("0.952381"))
        self.assertEqual(result["quality"], Decimal("0.950000"))
        self.assertEqual(result["oee"], Decimal("0.791667"))

    def test_missing_or_empty_sources_are_not_reported_as_zero_oee(self):
        missing = calculate_oee({"planned_production_minutes": 480})
        empty = calculate_oee({
            "planned_production_minutes": 480,
            "unplanned_downtime_minutes": 0,
            "total_units": 0,
            "good_units": 0,
            "ideal_cycle_minutes": 4,
        })
        self.assertEqual(missing["status"], "unavailable")
        self.assertIsNone(missing["oee"])
        self.assertEqual(empty["status"], "partial")
        self.assertIsNone(empty["oee"])

    def test_impossible_quality_and_downtime_inputs_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "good_units"):
            calculate_oee({
                "planned_production_minutes": 10, "unplanned_downtime_minutes": 0,
                "total_units": 2, "good_units": 3, "ideal_cycle_minutes": 1,
            })
        with self.assertRaisesRegex(ValueError, "downtime"):
            calculate_oee({
                "planned_production_minutes": 10, "unplanned_downtime_minutes": 11,
                "total_units": 2, "good_units": 2, "ideal_cycle_minutes": 1,
            })

    def test_capa_requires_verification_before_effective_close(self):
        self.assertTrue(can_transition_capa("in_progress", "verification"))
        self.assertTrue(can_transition_capa("verification", "effective"))
        self.assertFalse(can_transition_capa("in_progress", "effective"))
        with self.assertRaisesRegex(ValueError, "not allowed"):
            require_capa_transition("draft", "effective")


if __name__ == "__main__":
    unittest.main()
