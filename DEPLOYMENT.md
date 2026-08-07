# DEPLOYMENT

## Принцип

Релиз создаётся как immutable-каталог `/opt/sewing-web/releases/<commit>-<UTC timestamp>`. Предыдущие каталоги не изменяются. Активация — атомарная смена `/opt/sewing-web/current`.

## Gate до публикации

1. `git status --short` не содержит неожиданных файлов.
2. HEAD и origin совпадают с release commit.
3. Compile, 249 тестов, Web smoke и `git diff --check` прошли.
4. E2E A–G имеют финальный статус; внешний WB blocker доказан без секретов.
5. SQLite и PostgreSQL backup созданы и проверены; rollback готов.

## Активация

1. Записать release commit в файл `COMMIT` внутри нового каталога.
2. Установить unit-файлы и выполнить `systemctl daemon-reload`.
3. Включить `sewing-production-wms-reconcile.timer` и обновлённый `sewing-web-monitor.timer`.
4. Атомарно переключить symlink и перезапустить только целевые сервисы.
5. Проверить `/health`, затем авторизацию, смену, задания, WMS, аналитику, очереди и read-only marketplace sync.

Конкретный release path, commit, backup ID и время переключения фиксируются в `E2E_ACCEPTANCE_REPORT.md`; секреты не записываются.
