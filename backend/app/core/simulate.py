"""Симулятор «было → стало» (+N дней) с позитивной и негативной ветками (§7.7, §8 Readme.md).

Чистая математика: стартовое состояние из фикстуры сценария, применение
решений (найм операторов), пересчёт метрик через ANCHORS-интерполяцию.
Негативная ветка учитывает компенсирующую причину (износ ламинатора).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional

from app.core.anchors import ANCHORS
from app.core.economics import loss_day
from app.core.interpolation import interp
from app.core.loader import load_scenario


@dataclass
class SimResult:
    """Результат симуляции за N дней."""

    days: int
    branch: str
    effect_byn: float
    verdict: str
    compensating_cause: Optional[str] = None
    recommendation: Optional[str] = None
    loss_day: float = 0.0
    defect_rate: float = 0.0
    downtime_h: float = 0.0
    final_snapshot: Dict[str, Any] = field(default_factory=dict)


def _get_node_value(snapshot: Mapping[str, Any], node_id: str) -> Optional[float]:
    node = snapshot.get(node_id)
    if isinstance(node, Mapping) and "value" in node:
        return float(node["value"])
    if isinstance(node, (int, float)):
        return float(node)
    return None


def _set_node(snapshot: Dict[str, Any], node_id: str, value: float, status: str = "green") -> None:
    snapshot[node_id] = {"value": value, "status": status}


def _initial_snapshot(branch: str) -> Dict[str, Any]:
    """Стартовое состояние из фикстуры сценария branch."""
    scenario = load_scenario(branch)
    snapshot: Dict[str, Any] = {}
    for node in scenario.nodes:
        snapshot[node.id] = {"value": node.value, "status": node.status}
    return snapshot


def _apply_hire(snapshot: Dict[str, Any], add_ops: int) -> float:
    """Применяет решение «нанять add_ops операторов». Возвращает новое число операторов."""
    current = _get_node_value(snapshot, "hr_operators_s3") or 4.0
    new_ops = current + add_ops
    status = "green" if new_ops >= 6 else "red"
    _set_node(snapshot, "hr_operators_s3", new_ops, status)
    return new_ops


def _recompute_metrics(snapshot: Dict[str, Any], ops: float, branch: str) -> None:
    """Пересчитывает все метрики, зависящие от числа операторов, через ANCHORS."""
    downtime = interp(ops, ANCHORS["downtime_h_by_ops"])
    sla = interp(ops, ANCHORS["sla_orders_by_ops"])
    revenue = interp(ops, ANCHORS["revenue_week_by_ops"])
    loss = interp(ops, ANCHORS["loss_day_by_ops"])

    _set_node(snapshot, "prod_downtime_l2", downtime, "green" if downtime <= 4 else "red")
    _set_node(snapshot, "sales_sla_breach", sla, "green" if sla <= 5 else "red")
    _set_node(snapshot, "fin_revenue_week", revenue, "yellow")
    _set_node(snapshot, "fin_loss_day", loss, "green" if loss <= 300 else "red")

    # Качество (дефект-рейт): зависит от ветки
    if branch == "neg":
        defect = ANCHORS["defect_rate_neg"]  # 11.0%
        _set_node(snapshot, "quality_defect_rate", defect, "red")
        _set_node(snapshot, "fin_loss_day", ANCHORS["loss_day_neg"], "red")
    else:
        defect = ANCHORS["defect_rate_after_hire"]  # 4.0%
        _set_node(snapshot, "quality_defect_rate", defect, "green")


def simulate(days: int, decisions: List[Dict[str, Any]], branch: str = "main") -> SimResult:
    """Симуляция за `days` дней.

    Параметры:
        days      — количество дней (обычно 14, из ANCHORS["sim_days"]).
        decisions — список решений. Поддерживается тип "hire" с полем "operators".
        branch    — "main" (позитив) или "neg" (негатив с компенсатором).
    """
    if branch not in ("main", "neg"):
        raise ValueError(f"Неизвестная ветка: {branch!r}. Допустимо: 'main', 'neg'")

    snapshot = _initial_snapshot(branch)

    # Применяем решения
    for dec in decisions:
        if dec.get("type") == "hire":
            add = int(dec.get("operators", 0))
            if add:
                ops = _apply_hire(snapshot, add)

    # Финальное число операторов
    ops = _get_node_value(snapshot, "hr_operators_s3") or 4.0

    # Пересчитываем метрики
    _recompute_metrics(snapshot, ops, branch)

    # Финальные значения для результата
    loss = _get_node_value(snapshot, "fin_loss_day") or loss_day(ops=ops)
    defect = _get_node_value(snapshot, "quality_defect_rate") or 9.0
    downtime = _get_node_value(snapshot, "prod_downtime_l2") or 14.0

    # Эффект в BYN за `days` дней: (базовые потери − новые потери) × дней
    base_loss = ANCHORS["loss_day_by_ops"][4]
    effect_byn = (base_loss - loss) * days

    # Вердикт и компенсатор
    verdict = "effective"
    compensating_cause: Optional[str] = None
    recommendation: Optional[str] = None

    if branch == "neg":
        wear = _get_node_value(snapshot, "equip_lamination_wear")
        if wear is not None and wear >= 90 and defect >= 8:
            verdict = "ineffective"
            compensating_cause = "equip_lamination_wear"
            recommendation = "внеплановое ТО узла ламинации"

    return SimResult(
        days=days,
        branch=branch,
        effect_byn=effect_byn,
        verdict=verdict,
        compensating_cause=compensating_cause,
        recommendation=recommendation,
        loss_day=loss,
        defect_rate=defect,
        downtime_h=downtime,
        final_snapshot=dict(snapshot),
    )
