# AUDIT BASELINE — «Шагаем вместе»

**Локальный срез:** 2026-08-07, Asia/Yekaterinburg  
**Серверный срез:** 2026-08-07T12:02:33+03:00  
**Назначение:** исходное состояние перед стабилизацией и сквозной приёмкой.

## 1. Канонический проект

| Параметр | Фактическое значение |
|---|---|
| Абсолютный путь | `/Users/konstantingorskih/Documents/New project/sewing-shift-bot-deploy-wms-ui` |
| Ветка | `codex/wms-integration` |
| Локальный HEAD | `f7cae4ecb29c81b0eed936b2d19afc266dec322f` |
| `origin/codex/wms-integration` | `f7cae4ecb29c81b0eed936b2d19afc266dec322f` |
| GitHub `refs/heads/codex/wms-integration` | `f7cae4ecb29c81b0eed936b2d19afc266dec322f` |
| Базовый коммит ТЗ | `f7cae4ecb29c81b0eed936b2d19afc266dec322f` |
| Совпадение базового коммита | Да |
| Remote | `https://github.com/k0ss97-bot/sewing-shift-bot-deploy.git` |

## 2. Локальное рабочее дерево до новых изменений

```text
 M miniapp_assets.py
 M scripts/smoke_web.py
?? PROJECT_AUDIT_2026-08-07.md
?? scripts/import_stock_snapshot.py
```

Классификация:

| Файл | Состояние | Решение |
|---|---|---|
| `miniapp_assets.py` | локальные исправления аналитики и интерфейса | проверить, покрыть тестами и оформить отдельным коммитом |
| `scripts/smoke_web.py` | проверки регрессий для локальных UI-исправлений | проверить вместе с `miniapp_assets.py` |
| `PROJECT_AUDIT_2026-08-07.md` | новый аудиторский документ | сохранить как документацию проекта |
| `scripts/import_stock_snapshot.py` | пользовательский неотслеживаемый файл | не читать, не изменять, не добавлять в коммит без отдельного решения владельца |

До начала работ `git diff --check` проходил. Diff отслеживаемых файлов составлял 75 добавлений и 26 удалений.

## 3. Документация

ТЗ потребовало прочитать фиксированный набор документов. Фактическое состояние:

| Документ | Статус | Примечание |
|---|---|---|
| `README.md` | отсутствует | есть `README_WEB.md`, но он не заменяет общий README |
| `STATUS.md` | есть, устарел | датирован 2026-07-27, содержит старую ветку, метрики и следующий шаг |
| `DECISIONS.md` | отсутствует | требуется создать |
| `LESSONS.md` | отсутствует | требуется создать |
| `NEXT_ACTION.md` | есть, устарел | датирован 2026-07-27 |
| `AGENTS.md` | есть, прочитан | запрещает чтение runtime-секретов, рабочих баз, backup, export и logs |
| `PROJECT_AUDIT_2026-08-07.md` | есть локально | 33 раздела, подробный реестр реализованного функционала |
| `README_WEB.md` | есть | актуальные базовые инструкции Web/PWA и изолированных тестов |

При расхождении документации с кодом источниками истины считаются текущий код, миграции, Git и отдельно подтверждённый runtime.

## 4. Серверный релиз

| Параметр | Фактическое значение |
|---|---|
| Хост | `shagaemfabrika.ru` |
| Активный release path | `/opt/sewing-web/releases/codex-f7cae4e-20260807T055152Z` |
| Current symlink | указывает на release выше |
| Основной service | `sewing-web.service` |
| Состояние | `active/running` |
| WorkingDirectory | `/opt/sewing-web/current` |
| ExecStart | `/opt/sewing-web/venv/bin/python /opt/sewing-web/current/webapp_server.py` |
| Process start | 2026-08-07 08:54:25 MSK |
| Commit marker | в релизе отсутствует |

Коммит релиза подтверждён именем immutable release-каталога и побайтовым сравнением ключевых файлов:

| Файл | SHA-256 HEAD | SHA-256 сервера | Совпадает |
|---|---|---|---|
| `miniapp_assets.py` | `ee11c5e32681a5a71b969a5b17db39577e5655f31c58f350fabff3b2e0b0d35a` | тот же | Да |
| `scripts/smoke_web.py` | `098b2b53f71544ac19ba8c7767b6b79a49ffef372c1714216633a9104abde9e3` | тот же | Да |

Локальное рабочее дерево уже отличается от сервера:

| Файл | SHA-256 локального рабочего файла |
|---|---|
| `miniapp_assets.py` | `f280301a5665c16e7fec82f752221de582cd1b8da587278ea10b033cb13ec54f` |
| `scripts/smoke_web.py` | `373ba0a8f9f0a8c3dda65ca2a6620bd30a3f5085a22c9c1d25ccd2f3a30039d7` |

Следовательно, локальные UI-исправления не опубликованы.

## 5. Python и зависимости

| Среда | Версия |
|---|---|
| Локальный системный Python | 3.13.14 |
| Локальный `.venv` | отсутствует |
| Серверный Python приложения | 3.12.3 |
| Целевая совместимость по ТЗ | Python 3.11 |
| SHA-256 локального `requirements.txt` | `029fcce43444121543207b439a51b4e221aad9ee603998d53d284a49f96462c9` |

