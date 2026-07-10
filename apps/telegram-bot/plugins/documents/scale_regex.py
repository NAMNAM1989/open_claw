from __future__ import annotations

import re

from plugins.documents.models import ScaleTicket

MAWB_RE = re.compile(r"\b(\d{3}[-\s]?\d{8})\b")
FLIGHT_RE = re.compile(r"\b([A-Z]{2}\d{2,4}[A-Z]?)\b")
KG_RE = re.compile(r"(?:gw|g\.?w|gross|tl|trọng|trong)[\s:]*([\d.,]+)", re.I)
CW_RE = re.compile(r"(?:cw|c\.?w|chargeable|tính cước|tinh cuoc)[\s:]*([\d.,]+)", re.I)
PCS_RE = re.compile(r"(?:pcs|kiện|kien|số kiện|so kien)[\s:]*(\d+)", re.I)


def _num(value: str) -> float:
    return float(value.replace(",", "."))


def parse_scale_from_text(text: str) -> ScaleTicket | None:
    raw = (text or "").strip()
    if not raw:
        return None

    ticket = ScaleTicket(source="regex")
    m = MAWB_RE.search(raw)
    if m:
        awb = re.sub(r"\s+", "", m.group(1).upper())
        ticket.awb = f"{awb[:3]}-{awb[3:11]}" if "-" not in awb else awb

    fm = FLIGHT_RE.search(raw)
    if fm:
        ticket.flight = fm.group(1)

    km = KG_RE.search(raw)
    if km:
        try:
            ticket.gross_kg = _num(km.group(1))
        except ValueError:
            pass

    cm = CW_RE.search(raw)
    if cm:
        try:
            ticket.chargeable_kg = _num(cm.group(1))
        except ValueError:
            pass

    pm = PCS_RE.search(raw)
    if pm:
        ticket.pieces = int(pm.group(1))

    if "scsc" in raw.lower():
        ticket.form_type = "SCSC"
    elif "tcs" in raw.lower():
        ticket.form_type = "TCS"

    if ticket.awb or ticket.gross_kg:
        return ticket
    return None
