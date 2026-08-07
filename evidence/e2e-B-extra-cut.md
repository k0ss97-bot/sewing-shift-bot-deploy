# E2E B — дополнительный готовый крой

- Дата: 2026-08-07
- Code commit: `cf3dcb8`
- Release path: не опубликован
- Автотест: `test_extra_finished_cut_keeps_original_plan_and_replay_creates_no_duplicate`

## Фактический auto-результат

Кардиган детский, чёрный, 116: 10 контуров × 5 слоёв = 50 плановых. На формировании добавлено +5. `contour_quantity` осталось 10; `formed_quantity` и складской полуфабрикат стали 55. В журнале одна произвольная операция на 5 и одно receipt-движение. Повтор атомарно отклонён и не создал дублей.

SQL-таблицы auto-сверки: `production_task_items`, `cutting_batch_arbitrary_operations`, `warehouse_stock`, `warehouse_stock_movements`.

## Живая приёмка

Авторизованный UI, production IDs, SQL до/после, журнал и скриншоты ещё не заполнены.

**Итог:** AUTO PASS; FINAL PENDING.
