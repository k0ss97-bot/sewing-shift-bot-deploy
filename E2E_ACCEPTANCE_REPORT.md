# E2E ACCEPTANCE REPORT

**Дата:** 2026-08-07  
**Кандидат:** `e7c48ca6f6447f38d5bdb1fdeb759853d2d0819e`

**Опубликовано:** `/opt/sewing-web/releases/codex-e7c48ca-20260807T100615Z`
**Живая приёмка:** не завершена

| Контур | Код | Тесты | Опубликовано | Живая приёмка | Итог |
|---|---|---|---|---|---|
| Сотрудники и auth | Есть | PASS | Да | invalid Origin 403; unauth mutation 401; signed-in flow pending | IN PROGRESS |
| Смены и операции | Есть | PASS | Да | Нет | IN PROGRESS |
| Производственные задания | Есть | PASS | Да | Нет | IN PROGRESS |
| Раскрой | Есть | PASS | Да | Нет | IN PROGRESS |
| Упаковка → WMS | Есть | PASS | Да | reconciliation success; business event pending | IN PROGRESS |
| WMS | Есть | PASS | Да | Нет/TSD | IN PROGRESS |
| Ozon | Есть | PASS contract | Да | marketplace sync success, health/supplies ready; cabinet reconciliation pending | IN PROGRESS |
| Wildberries | Есть | PASS contract | Базовая версия | HTTP 403 без secret | BLOCKED EXTERNAL |
| Единый каталог | Есть | PASS | Да | Нет | IN PROGRESS |
| Аналитика | Есть | PASS | Да | Нет | IN PROGRESS |
| Backup и monitoring | Есть | PASS | Да | forced backups success; timers/one-shots success | PASS |
| Security | Есть | PASS auth/SAST | Да | CSP/HSTS/origin/auth boundary PASS; signed session pending | IN PROGRESS |

## Автоматическое доказательство

```text
files=19
discovered=249
executed=249
passed=249
failed=0
skipped=0
excluded=0
duplicate_aliases_ignored=6
```

Изолированная PostgreSQL DB и распакованный код удалены после прогона. Production-базы в тестах не использовались.

## Решение о релизе

**NO-GO для отметки «принято на 100%».** Релиз опубликован и технический post-deploy smoke PASS, но A–G и физический TSD не имеют авторизованного живого протокола. Это отдельный приёмочный гейт, который нельзя заменить health-check или автотестами.
