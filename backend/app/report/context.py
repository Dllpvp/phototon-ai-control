"""Сборка контекста для Executive Summary PDF.

Собирает: топ-3 отклонения + причины, cost of inaction, решения (owner/due/verdict),
снимки «было → стало» из симуляции. Используется в `pdf.py`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from app.core.anchors import ANCHORS
from app.core.loader import load_scenario, load_graph, load_norms
from app.core.simulate import simulate
from app.db import DecisionStore


@dataclass
class TopDeviation:
    node_id: str
    name: str
    value: float
    unit: str
    status: str
    cost_per_day: float
    root_causes: list[str]


@dataclass
class DecisionInfo:
    type: str
    params: dict[str, Any]
    owner: str
    due_date: Optional[str]
    verdict: str
    expected_effect_byn: float
    jira_key: Optional[str]


@dataclass
class BeforeAfter:
    node_id: str
    name: str
    unit: str
    before: float
    after: float
    delta: float
    status_before: str
    status_after: str


@dataclass
class ReportContext:
    scenario_id: str
    as_of: str
    week: int
    top_deviations: list[TopDeviation]
    loss_counter_started_at: str
    decisions: list[DecisionInfo]
    before_after: list[BeforeAfter]
    total_effect_byn: float
    verdict: str
    compensating_cause: Optional[str]
    recommendation: Optional[str]


def _build_norms_map() -> dict[str, tuple[float | None, float | None, str]]:
    """metric_id -> (min, max, unit) из norms.json"""
    norms = load_norms()
    return {n.metric: (n.min, n.max, n.unit) for n in norms}


def _graph_node_names() -> dict[str, str]:
    """node_id -> name из graph.json"""
    graph = load_graph()
    return {node.id: node.name for node in graph.nodes}


def _graph_cost_per_day() -> dict[str, float]:
    """node_id -> cost_per_day из graph.json"""
    graph = load_graph()
    return {node.id: node.cost_per_day or 0.0 for node in graph.nodes}


def get_report_context(scenario_id: str = "main") -> ReportContext:
    """Полный контекст для Executive Summary PDF."""
    scenario = load_scenario(scenario_id)
    graph_names = _graph_node_names()
    graph_costs = _graph_cost_per_day()
    norms_map = _build_norms_map()

    # --- Top-3 отклонения по cost_per_day ---
    red_nodes = []
    for node in scenario.nodes:
        if node.status in ("red", "yellow"):
            cost = graph_costs.get(node.id, 0.0)
            if cost > 0:
                red_nodes.append((cost, node))

    red_nodes.sort(key=lambda x: x[0], reverse=True)
    top3 = red_nodes[:3]

    # Корневые причины из графа (path_hints)
    graph = load_graph()
    hints = {h.id: h.path for h in graph.path_hints}

    top_deviations = []
    for cost, node in top3:
        root_causes = hints.get(node.id, [])
        top_deviations.append(
            TopDeviation(
                node_id=node.id,
                name=graph_names.get(node.id, node.id),
                value=node.value,
                unit=norms_map.get(node.id, (None, None, ""))[2] or "",
                status=node.status,
                cost_per_day=cost,
                root_causes=root_causes,
            )
        )

    # --- Cost of Inaction (тикер) ---
    # loss_counter_started_at из дашборда — возьмём из сценария as_of
    loss_counter_started_at = scenario.as_of

    # --- Решения из БД ---
    store = DecisionStore()
    decisions_db = store.list_decisions(scenario_id=scenario_id)
    decisions = [
        DecisionInfo(
            type=d.type,
            params=d.params,
            owner=d.owner,
            due_date=d.due_date.isoformat() if d.due_date else None,
            verdict=d.verdict,
            expected_effect_byn=d.expected_effect_byn,
            jira_key=d.jira_key,
        )
        for d in decisions_db
    ]

    # --- Before/After из симуляции (+14 дней) ---
    sim_main = simulate(ANCHORS["sim_days"], [], branch="main")
    sim_neg = simulate(ANCHORS["sim_days"], [], branch="neg")

    # Берём снимок main (было) и после найма 2 операторов (стало)
    decisions_for_sim = [{"type": "hire", "operators": 2}]
    sim_after = simulate(ANCHORS["sim_days"], decisions_for_sim, branch="main")

    before_after: list[BeforeAfter] = []
    for node in scenario.nodes:
        nid = node.id
        if nid in sim_main.final_snapshot and nid in sim_after.final_snapshot:
            before_val = sim_main.final_snapshot[nid].get("value", node.value)
            after_val = sim_after.final_snapshot[nid].get("value", node.value)
            if abs(before_val - after_val) > 0.001:
                before_after.append(
                    BeforeAfter(
                        node_id=nid,
                        name=graph_names.get(nid, nid),
                        unit=norms_map.get(nid, (None, None, ""))[2] or "",
                        before=before_val,
                        after=after_val,
                        delta=after_val - before_val,
                        status_before=sim_main.final_snapshot[nid].get("status", node.status),
                        status_after=sim_after.final_snapshot[nid].get("status", node.status),
                    )
                )

    return ReportContext(
        scenario_id=scenario_id,
        as_of=scenario.as_of,
        week=scenario.week,
        top_deviations=top_deviations,
        loss_counter_started_at=loss_counter_started_at,
        decisions=decisions,
        before_after=before_after,
        total_effect_byn=sim_after.effect_byn,
        verdict=sim_after.verdict,
        compensating_cause=sim_after.compensating_cause,
        recommendation=sim_after.recommendation,
    )