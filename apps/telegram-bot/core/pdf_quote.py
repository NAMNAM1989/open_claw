from __future__ import annotations

import secrets
from dataclasses import dataclass
from datetime import date, datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib.styles import ParagraphStyle

from core.docs_parse import QuoteInput, chargeable_kg
from core.pdf_fonts import ensure_fonts


@dataclass
class QuoteResult:
    quote_code: str
    customer: str
    route: str
    actual_kg: float
    volumetric_kg: float | None
    chargeable_kg: float
    unit_price: float
    total: float
    currency: str
    pieces: int
    note: str
    disclaimer: str


def build_quote(
    q: QuoteInput,
    *,
    divisor: float = 6000.0,
) -> QuoteResult:
    chg, vol = chargeable_kg(q.weight_kg, q.dims, divisor)
    total = round(q.unit_price * chg, 0)
    code = f"Q-{date.today().strftime('%Y%m%d')}-{secrets.token_hex(2).upper()}"
    return QuoteResult(
        quote_code=code,
        customer=q.customer,
        route=q.route.upper(),
        actual_kg=q.weight_kg,
        volumetric_kg=vol,
        chargeable_kg=chg,
        unit_price=q.unit_price,
        total=total,
        currency=q.currency or "VND",
        pieces=q.pieces,
        note=q.note,
        disclaimer="Chưa gồm VAT/customs. Giá chốt khi booking.",
    )


def _fmt_money(n: float, currency: str) -> str:
    if currency.upper() == "VND":
        return f"{n:,.0f} VND".replace(",", ".")
    return f"{n:,.2f} {currency}"


def render_quote_pdf(result: QuoteResult) -> bytes:
    font, font_bold = ensure_fonts()
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
    )
    styles = {
        "h": ParagraphStyle("h", fontName=font_bold, fontSize=14, spaceAfter=4),
        "sub": ParagraphStyle("sub", fontName=font, fontSize=10, textColor=colors.grey),
        "b": ParagraphStyle("b", fontName=font, fontSize=10, leading=14),
        "small": ParagraphStyle("small", fontName=font, fontSize=8, textColor=colors.grey),
    }
    story = [
        Paragraph("NAM NAM LOGISTICS", styles["h"]),
        Paragraph("BÁO GIÁ VẬN CHUYỂN", styles["sub"]),
        Spacer(1, 8),
        Paragraph(f"<b>Mã:</b> {result.quote_code}", styles["b"]),
        Paragraph(f"<b>Ngày:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles["b"]),
    ]
    if result.customer:
        story.append(Paragraph(f"<b>Khách:</b> {result.customer}", styles["b"]))
    story.append(Paragraph(f"<b>Route:</b> {result.route}", styles["b"]))
    if result.pieces:
        story.append(Paragraph(f"<b>Kiện:</b> {result.pieces}", styles["b"]))
    if result.note:
        story.append(Paragraph(f"<b>Ghi chú:</b> {result.note}", styles["b"]))
    story.append(Spacer(1, 10))

    rows = [
        ["Hạng mục", "Giá trị"],
        ["Cân thực (kg)", f"{result.actual_kg:g}"],
    ]
    if result.volumetric_kg is not None:
        rows.append(["Cân thể tích (kg)", f"{result.volumetric_kg:g}"])
    rows.extend(
        [
            ["Cân tính cước (kg)", f"{result.chargeable_kg:g}"],
            ["Đơn giá / kg", _fmt_money(result.unit_price, result.currency)],
            ["Tổng ước tính", _fmt_money(result.total, result.currency)],
        ]
    )
    table = Table(rows, colWidths=[90 * mm, 70 * mm])
    table.setStyle(
        TableStyle(
            [
                ("FONT", (0, 0), (-1, 0), font_bold, 10),
                ("FONT", (0, 1), (-1, -1), font, 10),
                ("BACKGROUND", (0, 0), (-1, 0), colors.Color(0.92, 0.92, 0.92)),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("FONT", (0, -1), (-1, -1), font_bold, 10),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"⚠ {result.disclaimer}", styles["small"]))
    doc.build(story)
    return buf.getvalue()
