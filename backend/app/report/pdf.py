"""Executive Summary PDF — ReportLab Platypus, A4, DejaVuSans (кириллица).

Функция `generate_executive_summary(scenario_id: str) -> bytes`
вызывается из `app/api/decisions.py` после создания решения
и из `app/api/report.py` (GET /api/report/executive.pdf).
"""

from __future__ import annotations

import io

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.colors import HexColor

from app.report.context import get_report_context
from app.report.styles import get_styles, register_fonts, GREEN, ALERT_RED
from app.report.tables import _deviations_table, _decisions_table, _before_after_table


def generate_executive_summary(scenario_id: str = "main") -> bytes:
    """Собирает Executive Summary PDF (A4, кириллица) и возвращает bytes."""
    ctx = get_report_context(scenario_id)
    styles = get_styles()
    register_fonts()

    buffer = io.BytesIO()
    
    # Поля страницы: 15 мм со всех сторон
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=15*mm,
        rightMargin=15*mm,
        topMargin=15*mm,
        bottomMargin=15*mm,
    )
    
    story = []
    
    # ===== Header =====
    story.append(Paragraph("Executive Summary", styles["title"]))
    story.append(Paragraph(
        f"Сценарий: {ctx.scenario_id} &nbsp;|&nbsp; Неделя {ctx.week} &nbsp;|&nbsp; Отчёт на {ctx.as_of}",
        styles["subtitle"]
    ))
    
    # Заголовок-тикер: Cost of Inaction
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        f"💸 Cost of Inaction: <b>{ctx.loss_counter_started_at}</b> — нарастающие потери с момента старта тикера",
        styles["alert"]
    ))
    
    # ===== Секция 1: Топ-3 отклонения + причины =====
    story.append(Paragraph("Топ-3 отклонения и корневые причины", styles["section"]))
    story.append(_deviations_table(ctx, styles))
    
    # ===== Секция 2: Решения =====
    story.append(Paragraph("Принятые решения", styles["section"]))
    story.append(_decisions_table(ctx, styles))
    
    # ===== Секция 3: Было → Стало (+14 дней) =====
    story.append(Paragraph("Было → Стало (симуляция +14 дней)", styles["section"]))
    
    # Итоговый эффект
    effect_color = GREEN if ctx.total_effect_byn > 0 else ALERT_RED
    effect_html = f'<font color="#{effect_color.hexval()[2:]}">{ctx.total_effect_byn:,.0f} BYN</font>'.replace(",", " ")
    story.append(Paragraph(
        f"Суммарный эффект от найма 2 операторов: {effect_html} за 14 дней. Вердикт: <b>{ctx.verdict}</b>",
        styles["body_bold"]
    ))
    
    if ctx.compensating_cause:
        story.append(Paragraph(
            f"⚠ Компенсирующая причина: {ctx.compensating_cause}. Рекомендация: {ctx.recommendation}",
            styles["alert"]
        ))
    
    story.append(Spacer(1, 6))
    story.append(_before_after_table(ctx, styles))
    
    # ===== Footer =====
    story.append(Spacer(1, 16))
    story.append(Paragraph(
        "Фотопринт·Контроль — управленческий MVP для фабрики фотокниг. "
        "Данные синтетические, калиброванные по открытым бенчмаркам CEWE/Shutterfly.",
        styles["footer"]
    ))
    
    # Сборка
    doc.build(story)
    return buffer.getvalue()
