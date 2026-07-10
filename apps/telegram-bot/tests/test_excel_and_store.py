from io import BytesIO

import pytest
from openpyxl import Workbook

from core.supabase_client import LogisticsStore, reset_store
from plugins.sales.excel_importer import ExcelImportError, parse_tariff_excel
from plugins.sales.models import PriceRow, QuoteLine, QuoteRequest, QuoteResult
from plugins.sales.quote_engine import compute_quote


def _make_xlsx(rows: list[list]) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.append(
        [
            "Route",
            "Carrier",
            "Cargo",
            "Min_kg",
            "Max_kg",
            "Buy_rate",
            "Sell_rate",
            "Currency",
        ]
    )
    for row in rows:
        ws.append(row)
    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()


def test_parse_tariff_excel_ok():
    data = _make_xlsx(
        [
            ["SGN-HKG", "CX", "general", 45, 100, 13000, 16000, "VND"],
            ["SGN-HKG", "CX", "general", 100, 0, 12000, 14000, "VND"],
        ]
    )
    rows = parse_tariff_excel(data)
    assert len(rows) == 2
    assert rows[0].price_per_kg == 16000
    assert rows[1].weight_min_kg == 100


def test_parse_tariff_missing_column():
    wb = Workbook()
    ws = wb.active
    ws.append(["Route", "Min_kg"])
    ws.append(["SGN-HKG", 0])
    buf = BytesIO()
    wb.save(buf)
    with pytest.raises(ExcelImportError, match="Sell_rate"):
        parse_tariff_excel(buf.getvalue())


def test_memory_store_tariff_and_quote():
    reset_store()
    store = LogisticsStore(url="", key="")
    rows = [
        PriceRow(route="SGN-HKG", weight_min_kg=45, weight_max_kg=0, price_per_kg=16000),
    ]
    store.insert_tariff(1001, rows, source="test")
    latest = store.get_latest_tariff(1001)
    assert latest is not None
    assert len(latest.rows) == 1

    result = compute_quote(QuoteRequest(route="SGN-HKG", weight_kg=120), latest.rows)
    assert result is not None
    result.tariff_id = latest.id
    store.insert_quote(1001, result)
    assert len(store._memory_quotes) == 1
