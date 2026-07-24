# WMS — HANDOFF для продолжения работы

> Этот документ — полная сводка того, что сделано по складской системе (WMS),
> чтобы другая ИИ/разработчик могла продолжить без потери контекста.
> Дата: 2026-07-22. Ветки: `wms-core` (backend), `wms-ui` (frontend, поверх wms-core).

---

## 1. Контекст проекта

**Репозиторий:** `github.com/k0ss97-bot/sewing-shift-bot-deploy`
**Проект:** швейная фабрика «Шагаем вместе» (shagaemfabrika.ru).
Telegram-бот + PWA для учёта производства: смены, операции, маршруты партий,
остатки тканей и готовой продукции. Стек: Python 3.11, aiogram 3.29, SQLite,
vanilla JS SPA (всё в `miniapp_assets.py`, 7600+ строк инлайн HTML/CSS/JS).

**Задача (из плана на 1800 строк):** построить WMS — единую складскую систему
поверх существующего проекта. Этапы 0-2 (аудит + каталог + складское ядро + ТСД).
Подробный план: см. отдельный документ «Полный план внедрения единой складской
системы» (1800 строк).

---

## 2. Принятые архитектурные решения

1. **Гибрид SQLite + PostgreSQL.** Существующий проект весь на SQLite
   (`database.py` ~9700 строк, raw `sqlite3`). Мигрировать всё на Postgres =
   переписать проект. Решено: **только `warehouse_stock` переезжает в Postgres**
   (как master для WMS); остальное (employees, shifts, fabric_stock, routes)
   остаётся в SQLite и ссылается по integer id без cross-DB FK.
2. **Zero-breakage.** Существующий production (shagaemfabrika.ru, работает 24/7)
   не ломается. `database.py`, `main.py`, `miniapp_server.py` — **не изменены**.
   Новый код живёт в отдельном модуле `wms/`.
3. **Без Ozon/WB на первом этапе.** Маркетплейсы — Этап 4, отдельный трек.
4. **Доступ к ТСД по роли:** `is_admin` ИЛИ `position === "Кладовщик"`
   (функция `canAccessWms()` в JS).
5. **3 ключевые операции сначала:** приёмка (receive), размещение (putaway),
   перемещение (transfer). Инвентаризация и списание — следующая итерация.

---

## 3. Что сделано — backend (ветка `wms-core`, коммит `78b4085`)

### Модуль `wms/` (11 файлов)

| Файл | Назначение | Статус |
|---|---|---|
| `wms/__init__.py` | версия пакета | ✅ готов |
| `wms/connection.py` | Postgres-подключение (cached, `WMS_DATABASE_URL` env) | ✅ готов |
| `wms/migrate.py` | runner SQL-миграций с version-трекингом (`schema_migrations`) | ✅ готов |
| `wms/models.py` | dataclass: `ProductKey` (6-полей), `Zone`, `Location`, `WarehouseStock`, `Movement`, `OperationResult` | ✅ готов |
| `wms/repository.py` | CRUD к Postgres: zones/locations/stock/movements, upsert с `ON CONFLICT` | ✅ готов |
| `wms/operations.py` | **5 складских операций** (receive, putaway, transfer, scrap, inventory_count), транзакционные + идемпотентные | ✅ готов |
| `wms/bridge.py` | синхронизация SQLite `warehouse_stock` → Postgres (read-only к SQLite) | ✅ готов |
| `wms/barcode.py` | реестр штрихкодов + парсинг `LOC:` / `LPN:` / товарных | ✅ готов |
| `wms/api.py` | HTTP-обработчики (`handle(path, payload)`) для miniapp_server | ✅ готов |
| `wms_migrations/001_initial_wms.sql` | DDL: zones, locations, item_states, barcodes, containers, warehouse_stock (PG), movements, inventory | ✅ готов |
| `wms_migrations/002_seed_reference.sql` | seed: 11 зон + 9 состояний товара | ✅ готов |

### Схема БД (Postgres)

Ключевые таблицы (полный DDL в `wms_migrations/001_initial_wms.sql`):
- `wms_zones` — зоны (RECEIVE, STORAGE, PICK, PACK, ... 11 шт, seeded).
- `wms_locations` — ячейки (code `A-03-02`, barcode `LOC:A-03-02`, zone_id, status).
- `wms_item_states` — 9 состояний (SELLABLE, RESERVED, ..., SCRAPPED, seeded).
- `wms_barcodes` — реестр штрихкодов (barcode → entity).
- `wms_containers` — короба/палеты (LPN:...).
- `warehouse_stock` — master для WMS (6-полейный ProductKey + quantity + reserved + item_state + location_id). UNIQUE по (item_type, product_name, size, color, stage, ready_for_position, unit, item_state).
- `wms_movements` — **неизменяемый журнал** с `request_key UNIQUE` (идемпотентность), signed quantity, from/to location, from/to state.
- `wms_inventory_counts` + `wms_inventory_count_lines` — слепой пересчёт.

