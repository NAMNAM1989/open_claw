import logging
import sys

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from bot.handlers.chat import cmd_ask, cmd_clear, on_document, on_photo, on_text
from bot.handlers.docs import cmd_baogia, cmd_pkl
from bot.handlers.system import cmd_chatid, cmd_ping, cmd_start
from core.openclaw_client import OpenClawClient
from core.settings import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
log = logging.getLogger("namnam-bot")


def main() -> None:
    if not settings.telegram_bot_token:
        log.error("TELEGRAM_BOT_TOKEN is required")
        sys.exit(1)
    if not settings.openclaw_gateway_token:
        log.error("OPENCLAW_GATEWAY_TOKEN is required")
        sys.exit(1)

    allowed = settings.allowed_ids()
    if not allowed:
        log.warning("ALLOWED_CHAT_IDS empty — bot will ignore all chats until configured")

    app = (
        Application.builder()
        .token(settings.telegram_bot_token)
        .build()
    )
    app.bot_data["allowed_ids"] = allowed
    app.bot_data["openclaw"] = OpenClawClient()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("ping", cmd_ping))
    app.add_handler(CommandHandler("chatid", cmd_chatid))
    app.add_handler(CommandHandler("ask", cmd_ask))
    app.add_handler(CommandHandler("clear", cmd_clear))
    app.add_handler(CommandHandler("baogia", cmd_baogia))
    app.add_handler(CommandHandler("pkl", cmd_pkl))
    app.add_handler(MessageHandler(filters.PHOTO, on_photo))
    app.add_handler(MessageHandler(filters.Document.ALL, on_document))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))

    log.info("NamNam Ops bot starting (allowed_chats=%s)", sorted(allowed))
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()
