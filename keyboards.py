from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from catalog import format_color_label


def employee_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Отчёт"),
                KeyboardButton(text="Закрыть смену"),
            ],
            [
                KeyboardButton(text="Обратная связь"),
            ],
            [
                KeyboardButton(text="Маршрутные карты"),
            ],
            [
                KeyboardButton(text="Админ-панель"),
            ],
        ],
        resize_keyboard=True,
    )


def report_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Отправить отчёт"),
                KeyboardButton(text="Текущий отчёт"),
            ],
            [
                KeyboardButton(text="Изменить отчёт"),
                KeyboardButton(text="Удалить операцию"),
            ],
            [
                KeyboardButton(text="Отчёт за даты"),
                KeyboardButton(text="Назад"),
            ],
        ],
        resize_keyboard=True,
    )


def admin_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Отчёты"),
                KeyboardButton(text="Смены"),
            ],
            [
                KeyboardButton(text="Сотрудники"),
                KeyboardButton(text="Операции"),
            ],
            [
                KeyboardButton(text="Файлы"),
                KeyboardButton(text="В меню сотрудника"),
            ],
        ],
        resize_keyboard=True,
    )


def admin_reports_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Отчёт за сегодня"),
                KeyboardButton(text="Отчёт за месяц"),
            ],
            [
                KeyboardButton(text="Отчёт за период"),
                KeyboardButton(text="Excel за период"),
            ],
            [
                KeyboardButton(text="Отчёт по сотруднику"),
                KeyboardButton(text="Править отчёт"),
            ],
            [
                KeyboardButton(text="Выгрузить отчёт"),
                KeyboardButton(text="Партии раскроя"),
            ],
            [
                KeyboardButton(text="Админ меню"),
            ],
        ],
        resize_keyboard=True,
    )


def admin_shifts_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Открытые смены"),
                KeyboardButton(text="Последние смены"),
            ],
            [
                KeyboardButton(text="Удалить смену"),
                KeyboardButton(text="Админ меню"),
            ],
        ],
        resize_keyboard=True,
    )


def admin_employees_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Заявки"),
                KeyboardButton(text="Список сотрудников"),
            ],
            [
                KeyboardButton(text="Активные сотрудники"),
                KeyboardButton(text="Неактивные сотрудники"),
            ],
            [
                KeyboardButton(text="Активировать сотрудника"),
                KeyboardButton(text="Отключить сотрудника"),
            ],
            [
                KeyboardButton(text="Сменить должность"),
            ],
            [
                KeyboardButton(text="Админ меню"),
            ],
        ],
        resize_keyboard=True,
    )


def admin_operations_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Список операций"),
                KeyboardButton(text="Добавить операцию"),
            ],
            [
                KeyboardButton(text="Изменить операцию"),
            ],
            [
                KeyboardButton(text="Скрыть операцию"),
                KeyboardButton(text="Вернуть операцию"),
            ],
            [
                KeyboardButton(text="Админ меню"),
            ],
        ],
        resize_keyboard=True,
    )


def admin_files_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Журнал"),
                KeyboardButton(text="Скачать базу"),
            ],
            [
                KeyboardButton(text="Проверка базы"),
            ],
            [
                KeyboardButton(text="Загрузить базу"),
            ],
            [
                KeyboardButton(text="Создать копию базы"),
                KeyboardButton(text="Ошибки"),
            ],
            [
                KeyboardButton(text="Админ меню"),
            ],
        ],
        resize_keyboard=True,
    )


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
        keyboard.append([
            InlineKeyboardButton(text="⬅️ Назад", callback_data="nav_back"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="nav_cancel"),
        ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def navigation_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⬅️ Назад", callback_data="nav_back"),
                InlineKeyboardButton(text="❌ Отмена", callback_data="nav_cancel"),
            ]
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
    keyboard.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data="nav_back"),
        InlineKeyboardButton(text="❌ Отмена", callback_data="nav_cancel"),
    ])

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
            [
                InlineKeyboardButton(text="⬅️ Назад", callback_data="nav_back"),
                InlineKeyboardButton(text="❌ Отмена", callback_data="nav_cancel"),
            ],
        ]
    )
