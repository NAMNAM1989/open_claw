"""E2E in-memory — mô phỏng luồng đầy đủ trước deploy (không cần Telegram/Supabase live)."""

from __future__ import annotations

import asyncio
from datetime import timedelta
from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from openpyxl import Workbook

from core.supabase_client import LogisticsStore, reset_store
from plugins.documents.extractors import extract_scale_ticket, extract_tariff_from_image
from plugins.ops.parser import parse_booking
from plugins.ops.runner import EcargoRunner
from plugins.reports.builder import build_ops_report, build_sales_report
from plugins.reports.period import parse_period
from plugins.sales.excel_importer import parse_tariff_excel
from plugins.sales.models import QuoteRequest
from plugins.sales.quote_engine import compute_quote
from plugins.chat.context import build_logistics_context


def _sample_xlsx() -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.append(["Route", "Min_kg", "Sell_rate", "Currency"])
    ws.append(["SGN-HKG", 45, 16000, "VND"])
    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()


def test_e2e_sales_ops_documents_flow():
    reset_store()
    store = LogisticsStore(url="", key="")
    chat_id = 9001

    # Phase 1 — Excel tariff + quote
    rows = parse_tariff_excel(_sample_xlsx())
    store.insert_tariff(chat_id, rows, source="excel")
    quote = compute_quote(QuoteRequest(route="SGN-HKG", weight_kg=120), rows)
    assert quote is not None
    store.insert_quote(chat_id, quote)

    # Phase 3 — vision mock
    client = MagicMock()
    client.configured = True
    client.chat_vision.side_effect = [
        '{"awb":"618-53186840","flight":"SQ185","pieces":2,"gross_kg":80,"chargeable_kg":85,"form_type":"SCSC"}',
        '{"rows":[{"route":"SGN-NRT","cargo_type":"general","weight_min_kg":0,"weight_max_kg":0,"price_per_kg":19000,"currency":"VND"}]}',
    ]
    ticket = extract_scale_ticket(b"img", client=client, user_key=f"tg:{chat_id}")
    store.save_scale_ticket(chat_id, ticket)
    vision_rows, _ = extract_tariff_from_image(b"img2", client=client, user_key=f"tg:{chat_id}")
    store.insert_tariff(chat_id, vision_rows, source="vision")

    # Phase 2 — booking dry-run
    booking = parse_booking("51F-12345\nVN123\n15/07/2026\nHKG\n618-53186840\n2\n80")
    assert booking is not None
    rec = store.save_booking_pending(chat_id, booking)
    result = asyncio.run(EcargoRunner(store).run_booking_job(chat_id, rec.id, booking))
    assert result.registration_no

    # Phase 4 — context + reports
    ctx = build_logistics_context(store, chat_id)
    assert "SGN-HKG" in ctx or "618" in ctx
    label, since = parse_period(["tuan"])
    ops = build_ops_report(store, chat_id, label=label, since=since - timedelta(days=1))
    sales = build_sales_report(store, chat_id, label=label, since=since - timedelta(days=1))
    assert "Ops" in ops
    assert "Sales" in sales

def test_template_excel_exists():
    path = Path(__file__).resolve().parents[1] / "templates" / "tariff_template.xlsx"
    assert path.is_file(), "Chạy: python scripts/make_tariff_template.py"
