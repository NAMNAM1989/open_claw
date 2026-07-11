from __future__ import annotations

from datetime import datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from core.docs_parse import PklInput, parse_dims
from core.pdf_fonts import ensure_fonts


def _vol_kg(dims_str: str, pieces: int, divisor: float = 6000.0) -> float | None:
    dims = parse_dims(dims_str, pieces)
    if not dims:
        return None
    return sum((d.L * d.W * d.H * d.pieces) / divisor for d in dims)


def render_pkl_pdf(p: PklInput, *, divisor: float = 6000.0) -> bytes:
    font, font_bold = ensure_fonts()
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=14 * mm,
        rightMargin=14 * mm,
        topMargin=14 * mm,
        bottomMargin=14 * mm,
    )
    styles = {
        "h": ParagraphStyle("h", fontName=font_bold, fontSize=14, spaceAfter=4),
        "sub": ParagraphStyle("sub", fontName=font, fontSize=10, textColor=colors.grey),
        "b": ParagraphStyle("b", fontName=font, fontSize=9, leading=12),
        "small": ParagraphStyle("small", fontName=font, fontSize=8, textColor=colors.grey),
    }
    story = [
        Paragraph("NAM NAM LOGISTICS", styles["h"]),
        Paragraph("PACKING LIST (PKL)", styles["sub"]),
        Spacer(1, 6),
    ]
    if p.mawb:
        story.append(Paragraph(f"<b>MAWB:</b> {p.mawb}", styles["b"]))
    story.append(
        Paragraph(
            f"<b>Ngày:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            styles["b"],
        )
    )
    if p.shipper:
        story.append(Paragraph(f"<b>Shipper:</b> {p.shipper}", styles["b"]))
    if p.consignee:
        story.append(Paragraph(f"<b>Consignee:</b> {p.consignee}", styles["b"]))
    if p.origin or p.dest:
        story.append(
            Paragraph(
                f"<b>Route:</b> {(p.origin or '—')} → {(p.dest or '—')}",
                styles["b"],
            )
        )
    if p.note:
        story.append(Paragraph(f"<b>Ghi chú:</b> {p.note}", styles["b"]))
    story.append(Spacer(1, 8))

    header = ["STT", "Mô tả", "Kiện", "Gross kg", "Kích thước", "Vol kg"]
    data = [header]
    total_pcs = 0
    total_kg = 0.0
    total_vol = 0.0
    for line in p.lines:
        vol = _vol_kg(line.dims, line.pieces, divisor)
        total_pcs += line.pieces
        total_kg += line.weight_kg
        if vol is not None:
            total_vol += vol
        data.append(
            [
                str(line.no),
                line.description,
                str(line.pieces),
                f"{line.weight_kg:g}",
                line.dims or "—",
                f"{vol:g}" if vol is not None else "—",
            ]
        )
    data.append(
        [
            "",
            "TỔNG",
            str(total_pcs),
            f"{total_kg:g}",
            "",
            f"{total_vol:g}" if total_vol else "—",
        ]
    )

    table = Table(
        data,
        colWidths=[12 * mm, 62 * mm, 16 * mm, 22 * mm, 36 * mm, 22 * mm],
    )
    table.setStyle(
        TableStyle(
            [
                ("FONT", (0, 0), (-1, 0), font_bold, 8),
                ("FONT", (0, 1), (-1, -2), font, 8),
                ("FONT", (0, -1), (-1, -1), font_bold, 8),
                ("BACKGROUND", (0, 0), (-1, 0), colors.Color(0.92, 0.92, 0.92)),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 10))
    story.append(
        Paragraph(
            "Tài liệu tham khảo nội bộ — kiểm tra lại trước khi dùng chính thức.",
            styles["small"],
        )
    )
    doc.build(story)
    return buf.getvalue()
