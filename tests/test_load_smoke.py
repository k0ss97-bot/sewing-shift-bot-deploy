from __future__ import annotations

import unittest

from scripts.load_smoke import percentile


class LoadSmokeTests(unittest.TestCase):
    def test_percentile_is_deterministic_and_bounded(self):
        self.assertEqual(percentile([], 0.95), 0)
        self.assertEqual(percentile([30, 10, 20], 0.0), 10)
        self.assertEqual(percentile([30, 10, 20], 0.95), 30)
        self.assertEqual(percentile([30, 10, 20], 2.0), 30)


if __name__ == "__main__":
    unittest.main()
