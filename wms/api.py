"""HTTP handlers for the WMS layer, designed to plug into miniapp_server.

Each handler takes the already-parsed JSON ``payload`` and the authenticated
``telegram_id`` (resolved upstream the same way existing routes do), and
returns ``(status_code, body_dict)``. The dispatch is intentionally simple so
it can be wired into the existing ``MiniAppRequestHandler`` ``if/elif`` chain
without pulling in a framework.

Routes (to be added to ``allowed_paths`` + dispatch in miniapp_server.py):

    POST /api/wms/receive     receive_from_production
    POST /api/wms/putaway     putaway
    POST /api/wms/transfer    transfer
    POST /api/wms/pick        pick from location
    POST /api/wms/scrap       scrap
    POST /api/wms/inventory   inventory_count
    GET  /api/wms/locations   list_locations
    GET  /api/wms/stock       get_stock_rows
    GET  /api/wms/movements   list_movements
"""

from __future__ import annotations

import logging
import re
import unicodedata
from typing import Any

from . import operations as ops
from . import repository as repo
from .barcode import (
    PHYSICAL_LOCATION_PATTERN,
    barcode_lookup_candidates,
    normalize_scanned_barcode,
    register_product_barcode,
    resolve_product_barcode,
)
from .connection import get_pg_connection
from .models import ProductKey


def handle(
    path: str,
    payload: dict[str, Any],
    *,
    employee_id: int,
) -> tuple[int, dict[str, Any]]:
    """Dispatch one WMS request.  Returns (http_status, body)."""
    try:
        if path == "/api/wms/receive":
            return _receive(payload, employee_id)
        if path == "/api/wms/material-receive":
            return _material_receive(payload, employee_id)
        if path == "/api/wms/stock-receipts/post":
            return _post_stock_receipt(payload, employee_id)
        if path == "/api/wms/putaway":
            return _putaway(payload, employee_id)
        if path == "/api/wms/transfer":
            return _transfer(payload, employee_id)
        if path == "/api/wms/pick":
            return _pick(payload, employee_id)
        if path in {"/api/wms/scrap", "/api/wms/admin/scrap"}:
            return _scrap(payload, employee_id)
        if path in {"/api/wms/inventory", "/api/wms/admin/inventory"}:
            return _inventory(payload, employee_id)
        if path == "/api/wms/admin/bulk-writeoff":
            return _bulk_writeoff(payload, employee_id)
        if path == "/api/wms/admin/product-lookup":
            return _admin_product_lookup(payload)
        if path == "/api/wms/locations":
            return _locations(payload)
        if path == "/api/wms/stock":
            return _stock(payload)
        if path == "/api/wms/movements":
            return _movements(payload)
        if path == "/api/wms/stock-receipts":
            return _stock_receipts(payload)
        if path == "/api/wms/barcode/resolve":
            return _resolve_barcode(payload)
        if path == "/api/wms/barcode/register":
            return _register_barcode(payload)
        if path == "/api/wms/locations/create":
            return _create_location(payload)
        return 404, {"ok": False, "message": "Складской маршрут не найден."}
    except KeyError as exc:
        return 400, {"ok": False, "message": f"Не заполнено обязательное поле: {exc}."}
    except ValueError as exc:
        return 400, {"ok": False, "message": str(exc)}
    except Exception:  # pragma: no cover - defensive
        logging.exception("WMS request failed: %s", path)
        return 500, {"ok": False, "message": "Внутренняя ошибка складской системы."}


# ──────────────────────────────────────────────────────────────────────
# POST handlers
# ──────────────────────────────────────────────────────────────────────


def _pk(payload: dict[str, Any]) -> ProductKey:
    return ProductKey.from_dict(payload["product_key"])


def _receive(payload: dict[str, Any], employee_id: int) -> tuple[int, dict[str, Any]]:
    result = ops.receive_from_production(
        _pk(payload),
        int(payload["quantity"]),
        employee_id=employee_id,
        request_key=payload.get("request_key"),
        reason=payload.get("reason"),
        tsd_device_id=payload.get("tsd_device_id"),
    )
    return _result_response(result)


