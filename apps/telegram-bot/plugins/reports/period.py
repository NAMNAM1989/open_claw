from __future__ import annotations

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

VN_TZ = ZoneInfo("Asia/Ho_Chi_Minh")


def parse_period(args: list[str] | None) -> tuple[str, datetime]:
    key = (args[0] if args else "tuan").lower().strip()
    if key in ("thang", "month", "m", "tháng"):
        label = "tháng"
        delta = timedelta(days=30)
    else:
        label = "tuần"
        delta = timedelta(days=7)
    since = datetime.now(VN_TZ) - delta
    return label, since
