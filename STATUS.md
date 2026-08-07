# STATUS — стабилизация «Шагаем вместе»

**Обновлено:** 2026-08-07

**Ветка:** `codex/wms-integration`

**Текущий локальный коммит:** `git HEAD` (код-кандидат `fc7328c` + эксплуатационная документация)

**Опубликованный коммит:** `f7cae4e`

**Активный release:** `/opt/sewing-web/releases/codex-f7cae4e-20260807T055152Z`

## Текущий этап

Выполняется ТЗ «Стабилизация, сквозная приёмка и выпуск эксплуатационного релиза».

| Этап | Статус | Доказательство |
|---|---|---|
| Baseline репозитория и сервера | PASS | `AUDIT_BASELINE.md` |
| Полный test discovery | PASS | 249 discovered/executed/passed, 0 failed/skipped/excluded на отдельной PostgreSQL test DB |
| Compile | PASS | 69 Python-файлов |
| Web smoke | PASS | временная SQLite, loopback, 7 локальных и 0 внешних ресурсов |
| A: частичное выполнение | AUTO PASS | 50 = 25 годных + 2 брака + 23 остатка; replay без дубля; live впереди |
| B: дополнительный крой | AUTO PASS | кардиган, чёрный, 116, +5; план не изменён; replay без дубля; live впереди |
| Учебный режим | CODE/AUTO PASS | persisted admin toggle, статус, actor/time history, snapshot на партии; не опубликован |
| C: упаковка → outbox → WMS | CODE/AUTO PASS | идемпотентная приёмка, retry и reconciliation; live впереди |
| D: ручное оприходование/размещение | AUTO PASS | контрактные и PostgreSQL-тесты; live UI/TSD впереди |
| E: Ozon | PENDING | требуется сверка с кабинетом и live WMS supply |
| F: Wildberries | BLOCKED EXTERNAL | FBW ответил HTTP 403 `base token without secret is not allowed`; secret не подтверждён |
| G: аналитика | LOCAL PASS | UI-исправления протестированы, ещё не опубликованы |
| Backup/restore | ISOLATED PASS | SQLite restore integrity=ok; PostgreSQL 11 миграций, 15 зон, 0 invalid balances; оба production backup timer active/enabled |
| Monitoring | CODE/AUTO PASS | диск 80/90%, RAM, swap, OOM, services, backup, snapshots, outbox, PostgreSQL, reconciliation; новый код не опубликован |
| Security review | IN PROGRESS | базовые защиты и dependency audit PASS; локальный Bandit: 0 high, 76 medium, 22 low; CI high gate добавлен, live headers/threat model впереди |

## Выполнено в текущей стабилизации

- Зафиксирован baseline кода и сервера.
- Test runner находит все тесты и не наследует production `WMS_DATABASE_URL`.
- Добавлен журналируемый переключатель учебного/строгого режима.
- Добавлена read-only reconciliation SQLite packaging/outbox → PostgreSQL WMS и timer раз в 10 минут.
- Reconciliation проверяет пропуски, ProductKey, количества, source ID, дубли, зависшие события и некорректные остатки.
- Исправлены SQL подтверждения critical notification и rollback неудачного read-only PostgreSQL-запроса.
- Закреплены точные приёмочные инварианты A и B.
- Монитор расширен порогами ресурсов и критическими проверками.

## Текущие ограничения

- Коммиты после `f7cae4e` не опубликованы и не развёрнуты.
- Production metadata: `sewing-web.service`, оба backup timer и monitor timer active/enabled; новый `sewing-production-wms-reconcile.timer` отсутствует до публикации кандидата.
- Рабочие базы не читались и не изменялись в unit/integration-тестах.
- На сервере есть failed transient test/sync units; они не удалялись до классификации.
- В активном релизе нет отдельного `COMMIT` marker.
- Сервер использует Python 3.12.3; целевая CI-совместимость — Python 3.11.
- Пользовательский `scripts/import_stock_snapshot.py` не включён в работу и коммиты.

## Quality gate

```text
discovered=249
executed=249
passed=249
failed=0
skipped=0
excluded=0
duplicate_aliases_ignored=6
```

Прогон выполнен на одноразовой серверной PostgreSQL test DB; база и распакованный код после теста удалены.
