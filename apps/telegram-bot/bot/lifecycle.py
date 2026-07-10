from __future__ import annotations

import asyncio
import logging

from telegram.ext import Application, ContextTypes

from core.openclaw_client import get_openclaw_client
from core.settings import settings
from core.supabase_client import get_store
from plugins.ops.gmail.watcher import GmailWatcher
from plugins.ops.session_health import check_ecargo_session, format_session_alert

log = logging.getLogger("namnam.mail_watch")


async def startup_health(app: Application) -> None:
    app.bot_data["store"] = get_store()
    session = check_ecargo_session()
    log.info("eCargo session: %s", session.message)
    if not session.ok:
        log.warning(format_session_alert(session))

    oc = get_openclaw_client()
    ok, msg = oc.health_check()
    log.info("OpenClaw: %s", msg)
    if not ok and settings.ai_provider == "openclaw":
        log.warning("OpenClaw health fail — /gia vision và /can vision có thể lỗi")

    if settings.mail_watch_enabled:
        app.bot_data["mail_task"] = asyncio.create_task(_mail_watch_loop(app))


async def shutdown(app: Application) -> None:
    task = app.bot_data.get("mail_task")
    if task:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


async def _mail_watch_loop(app: Application) -> None:
    watcher = GmailWatcher()
    if not watcher.configured:
        log.warning("Mail watch bật nhưng thiếu GMAIL_USER / GMAIL_APP_PASSWORD")
        return

    bot = app.bot
    store = app.bot_data.get("store") or get_store()
    interval = max(30, settings.mail_watch_interval_sec)

    while True:
        try:
            verify = await asyncio.to_thread(watcher.find_verify_mail)
            if verify and verify.verify_url:
                store.log_ops(
                    "info",
                    f"verify_mail reg={verify.registration_no}",
                    source="gmail",
                )
                for chat_id in settings.allowed_ids() or []:
                    await bot.send_message(
                        chat_id,
                        f"📧 Mail xác thực reg {verify.registration_no}\n{verify.verify_url}",
                    )

            qr = await asyncio.to_thread(watcher.find_qr_mail)
            if qr:
                store.log_ops("info", f"qr_mail vct={qr.vct_number}", source="gmail")
                for chat_id in settings.allowed_ids() or []:
                    if qr.image_bytes:
                        await bot.send_photo(
                            chat_id,
                            qr.image_bytes,
                            caption=f"📲 QR VCT {qr.vct_number or '—'} reg {qr.registration_no}",
                        )
                    else:
                        await bot.send_message(
                            chat_id,
                            f"📲 QR mail VCT {qr.vct_number} reg {qr.registration_no}",
                        )
        except Exception as exc:
            log.exception("mail watch error: %s", exc)
            store.log_ops("error", str(exc), source="gmail")
        await asyncio.sleep(interval)
