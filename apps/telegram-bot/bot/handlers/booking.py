from __future__ import annotations

import re

from telegram import Update
from telegram.ext import ContextTypes

from core.settings import settings
from core.supabase_client import LogisticsStore, get_store
from plugins.ops.parser import parse_booking
from plugins.ops.runner import EcargoRunner
from plugins.ops.session_health import check_ecargo_session, format_session_alert
from plugins.ops.validator import BookingValidationError, validate_booking

CONFIRM_RE = re.compile(r"^(có|co|ok|yes|✅|👍|/go)$", re.I)


def _store_from_context(context: ContextTypes.DEFAULT_TYPE) -> LogisticsStore:
    return context.application.bot_data.get("store") or get_store()


async def cmd_chatid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat:
        await update.message.reply_text(f"chat_id: {update.effective_chat.id}")


async def cmd_booking(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    store = _store_from_context(context)
    chat_id = update.effective_chat.id
    pending = store.get_pending_booking(chat_id)
    if not pending:
        await update.message.reply_text("Không có booking pending.")
        return
    await update.message.reply_text(
        f"📋 Booking pending\n\n{pending.booking.summary()}\n\nGõ `có` hoặc `/go` để chạy eCargo."
    )


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    store = _store_from_context(context)
    job = store.get_latest_job_run(update.effective_chat.id)
    if not job:
        await update.message.reply_text("Chưa có job eCargo nào.")
        return
    await update.message.reply_text(
        "📊 Job gần nhất\n"
        f"• Reg: {job.get('registration_no', '—')}\n"
        f"• VCT: {job.get('vct_number', '—')}\n"
        f"• Status: {job.get('status_text', '—')}"
    )


async def cmd_go(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _run_pending(update, context)


async def handle_booking_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not settings.ops_enabled or not update.message or not update.message.text:
        return
    text = update.message.text.strip()
    if text.startswith("/"):
        return
    if CONFIRM_RE.match(text):
        await _run_pending(update, context)
        return

    booking = parse_booking(
        text,
        default_pcs=settings.ecargo_default_pcs,
        default_gw=settings.ecargo_default_gw,
    )
    if not booking:
        return

    errors = validate_booking(booking)
    store = _store_from_context(context)
    if errors:
        await update.message.reply_text(
            "⚠️ Booking chưa hợp lệ:\n" + "\n".join(f"• {e}" for e in errors)
        )
        return

    record = store.save_booking_pending(update.effective_chat.id, booking)
    await update.message.reply_text(
        f"✅ Đã lưu booking pending\n\n{booking.summary()}\n\nGõ `có` hoặc `/go` để đăng ký eCargo."
    )
    store.log_ops("info", "booking_pending", meta={"chat_id": update.effective_chat.id, "mawb": booking.mawb})


async def _run_pending(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not settings.ops_enabled:
        await update.message.reply_text("Ops/eCargo đang tắt.")
        return

    store = _store_from_context(context)
    chat_id = update.effective_chat.id
    pending = store.get_pending_booking(chat_id)
    if not pending:
        await update.message.reply_text("Không có booking pending — gửi thông tin xe/chuyến/MAWB trước.")
        return

    session = check_ecargo_session()
    if not session.ok and not settings.ecargo_dry_run:
        await update.message.reply_text(format_session_alert(session))
        return

    await update.message.reply_text("⏳ Đang chạy eCargo…")
    runner = EcargoRunner(store)
    try:
        result = await runner.run_booking_job(chat_id, pending.id, pending.booking)
    except BookingValidationError as exc:
        await update.message.reply_text(f"❌ {exc}")
        return
    except RuntimeError as exc:
        await update.message.reply_text(str(exc))
        return

    lines = [
        "✅ eCargo xong",
        f"• Reg: {result.registration_no or '—'}",
        f"• VCT: {result.vct_number or '—'}",
        f"• {result.status_text or 'ok'}",
    ]
    if settings.ecargo_dry_run:
        lines.append("_(dry-run — chưa gửi form thật)_")
    if settings.mail_watch_enabled:
        lines.append("📧 Đang chờ mail xác thực/QR (mail watcher).")
    await update.message.reply_text("\n".join(lines))
