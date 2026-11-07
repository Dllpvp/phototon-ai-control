"""API эндпоинт: GET /api/snapshot (§9.2 Readme.md).

Возвращает полный снимок сценария: узлы + рёбра.
"""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query

from app.core.loader import GraphNodePayload, GraphPayload, ScenarioNode, load_norms, load_scenario
from app.dependencies import get_graph
from app.schemas import GraphEdge, GraphNode, Norm, Snapshot

router = APIRouter(prefix="/api", tags=["snapshot"])


def _build_norm(node: GraphNodePayload, norms: list) -> Norm | None:
    """Строит Norm для узла из norms.json."""
    for n in norms:
        if n.metric == node.id:
            return Norm(lo=n.min, hi=n.max, unit=n.unit)
    return None


def _build_graph_nodes(
    scenario_nodes: list[ScenarioNode],
    graph: GraphPayload,
    norms: list,
) -> list[GraphNode]:
    """Строит список GraphNode из сценария + графа + норм."""
    nodes: list[GraphNode] = []
    node_map = {n.id: n for n in graph.nodes}
    
    for sn in scenario_nodes:
        gn = node_map.get(sn.id)
        if gn is None:
            continue
        
        norm = _build_norm(gn, norms)
        # Определяем literal: это узел, значение которого из ANCHORS
        literal = gn.id in ("fin_margin", "fin_loss_day", "fin_revenue_week", 
                            "prod_downtime_l2", "sales_sla_breach", 
                            "hr_operators_s3", "quality_defect_rate")
        
        nodes.append(GraphNode(
            id=gn.id,
            domain=gn.domain,
            name=gn.name,
            unit=gn.unit,
            value=sn.value,
            norm=norm,
            status=sn.status,
            cost_per_day=gn.cost_per_day,
            description=None,  # можно добавить из отдельного справочника
            literal=literal,
        ))
    
    return nodes


def _build_graph_edges(graph: GraphPayload) -> list[GraphEdge]:
    """Строит список GraphEdge из графа."""
    edges: list[GraphEdge] = []
    for e in graph.edges:
        edges.append(GraphEdge(
            from_=e.from_,
            to=e.to,
            sign=e.sign,
            weight=e.weight,
            curvature=e.curvature,
            lag_days=e.lag_days,
            note=e.note,
        ))
    return edges


@router.get("/snapshot", response_model=Snapshot)
async def get_snapshot(
    scenario: str = Query("main", description="ID сценария: main|neg|peak"),
    graph: GraphPayload = Depends(get_graph),
) -> Snapshot:
    """Полный снимок сценария: узлы + рёбра."""
    scenario_data = load_scenario(scenario)
    norms = load_norms()
    
    nodes = _build_graph_nodes(scenario_data.nodes, graph, norms)
    edges = _build_graph_edges(graph)
    
    return Snapshot(
        scenario_id=scenario_data.scenario_id,
        as_of=date.fromisoformat(scenario_data.as_of),
        nodes=nodes,
        edges=edges,
    )