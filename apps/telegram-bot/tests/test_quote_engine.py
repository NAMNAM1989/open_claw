import pytest

from plugins.sales.models import Dim, PriceRow, QuoteRequest
from plugins.sales.quote_engine import compute_quote, make_quote_code, match_price_row, normalize_route
from plugins.sales.volumetric import chargeable_kg


def test_normalize_route_aliases():
    assert normalize_route("HCM-HKG", {"HCM": "SGN"}) == "SGN-HKG"


def test_volumetric_wins():
    dims = [Dim(60, 40, 40, pieces=2)]
    cw, vol = chargeable_kg(50, dims, divisor=6000)
    assert vol == pytest.approx(32.0)
    assert cw == 50


def test_volumetric_higher_than_actual():
    dims = [Dim(100, 100, 100, pieces=1)]
    cw, vol = chargeable_kg(50, dims, divisor=6000)
    assert vol == pytest.approx(166.667, rel=1e-3)
    assert cw == pytest.approx(166.667, rel=1e-3)


def test_match_break_weight():
    rows = [
        PriceRow(route="SGN-HKG", weight_min_kg=0, weight_max_kg=45, price_per_kg=18500),
        PriceRow(route="SGN-HKG", weight_min_kg=45, weight_max_kg=100, price_per_kg=16000),
        PriceRow(route="SGN-HKG", weight_min_kg=100, weight_max_kg=0, price_per_kg=14000),
    ]
    matched = match_price_row(rows, "SGN-HKG", 120, "general")
    assert matched is not None
    assert matched.weight_min_kg == 100


def test_compute_quote():
    rows = [
        PriceRow(route="SGN-HKG", weight_min_kg=45, weight_max_kg=0, price_per_kg=16000),
    ]
    result = compute_quote(QuoteRequest(route="SGN-HKG", weight_kg=120), rows)
    assert result is not None
    assert result.total == 120 * 16000
    assert result.quote_code.startswith("Q-")


def test_quote_code_unique():
    a = make_quote_code()
    b = make_quote_code()
    assert a != b
