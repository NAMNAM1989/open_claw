from __future__ import annotations

import asyncio

from telegram import Update
from telegram.ext import ContextTypes

from core.openclaw_client import OpenClawError, get_openclaw_client
from core.settings import settings
from core.supabase_client import LogisticsStore, get_store
from plugins.chat.context import CHAT_SYSTEM, build_logistics_context


def _store(context: ContextTypes.DEFAULT_TYPE) -> LogisticsStore:
    return context.application.bot_data.get("store") or get_store()


async def cmd_ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not settings.chat_enabled:
        await update.message.reply_text("Chat AI đang tắt.")
        return

    question = " ".join(context.args or []).strip()
    if not question and update.message.reply_to_message:
        question = (update.message.reply_to_message.text or "").strip()
    if not question:
        await update.message.reply_text("Cú pháp: /ask <câu hỏi>")
        return

    await _answer(update, context, question)


async def handle_ask_mention(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Reply trực tiếp tin nhắn bot (không cần /ask)."""
    if not settings.chat_enabled or not update.message:
        return
    reply = update.message.reply_to_message
    if not reply or not reply.from_user or not reply.from_user.is_bot:
        return
    text = (update.message.text or "").strip()
    if not text or text.startswith("/"):
        return
    await _answer(update, context, text)


async def _answer(update: Update, context: ContextTypes.DEFAULT_TYPE, question: str) -> None:
    client = get_openclaw_client()
    if not client.configured:
        await update.message.reply_text("Chưa cấu hình OpenClaw Gateway cho /ask.")
        return

    store = _store(context)
    chat_id = update.effective_chat.id
    ctx = build_logistics_context(store, chat_id)
    system = f"{CHAT_SYSTEM}\n\n{ctx}"

    await update.message.reply_chat_action("typing")
    try:
        answer = await asyncio.to_thread(
            client.chat,
            question,
            system=system,
            user_key=f"tg:{chat_id}",
        )
    except OpenClawError as exc:
        store.log_ops("error", str(exc), source="openclaw")
        await update.message.reply_text(f"❌ OpenClaw: {exc}")
        return

    store.log_ops("info", "chat_ok", source="openclaw", meta={"chat_id": chat_id})
    if len(answer) > 4000:
        answer = answer[:3990] + "…"
    await update.message.reply_text(answer)
