# E2E A — частичное выполнение

- Дата: 2026-08-07
- Code commit: `cf3dcb8`
- Release path: не опубликован
- Тестовые лица: `9122` и `9123`, изолированная SQLite
- Автотест: `test_partial_route_completion_returns_unfinished_quantity_to_free_tasks`

## Фактический auto-результат

Задание 50 шт. взято первым сотрудником. Подтверждено 25 годных и 2 брака. На следующий этап создано 25; брак сохранён отдельно; 23 вернулись свободным заданием и взяты вторым сотрудником. Replay `partial-route-25-of-50` не создал второй остаток.

```text
50 = 25 good + 2 defect + 23 remainder
```

SQL-таблицы auto-сверки: `route_batches`, `route_batch_defects`, `route_batch_inputs`, `warehouse_stock`.

## Живая приёмка

Действия в авторизованном UI, production IDs, SQL до/после, movement journal и скриншоты ещё не заполнены.

**Итог:** AUTO PASS; FINAL PENDING.
