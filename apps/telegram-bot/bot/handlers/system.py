from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from core.settings import settings


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "NamNam Ops — bot logistics (open_claw).\n"
        "Lệnh: /help"
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "📦 NamNam Ops\n\n"
        "Sales:\n"
        "• /import_gia — Excel tariff\n"
        "• /gia + ảnh — bảng giá (OpenClaw vision)\n"
        "• /tariff · /bao_gia <route> <kg>\n\n"
        "Documents:\n"
        "• /can + ảnh — phiếu cân\n\n"
        "Chat & báo cáo:\n"
        "• /ask <câu hỏi> — AI logistics (OpenClaw)\n"
        "• /ops [tuan|thang] — báo cáo vận hành\n"
        "• /sales [tuan|thang] — báo cáo sales\n\n"
        "Ops eCargo:\n"
        "• Gửi booking (5 dòng hoặc nhãn Xe/Chuyến/MAWB)\n"
        "• `có` hoặc /go — chạy đăng ký\n"
        "• /booking — pending\n"
        "• /status — job gần nhất\n"
        "• /chatid — lấy ID nhóm"
    )


async def cmd_ping(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("pong")
