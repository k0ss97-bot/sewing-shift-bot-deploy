# Самостоятельное веб-приложение и Telegram Mini App

Один интерфейс работает в двух режимах:

- как самостоятельное мобильное веб-приложение (PWA) с логином и паролем;
- как Telegram Mini App с проверкой данных Telegram.

HTML/CSS/JavaScript находятся в `miniapp_assets.py`, HTTP API — в
`miniapp_server.py`, веб-сессии — в `webapp_auth.py`, PWA-ресурсы — в
`webapp_pwa.py`. Режимы используют одну производственную логику и одну SQLite.

## Быстрый тест сайта

Тестовый запуск не использует Telegram и рабочую базу:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python webapp_demo.py --reset --port 8878
```

Откройте `http://127.0.0.1:8878/app`. Тестовые аккаунты:

| Роль | Логин | Пароль |
| --- | --- | --- |
| Администратор | `admin` | `admin-demo-2026` |
| Раскройщик | `cutter` | `cutter-demo-2026` |
| Швея | `sewer` | `sewer-demo-2026` |
| Упаковщик | `packer` | `packer-demo-2026` |

Демонстрационные данные создаются только в `.web-demo-data/`, которая исключена
из Git. Эти пароли нельзя использовать на сервере.

## Требования

- Python 3.11;
- зависимости из `requirements.txt`;
- приватный постоянный каталог для SQLite и резервных копий;
- публичный HTTPS-адрес для рабочего сайта и Telegram Mini App.

## Настройка

Создайте локальный `.env` на основе `.env.example`. Реальные секреты, `.env`,
`bot.db`, выгрузки и резервные копии не должны попадать в Git и CI.

| Переменная | Назначение |
| --- | --- |
| `BOT_TOKEN` | токен Telegram-бота; нужен, пока запускается `main.py` |
| `ADMIN_IDS` | Telegram ID администраторов через запятую |
| `MINIAPP_URL` | публичный HTTPS URL приложения |
| `MINIAPP_HOST`, `PORT` | адрес и порт HTTP-сервера |
| `MINIAPP_DEBUG` | упрощённый локальный вход; на сервере всегда `0` |
| `WEBAPP_ENV` | для сервера значение `production` |
| `WEBAPP_PUBLIC_ORIGIN` | точный внешний origin, например `https://app.example.ru` |
| `WEBAPP_SESSION_TTL_SECONDS` | полный срок сессии, по умолчанию 12 часов |
| `WEBAPP_SESSION_IDLE_SECONDS` | выход при бездействии, по умолчанию 2 часа |
| `WEBAPP_COOKIE_SECURE` | на HTTPS-сервере обязательно `1` |
| `TRUST_PROXY_HEADERS` | `1` только за контролируемым reverse proxy |
| `DB_DIR` | абсолютный путь к приватному постоянному каталогу SQLite |

При `WEBAPP_ENV=production` сервер не запустится с HTTP-origin, небезопасной
cookie или включённым debug-входом. `TRUST_PROXY_HEADERS=1` допустим только если
proxy удаляет входящие пользовательские `X-Forwarded-*` и выставляет свои.

## Веб-аккаунты

Сначала сотрудник должен существовать и быть активным в общей базе. Затем
создайте или обновите его веб-аккаунт, указав тот же Telegram ID:

```bash
DB_DIR=/absolute/path/to/private/data \
  .venv/bin/python webapp_auth.py set-account \
  --username employee-login --telegram-id 123456789
```

Пароль вводится скрыто и не попадает в историю команд. Обновление пароля
автоматически завершает старые веб-сессии пользователя.

## Рабочий запуск

Самостоятельный сайт без запуска Telegram-бота:

```bash
.venv/bin/python webapp_server.py
```

Пока Telegram-бот остаётся частью процесса, общий запуск выполняется так:

```bash
.venv/bin/python main.py
```

Доступность:

```text
GET /health      -> {"ok": true}
GET /app         -> приложение или форма веб-входа
GET /manifest... -> PWA manifest
```

Не запускайте разработку в каталоге с рабочим `bot.db`. Для тестов используйте
только демонстрационный сервер и изолированные проверки.

## Проверки

```bash
python3 scripts/check_python_compile.py
python3 scripts/run_unittests_isolated.py
python3 scripts/smoke_web.py
```

Проверки создают временную SQLite, работают на `127.0.0.1` и не читают рабочую
базу. Smoke-аудит проверяет HTML, PWA, вход, cookie, CSRF, границы авторизации и
локальные ресурсы без скачивания внешнего Telegram-скрипта.

## Перенос истории из старого Telegram-бота

Сотрудники, смены и строки выполненных операций переносятся без замены текущей
базы сайта. Сначала сделайте резервную копию и выполните проверку с откатом:

```bash
.venv/bin/python scripts/import_legacy_bot_data.py \
  --source /path/to/legacy/bot.db \
  --target /var/lib/sewing-web/bot.db
```

Если итоговые количества верны, повторите команду с `--apply`. Импорт можно
запускать повторно: сотрудники сопоставляются по Telegram ID, смены — по
сотруднику, дате и времени начала, а операции — по номеру справочника. Старые
незакрытые смены прошлых дат переносятся как закрытые исторические смены.

## Автоматизация

Workflow `.github/workflows/quality.yml` запускается для pull request, вручную,
при push в `main` и в ветки `codex/**`. Он имеет только `contents: read`, не
получает рабочие данные и не выполняет публикацию или deployment.

Специализированные роли находятся в `.codex/agents/`: `database`, `backend`,
`frontend` и read-only `qa`. Правила изоляции и совместной работы описаны в
`AGENTS.md`. Ни один агент не имеет права автоматически отправлять изменения на
сервер или менять рабочую базу.

## Ubuntu-сервер

Готовые файлы эксплуатации находятся в `deploy/`: systemd-сервисы приложения и
ежедневного SQLite-backup, timer, Caddyfile для HTTPS и безопасные настройки
SSH. На сервере приложение слушает только `127.0.0.1:3000`; наружу открыты Caddy
на 80/443 и SSH по ключу.
