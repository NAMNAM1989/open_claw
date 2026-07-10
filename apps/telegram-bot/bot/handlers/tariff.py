from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from core.settings import settings
from core.supabase_client import LogisticsStore, get_store
from plugins.sales.excel_importer import ExcelImportError, parse_tariff_excel
from plugins.sales.models import QuoteRequest
from plugins.sales.quote_engine import compute_quote


def _format_quote(result) -> str:
    lines = [
        f"💰 Báo giá {result.quote_code}",
        f"{result.route} · tính cườc {result.chargeable_kg:g} kg",
        "",
        f"• Cân thực: {result.actual_kg:g} kg",
    ]
    if result.volumetric_kg:
        lines.append(f"• Cân quy đổi: {result.volumetric_kg:g} kg")
    for item in result.line_items:
        if item.formula:
            lines.append(
                f"• {item.label}: {item.formula} = {item.amount:,.0f} {result.currency}"
            )
        else:
            lines.append(f"• {item.label}: {item.amount:,.0f} {result.currency}")
    lines.extend(
        [
            f"• Tổng ước tính: {result.total:,.0f} {result.currency}",
            "",
            f"⚠️ {result.disclaimer}",
        ]
    )
    return "\n".join(lines)


def _store_from_context(context: ContextTypes.DEFAULT_TYPE) -> LogisticsStore:
    return context.application.bot_data.get("store") or get_store()


async def _download_document_bytes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bytes | None:
    message = update.message
    if not message:
        return None

    doc = message.document
    if not doc and message.reply_to_message:
        doc = message.reply_to_message.document
    if not doc:
        return None

    name = (doc.file_name or "").lower()
    if not name.endswith((".xlsx", ".xlsm")):
        return None

    tg_file = await context.bot.get_file(doc.file_id)
    return bytes(await tg_file.download_as_bytearray())


def _preview_rows(rows, limit: int = 5) -> str:
    lines = []
    for row in rows[:limit]:
        band = row.weight_range or f"{row.weight_min_kg:g}+"
        lines.append(f"• {row.route} [{band}] {row.price_per_kg:,.0f} {row.currency}/kg")
    if len(rows) > limit:
        lines.append(f"… và {len(rows) - limit} dòng khác")
    return "\n".join(lines)


async def cmd_import_gia(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    if not message:
        return

    raw = await _download_document_bytes(update, context)
    if raw is None:
        await message.reply_text(
            "Gửi file Excel (.xlsx) kèm caption `/import_gia`\n"
            "hoặc reply file Excel bằng `/import_gia`.\n\n"
            "Cột bắt buộc: Route, Min_kg, Sell_rate.\n"
            "Mẫu: `templates/tariff_template.xlsx` trong repo."
        )
        return

    try:
        rows = parse_tariff_excel(raw)
    except ExcelImportError as exc:
        await message.reply_text(f"❌ Import lỗi: {exc}")
        return

    store = _store_from_context(context)
    chat_id = message.chat_id
    record = store.insert_tariff(
        chat_id,
        rows,
        source="excel",
        notes=f"file={message.document.file_name if message.document else 'reply'}",
    )
    store.log_ops(
        "info",
        f"import_gia {len(rows)} rows",
        meta={"chat_id": chat_id, "tariff_id": str(record.id) if record.id else None},
    )

    mode = "Supabase" if store.is_remote else "in-memory"
    await message.reply_text(
        f"✅ Đã import {len(rows)} dòng giá ({mode}).\n\n"
        f"{_preview_rows(rows)}\n\n"
        "Dùng `/bao_gia SGN-HKG 120` để tính thử."
    )


async def cmd_tariff(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    if not message:
        return

    store = _store_from_context(context)
    record = store.get_latest_tariff(message.chat_id)
    if not record or not record.rows:
        await message.reply_text(
            "Chưa có bảng giá.\nGửi Excel + caption `/import_gia`."
        )
        return

    created = ""
    if record.created_at:
        created = record.created_at.strftime("%d/%m/%Y %H:%M")
    header = f"📋 Tariff active — {len(record.rows)} dòng"
    if created:
        header += f" ({created})"
    await message.reply_text(f"{header}\n\n{_preview_rows(record.rows, limit=8)}")


async def cmd_bao_gia(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    if not message:
        return

    if not settings.quote_engine_enabled:
        await message.reply_text("Quote engine đang tắt.")
        return

    args = context.args or []
    if len(args) < 2:
        await message.reply_text(
            "Cú pháp: /bao_gia SGN-HKG 120\n"
            "Import tariff trước: Excel + `/import_gia`."
        )
        return

    route, weight_raw = args[0], args[1]
    try:
        weight = float(weight_raw.replace(",", "."))
    except ValueError:
        await message.reply_text("Khối lượng không hợp lệ.")
        return

    store = _store_from_context(context)
    tariff = store.get_latest_tariff(message.chat_id)
    if not tariff or not tariff.rows:
        await message.reply_text(
            "Chưa có bảng giá cho nhóm này.\n"
            "Gửi Excel + caption `/import_gia`."
        )
        return

    result = compute_quote(
        QuoteRequest(route=route, weight_kg=weight),
        tariff.rows,
        divisor=settings.volumetric_divisor,
        fuel_pct=settings.quote_fuel_surcharge_pct,
        min_charge=settings.quote_min_charge_default,
        route_aliases=settings.route_alias_map(),
        tariff_id=tariff.id,
    )
    if not result:
        await message.reply_text("Không khớp bậc giá cho route/khối lượng này.")
        return

    store.insert_quote(message.chat_id, result)
    await message.reply_text(_format_quote(result))
