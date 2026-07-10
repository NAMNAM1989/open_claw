from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ScaleTicket:
    awb: str = ""
    flight: str = ""
    flight_date: str = ""
    pieces: int = 0
    gross_kg: float = 0.0
    chargeable_kg: float = 0.0
    form_type: str = ""
    source: str = ""

    def summary(self) -> str:
        lines = [
            "⚖️ Phiếu cân",
            f"• AWB: {self.awb or '—'}",
            f"• Chuyến: {self.flight or '—'} · {self.flight_date or '—'}",
            f"• Kiện: {self.pieces or '—'}",
            f"• GW: {self.gross_kg:g} kg" if self.gross_kg else "• GW: —",
        ]
        if self.chargeable_kg:
            lines.append(f"• CW: {self.chargeable_kg:g} kg")
        if self.form_type:
            lines.append(f"• Form: {self.form_type}")
        if self.source:
            lines.append(f"• Nguồn: {self.source}")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        return {
            "awb": self.awb,
            "flight": self.flight,
            "flight_date": self.flight_date,
            "pieces": self.pieces,
            "gross_kg": self.gross_kg,
            "chargeable_kg": self.chargeable_kg,
            "form_type": self.form_type,
            "source": self.source,
        }


@dataclass
class TariffVisionResult:
    rows: list[dict[str, Any]] = field(default_factory=list)
    source: str = "vision"
    notes: str = ""
