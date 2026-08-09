from __future__ import annotations

from pathlib import Path
import unittest

from miniapp_assets import (
    MINIAPP_CSS,
    MINIAPP_CSS_PATH,
    MINIAPP_JS,
    MINIAPP_JS_PATH,
    MINIAPP_SHELL_HTML,
)
from webapp_pwa import build_service_worker, get_pwa_resource, inject_pwa_markup
from miniapp_server import CONTENT_SECURITY_POLICY


class FrontendPerformanceContractTests(unittest.TestCase):
    def test_frontend_sources_are_split_from_python_loader(self):
        root = Path(__file__).resolve().parents[1]
        loader = (root / "miniapp_assets.py").read_text(encoding="utf-8")
        self.assertLess(len(loader.splitlines()), 100)
        self.assertNotIn("<!doctype html>", loader)
        self.assertEqual((root / "assets/app/app.css").read_text(encoding="utf-8"), MINIAPP_CSS)
        self.assertEqual((root / "assets/app/app.js").read_text(encoding="utf-8"), MINIAPP_JS)
        shell_template = (root / "assets/app/shell.html").read_text(encoding="utf-8")
        self.assertIn("{{MINIAPP_CSS_PATH}}", shell_template)
        self.assertIn("{{MINIAPP_JS_PATH}}", shell_template)

    def test_served_app_shell_is_under_fifty_kilobytes(self):
        rendered = inject_pwa_markup(MINIAPP_SHELL_HTML).encode("utf-8")
        self.assertLess(len(rendered), 50 * 1024)
        self.assertIn(MINIAPP_CSS_PATH, MINIAPP_SHELL_HTML)
        self.assertIn(MINIAPP_JS_PATH, MINIAPP_SHELL_HTML)
        self.assertNotIn(MINIAPP_CSS[:200], MINIAPP_SHELL_HTML)
        self.assertNotIn(MINIAPP_JS[:200], MINIAPP_SHELL_HTML)

    def test_versioned_css_and_javascript_are_immutable_and_precached(self):
        css = get_pwa_resource(MINIAPP_CSS_PATH)
        javascript = get_pwa_resource(MINIAPP_JS_PATH)
        self.assertEqual(css.body.decode("utf-8"), MINIAPP_CSS)
        self.assertEqual(javascript.body.decode("utf-8"), MINIAPP_JS)
        self.assertEqual(css.cache_control, "public, max-age=31536000, immutable")
        self.assertEqual(javascript.cache_control, "public, max-age=31536000, immutable")
        worker = build_service_worker("frontend-contract")
        self.assertIn(MINIAPP_CSS_PATH, worker)
        self.assertIn(MINIAPP_JS_PATH, worker)

    def test_production_task_views_render_at_most_fifty_cards_per_page(self):
        self.assertIn("const ORDER_DOM_WINDOW = 50;", MINIAPP_JS)
        self.assertIn(
            "rows.slice(pageStart, pageStart + ORDER_DOM_WINDOW)",
            MINIAPP_JS,
        )
        self.assertIn("renderOrderPager(allTasks.length", MINIAPP_JS)
        self.assertIn('data-order-action="next-page"', MINIAPP_JS)

    def test_operational_controls_have_accessible_touch_targets(self):
        self.assertIn(
            ':where(button, [role="button"], input:not([type="checkbox"]):not([type="radio"]), select, textarea)',
            MINIAPP_CSS,
        )
        self.assertIn("min-height: 48px;", MINIAPP_CSS)
        self.assertIn(":focus-visible", MINIAPP_CSS)

    def test_marketplace_filters_and_views_are_persisted_safely(self):
        for key in (
            '"marketplaceSupplyView"',
            '"marketplacePeriod"',
            '"marketplaceOrderView"',
            '"marketplaceFilters"',
        ):
            self.assertIn(key, MINIAPP_JS)
        self.assertIn("marketplaceFilterSnapshot", MINIAPP_JS)
        self.assertIn("state.marketplaceFilters = {...state.marketplaceFilterSnapshot}", MINIAPP_JS)
        self.assertIn('orderStatus: String(state.marketplaceFilters.orderStatus || "all").slice(0, 80)', MINIAPP_JS)

    def test_external_business_statuses_are_presented_in_russian(self):
        self.assertIn("function businessStatusLabel(value)", MINIAPP_JS)
        self.assertIn('sync_error: "Ошибка синхронизации"', MINIAPP_JS)
        self.assertIn('ready_to_pick: "Готова к отбору"', MINIAPP_JS)
        self.assertNotIn("Ошибка sync", MINIAPP_JS)

    def test_strict_csp_does_not_allow_inline_style_attributes(self):
        self.assertIn("style-src-attr 'none'", CONTENT_SECURITY_POLICY)
        self.assertNotIn("style-src-attr 'unsafe-inline'", CONTENT_SECURITY_POLICY)
        self.assertNotIn('style="', MINIAPP_JS)
        self.assertNotIn(".style.", MINIAPP_JS)

    def test_authenticated_reload_restores_verified_session_state_without_blocking(self):
        self.assertIn("function cacheAppState(data)", MINIAPP_JS)
        self.assertIn("function restoreCachedAppState()", MINIAPP_JS)
        self.assertIn("window.sessionStorage.setItem(appStateCacheKey(identity), serialized)", MINIAPP_JS)
        self.assertNotIn("window.localStorage.setItem(appStateCacheKey(identity)", MINIAPP_JS)
        self.assertIn('if (result.status === "authenticated")', MINIAPP_JS)
        authenticated_flow = MINIAPP_JS.split('if (result.status === "authenticated")', 1)[1]
        self.assertLess(authenticated_flow.index("restoreCachedAppState()"), authenticated_flow.index('refreshState("", {silent: true})'))
        self.assertIn("clearCachedAppState();\n        clearWebIdentity();", MINIAPP_JS)


if __name__ == "__main__":
    unittest.main()
