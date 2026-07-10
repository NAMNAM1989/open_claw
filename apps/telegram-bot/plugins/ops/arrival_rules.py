from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from plugins.ops.models import ArrivalSlot

VN_TZ = ZoneInfo("Asia/Ho_Chi_Minh")


def compute_arrival(
    *,
    now: datetime | None = None,
    lead_hours: int = 2,
    evening_cutoff_hour: int = 19,
    next_morning_hour: int = 7,
) -> ArrivalSlot:
    """
    Quy tắc hàng vào kho SCSC (greenfield):
    - Mặc định = now + lead_hours (VN)
    - Sau evening_cutoff_hour → 07:00 ngày hôm sau
    """
    now = now or datetime.now(VN_TZ)
    if now.tzinfo is None:
        now = now.replace(tzinfo=VN_TZ)

    if now.hour >= evening_cutoff_hour:
        target = (now + timedelta(days=1)).replace(
            hour=next_morning_hour, minute=0, second=0, microsecond=0
        )
    else:
        target = now + timedelta(hours=lead_hours)
        if target.hour >= evening_cutoff_hour:
            target = (now + timedelta(days=1)).replace(
                hour=next_morning_hour, minute=0, second=0, microsecond=0
            )

    return ArrivalSlot(
        date_str=target.strftime("%d/%m/%Y"),
        time_str=target.strftime("%H:%M"),
    )
