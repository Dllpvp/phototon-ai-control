"""API эндпоинт: GET /api/dashboard (§9.2 Readme.md).

Возвращает DashboardDTO: KPI + алерты + loss_counter_started_at.
"""

from __future__ import annotations

from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from app.core.anchors import ANCHORS
from app.core.loader import GraphNodePayload, GraphPayload, ScenarioNode, load_norms, load_scenario
from app.dependencies import get_graph
from app.schemas import AlertDTO, DashboardDTO, KpiDTO, Norm, SliceDescDTO
from app.security.rbac import filter_dashboard, get_allowed_domains, get_dept, get_role

router = APIRouter(prefix="", tags=["dashboard"])


def _build_norm(node: GraphNodePayload, norms: list) -> Norm | None:
    """Строит Norm для узла из norms.json."""
    for n in norms:
        if n.metric == node.id:
            return Norm(lo=n.min, hi=n.max, unit=n.unit)
    return None


def _build_kpis(
    scenario_nodes: list[ScenarioNode],
    graph: GraphPayload,
    norms: list,
) -> list[KpiDTO]:
    """Строит список KPI из узлов сценария + графа + норм."""
    kpis: list[KpiDTO] = []
    node_map = {n.id: n for n in graph.nodes}
    
    for sn in scenario_nodes:
        gn = node_map.get(sn.id)
        if gn is None:
            continue
        
        norm = _build_norm(gn, norms)
        kpis.append(KpiDTO(
            node_id=gn.id,
            domain=gn.domain,
            name=gn.name,
            unit=gn.unit,
            value=sn.value,
            status=sn.status,
            norm=norm,
            cost_per_day=gn.cost_per_day,
        ))
    
    return kpis


def _build_alerts(
    scenario_nodes: list[ScenarioNode],
    graph: GraphPayload,
    norms: list,
    week: int,
) -> list[AlertDTO]:
    """Строит список алертов для красных/жёлтых узлов, сортирует по cost_per_day desc."""
    alerts: list[AlertDTO] = []
    node_map = {n.id: n for n in graph.nodes}
    
    for sn in scenario_nodes:
        if sn.status == "green":
            continue
        
        gn = node_map.get(sn.id)
        if gn is None or gn.cost_per_day is None or gn.cost_per_day <= 0:
            continue
        
        # Находим норму для delta_text
        norm = _build_norm(gn, norms)
        delta_text = ""
        if norm and norm.lo is not None and norm.hi is not None:
            # Для процентов и абсолютных значений
            if gn.unit == "%":
                delta_text = f"{sn.value - norm.lo:+.1f} п.п."
            else:
                delta_text = f"{sn.value - norm.lo:+.0f}"
        elif norm and norm.hi is not None:
            delta_text = f"{sn.value - norm.hi:+.0f}"
        else:
            delta_text = f"{sn.value:+.1f}"
        
        value_text = f"{sn.value:.1f}{gn.unit.replace('BYN/сут', ' BYN/сут').replace('BYN/нед', ' BYN/нед')}"
        
        alerts.append(AlertDTO(
            node_id=gn.id,
            title=gn.name,
            delta_text=delta_text,
            value_text=value_text,
            status=sn.status,
            cost_per_day=gn.cost_per_day,
            week=week,
            slice=SliceDescDTO(week=week),
        ))
    
    # Сортируем по cost_per_day desc
    alerts.sort(key=lambda a: a.cost_per_day, reverse=True)
    return alerts


@router.get("/dashboard", response_model=DashboardDTO)
async def get_dashboard(
    scenario: str = Query("main", description="ID сценария: main|neg|peak"),
    graph: GraphPayload = Depends(get_graph),
    request: Request = None,
) -> DashboardDTO:
    """Дашборд: KPI сетка + алерты + loss counter."""
    try:
        scenario_data = load_scenario(scenario)
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Unknown scenario: {scenario}") from e

    norms = load_norms()

    kpis = _build_kpis(scenario_data.nodes, graph, norms)
    alerts = _build_alerts(scenario_data.nodes, graph, norms, scenario_data.week)

    # Headline: основная проблема
    red_alerts = [a for a in alerts if a.status == "red"]
    if red_alerts:
        main = red_alerts[0]
        headline = f"{main.title} {main.delta_text}, {main.cost_per_day:,.0f} BYN/сут".replace(",", " ")
    else:
        headline = "Все показатели в норме"

    # loss_counter_started_at — дата as_of сценария в 00:00
    started_at = datetime.strptime(scenario_data.as_of, "%Y-%m-%d")

    dto = DashboardDTO(
        scenario_id=scenario_data.scenario_id,
        as_of=date.fromisoformat(scenario_data.as_of),
        week=scenario_data.week,
        kpis=kpis,
        alerts=alerts,
        loss_counter_started_at=started_at,
        headline=headline,
        updated_at=datetime.now(),
    )

    # Демо-RBAC (T9b): фильтруем kpis/alerts по заголовку X-Demo-Role
    allowed = get_allowed_domains(get_role(request), get_dept(request))
    return filter_dashboard(dto, allowed)