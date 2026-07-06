from collections import Counter

from catalog import (
    CUTTING_PRODUCTS,
    PACKING_PRODUCTS,
    PREPARATION_MATERIAL_COLORS,
    PREPARATION_OPERATION_OPTIONS,
    PRODUCT_OPTIONS,
    PRODUCTION_OPERATIONS,
)


def has_bad_color_format(color: str):
    return color != color.strip() or "  " in color or " - " in color or color[:1].islower()


def main():
    errors = []

    for product in sorted(set(CUTTING_PRODUCTS) | set(PACKING_PRODUCTS)):
        options = PRODUCT_OPTIONS.get(product)

        if not options:
            errors.append(f"Нет размеров/цветов для изделия: {product}")
            continue

        if not options.get("sizes"):
            errors.append(f"Нет размеров для изделия: {product}")

        if not options.get("colors"):
            errors.append(f"Нет цветов для изделия: {product}")

    for folder in ["Подготовка", "Нарезание резинки", "Нарезание дублерина", "Дублирование"]:
        if folder not in PRODUCT_OPTIONS:
            errors.append(f"Нет служебной папки в PRODUCT_OPTIONS: {folder}")

    operation_counter = Counter(PRODUCTION_OPERATIONS)
    for operation, count in operation_counter.items():
        if count > 1:
            errors.append(f"Дубль операции: {operation} — {count} раза")

    for name, options in PREPARATION_OPERATION_OPTIONS.items():
        if not options.get("folder"):
            errors.append(f"У подготовки нет папки: {name}")

        if not options.get("sizes"):
            errors.append(f"У подготовки нет размеров: {name}")

        for color in options.get("colors", []):
            if has_bad_color_format(color):
                errors.append(f"Проверь цвет в подготовке {name}: {color}")

    if PREPARATION_MATERIAL_COLORS != ["Черный", "Белый"]:
        errors.append("Цвета материалов подготовки должны быть только: Черный, Белый")

    for product, options in PRODUCT_OPTIONS.items():
        colors = options.get("colors", [])

        for color in colors:
            if has_bad_color_format(color):
                errors.append(f"Проверь цвет в изделии {product}: {color}")

        duplicates = [color for color, count in Counter(colors).items() if count > 1]
        if duplicates:
            errors.append(f"Дубли цветов в изделии {product}: {', '.join(duplicates)}")

    if errors:
        print("Проверка справочника: есть вопросы")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("Проверка справочника: всё хорошо")


if __name__ == "__main__":
    main()
