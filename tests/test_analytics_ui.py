import unittest

from miniapp_assets import MINIAPP_HTML


class AnalyticsUITests(unittest.TestCase):
    def test_loading_state_is_not_reported_as_unavailable(self):
        self.assertIn('["Загружаем данные", "loading"]', MINIAPP_HTML)
        self.assertIn('overviewState.loading ? "Загрузка…" : "Обновить"', MINIAPP_HTML)

    def test_region_page_contains_interactive_ozon_map(self):
        self.assertIn('Карта кластеров Ozon', MINIAPP_HTML)
        self.assertIn('Карта продаж по кластерам Ozon', MINIAPP_HTML)
        self.assertIn('Размер круга — сумма заказов', MINIAPP_HTML)
        self.assertIn('class="ac-region-bubble"', MINIAPP_HTML)

    def test_analytics_workspace_is_not_named_report(self):
        self.assertIn('data-workspace="analytics">Аналитика</button>', MINIAPP_HTML)
        self.assertNotIn('data-workspace="analytics">Отчёт</button>', MINIAPP_HTML)
        self.assertIn('data-workspace="analytics">Открыть аналитику ›</button>', MINIAPP_HTML)


if __name__ == "__main__":
    unittest.main()