Отклонение: локальная и серверная версии Python не равны целевой 3.11. Автотесты необходимо запускать текущим Python, а перед итоговым релизом отдельно подтвердить CI на Python 3.11.

Фактические серверные зависимости:

```text
aiofiles==25.1.0
aiogram==3.29.0
aiohappyeyeballs==2.7.1
aiohttp==3.14.1
aiosignal==1.4.0
annotated-types==0.7.0
attrs==26.1.0
certifi==2026.6.17
cffi==2.1.0
chardet==7.4.3
charset-normalizer==3.4.9
cryptography==49.0.0
et_xmlfile==2.0.0
frozenlist==1.8.0
http_ece==1.2.1
idna==3.18
magic-filter==1.0.12
multidict==6.7.1
openpyxl==3.1.5
pillow==12.3.0
propcache==0.5.2
psycopg2-binary==2.9.10
py-vapid==1.9.4
pycparser==3.0
pydantic==2.13.4
pydantic_core==2.46.4
python-dotenv==1.2.2
pywebpush==2.1.1
qrcode==8.2
reportlab==4.2.5
requests==2.34.2
six==1.17.0
typing-inspection==0.4.2
typing_extensions==4.16.0
urllib3==2.7.0
yarl==1.24.5
```

## 6. systemd — фактический срез

Постоянно включённые/используемые units:

| Unit | Фактическое состояние/тип |
|---|---|
| `sewing-web.service` | enabled, active/running |
| `sewing-web-backup.timer` | enabled |
| `sewing-wms-backup.timer` | enabled |
| `sewing-web-monitor.timer` | enabled |
| `sewing-web-healthcheck.timer` | enabled |
| `sewing-marketplaces-sync.timer` | enabled, service был `activating` в момент среза |
| `sewing-marketplace-report-export.timer` | enabled |
| `sewing-wms-report-export.timer` | enabled |
| `postgresql@16-main.service` | active/running |
| `caddy.service` | active/running |

Следующие transient/ad-hoc units остались в состоянии `failed` и требуют безопасной классификации/очистки после выяснения назначения:

```text
codex-marketplace-pg-integration.service
codex-marketplace-pg-integration-2.service
run-u20144.service
sewing-marketplace-full-sync-d6d0d42.service
sewing-ozon-supplies-final.service
sewing-wb-sync-29f2d26.service
sewing-wb-sync-29f2d26b.service
sewing-wms-backup-codex-20260806.service
```

Удаление или reset failed на этапе baseline не выполнялись.

## 7. Хранилища и миграции

### SQLite

- Service разрешает запись только в `/var/lib/sewing-web`.
- Конфигурация загружается из `/etc/sewing-web/sewing-web.env`.
- Содержимое environment-файла и рабочей SQLite не читалось.
- Ожидаемый runtime-каталог: `/var/lib/sewing-web`.

### PostgreSQL

- Кластер: PostgreSQL 16, `postgresql@16-main.service` active/running.
- WMS backup unit использует локальный socket `/var/run/postgresql` и базу `sewing_wms`.
- Пароль/DSN с секретами не читались и не публикуются.

### Миграции

В активном релизе присутствуют файлы:

```text
001_initial_wms.sql
002_seed_reference.sql
003_stock_per_location.sql
004_seed_physical_storage.sql
005_marketplace_phase1a.sql
006_marketplace_rich_catalog_orders.sql
007_marketplace_complete_read_model.sql
008_marketplace_read_model_permissions.sql
009_marketplace_ozon_supplies.sql
010_wms_stock_receipts.sql
011_unified_catalog_and_bulk_writeoff.sql
```

Фактически применённый список не запрашивался: `AGENTS.md` запрещает проверкам обращаться к рабочим базам. Его необходимо подтвердить в отдельном авторизованном production DB-аудите после backup, либо штатной командой `python -m wms.migrate --status` под контролем владельца данных.

## 8. Исходные отклонения и риски

1. Обязательные `README.md`, `DECISIONS.md`, `LESSONS.md` отсутствуют.
2. `STATUS.md` и `NEXT_ACTION.md` не соответствуют текущей ветке и релизу.
3. Локальные UI-исправления не опубликованы.
4. В immutable release отсутствует отдельный `COMMIT` marker.
5. Python среды расходятся с целевой 3.11.
6. На сервере остались failed transient test/sync units.
7. Фактически применённые миграции не подтверждены без обращения к рабочей базе.
8. Стандартный test runner ещё не публикует формальный отчёт `discovered/executed/passed/failed/skipped/excluded`.
9. Reconciliation SQLite → PostgreSQL необходимо подтвердить или реализовать.
10. Живые E2E A–G ещё не оформлены доказательствами по шаблону ТЗ.

## 9. Baseline verdict

**Репозиторий и опубликованный релиз совпадают на коммите `f7cae4e` для проверенных файлов.** Локальное рабочее дерево содержит более новые UI-исправления и документацию. Переход к изменению кода допустим после сохранения этого baseline; публикация возможна только после автоматических проверок, E2E-доказательств, backup/rollback и фиксации внешних blockers.

