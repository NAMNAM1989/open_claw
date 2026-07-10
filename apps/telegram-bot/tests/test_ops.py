import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from core.supabase_client import LogisticsStore, reset_store
from plugins.ops.arrival_rules import compute_arrival
from plugins.ops.parser import parse_booking
from plugins.ops.runner import EcargoRunner
from plugins.ops.validator import validate_booking

VN = ZoneInfo("Asia/Ho_Chi_Minh")


def test_parse_booking_five_lines():
    text = "\n".join(
        [
            "51F-12345",
            "VN123",
            "10JUL2026",
            "HKG",
            "618-53186840",
            "3",
            "120",
        ]
    )
    b = parse_booking(text)
    assert b is not None
    assert b.vehicle_no == "51F-12345"
    assert b.mawb == "618-53186840"
    assert b.pcs == 3
    assert b.gross_weight == 120


def test_parse_booking_labels():
    text = """
    Xe: 51F-99999
    Chuyến: SQ185
    Ngày: 15/07/2026
    Đích: NRT
    MAWB: 618-12345678
    Kiện: 2
    TL: 80
    """
    b = parse_booking(text)
    assert b is not None
    assert b.flight == "SQ185"
    assert b.destination == "NRT"


def test_validate_booking_ok():
    b = parse_booking(
        "51F-12345\nVN123\n15/07/2026\nHKG\n618-53186840\n1\n10",
    )
    assert b is not None
    errors = validate_booking(
        b,
        now=datetime(2026, 7, 10, 10, 0, tzinfo=VN),
    )
    assert errors == []


def test_arrival_evening_rolls_to_morning():
    slot = compute_arrival(now=datetime(2026, 7, 10, 20, 0, tzinfo=VN))
    assert slot.time_str == "07:00"
    assert slot.date_str == "11/07/2026"


def test_runner_dry_run():
    reset_store()
    store = LogisticsStore(url="", key="")
    b = parse_booking("51F-12345\nVN123\n15/07/2026\nHKG\n618-53186840\n1\n10")
    assert b is not None
    rec = store.save_booking_pending(99, b)
    runner = EcargoRunner(store)

    result = asyncio.run(runner.run_booking_job(99, rec.id, b))
    assert result.registration_no.startswith("DRY")
    job = store.get_latest_job_run(99)
    assert job is not None
