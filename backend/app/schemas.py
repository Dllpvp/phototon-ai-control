"""Pydantic DTO для API «Фотопринт·Контроль» (§9 Readme.md).

Единственный источник DTO для бэкенда. Фронтенд зеркалит их в
`frontend/src/api/types.ts` (руками или через openapi-typescript).
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


# ──────────────────────────────────────────────────────────────────────
# Общие DTO (§9.1)
# ──────────────────────────────────────────────────────────────────────

class Norm(BaseModel):
    """Норма метрики: нижняя/верхняя граница + единица измерения."""
    lo: float | None = None
    hi: float | None = None
    unit: str


class GraphNode(BaseModel):
    """Узел графа причин для API (§9.1).
    
    Отличается от GraphNodePayload (loader.py) наличием `name`, `description`,
    `literal` и полем `norm` типа `Norm` вместо списка.
    """
    id: str
    domain: Literal["finance", "clients", "production", "hr", "quality", "season"]
    name: str
    unit: str
    value: float
    norm: Norm | None = None
    status: Literal["red", "yellow", "green"]
    cost_per_day: float | None = None
    description: str | None = None
    literal: bool = False


class GraphEdge(BaseModel):
    """Ребро графа причин для API (§9.1).
    
    Поле `from_` с алиасом `from` для совместимости с JSON.
    """
    model_config = ConfigDict(populate_by_name=True)
    
    from_: str = Field(alias="from")
    to: str
    sign: Literal[-1, 1]
    weight: float
    curvature: float | None = None
    lag_days: int = 0
    note: str | None = None


class Snapshot(BaseModel):
    """Полный снимок сценария: узлы + рёбра (§9.1)."""
    scenario_id: Literal["main", "neg", "peak"]
    as_of: date
    nodes: list[GraphNode]
    edges: list[GraphEdge]


# ──────────────────────────────────────────────────────────────────────
# DTO для эндпоинтов (§9.3)
# ──────────────────────────────────────────────────────────────────────

class SliceDescDTO(BaseModel):
    """Описание среза для кросс-фильтрации (неделя, линия, смена)."""
    week: int
    line: str | None = None
    shift: int | None = None


class AlertDTO(BaseModel):
    """Алерт для дашборда (§9.3). Сортируются по cost_per_day desc."""
    node_id: str
    title: str
    delta_text: str          # "−10 п.п."
    value_text: str          # "32.0%"
    status: Literal["red", "yellow"]
    cost_per_day: float      # 1840
    week: int
    slice: SliceDescDTO


class KpiDTO(BaseModel):
    """KPI карточка для сетки 4×3 на дашборде (§10.1)."""
    node_id: str
    domain: Literal["finance", "clients", "production", "hr", "quality", "season"]
    name: str
    unit: str
    value: float
    status: Literal["red", "yellow", "green"]
    norm: Norm | None = None
    cost_per_day: float | None = None


class DashboardDTO(BaseModel):
    """Ответ GET /api/dashboard (§9.3)."""
    scenario_id: str
    as_of: date
    week: int
    kpis: list[KpiDTO]                  # 12 узлов, по 3 на домен
    alerts: list[AlertDTO]              # сортированы: cost_per_day desc
    loss_counter_started_at: datetime   # ISO; UI тикает от него
    headline: str                       # "Маржа −10 п.п., −1 840 BYN/сут"
    updated_at: datetime


class WhatIfDeltaDTO(BaseModel):
    """Дельта What-If относительно текущего состояния."""
    d_downtime: float
    d_sla: float
    d_revenue: float
    d_loss: float


class RecommendedDTO(BaseModel):
    """Рекомендуемое решение на основе What-If."""
    type: Literal["hire"]
    operators: int
    expected_effect_byn: float
    expected_defect_rate: float
    expected_downtime_h: float


class WhatIfDTO(BaseModel):
    """Ответ POST /api/whatif (§9.3). Всегда точно отвечает на 4/5/6 = числа плана."""
    ops: float
    downtime_h: float
    sla_orders: int
    revenue_week: float
    loss_day: float
    vs_now: WhatIfDeltaDTO
    recommended: RecommendedDTO
    chain_preview: list[str]      # ids цепочки влияния


class ForecastDTO(BaseModel):
    """Ответ GET /api/forecast (§9.3). Пиковая карточка недели 47."""
    week: int
    seasonality_coeff: float
    forecast_orders: int
    capacity_orders: int
    deficit: int
    downtime_h: float
    loss_day: float
    recommended_action: str | None = None
    downtime_h_after: float | None = None
    loss_day_after: float | None = None


class UnitEconDTO(BaseModel):
    """Строка таблицы юнит-экономики (§7.8, §9.3). 5 SKU/клиентов."""
    sku: str
    price: float
    paper: float
    printing: float
    binding: float
    labor: float
    defect: float
    margin_pct: float


class ChainNodeDTO(BaseModel):
    """Узел в цепочке drill-down (/api/chain)."""
    node_id: str
    name: str
    domain: str
    value: float
    unit: str
    status: Literal["red", "yellow", "green"]
    cost_per_day: float | None = None
    delta_from_parent: float | None = None  # изменение относительно родителя


class ChainDTO(BaseModel):
    """Ответ GET /api/chain/{node_id} (§9.3).
    
    Использует path_hint из graph.json для fin_margin (target=hr_operators_s3).
    Возвращает цепочку длиной 4, заканчивающуюся на hr_operators_s3.
    """
    source: Literal["hint", "algorithm"]
    chain: list[ChainNodeDTO]


class SliceFactDTO(BaseModel):
    """Один факт в срезе по дням (/api/slice)."""
    ts: date
    domain: str
    metric: str
    value: float
    dims: dict[str, str] = {}


class SliceDTO(BaseModel):
    """Ответ GET /api/slice (§9.3). Кросс-фильтр: серия по дням."""
    from_: date = Field(alias="from")
    to: date
    line: str | None = None
    shift: int | None = None
    facts: list[SliceFactDTO]


class SimulationDTO(BaseModel):
    """Результат симуляции «было → стало» (+14 дней) (§7.7)."""
    days: int
    branch: Literal["main", "neg"]
    effect_byn: float
    verdict: Literal["effective", "ineffective"]
    recommendation: str | None = None
    compensating_cause: str | None = None
    loss_day: float
    defect_rate: float
    downtime_h: float
    final_snapshot: dict[str, dict[str, float]]  # node_id -> {value, status}


# ──────────────────────────────────────────────────────────────────────
# DTO для будущих эндпоинтов (decisions, AI, Jira, notifications)
# Оставлены как заглушки для совместимости OpenAPI схемы
# ──────────────────────────────────────────────────────────────────────

class DecisionDTO(BaseModel):
    id: str | None = None
    scenario_id: str
    type: Literal["hire", "maintenance", "other"]
    params: dict[str, float | int | str]
    owner: str
    due_date: date | None = None
    expected_effect_byn: float = 0.0
    notes: str | None = None
    baseline_snapshot: dict[str, float] | None = None
    actual_effect_byn: float = 0.0
    verdict: Literal["effective", "ineffective", "pending"] = "pending"
    created_at: datetime | None = None
    jira_key: str | None = None


class AiDTO(BaseModel):
    scene: str
    node_id: str
    chain: list[str]
    delta: dict[str, float]
    cost_per_day: float
    interpretation: str
    source: Literal["cache", "deepseek", "fallback"]
    cache_hit: bool


class NotificationDTO(BaseModel):
    id: str
    channel: Literal["telegram", "email", "inapp"]
    recipient: str
    subject: str
    body: str
    status: Literal["sent", "failed", "skipped_no_token"]
    created_at: datetime
    related_decision_id: str | None = None