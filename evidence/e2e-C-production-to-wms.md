# E2E C — упаковка → outbox → RECEIVE-01

- Дата: 2026-08-07
- Code commit: `3a0dc6f`, fix `7808c47`
- Release path: не опубликован
- Автотесты: `test_final_packaging_receives_finished_goods_in_wms_once`, `test_failed_wms_receipt_stays_queued_and_retries`, reconciliation tests

## Auto-результат

Только финальная упаковка создаёт outbox. ProductKey сохраняет изделие/размер/цвет/стадию. Replay с тем же request key не повторяет приёмку. При отказе PostgreSQL событие остаётся `failed`, а `attempts`/`last_error` обновляются; после retry оно становится `sent` без дубля. Reconciliation проверяет SQLite/WMS и пингует монитор.

## Живая приёмка

Production batch/outbox/movement IDs, PostgreSQL SQL до/после, `RECEIVE-01`, повторная доставка и скриншоты ещё не заполнены.

**Итог:** AUTO PASS; FINAL PENDING.
