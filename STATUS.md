# STATUS — стабилизация «Шагаем вместе»

**Обновлено:** 2026-08-07

**Ветка:** `codex/wms-integration`

**Текущий локальный коммит:** `e7c48ca6f6447f38d5bdb1fdeb759853d2d0819e`

**Опубликованный коммит:** `e7c48ca6f6447f38d5bdb1fdeb759853d2d0819e`

**Активный release:** `/opt/sewing-web/releases/codex-e7c48ca-20260807T100615Z`

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
| Учебный режим | DEPLOYED/AUTO PASS | persisted admin toggle, статус, actor/time history, snapshot на партии; авторизованный UI впереди |
| C: упаковка → outbox → WMS | DEPLOYED/AUTO PASS | идемпотентная приёмка, retry и reconciliation; live операция впереди |
| D: ручное оприходование/размещение | AUTO PASS | контрактные и PostgreSQL-тесты; live UI/TSD впереди |
| E: Ozon | LIVE SYNC PASS | штатный marketplace sync завершился success, health/supplies ready; сверка с кабинетом впереди |
| F: Wildberries | BLOCKED EXTERNAL | FBW ответил HTTP 403 `base token without secret is not allowed`; secret не подтверждён |
| G: аналитика | DEPLOYED/AUTO PASS | UI-исправления опубликованы; авторизованные периоды/mobile/performance впереди |
| Backup/restore | PASS PRE-RELEASE | isolated restore PASS; принудительные SQLite и PostgreSQL backup завершились success перед переключением |
| Monitoring | DEPLOYED/PASS | monitor и reconciliation timer active; оба one-shot post-deploy запуска success |
| Security review | IN PROGRESS | dependency audit и SAST high gate PASS; CSP/HSTS/origin/auth boundary live PASS; session cookie/CSRF и threat model впереди |

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

- Авторизованная браузерная сессия для A–G отсутствует: встроенный browser показывает форму входа, Chrome connector не установлен.
- Production metadata: `sewing-web.service`, оба backup timer, monitor timer и `sewing-production-wms-reconcile.timer` active/enabled.
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
