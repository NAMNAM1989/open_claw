from __future__ import annotations

import re
from datetime import date, datetime
from zoneinfo import ZoneInfo

from plugins.ops.models import Booking

VN_TZ = ZoneInfo("Asia/Ho_Chi_Minh")
MAWB_RE = re.compile(r"^\d{3}-\d{8}$")
PLATE_RE = re.compile(r"^\d{2}[A-Z]{1,2}-?\d{3,5}$", re.I)


class BookingValidationError(ValueError):
    pass


def _parse_flight_date(value: str, today: date) -> date | None:
    raw = (value or "").strip().upper()
    if not raw:
        return None

    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%d%m%Y"):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            pass

    m = re.match(r"(\d{1,2})([A-Z]{3})(\d{2,4})?", raw)
    if m:
        day = int(m.group(1))
        mon = m.group(2)
        year = int(m.group(3)) if m.group(3) else today.year
        if year < 100:
            year += 2000
        try:
            return datetime.strptime(f"{day}{mon}{year}", "%d%b%Y").date()
        except ValueError:
            return None
    return None


def validate_booking(booking: Booking, *, now: datetime | None = None) -> list[str]:
    errors: list[str] = []
    now = now or datetime.now(VN_TZ)
    today = now.date()

    plate = booking.vehicle_no.replace(" ", "").upper()
    if not plate:
        errors.append("Thiếu biển số xe.")
    elif not PLATE_RE.match(plate):
        errors.append(f"Biển số không hợp lệ: {booking.vehicle_no}")

    if not booking.flight:
        errors.append("Thiếu số hiệu chuyến bay.")

    fd = _parse_flight_date(booking.flight_date, today)
    if booking.flight_date and fd is None:
        errors.append(f"Ngày bay không đọc được: {booking.flight_date}")
    elif fd and fd < today:
        errors.append("Ngày bay phải >= hôm nay (VN).")

    if not booking.mawb:
        errors.append("Thiếu MAWB.")
    elif not MAWB_RE.match(booking.mawb):
        errors.append(f"MAWB không đúng 11 số (xxx-xxxxxxxx): {booking.mawb}")

    if booking.pcs <= 0:
        errors.append("Số kiện phải > 0.")
    if booking.gross_weight <= 0:
        errors.append("Trọng lượng phải > 0.")

    return errors


def require_valid_booking(booking: Booking, *, now: datetime | None = None) -> None:
    errors = validate_booking(booking, now=now)
    if errors:
        raise BookingValidationError("\n".join(errors))
