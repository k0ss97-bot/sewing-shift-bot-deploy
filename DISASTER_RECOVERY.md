# DISASTER RECOVERY

## Утверждённые цели

- RPO производства и WMS: не более 15 минут.
- RTO производства и WMS: не более 2 часов.
- SQLite до окончательной миграции: ежедневная проверенная локальная копия; фактический риск между копиями должен быть явно виден в мониторе.
- PostgreSQL: ежедневный verified custom dump плюс непрерывный WAL archive для PITR.
- Обе технологии: зашифрованная копия в другом аккаунте/регионе по правилу 3-2-1.

## Защита, реализованная приложением

1. `backup_webapp.py` делает SQLite online backup и `integrity_check`.
2. `backup_wms.py` делает custom dump, выполняет `pg_restore --list`, считает SHA-256 и публикует версию WMS-миграций.
3. `replicate_backups_offsite.py` принимает только отдельный mount point на другом filesystem, атомарно переносит обе копии и повторно сверяет SHA-256.
4. Производственный монитор создаёт отдельные критические события для SQLite, WMS, off-site и PITR.
5. PITR считается исправным только при `archive_mode=on/always`, настроенном `archive_command`, `archive_timeout <= 15 min`, свежем успешном WAL и отсутствии более новой ошибки.

## Что настраивается на сервере

1. Создать отдельный зашифрованный storage/account/region и смонтировать его в `/mnt/sewing-offsite`. Обычная папка и тот же filesystem будут отвергнуты.
2. Создать `/etc/sewing-web/offsite-backup.env` с абсолютными путями `BACKUP_OFFSITE_DIR`, `SQLITE_BACKUP_DIR` и `WMS_BACKUP_DIR`; секреты в репозиторий не помещать.
3. Установить и включить `sewing-offsite-backup.service/.timer`.
4. Настроить WAL uploader в отдельное хранилище, затем применить параметры из `deploy/postgresql-sewing-pitr.conf.example` и проверить `pg_stat_archiver`.
5. После каждого изменения принудительно запустить backup/off-site, затем `sewing-web-monitor.service`. Все четыре backup/PITR-показателя должны быть `true`.

## Проверка восстановления

- Ежемесячно: восстановить SQLite и PostgreSQL dump только в изолированные test-базы, выполнить integrity, migrations и WMS balance checks.
- Ежеквартально: провести бизнес-drill с замером времени до входа сотрудника, открытия задания и контрольного WMS-движения.
- Никогда не восстанавливать проверочную копию поверх production и не использовать URL базы без `test` в имени.
- Протокол каждого drill должен содержать время точки восстановления, фактические RPO/RTO и результат контрольных запросов без персональных данных.
