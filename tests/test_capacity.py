from __future__ import annotations

from decimal import Decimal
import unittest

from wms.capacity import calculate_capacity_plan


class CapacityPlanningTests(unittest.TestCase):
    def test_jobs_only_go_to_resources_with_the_required_skill(self):
        plan = calculate_capacity_plan(
            [{"job_key":"J1","operation_code":"SEW","quantity":10,"standard_minutes_per_unit":5}],
            [
                {"resource_id":1,"name":"Швея","capacity_minutes":60,"skills":{"SEW":1}},
                {"resource_id":2,"name":"Закройщик","capacity_minutes":500,"skills":{"CUT":1}},
            ],
        )
        assigned = [row for row in plan["assignments"] if row["assignment_status"] == "assigned"]
        self.assertEqual([row["resource_id"] for row in assigned], [1])
        self.assertEqual(plan["status"], "ready")

    def test_capacity_overload_is_visible_and_never_overbooks_resource(self):
        plan = calculate_capacity_plan(
            [{"job_key":"J1","operation_code":"SEW","quantity":20,"standard_minutes_per_unit":5}],
            [{"resource_id":1,"capacity_minutes":60,"skills":{"SEW":1}}],
        )
        self.assertEqual(plan["status"], "over_capacity")
        self.assertEqual(plan["resource_remaining_minutes"][1], Decimal("0.000000"))
        unassigned = [row for row in plan["assignments"] if row["assignment_status"] == "unassigned"]
        self.assertEqual(unassigned[0]["standard_minutes"], Decimal("40.000000"))
        self.assertEqual(unassigned[0]["reason"], "Недостаточно доступной мощности")

    def test_proficiency_changes_clock_time_without_changing_standard_work(self):
        plan = calculate_capacity_plan(
            [{"job_key":"J1","operation_code":"PACK","quantity":10,"standard_minutes_per_unit":6}],
            [{"resource_id":3,"capacity_minutes":30,"skills":{"PACK":"2"}}],
        )
        row = plan["assignments"][0]
        self.assertEqual(row["standard_minutes"], Decimal("60.000000"))
        self.assertEqual(row["clock_minutes"], Decimal("30.000000"))
        self.assertEqual(plan["status"], "ready")

    def test_non_splittable_job_is_not_partially_assigned(self):
        plan = calculate_capacity_plan(
            [{"job_key":"J1","operation_code":"CUT","quantity":10,"standard_minutes_per_unit":10,"splittable":False}],
            [
                {"resource_id":1,"capacity_minutes":60,"skills":{"CUT":1}},
                {"resource_id":2,"capacity_minutes":30,"skills":{"CUT":1}},
            ],
        )
        self.assertEqual(plan["status"], "over_capacity")
        self.assertFalse(any(row["assignment_status"] == "assigned" for row in plan["assignments"]))
        self.assertEqual(plan["resource_remaining_minutes"][1], Decimal("60.000000"))


if __name__ == "__main__":
    unittest.main()
