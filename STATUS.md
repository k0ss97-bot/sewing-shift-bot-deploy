# STATUS — текущая стабилизация «Шагаем вместе»

**Обновлено:** 2026-08-09

**Ветка разработки:** `codex/article-first-wms`

Этот файл описывает состояние кода, а не автоматически подтверждает состояние production. Перед выкладкой и при инциденте формируется `release-manifest.json`:

```bash
python3 scripts/build_release_manifest.py --output /path/to/release-manifest.json
```

Manifest содержит полный commit, признак dirty tree, версии и SHA-256 всех WMS-миграций, хеши frontend-исходников, Python и безопасный allowlist feature flags. Секреты и значения токенов в него не попадают.

## Текущий этап

Выполняются исправления из аудита 2026-08-09 последовательно, с тестом после каждого пункта.

| Направление | Состояние кода |
|---|---|
| PostgreSQL request lifecycle | исправлено; соединения возвращаются в ограниченный pool |
| PostgreSQL DB-тесты | PostgreSQL 16 обязателен в CI, skip gate включён |
| Backup / DR | проверка WMS dump, checksum, off-site и PITR status добавлены; внешний mount и WAL uploader требуют настройки инфраструктуры |
| Admin security | TOTP MFA и одноразовые recovery-коды обязательны |
| Frontend performance | shell < 50 КБ, versioned CSS/JS, не более 50 заданий на странице |
| HTTP saturation | перегрузка возвращает 503 + Retry-After вместо обрыва сокета |
| Release identity | manifest создаётся и проверяется в CI |

## Последний локальный quality gate

```text
discovered=283
executed=269
passed=269
failed=0
skipped=14
skip_gate=passed
web_smoke=PASS
python_files_compiled=72
```

14 PostgreSQL-тестов пропущены только локально из-за отсутствия одноразовой test DB. В GitHub Actions PostgreSQL service обязателен и любой skip завершает gate ошибкой.

## Что production не подтверждено этим файлом

- Текущий production commit и активный release-каталог проверяются manifest на сервере.
- Off-site backup считается готовым только на отдельной смонтированной файловой системе.
- PITR считается готовым только после настройки WAL archive и успешного restore drill.
- Изменения этой рабочей ветки не считаются опубликованными без отдельной команды на canary/deploy.
