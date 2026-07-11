import pytest

from core.docs_parse import chargeable_kg, parse_pkl, parse_quote, Dim


def test_parse_quote_short():
    q = parse_quote("SGN-HKG 120kg 16000")
    assert q.route == "SGN-HKG"
    assert q.weight_kg == 120
    assert q.unit_price == 16000


def test_parse_quote_kv_and_vol():
    text = """
Khách: Công ty ABC
Route: SGN-HKG
KL: 50
Đơn giá: 16000
Kiện: 1
Kích thước: 60x40x40
"""
    q = parse_quote(text)
    assert q.customer == "Công ty ABC"
    assert q.pieces == 1
    assert len(q.dims) == 1
    chg, vol = chargeable_kg(q.weight_kg, q.dims, 6000)
    assert vol == pytest.approx(16.0)
    assert chg == 50


def test_parse_quote_missing_price():
    with pytest.raises(ValueError, match="Đơn giá"):
        parse_quote("Route: SGN-HKG\nKL: 10")


def test_parse_pkl_lines():
    text = """
MAWB: 123-45678900
Shipper: A Co
Consignee: B Co
Origin: SGN
Dest: HKG
1. Widget A | 10 | 100kg | 50x40x40
2. Widget B | 5 | 40kg | 30x30x30
"""
    p = parse_pkl(text)
    assert p.mawb == "123-45678900"
    assert len(p.lines) == 2
    assert p.lines[0].description == "Widget A"
    assert p.lines[1].weight_kg == 40


def test_chargeable_vol_wins():
    chg, vol = chargeable_kg(50, [Dim(100, 100, 100, 1)], 6000)
    assert vol == pytest.approx(166.666, rel=1e-3)
    assert chg == vol
