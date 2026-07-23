# WMS-модуль: схема и план интеграции (Этапы 0–2)

WMS (warehouse management) — складской слой поверх существующего проекта
`sewing-shift-bot-deploy`. Реализует зоны, ячейки, штрихкоды, состояния товара,
неизменяемый журнал движений с идемпотентностью, и складские операции
(приёмка, размещение, перемещение, инвентаризация, списание).

## Архитектура: гибрид SQLite + PostgreSQL

Существующий проект работает на **SQLite** (`bot.db`, ~9700 строк `database.py`).
WMS использует отдельную **PostgreSQL** базу — `warehouse_stock` переезжает туда
как master для склада. Остальное (employees, shifts, fabric_stock, routes)
остаётся в SQLite и **ссылается по integer id без cross-DB FK**.

```
SQLite (без изменений)            PostgreSQL (новый WMS-слой)
──────────────────────            ──────────────────────────
employees ──────┐                 wms_zones
shifts          │ employee_id ──→ wms_locations
fabric_stock    │ (без FK)        wms_item_states
routes          │                 wms_barcodes
warehouse_stock │                 wms_containers
  (legacy, RO)  │                 warehouse_stock (master для WMS)
                │                 wms_movements (immutable журнал)
                └─ bridge ─────→  wms_inventory_counts (+ lines)
                  (SQLite→PG)
```

**Bridge** (`wms/bridge.py`) делает одностороннюю синхронизацию SQLite
`warehouse_stock` → Postgres. Не меняет `database.py`.

## Состав модуля `wms/`

| Файл | Назначение |
|---|---|
| `connection.py` | Postgres-подключение (cached, `WMS_DATABASE_URL` env) |
| `migrate.py` | Применение SQL-миграций с version-трекингом (`schema_migrations`) |
| `models.py` | Dataclass-модели: `ProductKey`, `Zone`, `Location`, `WarehouseStock`, `Movement` |
| `repository.py` | CRUD к Postgres: zones/locations/stock/movements |
| `operations.py` | Складские операции (транзакционные, идемпотентные) |
| `bridge.py` | Синхронизация SQLite `warehouse_stock` → Postgres |
| `barcode.py` | Реестр штрихкодов + парсинг `LOC:` / `LPN:` / товарных |
| `api.py` | HTTP-обработчики для `miniapp_server` |
| `wms_migrations/001_initial_wms.sql` | DDL: зоны, ячейки, штрихкоды, состояния, движения, инвентаризация |
| `wms_migrations/002_seed_reference.sql` | Эталонные зоны (11 шт) + состояния товара (9 шт) |

## Схема данных

### Топология склада
- **`wms_zones`** — зоны: `RECEIVE` (Приёмка), `STORAGE` (Хранение), `PICK`
  (Отбор), `PACK` (Упаковка), `READY_TO_SHIP`, `RETURNS`, `QUARANTINE`,
  `DAMAGED`, `PRODUCTION`, `TRANSIT`. 11 эталонных зон из плана §5.1.
- **`wms_locations`** — ячейки с кодом (`A-03-02`), штрихкодом (`LOC:A-03-02`),
  зоной, приоритетом отбора, статусом (`active`/`blocked`/`inventory`).

### Идентификация товара
Товар идентифицируется бизнес-ключом **`ProductKey`** — кортеж из 6 полей
(унаследован от SQLite `warehouse_stock`):
`(item_type, product_name, product_size, product_color, stage_name, ready_for_position)`.

### Штрихкоды
- **`wms_barcodes`** — реестр: barcode → entity (product/location/container).
- Префиксы: `LOC:` (ячейка), `LPN:` (контейнер), остальное — товар.
- `wms_containers` — короба/палеты/тележки (`LPN:000012589`).

### Состояния товара (9)
`SELLABLE`, `RESERVED`, `PICKED`, `PACKED`, `IN_TRANSIT`,
`RETURN_INSPECTION`, `QUARANTINE`, `DAMAGED`, `SCRAPPED`.