def _material_receive(payload: dict[str, Any], employee_id: int) -> tuple[int, dict[str, Any]]:
    material_name = str(payload.get("material_name") or "").strip()
    product_color = str(payload.get("product_color") or "").strip()
    unit = str(payload.get("unit") or "рул").strip()
    if not material_name:
        raise ValueError("Введите название материала.")
    if not product_color:
        raise ValueError("Введите цвет материала.")
    if len(material_name) > 120 or len(product_color) > 120:
        raise ValueError("Название материала и цвет должны быть не длиннее 120 символов.")
    if unit != "рул":
        raise ValueError("Пока ручная приёмка материалов поддерживает только рулоны.")
    product_key = ProductKey(
        item_type="material",
        product_name=material_name,
        product_size="—",
        product_color=product_color,
        stage_name="Материал",
        ready_for_position="Склад",
    )
    result = ops.receive_material(
        product_key,
        int(payload["quantity"]),
        unit=unit,
        employee_id=employee_id,
        request_key=payload.get("request_key"),
        reason=payload.get("reason") or "Ручная приёмка материала",
        tsd_device_id=payload.get("tsd_device_id"),
    )
    return _result_response(result)


def _post_stock_receipt(payload: dict[str, Any], employee_id: int) -> tuple[int, dict[str, Any]]:
    raw_lines = payload.get("lines")
    if not isinstance(raw_lines, list) or not raw_lines:
        raise ValueError("Добавьте хотя бы один товар в документ.")
    if len(raw_lines) > 500:
        raise ValueError("В одном документе можно оприходовать не более 500 позиций.")

    lines: list[tuple[str, ProductKey, int]] = []
    for index, raw_line in enumerate(raw_lines, start=1):
        if not isinstance(raw_line, dict):
            raise ValueError(f"Строка {index}: неверный формат.")
        barcode = normalize_scanned_barcode(str(raw_line.get("barcode") or ""))
        if not barcode:
            raise ValueError(f"Строка {index}: штрихкод не указан.")
        if len(barcode) > 128:
            raise ValueError(f"Строка {index}: штрихкод слишком длинный.")
        product_key = _resolve_known_product(barcode)
        if product_key is None:
            raise ValueError(f"Строка {index}: штрихкод {barcode} не зарегистрирован.")
        if product_key.item_type != "finished":
            raise ValueError(f"Строка {index}: оприходовать можно только готовую продукцию.")
        raw_quantity = raw_line.get("quantity")
        if isinstance(raw_quantity, bool) or (
            isinstance(raw_quantity, float) and not raw_quantity.is_integer()
        ) or (
            isinstance(raw_quantity, str)
            and not re.fullmatch(r"[+]?[0-9]+", raw_quantity.strip())
        ):
            raise ValueError(f"Строка {index}: количество должно быть целым числом.")
        try:
            quantity = int(raw_quantity)
        except (TypeError, ValueError) as error:
            raise ValueError(f"Строка {index}: количество должно быть целым числом.") from error
        lines.append((barcode, product_key, quantity))

    result = ops.post_stock_receipt(
        lines,
        employee_id=employee_id,
        request_key=str(payload.get("request_key") or ""),
        comment=str(payload.get("comment") or ""),
        tsd_device_id=str(payload.get("tsd_device_id") or "")[:120] or None,
    )
    body = {
        "ok": result.ok,
        "status": result.status,
        "receipt_id": result.receipt_id,
        "number": result.number,
        "lines_count": result.lines_count,
        "total_quantity": result.total_quantity,
    }
    if result.reason:
        body["reason"] = result.reason
        body["message"] = result.reason
    if result.skipped_duplicate:
        body["duplicate"] = True
    return (200 if result.skipped_duplicate else 201) if result.ok else 409, body


def _putaway(payload: dict[str, Any], employee_id: int) -> tuple[int, dict[str, Any]]:
    result = ops.putaway(
        _pk(payload),
        int(payload["quantity"]),
        to_location_code=payload["to_location_code"],
        unit=str(payload.get("unit") or "шт").strip(),
        employee_id=employee_id,
        request_key=payload.get("request_key"),
        reason=payload.get("reason"),
        tsd_device_id=payload.get("tsd_device_id"),
    )
    return _result_response(result)


