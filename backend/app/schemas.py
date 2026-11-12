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
    """Норма метрики: нижняя/верхняя граница + единица измерения + мягкая граница (warn)."""
    lo: float | None = None
    hi: float | None = None
    unit: str
    warn: float | None = None


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
    status: Literal["red", "yellow", "green"] = "green"


class ChainNodeDTO(BaseModel):
    """Узел в цепочке drill-down (/api/chain)."""
    node_id: str
    name: str
    domain: str
    value: float | None  # None для скрытых доменов
    unit: str
    status: Literal["red", "yellow", "green", "hidden"]
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
    notification: NotificationDTO | None = None


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


DecisionDTO.model_rebuild()

# ──────────────────────────────────────────────────────────────────────
# T18: Каталог KPI (PLAN-V2 §22.4, §22.10) — additive, v1 DTO не менять
# ──────────────────────────────────────────────────────────────────────

class MetricCatalogItemDTO(BaseModel):
    """Карточка KPI из каталога 33 (T18).

    value резолвится на запросе: node → граф, anchor → ANCHORS v1,
    catalog → демо-значение лекции v2.2 (единственный источник — kpi_catalog.json).
    formula_status="assumption" — формула не подтверждена заказчиком («допущение»).
    """
    id: str
    name: str
    department: str
    unit: str
    norm: Norm | None = None
    value: float | None = None            # None: узел v2 ещё не смержен в граф
    available: bool = True                # False → UI показывает «—»
    value_kind: Literal["node", "anchor", "catalog"]
    node_id: str | None = None
    anchor_key: str | None = None
    formula: str
    formula_status: Literal["confirmed", "assumption"]
    origin: Literal["v1", "v2", "lecture_v22"]
    source_system: str


class MetricCatalogDTO(BaseModel):
    """Ответ GET /api/metrics/catalog?department= (T18)."""
    total: int
    department: str | None = None
    items: list[MetricCatalogItemDTO]

# ──────────────────────────────────────────────────────────────────────
# T20: Migration Layer (PLAN-V2 §22.6, §22.10) — additive
# ──────────────────────────────────────────────────────────────────────

class MigrationSourceDTO(BaseModel):
    """Источник данных для миграции. Реальный перенос — после доступов, сейчас контракт."""
    system: str
    name: str
    department: str
    objects: list[str]
    access_mode: Literal["read_api", "export", "webhook", "manual_csv"]
    pii_level: Literal["none", "personal", "commercial"]
    migration_status: Literal["contract_ready", "emulator", "pending_access"]
    notes: str | None = None


class MigrationStepDTO(BaseModel):
    """Шаг демо-миграции. mode=real — шаг делает настоящую работу, emulator — заглушка."""
    n: int
    key: str
    title: str
    status: Literal["completed", "failed", "skipped"]
    detail: str
    mode: Literal["real", "emulator"] = "emulator"


class MigrationRunDTO(BaseModel):
    """Ответ POST /api/migration/demo-run. Записывается в таблицу migration_runs."""
    run_id: str
    status: Literal["completed", "failed"]
    mode: Literal["emulator"] = "emulator"
    created_at: datetime
    sources_count: int
    pii_sources: int
    steps: list[MigrationStepDTO]


# ──────────────────────────────────────────────────────────────────────
# T22: ИИ-монитор и инциденты — additive
# ──────────────────────────────────────────────────────────────────────

class IncidentDTO(BaseModel):
    """Инцидент от монитора. Рекомендация — черновик, решение оформляет человек."""
    id: str
    cause_key: str
    node_id: str
    title: str
    value: float
    unit: str
    root_cause: str
    recommendation: str
    status: Literal["open", "acknowledged", "resolved"]
    resolution: Literal["accepted", "rejected"] | None = None
    created_at: datetime
    updated_at: datetime | None = None


class MonitorCheckResultDTO(BaseModel):
    """Ответ POST /api/monitor/check: сколько создано, сколько отклонено как дубли."""
    created: int
    duplicated: int
    open_total: int
    incidents: list[IncidentDTO]

