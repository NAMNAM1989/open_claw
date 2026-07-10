from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass
class Booking:
    vehicle_no: str = ""
    flight: str = ""
    flight_date: str = ""
    destination: str = ""
    mawb: str = ""
    pcs: int = 0
    gross_weight: float = 0.0
    raw_text: str = ""

    def summary(self) -> str:
        lines = [
            f"🚛 Xe: {self.vehicle_no or '—'}",
            f"✈️ Chuyến: {self.flight or '—'} · {self.flight_date or '—'}",
            f"📍 Đích: {self.destination or '—'}",
            f"📄 MAWB: {self.mawb or '—'}",
            f"📦 {self.pcs or '—'} kiện · {self.gross_weight or '—'} kg",
        ]
        return "\n".join(lines)


@dataclass
class BookingRecord:
    id: UUID | None
    chat_id: int
    booking: Booking
    status: str
    error_message: str = ""
    created_at: datetime | None = None


@dataclass
class JobResult:
    registration_no: str = ""
    vct_number: str = ""
    verify_code: str = ""
    status_text: str = ""
    error_raw: str = ""
    qr_image_bytes: bytes | None = None


@dataclass
class VerifyMail:
    subject: str = ""
    verify_url: str = ""
    registration_no: str = ""


@dataclass
class QrMail:
    subject: str = ""
    registration_no: str = ""
    vct_number: str = ""
    image_bytes: bytes | None = None


@dataclass
class ArrivalSlot:
    date_str: str  # dd/MM/yyyy for eCargo form
    time_str: str  # HH:mm
