"""API эндпоинт: POST /api/whatif (§9.2 Readme.md).

Интерполяция по ANCHORS через core/interpolation.py.
Всегда точно отвечает на 4/5/6 = числа плана.
"""

from __future__ import annotations

from fastapi import APIRouter, Body, Depends, Query
from pydantic import BaseModel

from app.core.anchors import ANCHORS
from app.core.interpolation import interp
from app.core.loader import GraphPayload, ScenarioNode, load_scenario
from app.dependencies import get_graph
from app.schemas import WhatIfDTO, WhatIfDeltaDTO, RecommendedDTO

router = APIRouter(tags=["whatif"])


class WhatIfRequest(BaseModel):
    """Тело запроса POST /api/whatif."""
    scenario: str = "main"
    node_id: str = "hr_operators_s3"
    value: float


@router.post("/whatif", response_model=WhatIfDTO)
async def post_whatif(
    request: WhatIfRequest = Body(...),
    graph: GraphPayload = Depends(get_graph),
) -> WhatIfDTO:
    """What-If симуляция: меняем число операторов, интерполируем метрики из ANCHORS."""
    scenario = request.scenario
    node_id = request.node_id
    ops = request.value
    
    # Валидация: только hr_operators_s3 поддерживается сейчас
    if node_id != "hr_operators_s3":
        raise ValueError(f"Node {node_id} не поддерживается для what-if. Используйте hr_operators_s3.")
    
    # Загружаем сценарий для текущего состояния
    scenario_data = load_scenario(scenario)
    current_ops = next((n.value for n in scenario_data.nodes if n.id == "hr_operators_s3"), 4.0)
    
    # Интерполяция из ANCHORS
    downtime_h = interp(ops, ANCHORS["downtime_h_by_ops"])
    sla_orders = int(round(interp(ops, ANCHORS["sla_orders_by_ops"])))
    revenue_week = interp(ops, ANCHORS["revenue_week_by_ops"])
    loss_day = interp(ops, ANCHORS["loss_day_by_ops"])
    
    # Текущие значения (для дельты)
    current_downtime = interp(current_ops, ANCHORS["downtime_h_by_ops"])
    current_sla = int(round(interp(current_ops, ANCHORS["sla_orders_by_ops"])))
    current_revenue = interp(current_ops, ANCHORS["revenue_week_by_ops"])
    current_loss = interp(current_ops, ANCHORS["loss_day_by_ops"])
    
    # Дельта vs_now
    vs_now = WhatIfDeltaDTO(
        d_downtime=round(downtime_h - current_downtime, 1),
        d_sla=sla_orders - current_sla,
        d_revenue=round(revenue_week - current_revenue, 0),
        d_loss=round(loss_day - current_loss, 0),
    )
    
    # Рекомендуемое решение
    # Если ops >= 6 — effective, иначе partial
    add_ops = max(0, int(round(ops - current_ops)))
    recommended = RecommendedDTO(
        type="hire",
        operators=add_ops,
        expected_effect_byn=round((current_loss - loss_day) * 14, 0),
        expected_defect_rate=ANCHORS["defect_rate_after_hire"] if ops >= 5 else ANCHORS["defect_rate_now"],
        expected_downtime_h=round(downtime_h, 1),
    )
    
    # Цепочка превью (из path_hint)
    chain_preview = ["fin_margin", "sales_sla_breach", "prod_downtime_l2", "hr_operators_s3"]
    
    return WhatIfDTO(
        ops=ops,
        downtime_h=round(downtime_h, 1),
        sla_orders=sla_orders,
        revenue_week=round(revenue_week, 0),
        loss_day=round(loss_day, 0),
        vs_now=vs_now,
        recommended=recommended,
        chain_preview=chain_preview,
    )


# Импорт BaseModel для WhatIfRequest
from pydantic import BaseModel