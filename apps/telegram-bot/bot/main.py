import logging

from telegram.ext import Application, CommandHandler, MessageHandler, filters

from bot.handlers.booking import (
    cmd_booking,
    cmd_chatid,
    cmd_go,
    cmd_status,
    handle_booking_text,
)
from bot.handlers.chat import cmd_ask, handle_ask_mention
from bot.handlers.documents import cmd_can, cmd_gia, handle_photo
from bot.handlers.reports import cmd_ops, cmd_sales
from bot.handlers.tariff import cmd_bao_gia, cmd_import_gia, cmd_tariff
from bot.handlers.system import cmd_help, cmd_ping, cmd_start
from bot.lifecycle import shutdown, startup_health
from core.settings import settings
from core.supabase_client import get_store

logging.basicConfig(
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
    level=logging.INFO,
)
log = logging.getLogger("namnam.bot")


def build_app() -> Application:
    if not settings.telegram_bot_token:
        raise SystemExit("TELEGRAM_BOT_TOKEN chưa cấu hình")

    app = (
        Application.builder()
        .token(settings.telegram_bot_token)
        .post_init(startup_health)
        .post_shutdown(shutdown)
        .build()
    )

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("ping", cmd_ping))
    app.add_handler(CommandHandler("chatid", cmd_chatid))
    app.add_handler(CommandHandler("bao_gia", cmd_bao_gia))
    app.add_handler(CommandHandler("tariff", cmd_tariff))
    app.add_handler(CommandHandler("import_gia", cmd_import_gia))
    app.add_handler(CommandHandler("can", cmd_can))
    app.add_handler(CommandHandler("gia", cmd_gia))
    app.add_handler(CommandHandler("booking", cmd_booking))
    app.add_handler(CommandHandler("go", cmd_go))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("ask", cmd_ask))
    app.add_handler(CommandHandler("ops", cmd_ops))
    app.add_handler(CommandHandler("sales", cmd_sales))
    app.add_handler(
        MessageHandler(filters.PHOTO, handle_photo),
        group=2,
    )
    app.add_handler(
        MessageHandler(filters.REPLY & filters.TEXT & ~filters.COMMAND, handle_ask_mention),
        group=3,
    )
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_booking_text),
        group=1,
    )
    app.bot_data["store"] = get_store()
    return app


def main() -> None:
    log.info("NamNam Ops bot starting (open_claw greenfield)")
    app = build_app()
    app.run_polling(allowed_updates=["message"])


if __name__ == "__main__":
    main()
