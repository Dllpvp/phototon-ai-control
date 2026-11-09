"""Экономика: cost of inaction, потери в день, статус узла (§7.1, §7.5 Readme.md).

`loss_day` возвращает значение потерь из ANCHORS["loss_day_by_ops"]
или напрямую из snapshot (если передан словарь с ключом `fin_loss_day`).

`node_status` вычисляет статус узла (red/yellow/green) по правилам §7.1:
- green: значение в норме (между min и max)
- yellow: нарушение мягкой границы (warn) — значение между warn и жесткой границей
- red: нарушение жёсткой границы (min/max)

`node_cost_per_day` возвращает стоимость бездействия в день для узла.
Для узлов с прямым cost_per_day в графе (fin_loss_day, fin_margin) берём из графа.
Для производных узлов вычисляем на основе ANCHORS.
"""

from __future__ import annotations

from typing import Any, Mapping

from app.core.anchors import ANCHORS
from app.core.interpolation import interp
from app.core.loader import GraphPayload, NormRecord


def loss_day(snapshot_or_anchors: Mapping[str, Any] | None = None, ops: float | None = None) -> float:
    """Потери в день, BYN/сут.

    Варианты вызова:
        loss_day(ops=4)                       — интерполяция из ANCHORS по числу операторов.
        loss_day({"fin_loss_day": {"value": 1840}}) — значение из snapshot-узла.
        loss_day()                            — значение по умолчанию (4 оператора, main).

    Приоритет: если передан `ops` — интерполируем ANCHORS["loss_day_by_ops"].
    Иначе если в словаре есть узел `fin_loss_day` с `value` — берём его.
    Иначе — ANCHORS["loss_day_by_ops"][4].
    """
    if ops is not None:
        return interp(ops, ANCHORS["loss_day_by_ops"])

    if snapshot_or_anchors is not None:
        node = snapshot_or_anchors.get("fin_loss_day")
        if isinstance(node, Mapping) and "value" in node:
            return float(node["value"])
        if isinstance(node, (int, float)):
            return float(node)

    return interp(4, ANCHORS["loss_day_by_ops"])


def loss_day_by_ops(ops: float) -> float:
    """Потери в день по числу операторов (интерполяция ANCHORS)."""
    return interp(ops, ANCHORS["loss_day_by_ops"])


def effect_14d() -> float:
    """Эффект решения за 14 дней: (loss(4) − loss(6)) × 14 = 22 120 BYN."""
    diff = ANCHORS["loss_day_by_ops"][4] - ANCHORS["loss_day_by_ops"][6]
    return diff * ANCHORS["sim_days"]


def node_status(value: float, norm: NormRecord | None) -> str:
    """Статус узла по правилам §7.1 Readme.md.

    Args:
        value: Текущее значение метрики.
        norm: Норма метрики (min, max, warn, unit) или None.

    Returns:
        "green" — значение в норме (между min и max, с учётом направления)
        "yellow" — нарушение мягкой границы (warn)
        "red" — нарушение жёсткой границы (min/max)
    """
    if norm is None:
        return "green"

    lo = norm.min
    hi = norm.max
    warn = norm.warn

    # Если нет жёстких границ — зелёный
    if lo is None and hi is None:
        return "green"

    # Определяем направление: для большинства метрик "больше лучше" или "меньше лучше"
    # По умолчанию считаем, что нарушение верхней границы — это red
    # Для метрик типа "loss_day", "defect_rate", "downtime", "sla_breach" — меньше лучше
    lower_is_better = norm.unit in ("BYN/сут", "%", "ч/сут", "зак/сут", "шт/нед")

    if lower_is_better:
        # Чем меньше, тем лучше: нарушение верхней границы (hi) — red
        if hi is not None and value > hi:
            return "red"
        if warn is not None and value > warn:
            return "yellow"
        return "green"
    else:
        # Чем больше, тем лучше: наружение нижней границы (lo) — red
        if lo is not None and value < lo:
            return "red"
        if warn is not None and value < warn:
            return "yellow"
        return "green"


