"""Влияние (impact) — единая формула распространения изменений по графу.

Реализация строго по §7.3 Readme.md: BFS по исходящим рёбрам,
аккумуляция изменений с учётом sign, weight и curvature через
`math.copysign(d * d, d)`.

Ограничение: линейная суперпозиция без норм (clamp'ится при показе).
Для what-if используется интерполяция по ANCHORS (см. interpolation.py),
а эта функция — для drill-down / «почему» (объяснение влияния).
"""

from __future__ import annotations

import math

from app.core.graph import GraphView, get_graph


def delta(
    graph: GraphView,
    node_id: str,
    d_input: float,
    depth: int = 6,
) -> dict[str, float]:
    """BFS по исходящим рёбрам, возвращает суммарное изменение каждого узла.

    Параметры:
        graph    — GraphView (граф причин).
        node_id  — стартовый узел (id).
        d_input  — входное изменение (например, +2 оператора).
        depth    — максимальная глубина обхода (по умолчанию 6).

    Возвращает:
        Словарь `{node_id: суммарное_изменение}`. Включает стартовый узел
        с `d_input`.

    Формула на каждом ребре (§7.3):
        d_to = d * edge.weight * edge.sign
        if edge.curvature:
            d_to += edge.curvature * math.copysign(d * d, d)
    """
    effects: dict[str, float] = {node_id: d_input}
    queue: list[tuple[str, float, int]] = [(node_id, d_input, 0)]

    while queue:
        src, d, dep = queue.pop(0)
        if dep >= depth:
            continue
        for edge in graph.out_edges(src):
            d_to = d * edge.weight * edge.sign
            if edge.curvature:
                d_to += edge.curvature * math.copysign(d * d, d)
            effects[edge.to] = effects.get(edge.to, 0.0) + d_to
            queue.append((edge.to, d_to, dep + 1))

    return effects


def delta_default(node_id: str, d_input: float, depth: int = 6) -> dict[str, float]:
    """То же, что `delta`, но с графом по умолчанию (`get_graph()`)."""
    return delta(get_graph(), node_id, d_input, depth)
