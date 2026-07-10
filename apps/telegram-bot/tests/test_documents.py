from unittest.mock import MagicMock, patch

import pytest

from core.openclaw_client import OpenClawClient, reset_openclaw_client
from core.supabase_client import LogisticsStore, reset_store
from plugins.documents.extractors import extract_scale_ticket, extract_tariff_from_image
from plugins.documents.json_parse import extract_json_object
from plugins.documents.models import ScaleTicket
from plugins.documents.scale_regex import parse_scale_from_text


def test_extract_json_object_from_fence():
    raw = '```json\n{"awb": "618-12345678"}\n```'
    data = extract_json_object(raw)
    assert data["awb"] == "618-12345678"


def test_parse_scale_from_text():
    t = parse_scale_from_text("MAWB 618-53186840 GW: 120 pcs 3 SQ185")
    assert t is not None
    assert t.awb == "618-53186840"
    assert t.gross_kg == 120
    assert t.pieces == 3


def test_extract_scale_ticket_vision():
    client = MagicMock()
    client.configured = True
    client.chat_vision.return_value = (
        '{"awb":"618-53186840","flight":"SQ185","flight_date":"21MAY",'
        '"pieces":3,"gross_kg":120,"chargeable_kg":127,"form_type":"SCSC"}'
    )
    ticket = extract_scale_ticket(b"fake-image", client=client, user_key="tg:1")
    assert ticket.awb == "618-53186840"
    assert ticket.chargeable_kg == 127


def test_extract_scale_ticket_regex_fallback():
    client = MagicMock()
    client.configured = False
    ticket = extract_scale_ticket(
        b"x",
        caption="phiếu cân AWB 618-12345678 GW 88",
        client=client,
        use_vision=False,
    )
    assert ticket.gross_kg == 88


def test_extract_tariff_from_image():
    client = MagicMock()
    client.configured = True
    client.chat_vision.return_value = (
        '{"rows":[{"route":"SGN-HKG","cargo_type":"general",'
        '"weight_min_kg":0,"weight_max_kg":45,"price_per_kg":18500,"currency":"VND"}]}'
    )
    rows, meta = extract_tariff_from_image(b"img", client=client)
    assert len(rows) == 1
    assert rows[0].price_per_kg == 18500
    assert meta.source == "vision"


def test_save_scale_ticket_memory():
    reset_store()
    store = LogisticsStore(url="", key="")
    ticket = ScaleTicket(awb="618-11111111", gross_kg=50, source="test")
    store.save_scale_ticket(42, ticket)
    latest = store.get_latest_scale_ticket(42)
    assert latest is not None
    assert latest["awb"] == "618-11111111"


def test_openclaw_health_mock():
    reset_openclaw_client()
    client = OpenClawClient(base_url="http://127.0.0.1:9", token="tok")
    with patch("httpx.Client") as mock_client_cls:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = '{"data":[{"id":"openclaw/default"}]}'
        mock_client_cls.return_value.__enter__.return_value.get.return_value = mock_resp
        ok, msg = client.health_check()
    assert ok is True
