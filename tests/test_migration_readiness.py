from __future__ import annotations

import unittest

from migration_readiness import REQUIRED_GLOBAL_GATES, evaluate_cutover_readiness, require_cutover_ready


class MigrationReadinessTests(unittest.TestCase):
    def _checkpoint(self, **overrides):
        row = {
            "table_name":"production_tasks", "source_row_count":100, "target_row_count":100,
            "source_checksum":"abc", "target_checksum":"abc",
            "replication_lag_seconds":1, "writes_quiesced":True,
        }
        row.update(overrides)
        return row

    def _gates(self):
        return {name: True for name in REQUIRED_GLOBAL_GATES}

    def test_all_table_and_global_evidence_is_required(self):
        report = evaluate_cutover_readiness([self._checkpoint()], self._gates())
        self.assertTrue(report["ready"])
        require_cutover_ready(report)

    def test_count_checksum_lag_and_write_mismatches_block_cutover(self):
        report = evaluate_cutover_readiness([
            self._checkpoint(target_row_count=99, target_checksum="bad", replication_lag_seconds=8, writes_quiesced=False),
        ], self._gates())
        self.assertFalse(report["ready"])
        self.assertEqual(len(report["blockers"]), 4)
        with self.assertRaisesRegex(RuntimeError, "blocked"):
            require_cutover_ready(report)

    def test_missing_gate_or_empty_table_evidence_fails_closed(self):
        gates = self._gates()
        gates.pop("rollback_rehearsed")
        report = evaluate_cutover_readiness([], gates)
        self.assertFalse(report["ready"])
        self.assertIn("Нет сверки таблиц", report["blockers"])
        self.assertTrue(any("rollback_rehearsed" in item for item in report["blockers"]))


if __name__ == "__main__":
    unittest.main()
