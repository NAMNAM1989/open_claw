from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from core.supabase_client import LogisticsStore, get_store
from plugins.reports.builder import build_ops_report, build_sales_report
from plugins.reports.period import parse_period


def _store(context: ContextTypes.DEFAULT_TYPE) -> LogisticsStore:
    return context.application.bot_data.get("store") or get_store()


async def cmd_ops(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    label, since = parse_period(context.args)
    text = build_ops_report(_store(context), update.effective_chat.id, label=label, since=since)
    await update.message.reply_text(text)


async def cmd_sales(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    label, since = parse_period(context.args)
    text = build_sales_report(_store(context), update.effective_chat.id, label=label, since=since)
    await update.message.reply_text(text)
