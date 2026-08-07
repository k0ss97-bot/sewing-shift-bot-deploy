# E2E G — аналитический центр

- Дата: 2026-08-07
- Code state: local candidate; active release ещё `f7cae4e`
- Разделы: Обзор, Продажи, Товары, Остатки, Производство, Поставки, Финансы, Регионы, Качество данных

## Auto/smoke-результат

Исправлены tooltip для штук/рублей, empty states, mobile navigation, accessibility labels и формат дат. Marketplace dashboard имеет TTL-cache/background refresh; периоды пересчитываются по загруженному snapshot. Production fact берётся из фактических WMS receipts, а не из плана.

После ошибки read-only PostgreSQL запроса транзакция откатывается и не заражает следующие запросы.

## Живая приёмка

Не заполнены: public release, периоды 7/30/текущий/предыдущий месяц, Ozon/WB штуки/рубли, partial source freshness, 390×844, console/network timings, screenshots и сверка цифр.

**Итог:** LOCAL AUTO PASS; FINAL PENDING.