def _transfer(payload: dict[str, Any], employee_id: int) -> tuple[int, dict[str, Any]]:
    result = ops.transfer(
        _pk(payload),
        int(payload["quantity"]),
        from_location_code=payload["from_location_code"],
        to_location_code=payload["to_location_code"],
        unit=str(payload.get("unit") or "шт").strip(),
        employee_id=employee_id,
        request_key=payload.get("request_key"),
        reason=payload.get("reason"),
        tsd_device_id=payload.get("tsd_device_id"),
    )
    return _result_response(result)


def _pick(payload: dict[str, Any], employee_id: int) -> tuple[int, dict[str, Any]]:
    result = ops.pick(
        _pk(payload),
        int(payload["quantity"]),
        from_location_code=payload["from_location_code"],
        unit=str(payload.get("unit") or "шт").strip(),
        employee_id=employee_id,
        request_key=payload.get("request_key"),
        reason=payload.get("reason"),
        tsd_device_id=payload.get("tsd_device_id"),
    )
    return _result_response(result)


def _scrap(payload: dict[str, Any], employee_id: int) -> tuple[int, dict[str, Any]]:
    reason = str(payload.get("reason") or "").strip()
    if not reason:
        raise ValueError("Укажите причину списания.")
    result = ops.scrap(
        _pk(payload),
        int(payload["quantity"]),
        reason=reason,
        target_state=payload.get("target_state", "SCRAPPED"),
        from_location_code=payload.get("from_location_code"),
        employee_id=employee_id,
        request_key=payload.get("request_key"),
        tsd_device_id=payload.get("tsd_device_id"),
    )
    return _result_response(result)


def _inventory(
    payload: dict[str, Any],
    employee_id: int,
) -> tuple[int, dict[str, Any]]:
    reason = str(payload.get("reason") or "").strip()
    result = ops.inventory_count(
        payload["location_code"],
        payload["counted"],
        employee_id=employee_id,
        request_key=payload.get("request_key"),
        reason=reason,
    )
    return _result_response(result)


def _bulk_writeoff(payload: dict[str, Any], employee_id: int) -> tuple[int, dict[str, Any]]:
    confirmation = str(payload.get("confirmation") or "").strip()
    if confirmation != "ОЧИСТИТЬ ВЕСЬ СКЛАД":
        raise ValueError("Для полного списания введите: ОЧИСТИТЬ ВЕСЬ СКЛАД")
    reason = str(payload.get("reason") or "").strip()
    if len(reason) < 10:
        raise ValueError("Подробно укажите причину полного списания (не менее 10 символов).")
    request_key = str(payload.get("request_key") or "").strip()
    result = ops.bulk_writeoff_goods(
        reason=reason,
        employee_id=employee_id,
        request_key=request_key,
    )
    if not result.ok:
        return 409, {"ok": False, "status": result.status, "message": result.reason}

    # PostgreSQL is the physical-stock master. Reconcile the retained SQLite
    # shipment documents afterwards; retrying the same request is safe and
    # repairs this projection even if the first HTTP request was interrupted.
    from marketplaces import release_open_warehouse_shipment_reservations_after_stock_clear

    shipment_projection = release_open_warehouse_shipment_reservations_after_stock_clear()
    return 200, {
        "ok": True,
        "status": result.status,
        "writeoff_id": result.writeoff_id,
        "rows_count": result.rows_count,
        "total_quantity": result.total_quantity,
        "released_reserved_quantity": result.released_reserved_quantity,
        "skipped_duplicate": result.skipped_duplicate,
        "shipment_projection": shipment_projection,
        "message": (
            f"Склад обнулён: списано {result.total_quantity} шт. "
            f"по {result.rows_count} строкам; снято резервов {result.released_reserved_quantity} шт."
        ),
    }


# ──────────────────────────────────────────────────────────────────────
# GET handlers
# ──────────────────────────────────────────────────────────────────────


