from __future__ import annotations

from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
JAVASCRIPT = (PROJECT_ROOT / "assets" / "app" / "app.js").read_text(encoding="utf-8")


class UiLocalizationTests(unittest.TestCase):
    def test_connection_retry_uses_human_readable_duration(self):
        self.assertIn("function formatWaitTime(totalSeconds)", JAVASCRIPT)
        self.assertIn("formatWaitTime(retryDelayMs / 1000)", JAVASCRIPT)
        self.assertNotIn("Math.ceil(retryDelayMs / 1000)} сек.", JAVASCRIPT)

    def test_marketplace_diagnostics_translate_technical_fields(self):
        self.assertIn("function diagnosticTerminationLabel(value)", JAVASCRIPT)
        self.assertIn('rate_limited: "Источник временно ограничил запросы"', JAVASCRIPT)
        self.assertIn("Последнее успешное обновление", JAVASCRIPT)
        self.assertIn("Страницы / повторные попытки", JAVASCRIPT)
        self.assertNotIn("Последний пригодный sync", JAVASCRIPT)
        self.assertNotIn("Страницы / retry", JAVASCRIPT)

    def test_capability_codes_have_business_labels_and_no_raw_fallback(self):
        self.assertIn('roles:"Права доступа Ozon"', JAVASCRIPT)
        self.assertIn('supplies:"Поставки"', JAVASCRIPT)
        self.assertIn('capabilityLabels[row.capability] || "Источник данных"', JAVASCRIPT)
        self.assertNotIn("Capabilities ещё не проверены", JAVASCRIPT)


if __name__ == "__main__":
    unittest.main()
