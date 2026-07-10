from __future__ import annotations

import re
from datetime import datetime
from zoneinfo import ZoneInfo

from plugins.ops.models import ArrivalSlot, Booking

VN_TZ = ZoneInfo("Asia/Ho_Chi_Minh")

LABEL_PATTERNS: list[tuple[str, str]] = [
    (r"(?:xe|biển|bien|vehicle)\s*[:=]\s*(.+)", "vehicle_no"),
    (r"(?:chuyến|chuyen|flight|bay)\s*[:=]\s*(.+)", "flight"),
    (r"(?:ngày|ngay|date|etd)\s*[:=]\s*(.+)", "flight_date"),
    (r"(?:đích|dich|dest|destination)\s*[:=]\s*(.+)", "destination"),
    (r"(?:mawb|awb|vận đơn|van don)\s*[:=]\s*(.+)", "mawb"),
    (r"(?:kiện|kien|pcs|số kiện|so kien)\s*[:=]\s*(\d+)", "pcs"),
    (r"(?:tl|trọng lượng|trong luong|gw|kg|weight)\s*[:=]\s*([\d.,]+)", "gross_weight"),
]

MAWB_RE = re.compile(r"\b(\d{3}[-\s]?\d{8})\b")
FLIGHT_RE = re.compile(r"\b([A-Z]{2}\d{2,4}[A-Z]?)\b")
PLATE_RE = re.compile(r"\b(\d{2}[A-Z]{1,2}[-\s]?\d{3,5})\b", re.I)


def _clean_mawb(value: str) -> str:
    raw = re.sub(r"\s+", "", value.upper())
    m = re.match(r"(\d{3})[-]?(\d{8})", raw)
    if m:
        return f"{m.group(1)}-{m.group(2)}"
    return raw


def _parse_float(value: str) -> float:
    return float(value.replace(",", "."))


def parse_booking(text: str, *, default_pcs: int = 1, default_gw: float = 1.0) -> Booking | None:
    raw = (text or "").strip()
    if not raw:
        return None

    booking = Booking(raw_text=raw)
    lower = raw.lower()
    has_labels = any(
        re.search(pat, lower)
        for pat, _ in LABEL_PATTERNS
    )

    if has_labels:
        for line in raw.splitlines():
            line_lower = line.strip().lower()
            for pattern, field in LABEL_PATTERNS:
                m = re.search(pattern, line_lower, re.I)
                if not m:
                    continue
                val = m.group(1).strip()
                if field == "vehicle_no":
                    booking.vehicle_no = val.upper()
                elif field == "flight":
                    booking.flight = val.upper().split()[0]
                elif field == "flight_date":
                    booking.flight_date = val.upper()
                elif field == "destination":
                    booking.destination = val.upper()
                elif field == "mawb":
                    booking.mawb = _clean_mawb(val)
                elif field == "pcs":
                    booking.pcs = int(val)
                elif field == "gross_weight":
                    booking.gross_weight = _parse_float(val)
        if booking.mawb or booking.vehicle_no:
            if not booking.pcs:
                booking.pcs = default_pcs
            if not booking.gross_weight:
                booking.gross_weight = default_gw
            return booking
        return None

    lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
    if len(lines) >= 5:
        booking.vehicle_no = lines[0].upper()
        booking.flight = lines[1].upper()
        booking.flight_date = lines[2].upper()
        booking.destination = lines[3].upper()
        booking.mawb = _clean_mawb(lines[4])
        if len(lines) >= 6 and lines[5].isdigit():
            booking.pcs = int(lines[5])
        if len(lines) >= 7:
            try:
                booking.gross_weight = _parse_float(lines[6])
            except ValueError:
                pass
        if not booking.pcs:
            booking.pcs = default_pcs
        if not booking.gross_weight:
            booking.gross_weight = default_gw
        return booking

    if MAWB_RE.search(raw):
        booking.mawb = _clean_mawb(MAWB_RE.search(raw).group(1))
        fm = FLIGHT_RE.search(raw)
        if fm:
            booking.flight = fm.group(1)
        pm = PLATE_RE.search(raw)
        if pm:
            booking.vehicle_no = pm.group(1).upper()
        if booking.mawb:
            if not booking.pcs:
                booking.pcs = default_pcs
            if not booking.gross_weight:
                booking.gross_weight = default_gw
            return booking

    return None