def _locations(payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    conn = get_pg_connection()
    locs = repo.list_locations(conn, zone_code=payload.get("zone_code"))
    return 200, {
        "locations": [
            {
                "id": l.id,
                "code": l.code,
                "barcode": l.barcode,
                "zone_id": l.zone_id,
                "status": l.status,
                "name_ru": l.name_ru,
            }
            for l in locs
        ]
    }


def _create_location(payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    zone_code = str(payload.get("zone_code") or "").strip().upper()
    code = str(payload.get("code") or "").strip().upper()
    if code.startswith("LOC:"):
        code = code[4:].strip()
    if not zone_code or not code:
        return 400, {"ok": False, "message": "Укажите зону и код ячейки."}
    if not re.fullmatch(r"[A-Z0-9][A-Z0-9._/-]{0,63}", code):
        return 400, {"ok": False, "message": "Код ячейки содержит недопустимые символы."}
    conn = get_pg_connection()
    try:
        zone = repo.get_zone_by_code(conn, zone_code)
        if zone is None:
            conn.rollback()
            return 400, {"ok": False, "message": "Неизвестная зона склада."}
        existing = repo.get_location_by_code(conn, code)
        if existing is not None:
            conn.rollback()
            return 409, {"ok": False, "message": "Ячейка с таким кодом уже существует."}
        requested_barcode = str(payload.get("barcode") or "").strip()
        location_barcode = requested_barcode or (
            code if PHYSICAL_LOCATION_PATTERN.fullmatch(code) else None
        )
        location = repo.create_location(
            conn,
            zone_id=zone.id,
            code=code,
            barcode=location_barcode,
            name_ru=str(payload.get("name_ru") or "").strip() or None,
        )
        conn.commit()
        return 201, {
            "ok": True,
            "message": "Ячейка создана.",
            "location": {"id": location.id, "code": location.code, "barcode": location.barcode},
        }
    except Exception:
        conn.rollback()
        raise


def _stock(payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    conn = get_pg_connection()
    raw_location_id = payload.get("location_id")
    location_id = int(raw_location_id) if raw_location_id not in (None, "") else None
    rows = repo.get_stock_rows(
        conn,
        location_id=location_id,
    )
    stock_payload = [
            {
                "id": r.id,
                "product_key": r.product_key.to_dict(),
                "quantity": r.quantity,
                "reserved_quantity": r.reserved_quantity,
                "item_state": r.item_state,
                "location_id": r.location_id,
                "unit": r.unit,
            }
            for r in rows
        ]
    try:
        from marketplaces import marketplace_metadata_for_wms_product_keys

        marketplace_rows = marketplace_metadata_for_wms_product_keys(
            [row["product_key"] for row in stock_payload]
        )
        for row, marketplace_product in zip(stock_payload, marketplace_rows):
            row["marketplace_product"] = marketplace_product
    except Exception:
        logging.exception("WMS stock marketplace metadata enrichment failed")
    return 200, {"stock": stock_payload}


def _stock_receipts(payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    conn = get_pg_connection()
    try:
        limit = max(1, min(int(payload.get("limit", 20)), 100))
        receipts = repo.list_stock_receipts(conn, limit=limit)
        conn.rollback()
        return 200, {"ok": True, "receipts": receipts}
    finally:
        conn.close()


def _normalized_identity(value: Any) -> str:
    return " ".join(
        unicodedata.normalize("NFKC", str(value or ""))
        .strip()
        .replace("ё", "е")
        .casefold()
        .split()
    )


def _same_product_identity(first: ProductKey, second: ProductKey) -> bool:
    if first.product_article or second.product_article:
        return bool(first.product_article) and first.product_article == second.product_article
    return all(
        _normalized_identity(getattr(first, field))
        == _normalized_identity(getattr(second, field))
        for field in ("item_type", "product_name", "product_size", "product_color")
    )


def _marketplace_scan_codes(product: dict[str, Any] | None) -> set[str]:
    if not product:
        return set()
    values = [
        product.get("barcode"),
        product.get("sku"),
        product.get("offer_id"),
        product.get("external_product_id"),
        *list(product.get("barcodes") or []),
    ]
    return {
        candidate
        for value in values
        if value
        for candidate in barcode_lookup_candidates(str(value))
    }


def _stock_row_payload(stock_row: Any) -> dict[str, Any]:
    return {
        "id": stock_row.id,
        "product_key": stock_row.product_key.to_dict(),
        "quantity": stock_row.quantity,
        "reserved_quantity": stock_row.reserved_quantity,
        "item_state": stock_row.item_state,
        "location_id": stock_row.location_id,
        "unit": stock_row.unit,
    }


def _matched_stock_response(stock_row: Any) -> tuple[int, dict[str, Any]]:
    return 200, {
        "ok": True,
        "product_key": stock_row.product_key.to_dict(),
        "matched_in_location": True,
        "stock_row": _stock_row_payload(stock_row),
    }


def _stock_row_for_resolved_product(
    stock_rows: list[Any],
    metadata: list[dict[str, Any] | None],
    product_key: ProductKey,
) -> Any | None:
    for stock_row in stock_rows:
        if _same_product_identity(stock_row.product_key, product_key):
            return stock_row
    for stock_row, marketplace_product in zip(stock_rows, metadata):
        if not marketplace_product:
            continue
        linked_key = ProductKey(
            item_type="finished",
            product_article=str(marketplace_product.get("offer_id") or ""),
            product_name=str(marketplace_product.get("production_product_name") or ""),
            product_size=str(marketplace_product.get("production_size") or ""),
            product_color=str(marketplace_product.get("production_color") or ""),
            stage_name="Упаковано",
            ready_for_position="Склад",
        )
        if linked_key.product_name and _same_product_identity(linked_key, product_key):
            return stock_row
    return None


def _resolve_barcode(payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    barcode = normalize_scanned_barcode(str(payload.get("barcode") or ""))
    if not barcode:
        return 400, {"ok": False, "message": "Штрихкод не указан."}
    if len(barcode) > 128:
        return 400, {"ok": False, "message": "Штрихкод слишком длинный."}
    scanned_codes = set(barcode_lookup_candidates(barcode))
    location_code = str(payload.get("location_code") or "").replace("LOC:", "").strip().upper()
    stock_rows: list[Any] = []
    marketplace_rows: list[dict[str, Any] | None] = []
    if location_code:
        conn = get_pg_connection()
        location = repo.get_location_by_code(conn, location_code)
        if location is not None:
            stock_rows = repo.get_stock_rows(conn, location_id=location.id)
            try:
                from marketplaces import marketplace_metadata_for_wms_product_keys

                marketplace_rows = marketplace_metadata_for_wms_product_keys(
                    [row.product_key.to_dict() for row in stock_rows]
                )
                for stock_row, marketplace_product in zip(stock_rows, marketplace_rows):
                    if scanned_codes & _marketplace_scan_codes(marketplace_product):
                        return _matched_stock_response(stock_row)
            except Exception:
                logging.exception("Location-aware marketplace barcode lookup failed")
    product_key = _resolve_known_product(barcode)
    if product_key is not None and stock_rows:
        stock_row = _stock_row_for_resolved_product(
            stock_rows, marketplace_rows, product_key
        )
        if stock_row is not None:
            return _matched_stock_response(stock_row)
    if product_key is None:
        return 404, {"ok": False, "message": "Штрихкод товара не зарегистрирован."}
    return 200, {"ok": True, "product_key": product_key.to_dict()}


def _admin_product_lookup(payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    query = str(payload.get("query") or "").strip()
    if len(query) < 2:
        return 400, {"ok": False, "message": "Введите минимум 2 символа артикула или штрихкода."}
    if len(query) > 128:
        return 400, {"ok": False, "message": "Артикул или штрихкод слишком длинный."}
    context = str(payload.get("context") or "receipt").strip().lower()
    if context not in {"receipt", "putaway"}:
        return 400, {"ok": False, "message": "Неизвестный режим ручного поиска."}

    from unified_catalog import lookup_products

    products = lookup_products(query, limit=20)
    if context == "receipt":
        products = [product for product in products if product.get("barcode")]
    else:
        conn = get_pg_connection()
        receive = repo.get_location_by_code(conn, "RECEIVE-01")
        stock_rows = repo.get_stock_rows(conn, location_id=receive.id) if receive else []
        marketplace_rows: list[dict[str, Any] | None] = [None] * len(stock_rows)
        if stock_rows:
            try:
                from marketplaces import marketplace_metadata_for_wms_product_keys

                marketplace_rows = marketplace_metadata_for_wms_product_keys(
                    [row.product_key.to_dict() for row in stock_rows]
                )
            except Exception:
                logging.exception("Manual putaway marketplace metadata lookup failed")
        available_products = []
        for product in products:
            stock_row = _stock_row_for_resolved_product(
                stock_rows,
                marketplace_rows,
                ProductKey.from_dict(product["product_key"]),
            )
            available = (
                max(0, int(stock_row.quantity) - int(stock_row.reserved_quantity))
                if stock_row is not None
                else 0
            )
            if available <= 0:
                continue
            product = dict(product)
            product["product_key"] = stock_row.product_key.to_dict()
            product["receive_available"] = available
            product["stock_row"] = _stock_row_payload(stock_row)
            available_products.append(product)
        products = available_products
        conn.rollback()

    if not products:
        message = (
            "Товар не найден среди доступных остатков зоны приёмки."
            if context == "putaway"
            else "Товар с таким артикулом или штрихкодом не найден."
        )
        return 404, {"ok": False, "message": message, "products": []}
    return 200, {"ok": True, "query": query, "context": context, "products": products}


def _resolve_known_product(barcode: str) -> ProductKey | None:
    product_key = resolve_product_barcode(barcode)
    if product_key is not None:
        return product_key
    # Marketplace cards are the master for finished-goods labels. A safe
    # automatic link exists only for variants mapped to a production route.
    try:
        from marketplaces import resolve_production_product_by_barcode

        marketplace_key = resolve_production_product_by_barcode(barcode)
        return ProductKey.from_dict(marketplace_key) if marketplace_key else None
    except Exception:
        logging.exception("Marketplace barcode fallback failed")
        return None


def _register_barcode(payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    barcode = normalize_scanned_barcode(str(payload.get("barcode") or ""))
    if not barcode:
        return 400, {"ok": False, "message": "Штрихкод не указан."}
    if len(barcode) > 128:
        return 400, {"ok": False, "message": "Штрихкод слишком длинный."}
    register_product_barcode(barcode, _pk(payload))
    return 200, {"ok": True, "message": "Штрихкод привязан к товару."}


def _movements(payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    conn = get_pg_connection()
    limit = max(1, min(int(payload.get("limit", 100)), 1000))
    movements = repo.list_movements(
        conn, limit=limit, movement_type=payload.get("movement_type")
    )
    return 200, {
        "movements": [
            {
                "id": m.id,
                "request_key": m.request_key,
                "movement_type": m.movement_type,
                "product_key": m.product_key.to_dict(),
                "quantity": m.quantity,
                "from_location_id": m.from_location_id,
                "to_location_id": m.to_location_id,
                "reason": m.reason,
                "occurred_at": m.occurred_at,
            }
            for m in movements
        ]
    }


# ──────────────────────────────────────────────────────────────────────
# helpers
# ──────────────────────────────────────────────────────────────────────


def _result_response(result) -> tuple[int, dict[str, Any]]:
    body: dict[str, Any] = {"ok": result.ok, "status": result.status}
    if result.movement_id is not None:
        body["movement_id"] = result.movement_id
    if result.reason:
        body["reason"] = result.reason
        body["message"] = result.reason
    if result.skipped_duplicate:
        return 200, body
    return 200 if result.ok else 409, body


WMS_WRITE_ROUTES = {
    "/api/wms/receive",
    "/api/wms/material-receive",
    "/api/wms/stock-receipts/post",
    "/api/wms/putaway",
    "/api/wms/transfer",
    "/api/wms/pick",
    "/api/wms/scrap",
    "/api/wms/inventory",
    "/api/wms/admin/scrap",
    "/api/wms/admin/inventory",
    "/api/wms/admin/bulk-writeoff",
    "/api/wms/admin/product-lookup",
    "/api/wms/barcode/resolve",
    "/api/wms/barcode/register",
    "/api/wms/locations/create",
}

WMS_ADMIN_ROUTES = {
    "/api/wms/admin/scrap",
    "/api/wms/admin/inventory",
    "/api/wms/admin/bulk-writeoff",
    "/api/wms/admin/product-lookup",
}

WMS_READ_ROUTES = {
    "/api/wms/locations",
    "/api/wms/stock",
    "/api/wms/movements",
    "/api/wms/stock-receipts",
}

WMS_ROUTES = WMS_WRITE_ROUTES | WMS_READ_ROUTES
