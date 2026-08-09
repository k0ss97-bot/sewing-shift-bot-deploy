from __future__ import annotations

from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
JAVASCRIPT = (PROJECT_ROOT / "assets" / "app" / "app.js").read_text(encoding="utf-8")
CSS = (PROJECT_ROOT / "assets" / "app" / "app.css").read_text(encoding="utf-8")


class UiDensityTests(unittest.TestCase):
    def test_density_is_saved_per_authenticated_browser_identity(self):
        self.assertIn('"displayDensity"', JAVASCRIPT)
        self.assertIn('displayDensity: "auto"', JAVASCRIPT)
        self.assertIn('data-profile-action="density"', JAVASCRIPT)
        self.assertIn("persistUiState();", JAVASCRIPT)

    def test_auto_density_is_role_and_viewport_aware(self):
        self.assertIn('state.data.is_admin && window.matchMedia', JAVASCRIPT)
        self.assertIn('window.matchMedia("(min-width: 900px)").matches', JAVASCRIPT)
        self.assertIn('automaticCompact ? "compact" : "comfortable"', JAVASCRIPT)

    def test_compact_mode_preserves_global_touch_target_contract(self):
        self.assertIn("body.web-mode.density-compact", CSS)
        self.assertIn("mode only removes decorative whitespace", CSS)
        self.assertNotIn("density-compact button", CSS)
        self.assertIn("min-height: 48px;", CSS)


if __name__ == "__main__":
    unittest.main()
