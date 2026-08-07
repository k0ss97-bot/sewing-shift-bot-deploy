# Шагаем вместе

Операционная платформа швейного производства: Telegram-бот, Web/PWA/Mini App, производственные маршруты, адресный склад WMS, read-only интеграции Ozon/Wildberries, единый каталог и аналитический центр.

## Канонический контур

- Репозиторий: `k0ss97-bot/sewing-shift-bot-deploy`.
- Рабочая ветка: `codex/wms-integration`.
- Production Web: `https://www.shagaemfabrika.ru/app`.
- SQLite: сотрудники, смены и производство.
- PostgreSQL: адресный WMS и marketplace read models.

## Основной процесс

```text
сотрудник → смена → задание → раскрой → маршрут → упаковка
→ SQLite outbox → WMS RECEIVE-01 → размещение → подбор → аналитика
```

## Основные модули

| Модуль | Назначение |
|---|---|
| `database.py` | SQLite-схема и производственная бизнес-логика |
| `main.py` | Telegram-бот |
| `miniapp_server.py` | Web API |
| `miniapp_assets.py` | Web/PWA интерфейс |
| `route_maps.py` | производственные маршруты |
| `wms/` | PostgreSQL WMS |
| `marketplaces.py`, `marketplace_pg.py` | Ozon/WB read models |
| `analytics_overview.py` | аналитический срез |
| `production_wms_reconciliation.py` | сверка упаковки, outbox и WMS |

## Безопасная локальная проверка

Рабочие `.env`, `bot.db`, backups, exports и logs не используются.

```bash
python3 scripts/check_python_compile.py
python3 scripts/run_unittests_isolated.py
python3 scripts/smoke_web.py
git diff --check
```

PostgreSQL-тесты запускаются только с отдельной тестовой базой:

```bash
TEST_WMS_DATABASE_URL='postgresql://user:password@127.0.0.1:5432/sewing_wms_test' \
python3 scripts/run_unittests_isolated.py
```

Runner отвергает URL, если имя базы не содержит `test`.

## Документация

- `PROJECT_AUDIT_2026-08-07.md` — полный функциональный аудит.
- `AUDIT_BASELINE.md` — исходное состояние стабилизации.
- `STATUS.md` — текущая матрица выполнения.
- `NEXT_ACTION.md` — ровно одно ближайшее действие.
- `README_WEB.md` — Web/PWA и authentication.
- `WMS_DESIGN.md` — устройство адресного склада.
- `DECISIONS.md` — принятые архитектурные решения.
- `LESSONS.md` — обнаруженные ошибки и предотвращение повторов.
- `RELEASE_NOTES.md`, `DEPLOYMENT.md`, `ROLLBACK.md` — release gate, выкладка и откат.
- `BACKUP_RESTORE.md` — backup/restore SQLite и PostgreSQL.
- `SECURITY_REVIEW.md` — защитные механизмы, риски и release gate.
- `CATALOG_AUDIT.md` — правила аудита Ozon/WB ↔ производство.
- `E2E_ACCEPTANCE_REPORT.md` и `evidence/` — матрица приёмки и протоколы A–G.

## Production

Развёртывание выполняется immutable release-каталогами под `/opt/sewing-web/releases/` с атомарным переключением `/opt/sewing-web/current`. Успешный `/health` подтверждает readiness, но не заменяет авторизованный бизнес-smoke и проверку целевых движений.
