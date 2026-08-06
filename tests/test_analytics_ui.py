import unittest

from miniapp_assets import MINIAPP_HTML


class AnalyticsUITests(unittest.TestCase):
    def test_loading_state_is_not_reported_as_unavailable(self):
        self.assertIn('["Загружаем данные", "loading"]', MINIAPP_HTML)
        self.assertIn('overviewState.loading ? "Загрузка…" : "Обновить"', MINIAPP_HTML)
        self.assertIn('state.analyticsOverviewCache[request.key] = overview', MINIAPP_HTML)
        self.assertIn('if (!force && cached)', MINIAPP_HTML)
        self.assertIn('payload.catalog_reconciliation || root.catalog_reconciliation', MINIAPP_HTML)

    def test_region_page_contains_interactive_ozon_map(self):
        self.assertIn('Карта регионов:', MINIAPP_HTML)
        self.assertIn('Карта продаж по регионам', MINIAPP_HTML)
        self.assertIn('Размер круга — ${mapMetric', MINIAPP_HTML)
        self.assertIn('class="ac-region-bubble"', MINIAPP_HTML)
        self.assertIn('id="analyticsMapProduct"', MINIAPP_HTML)
        self.assertIn('data-ac-map-metric="units"', MINIAPP_HTML)
        self.assertIn('data-ac-map-metric="amount"', MINIAPP_HTML)
        self.assertIn('data-ac-map-zoom="in"', MINIAPP_HTML)
        self.assertNotIn('class="ac-region-leader"', MINIAPP_HTML)
        self.assertNotIn('class="ac-region-grid"', MINIAPP_HTML)
        self.assertNotIn('class="ac-region-land-detail"', MINIAPP_HTML)
        self.assertIn('data-ac-region-key=', MINIAPP_HTML)
        self.assertIn('class="ac-region-hover-card"', MINIAPP_HTML)
        self.assertIn('Распределение товаров', MINIAPP_HTML)
        self.assertIn('Все регионы = 100%', MINIAPP_HTML)
        self.assertIn('setAnalyticsRegionHighlight', MINIAPP_HTML)
        self.assertIn('class="ac-region-share-stack"', MINIAPP_HTML)
        self.assertIn('id="analyticsRegionDetail"', MINIAPP_HTML)
        self.assertIn('id="analyticsRegionDetailAverage"', MINIAPP_HTML)
        self.assertIn('Цвет круга совпадает с регионом в рейтинге.', MINIAPP_HTML)

    def test_all_analytics_sections_have_business_content(self):
        for label in (
            "Продажи по складам", "Продажи по товарам",
            "Каталог и связь с производством", "Остатки по SKU",
            "Спрос маркетплейсов → производство", "Поставки Ozon / Wildberries",
            "Финансы Ozon / Wildberries", "Продажи по регионам", "Наборы данных",
        ):
            self.assertIn(label, MINIAPP_HTML)

    def test_analytics_workspace_is_not_named_report(self):
        self.assertIn('data-workspace="analytics">Аналитика</button>', MINIAPP_HTML)
        self.assertNotIn('data-workspace="analytics">Отчёт</button>', MINIAPP_HTML)
        self.assertIn('data-workspace="analytics">Открыть аналитику ›</button>', MINIAPP_HTML)

    def test_production_has_own_analytics_scope_and_finished_goods_rule(self):
        self.assertIn('analyticsProvider: "all"', MINIAPP_HTML)
        self.assertIn('data-ac-provider="production"', MINIAPP_HTML)
        self.assertIn('>Производство</button>', MINIAPP_HTML)
        self.assertIn('Факт готовой продукции', MINIAPP_HTML)
        self.assertIn('Принято в RECEIVE', MINIAPP_HTML)
        self.assertIn('Полуфабрикаты в план и факт не входят.', MINIAPP_HTML)


if __name__ == "__main__":
    unittest.main()
