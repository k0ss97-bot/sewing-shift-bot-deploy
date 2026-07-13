"""Create and run an isolated local demo of the standalone web application."""

from __future__ import annotations

import argparse
import os
import sqlite3
import threading
from pathlib import Path


DEMO_USERS = {
    "admin": (99001, "Администратор Демо", "Администратор", "admin-demo-2026"),
    "cutter": (22001, "Раскройщик Демо", "Раскройщик", "cutter-demo-2026"),
    "sewer": (22002, "Швея Демо", "Швея", "sewer-demo-2026"),
    "packer": (22003, "Упаковщик Демо", "Упаковщик", "packer-demo-2026"),
}
DEMO_PRODUCT = "Брюки со стрелками детские"


def _ensure_employee(database, telegram_id: int, full_name: str, position: str, *, admin: bool = False):
    employee = database.get_employee_by_telegram_id(telegram_id)
    if employee is None:
        database.create_employee(telegram_id, full_name, position)
        employee = database.get_employee_by_telegram_id(telegram_id)
    database.update_employee_status(employee[0], "active")
    if admin:
        conn = sqlite3.connect(database.DB_NAME)
        conn.execute(
            "UPDATE employees SET full_name = ?, position = 'Администратор', role = 'admin', status = 'active' WHERE id = ?",
            (full_name, employee[0]),
        )
        conn.commit()
        conn.close()
    return database.get_employee_by_telegram_id(telegram_id)


def seed_demo(db_dir: Path, *, reset: bool = False) -> dict:
    db_dir.mkdir(parents=True, exist_ok=True)
    db_path = db_dir / "bot.db"
    if reset and db_path.exists():
        db_path.unlink()

    os.environ["DB_DIR"] = str(db_dir)
    os.environ["ADMIN_IDS"] = str(DEMO_USERS["admin"][0])

    import database
    from route_maps import PRODUCT_ROUTE_MAPS
    from webapp_auth import init_web_auth, upsert_web_account

    database.init_db()
    init_web_auth()
    employees = {}
    for username, (telegram_id, full_name, position, password) in DEMO_USERS.items():
        employees[username] = _ensure_employee(
            database,
            telegram_id,
            full_name,
            position,
            admin=username == "admin",
        )
        upsert_web_account(username, telegram_id, password)

    conn = sqlite3.connect(database.DB_NAME)
    existing_tasks = conn.execute("SELECT COUNT(*) FROM production_tasks").fetchone()[0]
    existing_batches = conn.execute("SELECT COUNT(*) FROM route_batches").fetchone()[0]
    conn.close()
    admin_employee_id = employees["admin"][0]

    if existing_tasks == 0:
        database.add_fabric_receipt("Ткань", "Чёрный", 6, admin_employee_id, comment="Демонстрационный приход")
        database.add_fabric_receipt("Ткань", "Бежевый", 4, admin_employee_id, comment="Демонстрационный приход")
        database.create_production_task(
            DEMO_PRODUCT,
            ["80", "86"],
            ["Чёрный", "Бежевый"],
            admin_employee_id,
            note="Демонстрационное задание на раскрой",
            fabric_rolls={"Чёрный": 2, "Бежевый": 2},
            priority="high",
        )

    if existing_batches == 0:
        route = PRODUCT_ROUTE_MAPS[DEMO_PRODUCT]
        packer_step = next(index for index, step in enumerate(route) if step["position"] == "Упаковщик")
        sewer_step = next(index for index, step in enumerate(route) if step["position"] == "Швея")
        database.create_route_batch(
            DEMO_PRODUCT,
            "80",
            "Чёрный",
            24,
            admin_employee_id,
            route_step_index=packer_step,
            priority="high",
        )
        database.create_route_batch(
            DEMO_PRODUCT,
            "86",
            "Бежевый",
            18,
            admin_employee_id,
            route_step_index=sewer_step,
            priority="normal",
        )

    return {
        "db_path": str(database.DB_NAME),
        "users": {username: {"telegram_id": values[0], "password": values[3]} for username, values in DEMO_USERS.items()},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Локальный тестовый веб-сайт «Шагаем вместе»")
    parser.add_argument("--db-dir", default=".web-demo-data")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8878)
    parser.add_argument("--reset", action="store_true")
    args = parser.parse_args()

    details = seed_demo(Path(args.db_dir).resolve(), reset=args.reset)
    from miniapp_server import start_miniapp_server

    server = start_miniapp_server("local-web-demo-secret", args.host, args.port, debug=False)
    if server is None:
        raise SystemExit("Не удалось запустить тестовый веб-сайт.")

    print(f"Тестовый сайт: http://{args.host}:{args.port}/app", flush=True)
    print(f"Тестовая база: {details['db_path']}", flush=True)
    for username, user in details["users"].items():
        print(f"{username}: {user['password']}", flush=True)
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
