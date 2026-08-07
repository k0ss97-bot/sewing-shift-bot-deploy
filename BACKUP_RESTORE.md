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

## Протокол изолированного restore 2026-08-07

- SQLite: создана temporary-база, backup скопирован как restored DB, `PRAGMA integrity_check=ok`, найдено 43 таблицы.
- PostgreSQL: одноразовая source test DB мигрирована, `pg_dump` создал custom archive, `pg_restore` восстановил отдельную test DB; подтверждены 11 миграций, 15 зон и 0 некорректных балансов.
- Обе test DB, архив и каталог кода удалены после проверки. Production-базы и production-backups не открывались.

## Production timer metadata 2026-08-07

- `sewing-web-backup.timer`: active/enabled; последний запуск 2026-08-07 03:18:41 MSK.
- `sewing-wms-backup.timer`: active/enabled; последний запуск 2026-08-07 02:30:17 MSK.
- Содержимое production-backups не открывалось; возраст и пригодность последнего production-артефакта должен подтвердить монитор после публикации кандидата.

**Текущий статус:** isolated restore обеих технологий PASS; production backup timers, принудительные pre-release backup и post-deploy monitor PASS.

## Pre-release backup 2026-08-07

- Перед переключением на `e7c48ca` принудительно выполнены `sewing-web-backup.service` и `sewing-wms-backup.service`.
- Оба one-shot завершились `Result=success`, `ExecMainStatus=0`; SQLite — 13:02:32 MSK, PostgreSQL — после старта 13:02:39 MSK.
- Содержимое и имена приватных backup-артефактов не читались и не копировались.
