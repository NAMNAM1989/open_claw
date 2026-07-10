import secrets
from datetime import date
from uuid import UUID

from plugins.sales.models import PriceRow, QuoteLine, QuoteRequest, QuoteResult
from plugins.sales.volumetric import chargeable_kg

DISCLAIMER = "Chưa gồm VAT/customs. Giá chốt khi booking."


def normalize_route(route: str, aliases: dict[str, str] | None = None) -> str:
    raw = route.strip().upper().replace(" ", "")
    if "-" not in raw:
        return raw
    origin, dest = raw.split("-", 1)
    aliases = aliases or {}
    origin = aliases.get(origin, origin)
    dest = aliases.get(dest, dest)
    return f"{origin}-{dest}"


def match_price_row(rows: list[PriceRow], route: str, chargeable: float, cargo_type: str) -> PriceRow | None:
    norm = normalize_route(route)
    cargo = (cargo_type or "general").lower()
    candidates: list[PriceRow] = []

    for row in rows:
        if normalize_route(row.route) != norm:
            continue
        row_cargo = (row.cargo_type or "general").lower()
        if row_cargo not in ("", "general") and row_cargo != cargo:
            continue
        if row.weight_max_kg and chargeable > row.weight_max_kg:
            continue
        if chargeable < row.weight_min_kg:
            continue
        candidates.append(row)

    if not candidates:
        return None
    return max(candidates, key=lambda r: r.weight_min_kg)


def make_quote_code(day: date | None = None) -> str:
    d = day or date.today()
    return f"Q-{d.strftime('%Y%m%d')}-{secrets.token_hex(2).upper()}"


def compute_quote(
    req: QuoteRequest,
    rows: list[PriceRow],
    *,
    divisor: int = 6000,
    fuel_pct: float = 0.0,
    min_charge: float = 0.0,
    route_aliases: dict[str, str] | None = None,
    tariff_id: UUID | None = None,
) -> QuoteResult | None:
    chargeable, vol = chargeable_kg(req.weight_kg, req.dims, divisor=divisor)
    matched = match_price_row(rows, req.route, chargeable, req.cargo_type)
    if not matched:
        return None

    freight = matched.price_per_kg * chargeable
    fuel = freight * (fuel_pct / 100.0)
    subtotal = freight + fuel
    total = max(subtotal, min_charge)

    line_items = [
        QuoteLine(
            label="cước_kg",
            amount=freight,
            formula=f"{matched.price_per_kg:,.0f} x {chargeable:g}",
        ),
    ]
    if fuel_pct:
        line_items.append(
            QuoteLine(label="fuel_surcharge", amount=fuel, pct=fuel_pct),
        )
    if min_charge and total == min_charge and subtotal < min_charge:
        line_items.append(QuoteLine(label="min_charge", amount=min_charge))

    return QuoteResult(
        quote_code=make_quote_code(),
        route=normalize_route(req.route, route_aliases),
        actual_kg=req.weight_kg,
        volumetric_kg=vol,
        chargeable_kg=chargeable,
        total=total,
        currency=matched.currency or req.currency,
        line_items=line_items,
        disclaimer=DISCLAIMER,
        tariff_id=tariff_id,
    )
