from io import BytesIO

from openpyxl import Workbook

from core.excel_read import excel_to_text, is_excel_filename


def _sample_xlsx() -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "Tariff"
    ws.append(["Route", "Min", "Max", "Price"])
    ws.append(["SGN-HKG", 0, 45, 18000])
    ws.append(["SGN-HKG", 45, 100, 16000])
    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()


def test_excel_to_text_contains_rows():
    text = excel_to_text(_sample_xlsx(), "gia.xlsx")
    assert "File: gia.xlsx" in text
    assert "Tariff" in text
    assert "SGN-HKG" in text
    assert "16000" in text


def test_is_excel_filename():
    assert is_excel_filename("a.xlsx")
    assert is_excel_filename("a.XLSM")
    assert not is_excel_filename("a.xls")
    assert not is_excel_filename("a.pdf")
