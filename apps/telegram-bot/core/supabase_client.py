from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from core.settings import settings
from plugins.ops.models import Booking, BookingRecord, JobResult
from plugins.documents.models import ScaleTicket
from plugins.sales.models import PriceRow, QuoteResult
from plugins.sales.tariff_codec import (
    TariffRecord,
    quote_to_breakdown,
    rows_from_json,
    rows_to_json,
)

log = logging.getLogger("namnam.store")


def _parse_uuid(value: Any) -> UUID | None:
    if not value:
        return None
    try:
        return UUID(str(value))
    except ValueError:
        return None


def _parse_dt(value: Any) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


class LogisticsStore:
    """Supabase khi có credentials; fallback bộ nhớ cho dev/test."""

    def __init__(self, url: str = "", key: str = "") -> None:
        self._url = url or settings.supabase_url
        self._key = key or settings.supabase_service_role_key
        self._client: Any = None
        self._memory_tariffs: dict[int, list[TariffRecord]] = {}
        self._memory_quotes: list[dict[str, Any]] = []
        self._memory_bookings: dict[int, list[BookingRecord]] = {}
        self._memory_jobs: list[dict[str, Any]] = []
        self._memory_scale_tickets: list[dict[str, Any]] = []
        self._memory_ops_log: list[dict[str, Any]] = []

        if self._url and self._key:
            from supabase import create_client

            self._client = create_client(self._url, self._key)
            log.info("LogisticsStore: Supabase connected")
        else:
            log.warning("LogisticsStore: chạy in-memory (chưa cấu hình Supabase)")

    @property
    def is_remote(self) -> bool:
        return self._client is not None

    def get_latest_tariff(self, chat_id: int) -> TariffRecord | None:
        if self._client:
            resp = (
                self._client.table("tariffs")
                .select("*")
                .eq("chat_id", chat_id)
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )
            rows = resp.data or []
            if not rows:
                return None
            row = rows[0]
            return TariffRecord(
                id=_parse_uuid(row.get("id")),
                chat_id=int(row["chat_id"]),
                rows=rows_from_json(row.get("rows_json") or []),
                source=str(row.get("source", "")),
                notes=str(row.get("notes", "")),
                created_at=_parse_dt(row.get("created_at")),
            )

        records = self._memory_tariffs.get(chat_id, [])
        return records[-1] if records else None

    def insert_tariff(
        self,
        chat_id: int,
        price_rows: list[PriceRow],
        *,
        source: str = "excel",
        notes: str = "",
    ) -> TariffRecord:
        payload_rows = rows_to_json(price_rows)
        if self._client:
            resp = (
                self._client.table("tariffs")
                .insert(
                    {
                        "chat_id": chat_id,
                        "source": source,
                        "rows_json": payload_rows,
                        "notes": notes,
                    }
                )
                .execute()
            )
            row = (resp.data or [{}])[0]
            record = TariffRecord(
                id=_parse_uuid(row.get("id")),
                chat_id=chat_id,
                rows=price_rows,
                source=source,
                notes=notes,
                created_at=_parse_dt(row.get("created_at")),
            )
            return record

        record = TariffRecord(
            id=None,
            chat_id=chat_id,
            rows=price_rows,
            source=source,
            notes=notes,
            created_at=datetime.now(timezone.utc),
        )
        self._memory_tariffs.setdefault(chat_id, []).append(record)
        return record

    def insert_quote(self, chat_id: int, result: QuoteResult) -> None:
        payload = {
            "quote_code": result.quote_code,
            "chat_id": chat_id,
            "tariff_id": str(result.tariff_id) if result.tariff_id else None,
            "route": result.route,
            "cargo_type": "general",
            "actual_kg": result.actual_kg,
            "volumetric_kg": result.volumetric_kg,
            "chargeable_kg": result.chargeable_kg,
            "currency": result.currency,
            "total_amount": result.total,
            "breakdown_json": quote_to_breakdown(result),
        }
        if self._client:
            self._client.table("quotes").insert(payload).execute()
            return
        payload["created_at"] = datetime.now(timezone.utc).isoformat()
        payload["chat_id"] = chat_id
        self._memory_quotes.append(payload)

    def log_ops(self, level: str, message: str, *, source: str = "bot", meta: dict | None = None) -> None:
        payload = {
            "level": level,
            "source": source,
            "message": message,
            "meta_json": meta or {},
        }
        if self._client:
            try:
                self._client.table("ops_log").insert(payload).execute()
            except Exception as exc:
                log.warning("ops_log insert failed: %s", exc)
            return
        payload["created_at"] = datetime.now(timezone.utc).isoformat()
        self._memory_ops_log.append(payload)
        log.info("[%s] %s %s", level, source, message)

    def _booking_from_row(self, row: dict[str, Any]) -> BookingRecord:
        booking = Booking(
            vehicle_no=str(row.get("vehicle_no", "")),
            flight=str(row.get("flight", "")),
            flight_date=str(row.get("flight_date", "")),
            destination=str(row.get("destination", "")),
            mawb=str(row.get("mawb", "")),
            pcs=int(row.get("pcs") or 0),
            gross_weight=float(row.get("gross_weight") or 0),
            raw_text=str(row.get("raw_text", "")),
        )
        return BookingRecord(
            id=_parse_uuid(row.get("id")),
            chat_id=int(row["chat_id"]),
            booking=booking,
            status=str(row.get("status", "pending")),
            error_message=str(row.get("error_message", "")),
        )

    def save_booking_pending(self, chat_id: int, booking: Booking) -> BookingRecord:
        payload = {
            "chat_id": chat_id,
            "raw_text": booking.raw_text,
            "vehicle_no": booking.vehicle_no,
            "flight": booking.flight,
            "flight_date": booking.flight_date,
            "destination": booking.destination,
            "mawb": booking.mawb,
            "pcs": booking.pcs,
            "gross_weight": booking.gross_weight,
            "status": "pending",
        }
        if self._client:
            resp = self._client.table("bookings").insert(payload).execute()
            row = (resp.data or [{}])[0]
            return self._booking_from_row(row)

        record = BookingRecord(
            id=uuid4(),
            chat_id=chat_id,
            booking=booking,
            status="pending",
            created_at=datetime.now(timezone.utc),
        )
        self._memory_bookings.setdefault(chat_id, []).append(record)
        return record

    def _memory_booking_dict(self, rec: BookingRecord) -> dict[str, Any]:
        created = rec.created_at or datetime.now(timezone.utc)
        return {
            "id": str(rec.id) if rec.id else None,
            "chat_id": rec.chat_id,
            "vehicle_no": rec.booking.vehicle_no,
            "flight": rec.booking.flight,
            "flight_date": rec.booking.flight_date,
            "destination": rec.booking.destination,
            "mawb": rec.booking.mawb,
            "pcs": rec.booking.pcs,
            "gross_weight": rec.booking.gross_weight,
            "raw_text": rec.booking.raw_text,
            "status": rec.status,
            "error_message": rec.error_message,
            "created_at": created.isoformat(),
        }

    def get_pending_booking(self, chat_id: int) -> BookingRecord | None:
        if self._client:
            resp = (
                self._client.table("bookings")
                .select("*")
                .eq("chat_id", chat_id)
                .eq("status", "pending")
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )
            rows = resp.data or []
            return self._booking_from_row(rows[0]) if rows else None

        for rec in reversed(self._memory_bookings.get(chat_id, [])):
            if rec.status == "pending":
                return rec
        return None

    def update_booking_status(
        self,
        booking_id: UUID | None,
        status: str,
        error_message: str = "",
    ) -> None:
        if not booking_id:
            return

        if self._client:
            self._client.table("bookings").update(
                {"status": status, "error_message": error_message}
            ).eq("id", str(booking_id)).execute()
            return

        for records in self._memory_bookings.values():
            for rec in records:
                if rec.id == booking_id:
                    rec.status = status
                    rec.error_message = error_message

    def save_job_run(self, booking_id: UUID | None, chat_id: int, result: JobResult) -> None:
        payload = {
            "booking_id": str(booking_id) if booking_id else None,
            "chat_id": chat_id,
            "registration_no": result.registration_no,
            "vct_number": result.vct_number,
            "verify_code": result.verify_code,
            "status_text": result.status_text,
            "error_raw": result.error_raw,
            "finished_at": datetime.now(timezone.utc).isoformat(),
        }
        if self._client:
            self._client.table("job_runs").insert(payload).execute()
            return
        payload["started_at"] = datetime.now(timezone.utc).isoformat()
        self._memory_jobs.insert(0, payload)

    def get_latest_job_run(self, chat_id: int) -> dict[str, Any] | None:
        if self._client:
            resp = (
                self._client.table("job_runs")
                .select("*")
                .eq("chat_id", chat_id)
                .order("started_at", desc=True)
                .limit(1)
                .execute()
            )
            rows = resp.data or []
            return rows[0] if rows else None

        jobs = [j for j in self._memory_jobs if j.get("chat_id") == chat_id]
        return jobs[0] if jobs else None

    def save_scale_ticket(self, chat_id: int, ticket: ScaleTicket) -> None:
        payload = {
            "chat_id": chat_id,
            "awb": ticket.awb,
            "flight": ticket.flight,
            "flight_date": ticket.flight_date,
            "pieces": ticket.pieces,
            "gross_kg": ticket.gross_kg,
            "chargeable_kg": ticket.chargeable_kg,
            "form_type": ticket.form_type,
            "source": ticket.source,
            "raw_json": ticket.to_dict(),
        }
        if self._client:
            self._client.table("scale_tickets").insert(payload).execute()
            return
        payload["created_at"] = datetime.now(timezone.utc).isoformat()
        self._memory_scale_tickets.insert(0, payload)

    def get_latest_scale_ticket(self, chat_id: int) -> dict[str, Any] | None:
        if self._client:
            resp = (
                self._client.table("scale_tickets")
                .select("*")
                .eq("chat_id", chat_id)
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )
            rows = resp.data or []
            return rows[0] if rows else None

        items = [t for t in self._memory_scale_tickets if t.get("chat_id") == chat_id]
        return items[0] if items else None

    def _filter_since(self, rows: list[dict[str, Any]], since: datetime | None, *time_fields: str) -> list[dict[str, Any]]:
        if since is None:
            return rows
        out = []
        for row in rows:
            for field in time_fields:
                dt = _parse_dt(row.get(field))
                if dt and dt >= since:
                    out.append(row)
                    break
        return out

    def list_quotes(self, chat_id: int, *, since: datetime | None = None, limit: int = 50) -> list[dict[str, Any]]:
        if self._client:
            q = (
                self._client.table("quotes")
                .select("*")
                .eq("chat_id", chat_id)
                .order("created_at", desc=True)
                .limit(limit)
            )
            if since:
                q = q.gte("created_at", since.isoformat())
            return q.execute().data or []

        rows = [q for q in self._memory_quotes if q.get("chat_id") == chat_id]
        rows = self._filter_since(rows, since, "created_at")
        rows.sort(key=lambda r: r.get("created_at", ""), reverse=True)
        return rows[:limit]

    def list_job_runs(self, chat_id: int, *, since: datetime | None = None, limit: int = 50) -> list[dict[str, Any]]:
        if self._client:
            q = (
                self._client.table("job_runs")
                .select("*")
                .eq("chat_id", chat_id)
                .order("started_at", desc=True)
                .limit(limit)
            )
            if since:
                q = q.gte("started_at", since.isoformat())
            return q.execute().data or []

        rows = [j for j in self._memory_jobs if j.get("chat_id") == chat_id]
        rows = self._filter_since(rows, since, "started_at", "finished_at")
        return rows[:limit]

    def list_bookings(self, chat_id: int, *, since: datetime | None = None, limit: int = 50) -> list[dict[str, Any]]:
        if self._client:
            q = (
                self._client.table("bookings")
                .select("*")
                .eq("chat_id", chat_id)
                .order("created_at", desc=True)
                .limit(limit)
            )
            if since:
                q = q.gte("created_at", since.isoformat())
            return q.execute().data or []

        rows = []
        for rec in self._memory_bookings.get(chat_id, []):
            rows.append(self._memory_booking_dict(rec))
        rows = self._filter_since(rows, since, "created_at")
        return rows[:limit]

    def list_scale_tickets(self, chat_id: int, *, since: datetime | None = None, limit: int = 50) -> list[dict[str, Any]]:
        if self._client:
            q = (
                self._client.table("scale_tickets")
                .select("*")
                .eq("chat_id", chat_id)
                .order("created_at", desc=True)
                .limit(limit)
            )
            if since:
                q = q.gte("created_at", since.isoformat())
            return q.execute().data or []

        rows = [t for t in self._memory_scale_tickets if t.get("chat_id") == chat_id]
        rows = self._filter_since(rows, since, "created_at")
        return rows[:limit]

    def list_ops_errors(self, *, since: datetime | None = None, source: str = "", limit: int = 20) -> list[dict[str, Any]]:
        if self._client:
            q = (
                self._client.table("ops_log")
                .select("*")
                .eq("level", "error")
                .order("created_at", desc=True)
                .limit(limit)
            )
            if source:
                q = q.eq("source", source)
            if since:
                q = q.gte("created_at", since.isoformat())
            return q.execute().data or []

        rows = [e for e in self._memory_ops_log if e.get("level") == "error"]
        if source:
            rows = [e for e in rows if e.get("source") == source]
        rows = self._filter_since(rows, since, "created_at")
        return rows[:limit]


_store: LogisticsStore | None = None


def get_store() -> LogisticsStore:
    global _store
    if _store is None:
        _store = LogisticsStore()
    return _store


def reset_store() -> None:
    global _store
    _store = None
