from __future__ import annotations

from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
JAVASCRIPT = (PROJECT_ROOT / "assets" / "app" / "app.js").read_text(encoding="utf-8")
CSS = (PROJECT_ROOT / "assets" / "app" / "app.css").read_text(encoding="utf-8")


class MobileNavigationTests(unittest.TestCase):
    def test_analytics_has_a_sticky_mobile_section_selector(self):
        self.assertIn('id="analyticsMobilePage"', JAVASCRIPT)
        self.assertIn('event.target.id === "analyticsMobilePage"', JAVASCRIPT)
        self.assertIn(".ac-sidebar{position:sticky;top:0;z-index:30", CSS)
        self.assertIn(".ac-mobile-nav select{width:100%;min-height:52px", CSS)

    def test_all_analytics_sections_are_available_in_mobile_selector(self):
        for identifier in (
            "general",
            "sales",
            "products",
            "inventory",
            "production",
            "supplies",
            "finance",
            "map",
            "data-quality",
        ):
            self.assertIn(f'"{identifier}"', JAVASCRIPT)
        self.assertIn('pages.map(([id, , label])', JAVASCRIPT)

    def test_mobile_selector_value_is_allowlisted_before_navigation(self):
        self.assertIn('allowed.has(event.target.value) ? event.target.value : "general"', JAVASCRIPT)
        self.assertIn("persistUiState();", JAVASCRIPT)


if __name__ == "__main__":
    unittest.main()
