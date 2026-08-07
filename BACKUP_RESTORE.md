# BACKUP AND RESTORE

## SQLite

`scripts/backup_webapp.py` открывает источник read-only, делает SQLite online backup в temporary-файл, выполняет `PRAGMA integrity_check`, ставит права `0600`, атомарно переименовывает и ограничивает retention 3–90 копиями.

Тест restore должен копировать выбранную копию в отдельный temporary-каталог, запустить `PRAGMA integrity_check` и контрольные read-only запросы. Рабочий `bot.db` не заменяется.

## PostgreSQL

`scripts/backup_wms.py` запускает `pg_dump --format=custom --no-owner --no-acl`, проверяет архив через `pg_restore --list`, ставит `0600`, атомарно переименовывает и ограничивает retention.

Тест restore выполняется только в отдельную базу с `test` в имени. После restore проверяются миграции, балансы, отсутствие отрицательных остатков и `pg_restore` exit code. Одноразовая база удаляется после протокола.

## Расписание и SLA

- `sewing-web-backup.timer`: SQLite ежедневно; монитор считает копию устаревшей после 26 часов.
- `sewing-wms-backup.timer`: PostgreSQL ежедневно.
- Кэши, browser profiles, `venv` и сами release-каталоги в ежедневный backup не входят.

**Текущий статус:** контрактные автотесты PASS; фактический test restore обеих баз и сверка live timers ещё не приняты.
