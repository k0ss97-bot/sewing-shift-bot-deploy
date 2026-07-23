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
    POST /api/wms/scrap       scrap
    POST /api/wms/inventory   inventory_count
    GET  /api/wms/locations   list_locations
    GET  /api/wms/stock       get_stock_rows
    GET  /api/wms/movements   list_movements
"""

from __future__ import annotations

import json
from typing import Any

from . import operations as ops
from . import repository as repo
from .connection import get_pg_connection
from .models import ProductKey


def handle(path: str, payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    """Dispatch one WMS request.  Returns (http_status, body)."""
    try:
        if path == "/api/wms/receive":
            return _receive(payload)
        if path == "/api/wms/putaway":
            return _putaway(payload)
        if path == "/api/wms/transfer":
            return _transfer(payload)
        if path == "/api/wms/scrap":
            return _scrap(payload)
        if path == "/api/wms/inventory":
            return _inventory(payload)
        if path == "/api/wms/locations":
            return _locations(payload)
        if path == "/api/wms/stock":
            return _stock(payload)
        if path == "/api/wms/movements":
            return _movements(payload)
        return 404, {"error": f"unknown WMS route: {path}"}
    except KeyError as exc:
        return 400, {"error": f"missing field: {exc}"}
    except ValueError as exc:
        return 400, {"error": str(exc)}
    except Exception as exc:  # pragma: no cover - defensive
        return 500, {"error": f"internal: {exc}"}


# ──────────────────────────────────────────────────────────────────────
# POST handlers
# ──────────────────────────────────────────────────────────────────────


def _pk(payload: dict[str, Any]) -> ProductKey:
    return ProductKey.from_dict(payload["product_key"])


def _receive(payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    result = ops.receive_from_production(
        _pk(payload),
        int(payload["quantity"]),
        employee_id=payload.get("employee_id"),
        request_key=payload.get("request_key"),
        reason=payload.get("reason"),
        tsd_device_id=payload.get("tsd_device_id"),
    )
    return _result_response(result)


def _putaway(payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    result = ops.putaway(
        _pk(payload),
        int(payload["quantity"]),
        to_location_code=payload["to_location_code"],
        employee_id=payload.get("employee_id"),
        request_key=payload.get("request_key"),
        reason=payload.get("reason"),
        tsd_device_id=payload.get("tsd_device_id"),
    )
    return _result_response(result)


def _transfer(payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    result = ops.transfer(
        _pk(payload),
        int(payload["quantity"]),
        from_location_code=payload["from_location_code"],
        to_location_code=payload["to_location_code"],
        employee_id=payload.get("employee_id"),
        request_key=payload.get("request_key"),
        reason=payload.get("reason"),
        tsd_device_id=payload.get("tsd_device_id"),
    )
    return _result_response(result)


def _scrap(payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    result = ops.scrap(
        _pk(payload),
        int(payload["quantity"]),
        reason=payload.get("reason", ""),
        target_state=payload.get("target_state", "SCRAPPED"),
        employee_id=payload.get("employee_id"),
        request_key=payload.get("request_key"),
        tsd_device_id=payload.get("tsd_device_id"),
    )
    return _result_response(result)


def _inventory(payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    result = ops.inventory_count(
        payload["location_code"],
        payload["counted"],
        employee_id=payload.get("employee_id"),
        request_key=payload.get("request_key"),
    )
    return _result_response(result)


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


def _stock(payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    conn = get_pg_connection()
    rows = repo.get_stock_rows(
        location_id=payload.get("location_id"),
    )
    return 200, {
        "stock": [
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
    }


def _movements(payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    conn = get_pg_connection()
    limit = min(int(payload.get("limit", 100)), 1000)
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
    body: dict[str, Any] = {"status": result.status}
    if result.movement_id is not None:
        body["movement_id"] = result.movement_id
    if result.reason:
        body["reason"] = result.reason
    if result.skipped_duplicate:
        return 200, body
    return 200 if result.ok else 409, body


WMS_ROUTES = {
    "/api/wms/receive",
    "/api/wms/putaway",
    "/api/wms/transfer",
    "/api/wms/scrap",
    "/api/wms/inventory",
    "/api/wms/locations",
    "/api/wms/stock",
    "/api/wms/movements",
}
