# E2E D — ручное оприходование и WMS-цикл

- Дата: 2026-08-07
- Code commit: базовая WMS-реализация + кандидат
- Release path: не опубликован
- Автотесты: manual receipt/putaway contracts и 13 PostgreSQL WMS DB tests

## Auto-результат

Поиск артикула/штрихкода, приёмка в `RECEIVE-01`, частичное размещение, перемещение, подбор, защита резерва, неотрицательные балансы и idempotency прошли на одноразовой PostgreSQL test DB.

## Живая приёмка

Ручной UI, production document/movement IDs, SQL до/после, подбор/отгрузка и физический TSD ещё не выполнены.

**Итог:** AUTO PASS; FINAL PENDING.
