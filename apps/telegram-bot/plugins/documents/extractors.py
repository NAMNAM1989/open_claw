from __future__ import annotations

import logging

from core.openclaw_client import OpenClawClient, OpenClawError, get_openclaw_client
from plugins.documents.json_parse import extract_json_object
from plugins.documents.models import ScaleTicket, TariffVisionResult
from plugins.documents.prompts import (
    SCALE_TICKET_PROMPT,
    SCALE_TICKET_SYSTEM,
    TARIFF_PROMPT,
    TARIFF_SYSTEM,
)
from plugins.documents.scale_regex import parse_scale_from_text
from plugins.sales.models import PriceRow
from plugins.sales.tariff_codec import price_row_from_dict, price_row_to_dict

log = logging.getLogger("namnam.documents")


def _scale_from_dict(data: dict) -> ScaleTicket:
    return ScaleTicket(
        awb=str(data.get("awb", "")).strip(),
        flight=str(data.get("flight", "")).strip().upper(),
        flight_date=str(data.get("flight_date", "")).strip().upper(),
        pieces=int(data.get("pieces") or 0),
        gross_kg=float(data.get("gross_kg") or 0),
        chargeable_kg=float(data.get("chargeable_kg") or 0),
        form_type=str(data.get("form_type", "")).strip().upper(),
        source="vision",
    )


def extract_scale_ticket(
    image_bytes: bytes,
    *,
    caption: str = "",
    client: OpenClawClient | None = None,
    user_key: str = "tg:bot",
    use_vision: bool = True,
) -> ScaleTicket:
    client = client or get_openclaw_client()

    if use_vision and client.configured:
        try:
            raw = client.chat_vision(
                image_bytes,
                SCALE_TICKET_PROMPT,
                system=SCALE_TICKET_SYSTEM,
                user_key=user_key,
            )
            data = extract_json_object(raw)
            ticket = _scale_from_dict(data)
            if ticket.awb or ticket.gross_kg:
                return ticket
        except (OpenClawError, ValueError) as exc:
            log.warning("scale vision failed: %s", exc)

    if caption:
        parsed = parse_scale_from_text(caption)
        if parsed:
            parsed.source = "regex+caption"
            return parsed

    raise ValueError(
        "Không đọc được phiếu cân — cần OpenClaw Gateway hoặc caption có AWB/kg."
    )


def extract_tariff_from_image(
    image_bytes: bytes,
    *,
    client: OpenClawClient | None = None,
    user_key: str = "tg:bot",
) -> tuple[list[PriceRow], TariffVisionResult]:
    client = client or get_openclaw_client()
    if not client.configured:
        raise ValueError("Chưa cấu hình OpenClaw — không đọc ảnh bảng giá.")

    raw = client.chat_vision(
        image_bytes,
        TARIFF_PROMPT,
        system=TARIFF_SYSTEM,
        user_key=user_key,
    )
    data = extract_json_object(raw)
    rows_raw = data.get("rows") or []
    if not isinstance(rows_raw, list) or not rows_raw:
        raise ValueError("Vision không trả rows[] hợp lệ.")

    rows: list[PriceRow] = []
    for item in rows_raw:
        if not isinstance(item, dict):
            continue
        row = price_row_from_dict(item)
        if row.route and row.price_per_kg > 0:
            rows.append(row)

    if not rows:
        raise ValueError("Không parse được dòng giá từ ảnh.")

    meta = TariffVisionResult(
        rows=[price_row_to_dict(r) for r in rows],
        source="vision",
    )
    return rows, meta
