from dataclasses import dataclass, field
from uuid import UUID


@dataclass
class Dim:
    length_cm: float
    width_cm: float
    height_cm: float
    pieces: int = 1


@dataclass
class PriceRow:
    route: str
    cargo_type: str = "general"
    weight_min_kg: float = 0.0
    weight_max_kg: float = 0.0
    weight_range: str = ""
    price_per_kg: float = 0.0
    currency: str = "VND"
    notes: str = ""


@dataclass
class QuoteRequest:
    route: str
    weight_kg: float
    cargo_type: str = "general"
    pieces: int = 0
    dims: list[Dim] = field(default_factory=list)
    currency: str = "VND"


@dataclass
class QuoteLine:
    label: str
    amount: float
    formula: str = ""
    pct: float | None = None


@dataclass
class QuoteResult:
    quote_code: str
    route: str
    actual_kg: float
    volumetric_kg: float | None
    chargeable_kg: float
    total: float
    currency: str
    line_items: list[QuoteLine]
    disclaimer: str
    tariff_id: UUID | None = None
