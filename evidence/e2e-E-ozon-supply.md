# E2E E — Ozon

- Дата: 2026-08-07
- Release path: active release остаётся на `f7cae4e`; кандидат не опубликован
- Режим: read-only для Ozon API; внутренние WMS-задания допустимы

Контрактные тесты каталога, цен, FBO/FBS stocks, orders, returns, finance, rating, supplies, pagination/checkpoints и неполного snapshot прошли.

Не заполнены: фактические sync run IDs, сверка заказов/штук/сумм/FBO/FBS/возвратов/начислений/удержаний с кабинетом, live supply → WMS подбор → история, SQL до/после и скриншоты.

**Итог:** PENDING.