### Складские операции (`wms/operations.py`)
Все транзакционные (`BEGIN` + `SELECT ... FOR UPDATE` + проверки + `COMMIT`/`ROLLBACK`),
все идемпотентные по `request_key` (повтор = no-op):
- `receive_from_production(product_key, quantity, ...)` — приёмка в RECEIVE.
- `putaway(product_key, quantity, to_location_code, ...)` — RECEIVE → ячейка.
- `transfer(product_key, quantity, from/to_location_code, ...)` — ячейка → ячейка.
- `scrap(product_key, quantity, reason, target_state, ...)` — SELLABLE → DAMAGED/SCRAPPED.
- `inventory_count(location_code, counted, ...)` — слепой пересчёт + корректировки.

### API (`wms/api.py`)
`handle(path, payload) -> (status_code, body_dict)`. Маршруты:
```
POST /api/wms/receive     POST /api/wms/putaway     POST /api/wms/transfer
POST /api/wms/scrap       POST /api/wms/inventory
GET  /api/wms/locations   GET /api/wms/stock        GET /api/wms/movements
```
`WMS_ROUTES` — множество путей для добавления в `miniapp_server.py` `allowed_paths`.

### Тесты (`tests/test_wms.py`)
16 тестов: 10 pure-Python (всегда проходят), 6 БД-зависимых (пропускаются без Postgres).

---

## 4. Что сделано — frontend (ветка `wms-ui`, коммит `2af8f7b`, поверх wms-core)

### Экраны ТСД в `miniapp_assets.py`
3 складских экрана в PWA (vanilla JS, существующие CSS-классы):
- **Приёмка** (`renderWmsReceive`) — форма: товар/размер/цвет/тип/количество → `POST /api/wms/receive`.
- **Размещение** (`renderWmsPutaway`) — товар + целевая ячейка (`LOC:`) + количество → `POST /api/wms/putaway`.
- **Перемещение** (`renderWmsTransfer`) — товар + из ячейки + в ячейку + количество → `POST /api/wms/transfer`.

Доступ: `canAccessWms()` = `is_admin || position === "Кладовщик"`.
Навигация: кнопка «ТСД» в bottom nav (role-gated) + sub-nav на 3 операции.
Сканер: `scanWms()` + `handleWmsScan()` — BarcodeDetector с форматами `[qr_code, code_128, ean_13, code_39]`, dispatch по префиксу `LOC:`/`LPN:`/товар.

### Что НЕ доделано во frontend
- **Инвентаризация и списание** — экраны не написаны (backend готов: `ops.inventory_count`, `ops.scrap`).
- **Product barcode → ProductKey resolve** — `handleWmsScan` пока только показывает штрихкод; нужен `POST /api/wms/barcode` (resolve) — endpoint НЕ написан в `wms/api.py`.
- **Offline-режим ТСД** — не реализован (есть паттерн `completionQueue` в существующем коде как образец).
- **Список ячеек в UI** — `GET /api/wms/locations` есть, но фронтенд его не вызывает (нет подсказок/автодополнения ячеек).

---

## 5. ⚠️ КРИТИЧНО: что ещё НЕ интегрировано

### Backend → miniapp_server (НЕ сделано)
`wms/api.py:handle()` готов, но **НЕ подключён** к `miniapp_server.py`.
Нужно:
1. Добавить `WMS_ROUTES` в `allowed_paths` (множество в `miniapp_server.py` ~строка 4812).
2. В dispatch chain (`if/elif path ==`) добавить вызов `wms_api.handle(path, payload)`.
3. Импорт: `from wms import api as wms_api`.
Это **обязательно** — без этого фронтенд получит 404 на `/api/wms/*`.

### Postgres (НЕ настроен)
Код написан под Postgres, но сервер не поднят. Нужно:
1. Установить PostgreSQL на сервере (или управляемый).
2. Создать БД + пользователя, задать `WMS_DATABASE_URL`.
3. `pip install psycopg2-binary` (уже в `requirements.txt`).
4. `python -m wms.migrate` — применить схему + seed.

### Bridge (НЕ запущен)
`wms/bridge.py:sync_warehouse_stock_from_sqlite()` готов, но не вызывается.
Нужно: запустить однократно после настройки Postgres для начального копирования
SQLite `warehouse_stock` → Postgres.

