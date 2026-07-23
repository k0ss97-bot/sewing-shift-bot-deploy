"""Typed dataclass models for WMS entities.

These mirror the Postgres tables but are pure Python dataclasses, used by the
repository and operations layers. They keep the product identity tuple
(``item_type, product_name, product_size, product_color, stage_name,
ready_for_position``) intact — it is how the legacy SQLite ``warehouse_stock``
identifies a stock row, so WMS reuses the same business key.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ProductKey:
    """The legacy warehouse_stock identity tuple.

    This exact 6-field combination is the UNIQUE key in the SQLite
    ``warehouse_stock`` table; WMS reuses it so stock rows map 1:1.
    """

    item_type: str            # 'semifinished' | 'finished'
    product_name: str
    product_size: str
    product_color: str
    stage_name: str
    ready_for_position: str

    def to_dict(self) -> dict[str, str]:
        return {
            "item_type": self.item_type,
            "product_name": self.product_name,
            "product_size": self.product_size,
            "product_color": self.product_color,
            "stage_name": self.stage_name,
            "ready_for_position": self.ready_for_position,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "ProductKey":
        return cls(
            item_type=str(d["item_type"]),
            product_name=str(d["product_name"]),
            product_size=str(d["product_size"]),
            product_color=str(d["product_color"]),
            stage_name=str(d["stage_name"]),
            ready_for_position=str(d["ready_for_position"]),
        )


@dataclass(frozen=True)
class Zone:
    id: int
    code: str
    name_ru: str
    zone_type: str
    sort_order: int
    is_active: bool


@dataclass(frozen=True)
class Location:
    id: int
    zone_id: int
    code: str
    barcode: str
    name_ru: str | None
    pick_priority: int
    route_order: int
    status: str  # active/blocked/inventory


@dataclass
class WarehouseStock:
    id: int
    product_key: ProductKey
    quantity: int
    reserved_quantity: int
    item_state: str
    location_id: int | None
    unit: str
    legacy_sqlite_id: int | None = None


@dataclass(frozen=True)
class Movement:
    id: int
    request_key: str
    movement_type: str
    product_key: ProductKey
    quantity: int
    from_location_id: int | None
    to_location_id: int | None
    from_state: str | None
    to_state: str | None
    source_type: str | None
    source_id: int | None
    reason: str | None
    actor_employee_id: int | None
    tsd_device_id: str | None
    occurred_at: str


# ──────────────────────────────────────────────────────────────────────
# Operation result
# ──────────────────────────────────────────────────────────────────────


@dataclass
class OperationResult:
    """Outcome of a warehouse operation."""

    ok: bool
    movement_id: int | None = None
    reason: str | None = None
    skipped_duplicate: bool = False

    @property
    def status(self) -> str:
        if self.skipped_duplicate:
            return "duplicate"
        return "ok" if self.ok else "error"
