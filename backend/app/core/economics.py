"""Экономика: cost of inaction, потери в день (§7.5 Readme.md).

`loss_day` возвращает значение потерь из ANCHORS["loss_day_by_ops"]
или напрямую из snapshot (если передан словарь с ключом `fin_loss_day`).

Все «красивые» числа живут в `anchors.py` — здесь только выбор источника.
"""

from __future__ import annotations

from typing import Any, Mapping

from app.core.anchors import ANCHORS
from app.core.interpolation import interp


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
