from __future__ import annotations

from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SHELL = (PROJECT_ROOT / "assets" / "app" / "shell.html").read_text(encoding="utf-8")
JAVASCRIPT = (PROJECT_ROOT / "assets" / "app" / "app.js").read_text(encoding="utf-8")
CSS = (PROJECT_ROOT / "assets" / "app" / "app.css").read_text(encoding="utf-8")


class HelpCenterTests(unittest.TestCase):
    def test_help_is_available_from_the_global_header(self):
        self.assertIn('id="helpBtn"', SHELL)
        self.assertIn('aria-label="Открыть помощь"', SHELL)
        self.assertIn('document.getElementById("helpBtn").addEventListener', JAVASCRIPT)
        self.assertIn('if (state.screen === "help") renderHelp();', JAVASCRIPT)

    def test_help_covers_all_user_facing_workspaces(self):
        for category in (
            "start",
            "production",
            "warehouse",
            "marketplaces",
            "analytics",
            "admin",
        ):
            self.assertIn(f'category:"{category}"', JAVASCRIPT)
        for required_article in (
            'id:"shift"',
            'id:"pause"',
            'id:"partial-task"',
            'id:"ready-cut"',
            'id:"receiving"',
            'id:"putaway"',
            'id:"marketplace-overview"',
            'id:"analytics"',
            'id:"admin-employees"',
            'id:"admin-shifts"',
        ):
            self.assertIn(required_article, JAVASCRIPT)

    def test_help_articles_have_annotated_synthetic_screens(self):
        self.assertIn('function helpScreenshot(type)', JAVASCRIPT)
        self.assertIn('class="help-pin help-pin-a"', JAVASCRIPT)
        self.assertIn('Выбор раздела', JAVASCRIPT)
        self.assertIn('Проверка данных', JAVASCRIPT)
        self.assertIn('Подтверждение', JAVASCRIPT)
        self.assertIn(".help-shot-layout", CSS)
        self.assertIn(".help-pin-a", CSS)

    def test_search_and_category_filters_are_persisted(self):
        for key in ('"helpCategory"', '"helpQuery"', '"helpArticle"'):
            self.assertIn(key, JAVASCRIPT)
        self.assertIn('id="helpSearch"', JAVASCRIPT)
        self.assertIn('data-help-category=', JAVASCRIPT)
        self.assertIn("function filteredHelpArticles()", JAVASCRIPT)

    def test_help_is_global_and_returns_to_previous_workspace(self):
        self.assertIn('state.helpReturnWorkspace = state.workspace;', JAVASCRIPT)
        self.assertIn('state.helpReturnScreen = state.screen;', JAVASCRIPT)
        self.assertIn('state.workspace = state.helpReturnWorkspace || "production";', JAVASCRIPT)
        self.assertIn('["warehouse", "profile", "help"]', JAVASCRIPT)
        self.assertIn('if (state.screen === "help" || state.workspace === "analytics")', JAVASCRIPT)


if __name__ == "__main__":
    unittest.main()
