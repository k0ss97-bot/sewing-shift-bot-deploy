#!/usr/bin/env python3
"""One-shot, narrow production correction requested on 2026-08-03."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from database import rename_fabric_stock_color, reset_cutting_tasks_to_contours_entry


EMPLOYEES = ["Курасова Наталия Валерьевна", "Курасова Наталья Валерьевна"]
PRODUCTS = ["Кардиган детский", "Брюки со стрелками детские"]


def main():
    reset = []
    for product_name in PRODUCTS:
        rows = reset_cutting_tasks_to_contours_entry(
            EMPLOYEES[0],
            [product_name],
            replacement_color="Брауни",
            task_ids=[3, 4],
        )
        if not rows:
            for employee_name in EMPLOYEES:
                rows = reset_cutting_tasks_to_contours_entry(
                    employee_name,
                    [product_name],
                    replacement_color="Брауни",
                )
                if rows:
                    break
        if rows:
            reset.extend(rows)
    if not reset:
        raise SystemExit("Не найдены подходящие активные задания или откат заблокирован завершённым следующим этапом.")

    renamed = rename_fabric_stock_color(
        "Ткань",
        "Капучино",
        "Брауни",
        employee_id=None,
        reason="Замена материала по заданию администратора",
    )
    if renamed is None:
        raise SystemExit("Задания откатились, но карточку ткани Капучино не удалось переименовать в Брауни.")

    print(f"Сброшено заданий: {len(reset)}; карточек материала обновлено: {len(renamed)}")


if __name__ == "__main__":
    main()
