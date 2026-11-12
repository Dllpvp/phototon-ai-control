"""Вспомогательные таблицы PDF (ReportLab)."""

from __future__ import annotations

from reportlab.lib.units import cm, mm  # noqa: F401
from reportlab.lib.colors import HexColor
from reportlab.platypus import Paragraph, Table, TableStyle
from app.report.styles import DARK_BG, PANEL_BG, TEXT_PRIMARY, TEXT_MUTED, ALERT_RED, GREEN, AMBER


def _deviations_table(ctx, styles) -> Table:
    """Таблица топ-3 отклонений с причинами."""
    data = [[
        Paragraph("Метрика", styles["table_header"]),
        Paragraph("Значение", styles["table_header"]),
        Paragraph("Статус", styles["table_header"]),
        Paragraph("Потери, BYN/сут", styles["table_header"]),
        Paragraph("Корневые причины", styles["table_header"]),
    ]]
    for dev in ctx.top_deviations:
        status_color = ALERT_RED if dev.status == "red" else AMBER
        status_html = f'<font color="#{status_color.hexval()[2:]}">{dev.status.upper()}</font>'
        
        causes = ", ".join(dev.root_causes) if dev.root_causes else "—"
        data.append([
            Paragraph(dev.name, styles["table_cell"]),
            Paragraph(f"{dev.value:,.0f} {dev.unit}".replace(",", " "), styles["table_cell_right"]),
            Paragraph(status_html, styles["table_cell_center"]),
            Paragraph(f"{dev.cost_per_day:,.0f}".replace(",", " "), styles["table_cell_right"]),
            Paragraph(causes, styles["table_cell"]),
        ])
    
    col_widths = [5.5*cm, 2.5*cm, 1.8*cm, 2.5*cm, 4.5*cm]
    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PANEL_BG),
        ("TEXTCOLOR", (0, 0), (-1, 0), TEXT_PRIMARY),
        ("FONTNAME", (0, 0), (-1, 0), "DejaVuSans-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#2A3A4F")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [DARK_BG, PANEL_BG]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    return table


def _decisions_table(ctx, styles) -> Table:
    """Таблица принятых решений: owner, due, verdict, Jira."""
    data = [[
        Paragraph("Тип", styles["table_header"]),
        Paragraph("Параметры", styles["table_header"]),
        Paragraph("Owner", styles["table_header"]),
        Paragraph("Срок", styles["table_header"]),
        Paragraph("Вердикт", styles["table_header"]),
        Paragraph("Jira", styles["table_header"]),
        Paragraph("Ожид. эффект, BYN", styles["table_header"]),
    ]]
    for dec in ctx.decisions:
        params = ", ".join(f"{k}={v}" for k, v in dec.params.items()) if dec.params else "—"
        due = dec.due_date or "—"
        jira = dec.jira_key or "—"
        
        verdict_color = GREEN if dec.verdict == "effective" else ALERT_RED if dec.verdict == "ineffective" else AMBER
        verdict_html = f'<font color="#{verdict_color.hexval()[2:]}">{dec.verdict.upper()}</font>'
        
        data.append([
            Paragraph(dec.type, styles["table_cell_center"]),
            Paragraph(params, styles["table_cell"]),
            Paragraph(dec.owner, styles["table_cell_center"]),
            Paragraph(due, styles["table_cell_center"]),
            Paragraph(verdict_html, styles["table_cell_center"]),
            Paragraph(jira, styles["table_cell_center"]),
            Paragraph(f"{dec.expected_effect_byn:,.0f}".replace(",", " "), styles["table_cell_right"]),
        ])
    
    if len(data) == 1:
        data.append([Paragraph("Решений нет", styles["table_cell"])] + [Paragraph("—", styles["table_cell"])] * 6)
    
    col_widths = [1.8*cm, 2.5*cm, 2*cm, 2*cm, 1.8*cm, 2*cm, 2.5*cm]
    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PANEL_BG),
        ("TEXTCOLOR", (0, 0), (-1, 0), TEXT_PRIMARY),
        ("FONTNAME", (0, 0), (-1, 0), "DejaVuSans-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#2A3A4F")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [DARK_BG, PANEL_BG]),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
    ]))
    return table


def _before_after_table(ctx, styles) -> Table:
    """Таблица «Было → Стало» после +14 дней."""
    data = [[
        Paragraph("Метрика", styles["table_header"]),
        Paragraph("Было", styles["table_header"]),
        Paragraph("Стало", styles["table_header"]),
        Paragraph("Δ", styles["table_header"]),
        Paragraph("Статус был → стал", styles["table_header"]),
    ]]
    for ba in ctx.before_after:
        delta = ba.after - ba.before
        delta_color = GREEN if delta < 0 else ALERT_RED if delta > 0 else TEXT_MUTED
        delta_str = f"{delta:+.1f}".replace(".", ",")
        delta_html = f'<font color="#{delta_color.hexval()[2:]}">{delta_str}</font>'
        
        status_arrow = f"{ba.status_before} → {ba.status_after}"
        
        data.append([
            Paragraph(ba.name, styles["table_cell"]),
            Paragraph(f"{ba.before:,.1f} {ba.unit}".replace(",", " "), styles["table_cell_right"]),
            Paragraph(f"{ba.after:,.1f} {ba.unit}".replace(",", " "), styles["table_cell_right"]),
            Paragraph(delta_html, styles["table_cell_center"]),
            Paragraph(status_arrow, styles["table_cell_center"]),
        ])
    
    if len(data) == 1:
        data.append([Paragraph("Нет изменений", styles["table_cell"])] + [Paragraph("—", styles["table_cell"])] * 4)
    
    col_widths = [5*cm, 2.5*cm, 2.5*cm, 2*cm, 3*cm]
    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PANEL_BG),
        ("TEXTCOLOR", (0, 0), (-1, 0), TEXT_PRIMARY),
        ("FONTNAME", (0, 0), (-1, 0), "DejaVuSans-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#2A3A4F")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [DARK_BG, PANEL_BG]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    return table
