import logging

from telegram import Update
from telegram.ext import ContextTypes

from bot.handlers.system import _deny_or_none
from core.chat_memory import sessions
from core.excel_read import excel_to_text, is_excel_filename, is_excel_mime
from core.openclaw_client import OpenClawClient

log = logging.getLogger("namnam-bot.handlers")

_MAX_IMAGE_BYTES = 500_000  # ~0.5MB
_MAX_EXCEL_BYTES = 2 * 1024 * 1024  # 2MB
_TARGET_PHOTO_WIDTH = 800


def _pick_photo(photos: list):
    """Chọn ảnh gần ~800px thay vì bản lớn nhất (tiết kiệm token vision)."""
    if not photos:
        return None
    best = photos[0]
    best_gap = abs((best.width or 0) - _TARGET_PHOTO_WIDTH)
    for p in photos[1:]:
        gap = abs((p.width or 0) - _TARGET_PHOTO_WIDTH)
        if gap < best_gap:
            best, best_gap = p, gap
    return best


async def cmd_ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await _deny_or_none(update, context):
        return
    msg = update.effective_message
    if not msg:
        return
    question = " ".join(context.args).strip()
    if not question:
        await msg.reply_text("Dùng: /ask <câu hỏi>")
        return
    await _reply_openclaw(msg, update.effective_chat.id, question, context)


async def cmd_clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await _deny_or_none(update, context):
        return
    msg = update.effective_message
    chat = update.effective_chat
    if not msg or not chat:
        return
    sessions.clear(chat.id)
    await msg.reply_text("Đã xóa bộ nhớ hội thoại của chat này.")


async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await _deny_or_none(update, context):
        return
    msg = update.effective_message
    if not msg or not msg.text or msg.text.startswith("/"):
        return
    text = msg.text.strip()
    low = text.lower()
    if low.startswith(("baogia", "báo giá", "bao gia")):
        await msg.reply_text("Dùng /baogia … để tạo PDF báo giá (không qua AI).")
        return
    if low.startswith("pkl") or low.startswith("packing"):
        await msg.reply_text("Dùng /pkl … để tạo PDF packing list (không qua AI).")
        return
    await _reply_openclaw(msg, update.effective_chat.id, text, context)


async def on_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await _deny_or_none(update, context):
        return
    msg = update.effective_message
    chat = update.effective_chat
    if not msg or not chat or not msg.photo:
        return

    photo = _pick_photo(list(msg.photo))
    if photo is None:
        return
    caption = (msg.caption or "").strip()
    client: OpenClawClient = context.bot_data["openclaw"]
    user = f"{sessions.user_key(chat.id)}:vision"

    try:
        await msg.chat.send_action("typing")
        tg_file = await context.bot.get_file(photo.file_id)
        image_bytes = bytes(await tg_file.download_as_bytearray())
        if len(image_bytes) > _MAX_IMAGE_BYTES:
            await msg.reply_text("Ảnh quá lớn. Gửi ảnh nhỏ hơn (~1MB).")
            return

        answer = await client.chat_vision(
            chat.id,
            caption,
            image_bytes,
            mime="image/jpeg",
            user=user,
        )
        await msg.reply_text(answer[:4000])
    except Exception as exc:
        log.warning("openclaw vision error chat_id=%s: %s", chat.id, exc)
        await msg.reply_text(str(exc))


async def on_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await _deny_or_none(update, context):
        return
    msg = update.effective_message
    chat = update.effective_chat
    if not msg or not chat or not msg.document:
        return

    doc = msg.document
    name = doc.file_name or "file"
    mime = doc.mime_type or ""
    if not (is_excel_filename(name) or is_excel_mime(mime)):
        await msg.reply_text(
            "Hiện chỉ đọc Excel (.xlsx). Gửi file .xlsx hoặc ảnh/chữ."
        )
        return
    if name.lower().endswith(".xls") and not name.lower().endswith((".xlsx", ".xlsm")):
        await msg.reply_text("File .xls cũ chưa hỗ trợ. Lưu lại thành .xlsx rồi gửi.")
        return

    caption = (msg.caption or "").strip()
    try:
        await msg.chat.send_action("typing")
        if doc.file_size and doc.file_size > _MAX_EXCEL_BYTES:
            await msg.reply_text("File Excel quá lớn (giới hạn ~2MB).")
            return
        tg_file = await context.bot.get_file(doc.file_id)
        raw = bytes(await tg_file.download_as_bytearray())
        if len(raw) > _MAX_EXCEL_BYTES:
            await msg.reply_text("File Excel quá lớn (giới hạn ~2MB).")
            return

        table = excel_to_text(raw, name)
        prompt = (
            f"{caption}\n\n--- Nội dung Excel ---\n{table}"
            if caption
            else f"Tóm tắt ngắn nội dung Excel (ý chính, số liệu nổi bật):\n\n{table}"
        )
        await _reply_openclaw(msg, chat.id, prompt, context, max_chars=4000)
    except Exception as exc:
        log.warning("excel read error chat_id=%s: %s", chat.id, exc)
        await msg.reply_text(f"Không đọc được Excel: {exc}")


async def _reply_openclaw(
    msg,
    chat_id: int,
    text: str,
    context: ContextTypes.DEFAULT_TYPE,
    *,
    max_chars: int | None = None,
) -> None:
    client: OpenClawClient = context.bot_data["openclaw"]
    user = sessions.user_key(chat_id)
    try:
        await msg.chat.send_action("typing")
        answer = await client.chat(chat_id, text, user=user, max_chars=max_chars)
        await msg.reply_text(answer[:4000])
    except Exception as exc:
        log.warning("openclaw error chat_id=%s: %s", chat_id, exc)
        await msg.reply_text(str(exc))
