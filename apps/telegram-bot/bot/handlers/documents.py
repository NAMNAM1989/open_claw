from __future__ import annotations

import re

from telegram import Update
from telegram.ext import ContextTypes

from core.openclaw_client import OpenClawError, get_openclaw_client
from core.settings import settings
from core.supabase_client import LogisticsStore, get_store
from plugins.documents.extractors import extract_scale_ticket, extract_tariff_from_image
from plugins.documents.models import ScaleTicket

SCALE_HINT = re.compile(r"(/can|phiếu cân|phieu can|cân hàng|can hang)", re.I)
TARIFF_HINT = re.compile(r"(/gia|bảng giá|bang gia|tariff|giá cước|gia cuoc)", re.I)


def _store(context: ContextTypes.DEFAULT_TYPE) -> LogisticsStore:
    return context.application.bot_data.get("store") or get_store()


def _hint_from_message(message) -> str:
    parts = [message.caption or "", message.text or ""]
    return " ".join(parts)


def _wants_scale(text: str) -> bool:
    return bool(SCALE_HINT.search(text))


def _wants_tariff(text: str) -> bool:
    return bool(TARIFF_HINT.search(text))


async def _download_photo_bytes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bytes | None:
    message = update.message
    if not message:
        return None

    photo = None
    if message.photo:
        photo = message.photo[-1]
    elif message.reply_to_message and message.reply_to_message.photo:
        photo = message.reply_to_message.photo[-1]
    if not photo:
        return None

    tg_file = await context.bot.get_file(photo.file_id)
    return bytes(await tg_file.download_as_bytearray())


def _preview_tariff_rows(rows, limit: int = 6) -> str:
    lines = []
    for row in rows[:limit]:
        band = row.weight_range or f"{row.weight_min_kg:g}+"
        lines.append(f"• {row.route} [{band}] {row.price_per_kg:,.0f} {row.currency}/kg")
    if len(rows) > limit:
        lines.append(f"… {len(rows) - limit} dòng khác")
    return "\n".join(lines)


async def cmd_can(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _process_scale(update, context, force=True)


async def cmd_gia(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _process_tariff(update, context, force=True)


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    if not message:
        return

    hint = _hint_from_message(message)
    if _wants_scale(hint):
        await _process_scale(update, context, force=False)
    elif _wants_tariff(hint):
        await _process_tariff(update, context, force=False)


async def _process_scale(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    *,
    force: bool,
) -> None:
    if not settings.scale_ticket_ocr_enabled:
        await update.message.reply_text("Đọc phiếu cân đang tắt.")
        return

    image = await _download_photo_bytes(update, context)
    if not image:
        await update.message.reply_text(
            "Gửi ảnh phiếu cân kèm caption `/can` hoặc reply ảnh bằng `/can`."
        )
        return

    store = _store(context)
    chat_id = update.effective_chat.id
    caption = _hint_from_message(update.message)
    user_key = f"tg:{chat_id}"

    try:
        ticket = extract_scale_ticket(
            image,
            caption=caption,
            user_key=user_key,
            use_vision=settings.ai_provider == "openclaw",
        )
    except ValueError as exc:
        await update.message.reply_text(f"❌ {exc}")
        return
    except OpenClawError as exc:
        await update.message.reply_text(f"❌ OpenClaw: {exc}")
        return

    store.save_scale_ticket(chat_id, ticket)
    store.log_ops("info", f"scale_ticket awb={ticket.awb}", source="documents")
    await update.message.reply_text(ticket.summary())


async def _process_tariff(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    *,
    force: bool,
) -> None:
    if not settings.image_reader_enabled:
        await update.message.reply_text("Đọc bảng giá ảnh đang tắt.")
        return

    image = await _download_photo_bytes(update, context)
    if not image:
        await update.message.reply_text(
            "Gửi ảnh bảng giá kèm caption `/gia` hoặc reply ảnh bằng `/gia`."
        )
        return

    store = _store(context)
    chat_id = update.effective_chat.id
    user_key = f"tg:{chat_id}"

    try:
        rows, _meta = extract_tariff_from_image(image, user_key=user_key)
    except (ValueError, OpenClawError) as exc:
        await update.message.reply_text(f"❌ {exc}")
        return

    record = store.insert_tariff(chat_id, rows, source="vision", notes="image /gia")
    store.log_ops("info", f"tariff_vision {len(rows)} rows", source="documents")
    mode = "Supabase" if store.is_remote else "in-memory"
    await update.message.reply_text(
        f"✅ Đã lưu {len(rows)} dòng giá từ ảnh ({mode}).\n\n"
        f"{_preview_tariff_rows(rows)}\n\n"
        "Dùng `/bao_gia SGN-HKG 120` để tính thử."
    )
