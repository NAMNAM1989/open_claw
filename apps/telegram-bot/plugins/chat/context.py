from __future__ import annotations

from core.supabase_client import LogisticsStore

CHAT_SYSTEM = """Bạn là NamNam Ops — trợ lý logistics cho NAM NAM LOGISTICS (forwarder hàng không, eCargo SCSC).
Trả lời ngắn gọn, tiếng Việt, đúng dữ liệu context. Không bịa MAWB/VCT/số tiền.
Nếu thiếu dữ liệu, nói rõ cần user làm gì (/booking, /import_gia, /go)."""


def build_logistics_context(store: LogisticsStore, chat_id: int) -> str:
    pending = store.get_pending_booking(chat_id)
    job = store.get_latest_job_run(chat_id)
    quote_rows = store.list_quotes(chat_id, limit=3)
    tariff = store.get_latest_tariff(chat_id)
    scale = store.get_latest_scale_ticket(chat_id)

    parts = [f"chat_id={chat_id}"]

    if pending:
        b = pending.booking
        parts.append(
            f"Booking pending: xe={b.vehicle_no} flight={b.flight} mawb={b.mawb} "
            f"pcs={b.pcs} gw={b.gross_weight}"
        )
    else:
        parts.append("Booking pending: không có")

    if job:
        parts.append(
            f"Job gần nhất: reg={job.get('registration_no')} vct={job.get('vct_number')} "
            f"status={job.get('status_text')}"
        )

    if quote_rows:
        codes = ", ".join(f"{q.get('quote_code')} {q.get('route')}" for q in quote_rows[:3])
        parts.append(f"Quotes gần đây: {codes}")

    if tariff and tariff.rows:
        parts.append(f"Tariff active: {len(tariff.rows)} dòng ({tariff.source})")

    if scale:
        parts.append(
            f"Phiếu cân gần nhất: awb={scale.get('awb')} gw={scale.get('gross_kg')}kg"
        )

    return "Context logistics:\n" + "\n".join(f"- {p}" for p in parts)
