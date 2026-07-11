import logging

from telegram import Update
from telegram.ext import ContextTypes

from bot.access import chat_id, is_allowed

log = logging.getLogger("namnam-bot.handlers")


async def _deny_or_none(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    allowed: set[int] = context.bot_data["allowed_ids"]
    cid = chat_id(update)
    if is_allowed(update, allowed):
        return False
    log.warning("denied chat_id=%s allowed=%s", cid, sorted(allowed))
    msg = update.effective_message
    if msg and cid is not None:
        await msg.reply_text(
            f"Chat chưa được phép (id={cid}).\n"
            "Gửi /chatid để xem ID, rồi thêm vào ALLOWED_CHAT_IDS trên Railway."
        )
    return True


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await _deny_or_none(update, context):
        return
    await update.effective_message.reply_text(
        "NamNam Ops.\n"
        "Lệnh: /ping · /chatid · /ask · /clear · /baogia · /pkl\n"
        "Gửi text, ảnh, hoặc Excel (.xlsx) để hỏi."
    )


async def cmd_ping(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await _deny_or_none(update, context):
        return
    await update.effective_message.reply_text("pong")


async def cmd_chatid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    cid = chat_id(update)
    if cid is None:
        return
    allowed: set[int] = context.bot_data["allowed_ids"]
    status = "đã phép" if cid in allowed else "chưa phép — thêm vào ALLOWED_CHAT_IDS"
    await update.effective_message.reply_text(f"chat_id={cid}\n({status})")
