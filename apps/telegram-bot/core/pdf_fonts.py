from __future__ import annotations

from pathlib import Path

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

_REGISTERED = False
FONT_NAME = "Helvetica"
FONT_BOLD = "Helvetica-Bold"

_CANDIDATES = [
    Path(__file__).resolve().parents[1] / "assets" / "fonts" / "DejaVuSans.ttf",
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    Path("/usr/share/fonts/dejavu/DejaVuSans.ttf"),
    Path("C:/Windows/Fonts/arial.ttf"),
]
_BOLD_CANDIDATES = [
    Path(__file__).resolve().parents[1] / "assets" / "fonts" / "DejaVuSans-Bold.ttf",
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    Path("/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf"),
    Path("C:/Windows/Fonts/arialbd.ttf"),
]


def ensure_fonts() -> tuple[str, str]:
    global _REGISTERED, FONT_NAME, FONT_BOLD
    if _REGISTERED:
        return FONT_NAME, FONT_BOLD

    regular = next((p for p in _CANDIDATES if p.is_file()), None)
    bold = next((p for p in _BOLD_CANDIDATES if p.is_file()), None)
    if regular:
        pdfmetrics.registerFont(TTFont("NNSans", str(regular)))
        FONT_NAME = "NNSans"
        if bold:
            pdfmetrics.registerFont(TTFont("NNSans-Bold", str(bold)))
            FONT_BOLD = "NNSans-Bold"
        else:
            FONT_BOLD = "NNSans"
    _REGISTERED = True
    return FONT_NAME, FONT_BOLD
