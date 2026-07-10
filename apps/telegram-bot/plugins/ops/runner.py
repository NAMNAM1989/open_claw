from __future__ import annotations

import asyncio
import logging
from uuid import UUID

from core.settings import settings
from core.supabase_client import LogisticsStore
from plugins.ops.ecargo.browser import get_ecargo_backend
from plugins.ops.error_catalog import format_user_error, is_session_error
from plugins.ops.models import Booking, JobResult
from plugins.ops.session_health import check_ecargo_session
from plugins.ops.validator import BookingValidationError, require_valid_booking

log = logging.getLogger("namnam.runner")


class EcargoRunner:
    def __init__(self, store: LogisticsStore) -> None:
        self._store = store

    async def run_booking_job(self, chat_id: int, booking_id: UUID | None, booking: Booking) -> JobResult:
        session = check_ecargo_session()
        if not session.ok and not settings.ecargo_dry_run:
            raise RuntimeError(session.message)

        require_valid_booking(booking)
        if booking_id:
            self._store.update_booking_status(booking_id, "running")

        try:
            backend = get_ecargo_backend()
            result = await asyncio.to_thread(backend.create_vct, booking)
            if booking_id:
                self._store.save_job_run(booking_id, chat_id, result)
                self._store.update_booking_status(booking_id, "done")
            self._store.log_ops(
                "info",
                f"job_ok reg={result.registration_no}",
                source="ecargo",
                meta={"chat_id": chat_id, "mawb": booking.mawb},
            )
            return result
        except BookingValidationError:
            raise
        except Exception as exc:
            raw = str(exc)
            if booking_id:
                self._store.update_booking_status(booking_id, "error", raw)
            self._store.log_ops("error", raw, source="ecargo", meta={"chat_id": chat_id})
            if is_session_error(raw):
                raise RuntimeError(session.message or raw) from exc
            raise RuntimeError(format_user_error(raw)) from exc
