import os
from urllib.parse import urlencode

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    WebAppInfo,
)

from catalog import format_color_label
from miniapp_auth import create_auth_token


def get_miniapp_url(telegram_id: int | None = None):
    base_url = os.getenv("MINIAPP_URL") or os.getenv("WEBAPP_URL")

    if not base_url:
        return ""

    app_url = f"{base_url.rstrip('/')}/app"
    bot_token = os.getenv("BOT_TOKEN", "")

    if telegram_id is None or not bot_token:
        return app_url

    query = urlencode({"auth": create_auth_token(telegram_id, bot_token)})
    return f"{app_url}?{query}"


def miniapp_inline_keyboard(telegram_id: int | None = None):
    miniapp_url = get_miniapp_url(telegram_id)

    if not miniapp_url:
        return None

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Открыть приложение",
                    web_app=WebAppInfo(url=miniapp_url),
                ),
            ],
        ],
    )


def miniapp_reply_button():
    miniapp_url = get_miniapp_url()

    if not miniapp_url:
        return KeyboardButton(text="Открыть приложение")

    return KeyboardButton(
        text="Открыть приложение",
        web_app=WebAppInfo(url=miniapp_url),
    )


def reply_keyboard(rows):
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                item if isinstance(item, KeyboardButton) else KeyboardButton(text=item)
                for item in row
            ]
            for row in rows
        ],
        resize_keyboard=True,
    )


def navigation_row():
    return [
        InlineKeyboardButton(text="⬅️ Назад", callback_data="nav_back"),
        InlineKeyboardButton(text="❌ Отмена", callback_data="nav_cancel"),
    ]


def employee_keyboard():
    return reply_keyboard([
        [miniapp_reply_button()],
        ["Отчёт", "Закрыть смену"],
        ["Обратная связь"],
        ["Маршрутные карты"],
        ["Админ-панель"],
    ])


def report_keyboard():
    return reply_keyboard([
        ["Отправить отчёт", "Текущий отчёт"],
        ["Изменить отчёт", "Удалить операцию"],
        ["Отчёт за даты", "Назад"],
    ])


def admin_keyboard():
    return reply_keyboard([
        ["Отчёты", "Смены"],
        ["Сотрудники", "Операции"],
        ["Производство"],
        ["Файлы", "В меню сотрудника"],
    ])


def admin_reports_keyboard():
    return reply_keyboard([
        ["Отчёт за сегодня", "Отчёт за месяц"],
        ["Отчёт за период", "Excel за период"],
        ["Отчёт по сотруднику", "Править отчёт"],
        ["Выгрузить отчёт", "Партии раскроя"],
        ["Админ меню"],
    ])


def admin_production_keyboard():
    return reply_keyboard([
        ["Приход ткани", "Остатки ткани"],
        ["Создать задание на раскрой", "Производственные задания"],
        ["Партии раскроя", "Админ меню"],
    ])


def admin_shifts_keyboard():
    return reply_keyboard([
        ["Открытые смены", "Последние смены"],
        ["Удалить смену", "Админ меню"],
    ])


def admin_employees_keyboard():
    return reply_keyboard([
        ["Заявки", "Список сотрудников"],
        ["Активные сотрудники", "Неактивные сотрудники"],
        ["Активировать сотрудника", "Отключить сотрудника"],
        ["Сменить должность"],
        ["Админ меню"],
    ])


def admin_operations_keyboard():
    return reply_keyboard([
        ["Список операций", "Добавить операцию"],
        ["Изменить операцию"],
        ["Скрыть операцию", "Вернуть операцию"],
        ["Админ меню"],
    ])


def admin_files_keyboard():
    return reply_keyboard([
        ["Журнал", "Скачать базу"],
        ["Проверка базы"],
        ["Загрузить базу"],
        ["Создать копию базы", "Ошибки"],
        ["Админ меню"],
    ])


def position_list_text():
    return (
        "1. Швея\n"
        "2. Упаковщик\n"
        "3. Раскройщик\n"
        "4. Ремонт"
    )


def choice_keyboard(prefix: str, items: dict[str, str | dict], with_navigation: bool = True):
    keyboard = []

    for number, item in items.items():
        if isinstance(item, dict):
            label = item.get("name", number)
        else:
            label = item
            if prefix.startswith("report_color"):
                label = format_color_label(label)

        button_text = label if prefix.startswith("report_color") else f"{number}. {label}"

        keyboard.append([
            InlineKeyboardButton(
                text=button_text,
                callback_data=f"{prefix}:{number}",
            )
        ])

    if with_navigation:
        keyboard.append(navigation_row())

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def navigation_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            navigation_row()
        ]
    )


def multi_choice_keyboard(prefix: str, items: dict[str, str], selected_numbers: list[str]):
    keyboard = []
    selected_set = set(selected_numbers)

    for number, label in items.items():
        mark = "☑️" if number in selected_set else "☐"
        display_label = format_color_label(label) if prefix.startswith("report_color") else label
        button_text = f"{mark} {display_label}" if prefix.startswith("report_color") else f"{mark} {number}. {display_label}"

        keyboard.append([
            InlineKeyboardButton(
                text=button_text,
                callback_data=f"{prefix}_toggle:{number}",
            )
        ])

    keyboard.append([
        InlineKeyboardButton(text="✅ Далее", callback_data=f"{prefix}_done"),
    ])
    keyboard.append(navigation_row())

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def progress_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="25%", callback_data="cutting_progress:25"),
                InlineKeyboardButton(text="50%", callback_data="cutting_progress:50"),
            ],
            [
                InlineKeyboardButton(text="75%", callback_data="cutting_progress:75"),
                InlineKeyboardButton(text="100%", callback_data="cutting_progress:100"),
            ],
            navigation_row(),
        ]
    )
