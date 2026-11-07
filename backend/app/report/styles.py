"""Палитра и стили PDF (ReportLab)."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# --- Шрифты --------------------------------------------------------------

FONTS_DIR = Path(__file__).resolve().parent / "fonts"
FONT_REGULAR = FONTS_DIR / "DejaVuSans.ttf"
FONT_BOLD = FONTS_DIR / "DejaVuSans-Bold.ttf"

_FONTS_REGISTERED = False


def register_fonts() -> None:
    """Регистрирует TTF шрифты для ReportLab. Идемпотентно."""
    global _FONTS_REGISTERED
    if _FONTS_REGISTERED:
        return
    try:
        pdfmetrics.registerFont(TTFont("DejaVuSans", str(FONT_REGULAR)))
        pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", str(FONT_BOLD)))
        _FONTS_REGISTERED = True
    except Exception:
        pass


# --- Цвета --------------------------------------------------------------

DARK_BG = HexColor("#0B0F14")
PANEL_BG = HexColor("#121821")
TEXT_PRIMARY = HexColor("#E5EDF5")
TEXT_MUTED = HexColor("#94A3B8")
ALERT_RED = HexColor("#EF4444")
GREEN = HexColor("#22C55E")
AMBER = HexColor("#F59E0B")


# --- Стили --------------------------------------------------------------

def get_styles():
    base = getSampleStyleSheet()
    register_fonts()
    return {
        "title": ParagraphStyle(
            "Title",
            parent=base["Title"],
            fontName="DejaVuSans-Bold",
            fontSize=18,
            leading=22,
            textColor=TEXT_PRIMARY,
            alignment=TA_LEFT,
            spaceAfter=6,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle",
            parent=base["Normal"],
            fontName="DejaVuSans",
            fontSize=10,
            leading=14,
            textColor=TEXT_MUTED,
            alignment=TA_LEFT,
            spaceAfter=16,
        ),
        "section": ParagraphStyle(
            "Section",
            parent=base["Heading2"],
            fontName="DejaVuSans-Bold",
            fontSize=13,
            leading=17,
            textColor=TEXT_PRIMARY,
            spaceBefore=14,
            spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["Normal"],
            fontName="DejaVuSans",
            fontSize=9.5,
            leading=13,
            textColor=TEXT_PRIMARY,
            spaceAfter=4,
        ),
        "body_bold": ParagraphStyle(
            "BodyBold",
            parent=base["Normal"],
            fontName="DejaVuSans-Bold",
            fontSize=9.5,
            leading=13,
            textColor=TEXT_PRIMARY,
            spaceAfter=4,
        ),
        "muted": ParagraphStyle(
            "Muted",
            parent=base["Normal"],
            fontName="DejaVuSans",
            fontSize=8.5,
            leading=11,
            textColor=TEXT_MUTED,
            spaceAfter=2,
        ),
        "table_header": ParagraphStyle(
            "TableHeader",
            parent=base["Normal"],
            fontName="DejaVuSans-Bold",
            fontSize=8.5,
            leading=11,
            textColor=TEXT_PRIMARY,
            alignment=TA_CENTER,
        ),
        "table_cell": ParagraphStyle(
            "TableCell",
            parent=base["Normal"],
            fontName="DejaVuSans",
            fontSize=8.5,
            leading=11,
            textColor=TEXT_PRIMARY,
            alignment=TA_LEFT,
        ),
        "table_cell_right": ParagraphStyle(
            "TableCellRight",
            parent=base["Normal"],
            fontName="DejaVuSans",
            fontSize=8.5,
            leading=11,
            textColor=TEXT_PRIMARY,
            alignment=TA_RIGHT,
        ),
        "table_cell_center": ParagraphStyle(
            "TableCellCenter",
            parent=base["Normal"],
            fontName="DejaVuSans",
            fontSize=8.5,
            leading=11,
            textColor=TEXT_PRIMARY,
            alignment=TA_CENTER,
        ),
        "alert": ParagraphStyle(
            "Alert",
            parent=base["Normal"],
            fontName="DejaVuSans-Bold",
            fontSize=9.5,
            leading=13,
            textColor=ALERT_RED,
            spaceAfter=4,
        ),
        "green": ParagraphStyle(
            "Green",
            parent=base["Normal"],
            fontName="DejaVuSans-Bold",
            fontSize=9.5,
            leading=13,
            textColor=GREEN,
            spaceAfter=4,
        ),
        "footer": ParagraphStyle(
            "Footer",
            parent=base["Normal"],
            fontName="DejaVuSans",
            fontSize=7.5,
            leading=10,
            textColor=TEXT_MUTED,
            alignment=TA_CENTER,
        ),
    }
