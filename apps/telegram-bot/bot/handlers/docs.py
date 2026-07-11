import logging
from io import BytesIO

from telegram import Update
from telegram.ext import ContextTypes

from bot.handlers.system import _deny_or_none
from core.docs_parse import parse_pkl, parse_quote
from core.pdf_pkl import render_pkl_pdf
from core.pdf_quote import build_quote, render_quote_pdf
from core.settings import settings

log = logging.getLogger("namnam-bot.handlers")

_HELP_BAOGIA = (
    "Dùng:\n"
    "/baogia SGN-HKG 120kg 16000\n"
    "hoặc:\n"
    "/baogia\n"
    "Khách: …\n"
    "Route: SGN-HKG\n"
    "KL: 120\n"
    "Đơn giá: 16000\n"
    "Kiện: 2\n"
    "Kích thước: 60x40x40"
)

_HELP_PKL = (
    "Dùng:\n"
    "/pkl\n"
    "MAWB: 123-45678900\n"
    "Shipper: …\n"
    "Consignee: …\n"
    "Origin: SGN\n"
    "Dest: HKG\n"
    "1. Hàng A | 10 | 100kg | 50x40x40"
)


def _body(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    args = " ".join(context.args).strip() if context.args else ""
    msg = update.effective_message
    # Cho phép dán nhiều dòng ngay sau lệnh trong cùng tin
    raw = (msg.text or msg.caption or "") if msg else ""
    # Bỏ phần /command@bot
    lines = raw.splitlines()
    if lines:
        first = lines[0]
        if first.startswith("/"):
            # giữ phần sau lệnh trên cùng dòng nếu có
            parts = first.split(maxsplit=1)
            rest_first = parts[1] if len(parts) > 1 else ""
            rest = "\n".join([rest_first] + lines[1:]).strip()
            return rest or args
    return args


async def cmd_baogia(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await _deny_or_none(update, context):
        return
    msg = update.effective_message
    if not msg:
        return
    body = _body(update, context)
    if not body:
        await msg.reply_text(_HELP_BAOGIA)
        return
    try:
        q = parse_quote(body)
        divisor = settings.volumetric_divisor
        result = build_quote(q, divisor=divisor)
        pdf = render_quote_pdf(result)
        caption = (
            f"Báo giá {result.quote_code}\n"
            f"{result.route} · {result.chargeable_kg:g} kg × "
            f"{result.unit_price:,.0f} = {result.total:,.0f} {result.currency}\n"
            f"{result.disclaimer}"
        ).replace(",", ".")
        await msg.reply_document(
            document=BytesIO(pdf),
            filename=f"{result.quote_code}.pdf",
            caption=caption[:1024],
        )
    except ValueError as exc:
        await msg.reply_text(str(exc))
    except Exception as exc:
        log.warning("baogia error: %s", exc)
        await msg.reply_text(f"Không tạo được PDF: {exc}")


async def cmd_pkl(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await _deny_or_none(update, context):
        return
    msg = update.effective_message
    if not msg:
        return
    body = _body(update, context)
    if not body:
        await msg.reply_text(_HELP_PKL)
        return
    try:
        p = parse_pkl(body)
        divisor = settings.volumetric_divisor
        pdf = render_pkl_pdf(p, divisor=divisor)
        total_kg = sum(x.weight_kg for x in p.lines)
        total_pcs = sum(x.pieces for x in p.lines)
        name = (p.mawb or "PKL").replace("/", "-").replace(" ", "")
        caption = (
            f"PKL {p.mawb or ''}\n"
            f"{p.origin or '—'}→{p.dest or '—'} · {len(p.lines)} dòng · "
            f"{total_pcs} kiện · {total_kg:g} kg"
        ).strip()
        await msg.reply_document(
            document=BytesIO(pdf),
            filename=f"PKL-{name}.pdf",
            caption=caption[:1024],
        )
    except ValueError as exc:
        await msg.reply_text(str(exc))
    except Exception as exc:
        log.warning("pkl error: %s", exc)
        await msg.reply_text(f"Không tạo được PDF: {exc}")
