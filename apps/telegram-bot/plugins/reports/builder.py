from __future__ import annotations

from collections import Counter
from datetime import datetime
from typing import Any

from core.supabase_client import LogisticsStore


def _parse_dt(value: Any) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def _in_period(row: dict[str, Any], since: datetime, *fields: str) -> bool:
    for field in fields:
        dt = _parse_dt(row.get(field))
        if dt and dt >= since:
            return True
    return False


def build_ops_report(store: LogisticsStore, chat_id: int, *, label: str, since: datetime) -> str:
    jobs = store.list_job_runs(chat_id, since=since)
    bookings = store.list_bookings(chat_id, since=since)
    scales = store.list_scale_tickets(chat_id, since=since)
    errors = store.list_ops_errors(since=since, source="ecargo")

    status_counts = Counter(b.get("status", "?") for b in bookings)
    done_jobs = [j for j in jobs if j.get("status_text") in ("submitted", "dry_run_ok", "ok")]

    lines = [
        f"📊 Báo cáo Ops — {label}",
        "",
        f"• Booking: {len(bookings)} (pending {status_counts.get('pending', 0)}, "
        f"done {status_counts.get('done', 0)}, error {status_counts.get('error', 0)})",
        f"• Job eCargo: {len(jobs)} (ok {len(done_jobs)})",
        f"• Phiếu cân: {len(scales)}",
        f"• Lỗi eCargo (log): {len(errors)}",
    ]

    if jobs:
        last = jobs[0]
        lines.extend(
            [
                "",
                "Job gần nhất:",
                f"• Reg {last.get('registration_no', '—')} · VCT {last.get('vct_number', '—')}",
            ]
        )
    return "\n".join(lines)


def build_sales_report(store: LogisticsStore, chat_id: int, *, label: str, since: datetime) -> str:
    quotes = store.list_quotes(chat_id, since=since)
    if not quotes:
        return f"📈 Báo cáo Sales — {label}\n\nChưa có quote trong kỳ."

    total = sum(float(q.get("total_amount") or 0) for q in quotes)
    currency = quotes[0].get("currency", "VND")
    routes = Counter(str(q.get("route", "?")) for q in quotes)
    top_route, top_count = routes.most_common(1)[0]

    lines = [
        f"📈 Báo cáo Sales — {label}",
        "",
        f"• Số quote: {len(quotes)}",
        f"• Tổng ước tính: {total:,.0f} {currency}",
        f"• Route nhiều nhất: {top_route} ({top_count} quote)",
    ]

    lines.append("")
    lines.append("Quote gần nhất:")
    last = quotes[0]
    lines.append(
        f"• {last.get('quote_code', '—')} · {last.get('route', '—')} · "
        f"{float(last.get('total_amount') or 0):,.0f} {currency}"
    )
    return "\n".join(lines)
