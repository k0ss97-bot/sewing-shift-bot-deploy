# E2E F — Wildberries

- Дата: 2026-08-07
- Режим: read-only
- Секреты в отчёте: отсутствуют

Код использует:

- FBS: `POST https://marketplace-api.wildberries.ru/api/v3/stocks/{warehouseId}` с `chrtIds`;
- FBW: `POST https://seller-analytics-api.wildberries.ru/api/analytics/v1/stocks-report/wb-warehouses`;
- ошибки не приводятся безусловно к `permission_required`;
- клиент поддерживает `X-Client-Secret`.

Фактический известный FBW-ответ: HTTP 403, safe body `base token without secret is not allowed`. Это доказывает ограничение типа авторизации, а не ошибку категории Analytics. Новый токен не предлагается.

Не заполнены: current production fingerprints по всем процессам, `X-Client-Secret` presence, request ID/Retry-After после конфигурации, FBS warehouse/chrtID и сверка с кабинетом.

**Итог:** BLOCKED — external `X-Client-Secret` не подтверждён; повторная live-диагностика после его настройки ожидается.
