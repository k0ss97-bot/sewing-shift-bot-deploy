# Передача проекта — 4 августа 2026

## Production

- Сайт: `https://www.shagaemfabrika.ru/app`
- Production-релиз: `18842cb` — `Link marketplace cards to production and warehouse`
- Рабочая ветка: `codex/wms-integration`
- GitHub: `https://github.com/k0ss97-bot/sewing-shift-bot-deploy`
- Проверка после релиза: `https://www.shagaemfabrika.ru/app` вернул HTTP 200.

## Что добавлено

В разделе **Маркетплейсы → Связи каталога** появился единый read-only каталог:

1. Каждая карточка Ozon/Wildberries показывает артикул, маршрут производства, остаток и адресные ячейки склада.
2. Каждая позиция готовой продукции на складе показывает связанные карточки Ozon и Wildberries.
3. Если у карточки нет маршрута производства или товара нет в ячейках, это явно показано; приложение не создаёт фиктивные остатки и карточки.
4. При включённом PostgreSQL-режиме Ozon складская карточка Wildberries больше не исчезает: она используется как fallback, когда текущая карточка Ozon не найдена.

## Важные технические детали

- Изменённые файлы: `marketplaces.py`, `miniapp_server.py`, `miniapp_assets.py`, `tests/test_marketplaces.py`.
- Ozon в production использует PostgreSQL Phase 1A как основной read model.
- Wildberries пока использует сохранённую общую marketplace-проекцию. Если WB API остатков недоступен, сайт честно показывает, что остаток маркетплейса не подтверждён.
- Физический адресный склад — PostgreSQL WMS. Связь с каталогом строится по безопасному производственному ключу `наименование + размер + цвет`; неподтверждённые связи выводятся как проблема, а не маскируются нулём.
- В текущем интерфейсе новый раздел доступен по адресу `/app/marketplaces/links`.

## Проверки перед релизом

- `python3 -m unittest tests.test_marketplaces tests.test_wms -q` — 54 теста успешно, 12 PostgreSQL-тестов пропущены без доступного тестового сервера.
- `python3 scripts/check_python_compile.py` — успешно.
- `python3 scripts/smoke_web.py` — успешно в изолированной временной БД.
- Полный `scripts/run_unittests_isolated.py`: один старый тест экспорта Excel не запускается в текущем окружении из-за отсутствующего пакета `openpyxl`; к изменениям каталога не относится.

## Как продолжить на другом ПК

```bash
git clone https://github.com/k0ss97-bot/sewing-shift-bot-deploy.git
cd sewing-shift-bot-deploy
git switch codex/wms-integration
git pull --ff-only origin codex/wms-integration
```

Перед изменениями обязательно прочитать `AGENTS.md`. Не открывать и не копировать `.env`, `bot.db`, `backups/`, `exports/` и `logs/`.

Для локальной проверки использовать только изолированные команды:

```bash
python3 scripts/check_python_compile.py
python3 scripts/run_unittests_isolated.py
python3 scripts/smoke_web.py
```

## Если понадобится следующий релиз

Использовать утверждённую процедуру deployment: резервная копия → новый изолированный релиз → compile и smoke → атомарное переключение → restart → локальный и внешний health-check. Не читать файлы окружения и базы production-сервера.
