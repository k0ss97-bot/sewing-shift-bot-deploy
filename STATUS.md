# STATUS — стабилизация «Шагаем вместе»

**Обновлено:** 2026-08-07

**Ветка:** `codex/wms-integration`

**Текущий локальный коммит:** `3a0dc6f`

**Опубликованный коммит:** `f7cae4e`

**Активный release:** `/opt/sewing-web/releases/codex-f7cae4e-20260807T055152Z`

## Текущий этап

Выполняется ТЗ «Стабилизация, сквозная приёмка и выпуск эксплуатационного релиза».

| Этап | Статус | Доказательство |
|---|---|---|
| Baseline репозитория и сервера | PASS | `AUDIT_BASELINE.md` |
| Полный test discovery | PASS | 243 discovered, 230 passed, 13 skipped, 0 failed/excluded |
| Локальный compile | PASS | 69 Python-файлов |
| Web smoke | PASS | временная SQLite, loopback, 7 локальных и 0 внешних ресурсов |
| A: частичное выполнение | AUTO PASS | unit/integration тесты; живая приёмка впереди |
| B: дополнительный крой | AUTO PASS | unit/integration тесты; живая приёмка впереди |
| Учебный режим | CODE PASS | добавлен admin toggle, статус и журнал; не опубликовано |
| C: упаковка → outbox → WMS | CODE/AUTO PASS | добавлен reconciliation; живая приёмка впереди |
| D: ручное оприходование/размещение | AUTO PASS | контрактные тесты; живой TSD впереди |
| E: Ozon | PENDING | требуется сверка с кабинетом и live WMS supply |
| F: Wildberries | BLOCKED EXTERNAL | FBW требует подтверждённый `X-Client-Secret` |
| G: аналитика | LOCAL PASS | UI-исправления протестированы, ещё не опубликованы |
| Backup/restore | PENDING | units включены; restore в тестовый контур не выполнен |
| Security review | PENDING | базовые механизмы есть, отдельный отчёт впереди |

## Выполнено в текущей стабилизации

- Созданы `PROJECT_AUDIT_2026-08-07.md` и `AUDIT_BASELINE.md`.
- Подтверждено совпадение origin и сервера с `f7cae4e` для проверенных файлов.
- Исправлен test runner: тесты из корня и `tests/` запускаются одной командой.
- Запрещено наследование production `WMS_DATABASE_URL` в unit-тестах.
- Добавлена проверка безопасного имени отдельной PostgreSQL test database.
- Добавлены точные счётчики discovered/executed/passed/failed/skipped/excluded.
- Добавлен журналируемый переключатель учебного/строгого режима для новых партий.
- Добавлен read-only reconciliation SQLite packaging/outbox → PostgreSQL WMS.
- Reconciliation проверяет отсутствие записей, ProductKey, количество, source ID, повторы, зависшие события и некорректные остатки.
- Результат reconciliation сохраняется и показывается администратору.
- Добавлен systemd timer reconciliation раз в 10 минут.
- Монитор формирует критическое уведомление при расхождении или устаревшей сверке.
- Исправлена SQL-ошибка подтверждения критического уведомления.
- Проверены локальные исправления единиц аналитики, mobile navigation, accessibility и дат.

## Текущие ограничения

- Новые коммиты `9b991b2` и `3a0dc6f` не опубликованы.
- 13 PostgreSQL WMS-тестов пропущены: локальная отдельная test DB недоступна.
- Рабочие базы не читались и не изменялись во время локальной проверки.
- На сервере есть failed transient test/sync units; они не удалялись без отдельной классификации.
- В релизе нет отдельного `COMMIT` marker.
- Сервер использует Python 3.12.3, целевая CI-совместимость — Python 3.11.
- Пользовательский `scripts/import_stock_snapshot.py` не включён в работу и коммиты.

## Quality gate

```text
discovered=243
executed=230
passed=230
failed=0
skipped=13
excluded=0
duplicate_aliases_ignored=6
```

Причина 13 пропусков: `Postgres not reachable at WMS_DATABASE_URL` для явно тестовой `wms_test` базы.
