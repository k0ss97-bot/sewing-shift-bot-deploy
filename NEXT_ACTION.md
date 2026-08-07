# NEXT ACTION

**Единственное ближайшее действие:** поднять отдельную PostgreSQL test database, запустить 13 изолированных WMS DB-тестов через `TEST_WMS_DATABASE_URL`, затем зафиксировать полный результат без пропусков.

Критерий завершения:

```text
discovered=243
executed=243
passed=243
failed=0
skipped=0
excluded=0
```

Запрещено подставлять рабочий `WMS_DATABASE_URL`. Runner принимает только `TEST_WMS_DATABASE_URL`, в имени базы которого присутствует `test`.
