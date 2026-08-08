"""Typed dataclass models for WMS entities.

These mirror the Postgres tables but are pure Python dataclasses, used by the
repository and operations layers. Finished goods use the seller article as the
primary cross-system identity. Descriptive fields are attributes; the legacy
identity remains available only for rows that do not yet have an article.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import unicodedata


def normalize_product_article(value: Any) -> str:
    """Return the canonical article shared by production, WMS and marketplaces."""

    normalized = unicodedata.normalize("NFKC", str(value or "")).strip().lstrip("'")
    return "".join(normalized.split()).upper().replace("Ё", "Е")


@dataclass(frozen=True)
class ProductKey:
    """Stable physical identity; article is authoritative for finished goods."""

    item_type: str            # 'semifinished' | 'finished' | 'material'
    product_name: str
    product_size: str
    product_color: str
    stage_name: str
    ready_for_position: str
    product_article: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "product_article", normalize_product_article(self.product_article))

    def to_dict(self) -> dict[str, str]:
        return {
            "item_type": self.item_type,
            "product_article": self.product_article,
            "product_name": self.product_name,
            "product_size": self.product_size,
            "product_color": self.product_color,
            "stage_name": self.stage_name,
            "ready_for_position": self.ready_for_position,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "ProductKey":
        values = {
            field_name: str(d[field_name] if d[field_name] is not None else "").strip()
            for field_name in (
                "item_type",
                "product_name",
                "product_size",
                "product_color",
                "stage_name",
                "ready_for_position",
            )
        }
        if any(not value for value in values.values()):
            raise ValueError("all product_key fields must be non-empty")
        if values["item_type"] not in {"finished", "semifinished", "material"}:
            raise ValueError("item_type must be finished, semifinished or material")
        return cls(
            **values,
            product_article=normalize_product_article(d.get("product_article") or d.get("article")),
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


@dataclass
class StockReceiptResult:
    """Outcome of posting one multi-line stock receipt document."""

    ok: bool
    receipt_id: int | None = None
    number: str | None = None
    lines_count: int = 0
    total_quantity: int = 0
    reason: str | None = None
    skipped_duplicate: bool = False

    @property
    def status(self) -> str:
        if self.skipped_duplicate:
            return "duplicate"
        return "posted" if self.ok else "error"


@dataclass
class BulkWriteoffResult:
    """Outcome of the explicitly confirmed full WMS balance write-off."""

    ok: bool
    writeoff_id: int | None = None
    rows_count: int = 0
    total_quantity: int = 0
    released_reserved_quantity: int = 0
    reason: str | None = None
    skipped_duplicate: bool = False

    @property
    def status(self) -> str:
        if self.skipped_duplicate:
            return "duplicate"
        return "posted" if self.ok else "error"