### Физические ячейки (НЕ созданы)
Зоны seeded (11 шт), но `wms_locations` пусты. Нужно создать ячейки под реальный
склад + напечатать штрихкоды `LOC:`. Нет UI/скрипта для этого — только через
`wms.repository.create_location()` или прямой SQL.

---

## 6. Конвенции проекта (AGENTS.md — соблюдать!)

- **DB_DIR:** каждый тест/demo/smoke запускается с свежим `DB_DIR` (temp dir).
  Перед `import database` установить `DB_DIR` и `cd` в пустую temp-директорию.
- **Зависимости:** НЕ добавлять без approval. Единственная добавленная —
  `psycopg2-binary==2.9.10` (для Postgres).
- **Приватное:** `bot.db`, `.env`, `backups/`, `exports/`, `logs/` — не трогать/коммитить.
- **Проверки:**
  ```bash
  python3 scripts/check_python_compile.py
  python3 scripts/run_unittests_isolated.py
  python3 scripts/smoke_web.py
  ```
- **Push:** никогда без явного запроса пользователя.
- **Язык:** UI-строки на русском, идентификаторы кода на английском.

---

## 7. Как продолжить — пошаговый план

### Шаг A (блокер): подключить WMS API к miniapp_server
```python
# miniapp_server.py, в allowed_paths (~строка 4812):
from wms.api import WMS_ROUTES
allowed_paths = allowed_paths.union(WMS_ROUTES)

# в dispatch chain (где if/elif path == ...):
if path.startswith("/api/wms/"):
    status, body = wms_api.handle(path, request_payload)
    self.send_json(status, body)
    return
```

### Шаг B: поднять Postgres + миграции
```bash
sudo apt install postgresql
sudo -u postgres createuser wms --pwprompt
sudo -u postgres createdb wms --owner=wms
export WMS_DATABASE_URL="postgresql://wms:PASSWORD@localhost:5432/wms"
pip install psycopg2-binary
python -m wms.migrate
```

### Шаг C: начальная синхронизация
```python
import database
from wms.bridge import sync_warehouse_stock_from_sqlite
conn = database.get_db_connection()
print(sync_warehouse_stock_from_sqlite(conn))
```

### Шаг D: создать ячейки склада
Скрипт или UI для `wms.repository.create_location()` — под реальные коды склада.

### Шаг E: доработать frontend
- Экраны inventory + scrap (backend `ops.inventory_count`, `ops.scap` готовы).
- Product barcode resolve (`POST /api/wms/barcode` — написать в `wms/api.py`).
- Подсказки ячеек (вызывать `GET /api/wms/locations`).

---

## 8. Структура веток

```
main (production, НЕ ТРОГАТЬ)
 └── wms-core (backend WMS: модуль wms/ + миграции + тесты, коммит 78b4085)
      └── wms-ui (frontend ТСД: miniapp_assets.py экраны, коммит 2af8f7b)
```
Обе ветки **не запушены** (AGENTS.md: push только по запросу). Для продолжения:
```bash
git clone https://github.com/k0ss97-bot/sewing-shift-bot-deploy.git
git checkout wms-ui   # содержит и backend, и frontend
```

---

## 9. Ключевые файлы для чтения

| Файл | Что |
|---|---|
| `WMS_DESIGN.md` | полная схема БД, операции, API, план интеграции |
| `WMS_HANDOFF.md` | **этот файл** |
| `wms/operations.py` | складские операции (главная бизнес-логика) |
| `wms/api.py` | HTTP-обработчики (контракт с frontend) |
| `wms/repository.py` | CRUD к Postgres |
| `wms_migrations/001_initial_wms.sql` | DDL всех таблиц |
| `miniapp_assets.py` (строки ~6232-6410) | экраны ТСД (renderWms*) |
| `miniapp_assets.py` (строки ~5267-5400) | async-функции wmsReceive/Putaway/Transfer |
| `AGENTS.md` | конвенции проекта (ОБЯЗАТЕЛЬНО прочитать) |

---

## 10. Известные риски

1. **Postgres не поднят** — весь WMS-код нельзя протестировать end-to-end без БД.
2. **API не подключён к miniapp_server** — фронтенд получит 404 (Шаг A — блокер).
3. **Двойной учёт** — пока bridge синхронизирует SQLite→Postgres, но операции ТСД
   пишут ТОЛЬКО в Postgres. Legacy-код (production routes) пишет в SQLite.
   Возможна рассинхронизация. Решение: либо bridge в обе стороны, либо перевести
   legacy на запись в Postgres.
4. **product_name как строка** — нет barcode-привязки товаров (штрихкод → ProductKey).
   Без этого сканер товара бесполезен. Нужен `wms_barcodes` + endpoint resolve.
5. **openpyxl не установлен локально** — 1 тест падает (не связано с WMS).
