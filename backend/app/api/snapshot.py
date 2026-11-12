"""API эндпоинт: GET /api/snapshot (§9.2 Readme.md).

Возвращает полный снимок сценария: 18 узлов с вычисленными status/cost_per_day и 17 рёбер.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from app.core.economics import node_cost_per_day, node_status
from app.core.loader import GraphPayload, NormRecord, load_norms, load_scenario
from app.dependencies import get_graph
from app.schemas import GraphEdge, GraphNode, Norm, Snapshot
from app.security.rbac import HIDDEN_STATUS, get_allowed_domains, get_dept, get_role


router = APIRouter(prefix="", tags=["snapshot"])


def _norm_record_by_id(norms: list[NormRecord]) -> dict[str, NormRecord]:
    return {n.metric: n for n in norms}


def build_norm(node_id: str, norms: list[NormRecord]) -> Norm | None:
    """Строит DTO Norm для узла из norms.json (lo/hi/warn/unit)."""
    for n in norms:
        if n.metric == node_id:
            return Norm(lo=n.min, hi=n.max, unit=n.unit, warn=n.warn)
    return None


def build_nodes(
    graph: GraphPayload,
    node_values: dict[str, float],
    norms: list[NormRecord],
) -> list[GraphNode]:
    """Узлы снимка с вычисленными status/cost_per_day (§7.1, §7.5)."""
    norm_records = _norm_record_by_id(norms)
    nodes: list[GraphNode] = []
    for gn in graph.nodes:
        value = node_values.get(gn.id, 0.0)
        norm_record = norm_records.get(gn.id)
        norm_dto = build_norm(gn.id, norms)
        nodes.append(
            GraphNode(
                id=gn.id,
                domain=gn.domain,
                name=gn.name,
                unit=gn.unit,
                value=value,
                norm=norm_dto,
                status=node_status(value, norm_record),   # type: ignore[arg-type]
                cost_per_day=node_cost_per_day(gn.id, value, graph, node_values),
                description=None,
                literal=False,
            )
        )
    return nodes


def hide_graph_values(nodes: list[GraphNode], allowed: set[str] | None) -> list[GraphNode]:
    """Скрывает значения узлов недоступных доменов, сохраняя узлы, порядок и рёбра (§22.3)."""
    if allowed is None:
        return nodes

    return [
        node
        if node.domain in allowed
        else node.model_copy(
            update={"value": None, "status": HIDDEN_STATUS, "cost_per_day": None}
        )
        for node in nodes
    ]


@router.get("/snapshot", response_model=Snapshot)
async def get_snapshot(
    request: Request,
    scenario: str = Query("main", description="ID сценария: main|neg|peak"),
    graph: GraphPayload = Depends(get_graph),
) -> Snapshot:
    """Полный снимок сценария: узлы с вычисленными status/cost_per_day + рёбра."""
    try:
        scenario_data = load_scenario(scenario)
        norms = load_norms()
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Неизвестный сценарий: {scenario}") from e
    except (OSError, ValueError) as e:
        raise HTTPException(status_code=500, detail="Ошибка чтения данных") from e

    node_values = {n.id: n.value for n in scenario_data.nodes}
    nodes = build_nodes(graph, node_values, norms)
    allowed = get_allowed_domains(get_role(request), get_dept(request))
    nodes = hide_graph_values(nodes, allowed)

    edges = [
        GraphEdge(
            from_=e.from_,
            to=e.to,
            sign=e.sign,
            weight=e.weight,
            curvature=e.curvature,
            lag_days=e.lag_days,
            note=e.note,
        )
        for e in graph.edges
    ]

    from datetime import date as _date

    return Snapshot(
        scenario_id=scenario_data.scenario_id,
        as_of=_date.fromisoformat(scenario_data.as_of),
        nodes=nodes,
        edges=edges,
    )
