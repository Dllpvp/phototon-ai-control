"""API эндпоинт: GET /api/chain/{node_id} (§9.2 Readme.md).

Возвращает цепочку drill-down. Использует path_hint из graph.json
для fin_margin (target=hr_operators_s3). Цепочка длиной 4.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Path, Query

from app.core.loader import GraphPayload, GraphNodePayload, ScenarioNode, load_scenario
from app.dependencies import get_graph
from app.schemas import ChainDTO, ChainNodeDTO

router = APIRouter(prefix="/api", tags=["chain"])


def _build_chain_node(
    node_id: str,
    scenario_nodes: list[ScenarioNode],
    graph: GraphPayload,
    delta_from_parent: float | None = None,
) -> ChainNodeDTO | None:
    """Строит ChainNodeDTO из узла графа + сценария."""
    gn = next((n for n in graph.nodes if n.id == node_id), None)
    sn = next((n for n in scenario_nodes if n.id == node_id), None)
    
    if gn is None or sn is None:
        return None
    
    return ChainNodeDTO(
        node_id=gn.id,
        name=gn.name,
        domain=gn.domain,
        value=sn.value,
        unit=gn.unit,
        status=sn.status,
        cost_per_day=gn.cost_per_day,
        delta_from_parent=delta_from_parent,
    )


@router.get("/chain/{node_id}", response_model=ChainDTO)
async def get_chain(
    node_id: str = Path(..., description="ID узла (например, fin_margin)"),
    scenario: str = Query("main", description="ID сценария: main|neg|peak"),
    graph: GraphPayload = Depends(get_graph),
) -> ChainDTO:
    """Цепочка drill-down от узла до корневой причины.
    
    Для fin_margin использует path_hint из graph.json:
    ["fin_margin", "sales_sla_breach", "prod_downtime_l2", "hr_operators_s3"]
    """
    scenario_data = load_scenario(scenario)
    
    # Ищем path_hint для этого узла
    hint_path: list[str] | None = None
    for hint in graph.path_hints:
        if hint.path and hint.path[0] == node_id:
            hint_path = hint.path
            break
    
    if hint_path:
        # Используем hint — цепочка уже готова
        chain_nodes: list[ChainNodeDTO] = []
        for i, nid in enumerate(hint_path):
            delta = None
            # Можно вычислить дельту от родителя через impact.py, но пока None
            chain_nodes.append(_build_chain_node(nid, scenario_data.nodes, graph, delta))
        
        # Фильтруем None
        chain_nodes = [n for n in chain_nodes if n is not None]
        
        return ChainDTO(source="hint", chain=chain_nodes)
    
    # Фолбэк: алгоритмический поиск пути к корневой причине
    # Ищем путь от node_id до любого из root_causes
    from collections import deque
    
    # Строим обратный граф (in_edges)
    in_edges_map: dict[str, list[str]] = {}
    for edge in graph.edges:
        in_edges_map.setdefault(edge.to, []).append(edge.from_)
    
    # BFS от node_id вверх по in_edges до root_cause
    queue = deque([(node_id, [node_id])])
    visited = {node_id}
    found_path: list[str] | None = None
    
    while queue:
        current, path = queue.popleft()
        
        if current in graph.root_causes:
            found_path = path
            break
        
        for parent in in_edges_map.get(current, []):
            if parent not in visited:
                visited.add(parent)
                queue.append((parent, path + [parent]))
    
    if found_path is None:
        found_path = [node_id]
    
    chain_nodes = []
    for i, nid in enumerate(found_path):
        delta = None
        chain_nodes.append(_build_chain_node(nid, scenario_data.nodes, graph, delta))
    
    chain_nodes = [n for n in chain_nodes if n is not None]
    
    return ChainDTO(source="algorithm", chain=chain_nodes)