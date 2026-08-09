from __future__ import annotations

from datetime import date
from pathlib import Path
import unittest

from wms.optimization import build_pick_waves, plan_cycle_counts, plan_replenishment, slotting_order


class WmsOptimizationTests(unittest.TestCase):
    def test_wave_migration_uses_external_shipment_id_during_sqlite_cutover(self):
        migration = (
            Path(__file__).resolve().parents[1]
            / "wms_migrations"
            / "016_wms_optimization.sql"
        ).read_text(encoding="utf-8")
        self.assertIn("shipment_task_id BIGINT NOT NULL", migration)
        self.assertNotIn("REFERENCES wms_shipment_tasks", migration)

    def test_replenishment_respects_pick_maximum_and_source_availability(self):
        rows = plan_replenishment([{
            "product_key":{"article":"A-1"}, "from_location_id":1, "to_location_id":2,
            "pick_available":2, "pick_minimum":5, "pick_maximum":12, "reserve_available":7,
        }])
        self.assertEqual(rows[0]["recommended_quantity"], 7)
        self.assertIn("ниже минимума", rows[0]["reason"])

    def test_no_replenishment_is_created_when_pick_face_is_healthy(self):
        self.assertEqual(plan_replenishment([{
            "from_location_id":1, "to_location_id":2, "pick_available":8,
            "pick_minimum":5, "pick_maximum":12, "reserve_available":100,
        }]), [])

    def test_pick_waves_do_not_mix_destinations_or_exceed_limit_normally(self):
        waves = build_pick_waves([
            {"shipment_task_id":1,"marketplace":"ozon","destination":"EKB","total_quantity":60,"due_at":"2026-08-10"},
            {"shipment_task_id":2,"marketplace":"ozon","destination":"EKB","total_quantity":50,"due_at":"2026-08-11"},
            {"shipment_task_id":3,"marketplace":"ozon","destination":"MSK","total_quantity":20,"due_at":"2026-08-10"},
        ], maximum_units=100)
        self.assertEqual([wave["shipments"] for wave in waves], [[1], [2], [3]])
        self.assertTrue(all(wave["total_quantity"] <= 100 for wave in waves))

    def test_cycle_count_prioritizes_never_counted_and_discrepant_locations(self):
        rows = plan_cycle_counts([
            {"location_id":1,"last_counted_at":"2026-08-08","movement_velocity":1,"discrepancy_rate":0},
            {"location_id":2,"last_counted_at":None,"movement_velocity":0,"discrepancy_rate":0},
            {"location_id":3,"last_counted_at":"2026-08-08","movement_velocity":1,"discrepancy_rate":"0.5"},
        ], today=date(2026, 8, 9), maximum_locations=2)
        self.assertEqual([row["location_id"] for row in rows], [2, 3])
        self.assertEqual([row["sequence_no"] for row in rows], [1, 2])

    def test_slotting_uses_article_and_confirmed_pick_frequency(self):
        ranked = slotting_order([
            {"article":"B","pick_count":10,"picked_units":100},
            {"article":"A","pick_count":20,"picked_units":25},
        ])
        self.assertEqual([row["article"] for row in ranked], ["A", "B"])
        self.assertEqual(ranked[0]["recommended_pick_priority"], 1)


if __name__ == "__main__":
    unittest.main()