def node_cost_per_day(
    node_id: str,
    value: float,
    graph: GraphPayload,
    node_values: dict[str, float],
    norms: list[NormRecord] | None = None,
) -> float | None:
    """Стоимость бездействия в день для узла (BYN/сут).

    Правила (§7.1, §7.5, graph.json):
    - fin_loss_day: прямое значение узла (value)
    - fin_margin: потери от снижения маржи = (target_margin - current_margin) * revenue / 100 / 7
    - fin_revenue_week: потери выручки в день = (target_revenue - current_revenue) / 7
    - sales_sla_breach, sales_b2b_orders, sales_b2c_churn_risk: косвенно через loss_day
    - hr_operators_s3: через downtime_h * COST_PER_DOWNTIME_H
    - Остальные узлы: None (нет прямой денежной оценки в день)

    Args:
        node_id: ID узла.
        value: Текущее значение узла.
        graph: Граф для навигации (получить norm, cost_per_day из payload).
        node_values: Словарь значений всех узлов сценария.
        norms: Список норм (опционально, для расчётов).

    Returns:
        Стоимость в BYN/сут или None.
    """
    # Узлы с прямым cost_per_day в graph.json
    node_payload = next((n for n in graph.nodes if n.id == node_id), None)
    if node_payload and node_payload.cost_per_day is not None:
        return float(node_payload.cost_per_day)

    # Специальные вычисления для ключевых узлов
    if node_id == "fin_margin":
        # Потери от снижения маржи: (target - current) * revenue / 100 / 7 дней
        target_margin = 35.0  # норма min из norms.json
        revenue = node_values.get("fin_revenue_week", ANCHORS["revenue_week_by_ops"][4])
        margin_gap = target_margin - value
        if margin_gap > 0:
            return margin_gap * revenue / 100 / 7
        return 0.0

    if node_id == "fin_revenue_week":
        # Потери выручки в день относительно нормы
        target_revenue = 45000.0  # норма min из norms.json
        revenue_gap = target_revenue - value
        if revenue_gap > 0:
            return revenue_gap / 7
        return 0.0

    if node_id == "hr_operators_s3":
        # Потери через простой: downtime_h * COST_PER_DOWNTIME_H
        # downtime_h зависит от числа операторов (ANCHORS)
        ops = value
        downtime = interp(ops, ANCHORS["downtime_h_by_ops"])
        from app.core.constants import COST_PER_DOWNTIME_H
        return downtime * COST_PER_DOWNTIME_H

    if node_id in ("sales_sla_breach", "sales_b2b_orders", "sales_b2c_churn_risk"):
        # Эти узлы влияют на loss_day косвенно — не считаем отдельно
        return None

    if node_id == "fin_loss_day":
        # Прямое значение уже обработано выше через node_payload.cost_per_day
        return float(value)

    # Для производственных метрик — нет прямой оценки в день
    return None


def unit_economics() -> list[UnitEconDTO]:
    """Юнит-экономика: 5 строк из §7.8 Readme.md.

    Данные из `unit_economics.json` (через loader) + расчет статуса
    по общей норме `unit_econ_margin`.
    """
    from app.core.loader import load_unit_economics, load_norms
    from app.schemas import UnitEconDTO

    rows = load_unit_economics()
    norms = load_norms()
    norm = next((n for n in norms if n.metric == "unit_econ_margin"), None)

    return [
        UnitEconDTO(
            sku=row.sku,
            price=row.price,
            paper=row.paper,
            printing=row.printing,
            binding=row.binding,
            labor=row.labor,
            defect=row.defect,
            margin_pct=row.margin_pct,
            status="red" if norm and row.margin_pct < (norm.min or float('-inf')) else "green",
        )
        for row in rows
    ]
