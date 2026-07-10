from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from plugins.sales.models import PriceRow, QuoteResult


@dataclass
class TariffRecord:
    id: UUID | None
    chat_id: int
    rows: list[PriceRow]
    source: str
    notes: str
    created_at: datetime | None = None


def price_row_to_dict(row: PriceRow) -> dict[str, Any]:
    return {
        "route": row.route,
        "cargo_type": row.cargo_type,
        "weight_min_kg": row.weight_min_kg,
        "weight_max_kg": row.weight_max_kg,
        "weight_range": row.weight_range,
        "price_per_kg": row.price_per_kg,
        "currency": row.currency,
        "notes": row.notes,
    }


def price_row_from_dict(data: dict[str, Any]) -> PriceRow:
    return PriceRow(
        route=str(data.get("route", "")),
        cargo_type=str(data.get("cargo_type", "general")),
        weight_min_kg=float(data.get("weight_min_kg", 0) or 0),
        weight_max_kg=float(data.get("weight_max_kg", 0) or 0),
        weight_range=str(data.get("weight_range", "")),
        price_per_kg=float(data.get("price_per_kg", 0) or 0),
        currency=str(data.get("currency", "VND")),
        notes=str(data.get("notes", "")),
    )


def rows_to_json(rows: list[PriceRow]) -> list[dict[str, Any]]:
    return [price_row_to_dict(r) for r in rows]


def rows_from_json(data: list[dict[str, Any]]) -> list[PriceRow]:
    return [price_row_from_dict(item) for item in data]


def quote_to_breakdown(result: QuoteResult) -> dict[str, Any]:
    return {
        "line_items": [
            {
                "label": item.label,
                "amount": item.amount,
                "formula": item.formula,
                "pct": item.pct,
            }
            for item in result.line_items
        ],
        "disclaimer": result.disclaimer,
    }