### Журнал движений (`wms_movements`)
Неизменяемый, идемпотентный:
- `request_key TEXT UNIQUE` — повтор = no-op (как `production_trace_events.request_key`).
- `quantity` — знаковое (+ приход, − расход).
- `from_location_id` / `to_location_id`, `from_state` / `to_state`.
- `source_type` (`production`/`order`/`inventory_count`/`manual`), `actor_employee_id`.

### Инвентаризация
- `wms_inventory_counts` (заголовок) + `wms_inventory_count_lines` (строки).
- Слепой пересчёт: `expected_quantity` записывается, но не показывается
  кладовщику. Расхождение → движение `count` с причиной.

## Складские операции (`wms/operations.py`)

| Операция | Функция | Движение |
|---|---|---|
| Приёмка от производства | `receive_from_production()` | `production_receipt`, stock+ в RECEIVE |
| Размещение | `putaway()` | RECEIVE → ячейка хранения |
| Перемещение | `transfer()` | ячейка → ячейка |
| Списание | `scrap()` | SELLABLE → DAMAGED/SCRAPPED/QUARANTINE |
| Инвентаризация | `inventory_count()` | слепой пересчёт → корректировки |

Все транзакционные: `BEGIN` + `SELECT … FOR UPDATE` + проверки + `COMMIT`/
`ROLLBACK`. Все идемпотентные по `request_key`.

## API (для интеграции в `miniapp_server.py`)

Маршруты (добавить в `allowed_paths` + dispatch chain):
```
POST /api/wms/receive     приёмка
POST /api/wms/putaway     размещение
POST /api/wms/transfer    перемещение
POST /api/wms/scrap       списание
POST /api/wms/inventory   инвентаризация
GET  /api/wms/locations   список ячеек
GET  /api/wms/stock       остатки
GET  /api/wms/movements   журнал движений
```

`wms/api.py:handle(path, payload)` возвращает `(status_code, body_dict)`.
`WMS_ROUTES` — множество путей для добавления в `allowed_paths`.

## Конфигурация

```
WMS_DATABASE_URL=postgresql://wms:wms@localhost:5432/wms
```

Новая зависимость: `psycopg2-binary==2.9.10` (единственное добавление в
`requirements.txt`).

## Запуск миграций

```bash
python -m wms.migrate           # применить все миграции
python -m wms.migrate --status  # список применённых
```

## Инварианты склада (проверяются тестами)

- `quantity >= 0` всегда.
- `reserved_quantity <= quantity`.
- Сумма остатков по ячейкам = сумма движений.
- Повторный запрос с тем же `request_key` = no-op.
- Движение имеет либо `from`, либо `to` (или оба).

## План интеграции (что осталось)

1. **Postgres на сервере**: поднять PostgreSQL, настроить `WMS_DATABASE_URL`,
   запустить `python -m wms.migrate`.
2. **Bridge**: запустить `sync_warehouse_stock_from_sqlite()` для начального
   копирования SQLite `warehouse_stock` → Postgres.
3. **Создать ячейки**: `wms_locations` для физических зон склада (коды,
   штрихкоды для печати `LOC:`).
4. **miniapp_server**: добавить `WMS_ROUTES` в `allowed_paths` + dispatch.
5. **miniapp_assets (PWA)**: экраны ТСД (приёмка/размещение/перемещение/
   инвентаризация) — отдельная frontend-задача.
6. **Маркетплейсы** (Ozon/WB) — Этап 4, отдельный трек.

## Тесты

```bash
python -m unittest tests.test_wms -v
```

- Pure-Python тесты (ProductKey, barcode, OperationResult) — всегда проходят.
- DB-зависимые тесты (schema, operations, idempotency) — пропускаются, если
  Postgres недоступен; проходят на сервере с БД.

## Что НЕ входит в Этапы 0–2

- Интеграция Ozon/Wildberries — Этап 4.
- Миграция `fabric_stock` в Postgres — только `warehouse_stock`.
- LLM-аналитика (DeepSeek/OpenAI) — Этап 5.
- Авто-распределение остатков по каналам — Этап 3 (резервы).
- PWA-экраны ТСД — frontend-задача; API готово.
