from datetime import datetime, timedelta, timezone

from core.supabase_client import LogisticsStore, reset_store
from plugins.ops.models import Booking
from plugins.reports.builder import build_ops_report, build_sales_report
from plugins.reports.period import parse_period
from plugins.sales.models import PriceRow, QuoteRequest
from plugins.chat.context import build_logistics_context
from plugins.sales.quote_engine import compute_quote
from plugins.sales.models import PriceRow


def test_parse_period_default_week():
    label, since = parse_period([])
    assert label == "tuần"
    assert since < datetime.now(timezone.utc)


def test_parse_period_month():
    label, _ = parse_period(["thang"])
    assert label == "tháng"


def test_ops_report_memory():
    reset_store()
    store = LogisticsStore(url="", key="")
    chat = 100
    b = Booking(vehicle_no="51F-1", flight="VN1", mawb="618-11111111", raw_text="x", pcs=1, gross_weight=10)
    rec = store.save_booking_pending(chat, b)
    store.update_booking_status(rec.id, "done")
    store.log_ops("error", "test", source="ecargo")

    label, since = parse_period(["tuan"])
    text = build_ops_report(store, chat, label=label, since=since - timedelta(days=1))
    assert "Booking:" in text
    assert "Ops" in text


def test_sales_report_memory():
    reset_store()
    store = LogisticsStore(url="", key="")
    chat = 101
    rows = [PriceRow(route="SGN-HKG", weight_min_kg=0, weight_max_kg=0, price_per_kg=10000)]
    store.insert_tariff(chat, rows)
    result = compute_quote(QuoteRequest(route="SGN-HKG", weight_kg=50), rows)
    assert result
    store.insert_quote(chat, result)

    label, since = parse_period([])
    text = build_sales_report(store, chat, label=label, since=since - timedelta(days=1))
    assert "Sales" in text
    assert "quote" in text.lower()


def test_chat_context_includes_pending():
    reset_store()
    store = LogisticsStore(url="", key="")
    chat = 102
    store.save_booking_pending(chat, Booking(mawb="618-22222222", raw_text="t", pcs=1, gross_weight=1))
    ctx = build_logistics_context(store, chat)
    assert "618-22222222" in ctx
    assert "pending" in ctx.lower()
