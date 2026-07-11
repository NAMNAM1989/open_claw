from core.docs_parse import parse_pkl, parse_quote
from core.pdf_pkl import render_pkl_pdf
from core.pdf_quote import build_quote, render_quote_pdf


def test_quote_pdf_not_empty():
    q = parse_quote("SGN-HKG 120kg 16000")
    result = build_quote(q)
    pdf = render_quote_pdf(result)
    assert pdf.startswith(b"%PDF")
    assert len(pdf) > 500
    assert result.total == 120 * 16000


def test_pkl_pdf_not_empty():
    p = parse_pkl(
        "MAWB: 123-45678900\n"
        "Origin: SGN\n"
        "Dest: HKG\n"
        "1. Widget A | 10 | 100kg | 50x40x40\n"
    )
    pdf = render_pkl_pdf(p)
    assert pdf.startswith(b"%PDF")
    assert len(pdf) > 500
