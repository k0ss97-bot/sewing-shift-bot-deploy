# RELEASE NOTES — кандидат стабилизации

**Дата:** 2026-08-07  
**Ветка:** `codex/wms-integration`  
**База:** `f7cae4ecb29c81b0eed936b2d19afc266dec322f`  
**Статус:** кандидат не опубликован и не развёрнут.

## Изменения

- Полный изолированный test discovery с явными счётчиками и защитой от production PostgreSQL URL.
- Persisted admin toggle учебного/строгого режима с actor/time history; имеющиеся партии сохраняют snapshot.
- Read-only production → WMS reconciliation, журнал, admin-диагностика и systemd timer.
- Мониторинг диска, RAM, swap, OOM, сервисов, backup, marketplace snapshot, outbox, PostgreSQL и reconciliation.
- Исправлен SQL подтверждения critical notification.
- Исправлен rollback кэшируемой PostgreSQL-транзакции после ошибки read-only аналитики.
- Локальные UI-исправления аналитики: единицы tooltip, empty states, mobile navigation, accessibility labels, даты.

## Quality gate

`249 discovered / 249 executed / 249 passed / 0 failed / 0 skipped / 0 excluded` на одноразовой PostgreSQL test DB. Compile и Web smoke проходят.

## Не принято

- Живая авторизованная приёмка A–G.
- Физический TSD.
- Сверка Ozon с кабинетом.
- WB FBW до получения фактического `X-Client-Secret`.
- Test restore обеих баз, live security headers и бизнес-smoke после релиза.
