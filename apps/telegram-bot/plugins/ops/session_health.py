from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

from core.settings import settings


@dataclass
class SessionStatus:
    ok: bool
    message: str
    age_days: float | None = None


def ecargo_storage_path() -> Path | None:
    rel = (settings.ecargo_storage_state or "").strip()
    if not rel:
        return None
    return Path(rel)


def check_ecargo_session(*, max_age_days: float = 7.0) -> SessionStatus:
    path = ecargo_storage_path()
    if not path:
        return SessionStatus(False, "Chưa cấu hình ECARGO_STORAGE_STATE.")
    if not path.is_file():
        return SessionStatus(
            False,
            f"Thiếu file session: {path}\nChạy scripts/save_ecargo_session.py",
        )

    age_days = (time.time() - path.stat().st_mtime) / 86400
    if age_days > max_age_days:
        return SessionStatus(
            False,
            f"Session eCargo cũ ({age_days:.1f} ngày) — nên refresh.",
            age_days=age_days,
        )
    return SessionStatus(True, "Session eCargo OK.", age_days=age_days)


def format_session_alert(status: SessionStatus) -> str:
    if status.ok:
        return f"✅ {status.message}"
    return f"⚠️ {status.message}"
