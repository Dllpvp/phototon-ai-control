"""Лоадер данных с диска (§4.1, §5, §6 Readme.md).

Слой `core/` читает JSON-файлы и отдаёт их в виде валидированных Pydantic-
моделей. Здесь **нет** математики и нет импортов из `api/` — только чтение и
базовая проверка структуры (полные DTO §9 — Этап 3).

Источники:
    backend/data/graph.json        — граф причин (§6)
    backend/data/norms.json        — нормы метрик (§5.4)
    backend/data/seasonality.json  — коэффициенты недель (§5.3)
    backend/data/facts.json        — факты по дням (§5.6)
    backend/app/data/scenarios/*.json — фикстуры сценариев (§8)

Каждый публичный `load_*` кэширован через `functools.lru_cache`: файл
читается с диска **один раз** за жизнь процесса. Повторный вызов возвращает
тот же объект (`load_graph() is load_graph()`).

Каталог данных можно переопределить переменной окружения
`FOTOPRINT_DATA_DIR` (удобно для тестов); по умолчанию — `backend/data`.
"""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

# --- Пути ---------------------------------------------------------------

APP_DIR = Path(__file__).resolve().parents[1]          # backend/app
BACKEND_DIR = APP_DIR.parent                            # backend
DATA_DIR = Path(os.environ.get("FOTOPRINT_DATA_DIR", BACKEND_DIR / "data"))
SCENARIOS_DIR = APP_DIR / "data" / "scenarios"

SCENARIO_IDS = frozenset({"main", "neg", "peak"})

# --- DTO лоадера (базовая структура §5–§9) ------------------------------


class GraphNodePayload(BaseModel):
    """Узел графа из `graph.json` (§6.1)."""

    id: str
    domain: Literal["finance", "clients", "production", "hr", "quality", "season"]
    name: str
    unit: str
    value_main: float
    norm: list[float | None] | None = None
    status_main: Literal["red", "yellow", "green"]
    cost_per_day: float | None = None


class GraphEdgePayload(BaseModel):
    """Ребро графа из `graph.json` (§6.2). `from` — зарезервированное слово."""

    model_config = ConfigDict(populate_by_name=True)

    from_: str = Field(alias="from")
    to: str
    sign: Literal[-1, 1]
    weight: float
    curvature: float | None = None
    lag_days: int = 0
    note: str | None = None


class PathHint(BaseModel):
    """Подсказка drill-down (§6.5): готовый путь до корня."""

    id: str
    path: list[str]
    label: str


class GraphPayload(BaseModel):
    """Полный граф причин (§6)."""

    nodes: list[GraphNodePayload]
    edges: list[GraphEdgePayload]
    root_causes: list[str] = Field(default_factory=list)
    path_hints: list[PathHint] = Field(default_factory=list)


class NormRecord(BaseModel):
    """Норма метрики (§5.4)."""

    metric: str
    domain: str
    min: float | None = None
    max: float | None = None
    unit: str
    warn: float | None = None


class SeasonalityWeek(BaseModel):
    """Недельный коэффициент сезонности (§5.3)."""

    week: int
    week_to: int
    coeff: float
    source: str
    comment: str = ""


class FactRecord(BaseModel):
    """Один факт по дню (§5.6)."""

    ts: str
    domain: str
    metric: str
    value: float
    dims: dict[str, Any] = Field(default_factory=dict)


class Period(BaseModel):
    """Окно фактов (§5.2). `from` — зарезервированное слово."""

    model_config = ConfigDict(populate_by_name=True)

    from_: str = Field(alias="from")
    to: str
    granularity: str


class FactsPayload(BaseModel):
    """Файл `facts.json` целиком."""

    period: Period
    facts: list[FactRecord]


class ScenarioNode(BaseModel):
    """Переопределение узла внутри сценария (§8)."""

    id: str
    value: float
    status: Literal["red", "yellow", "green"]


class Scenario(BaseModel):
    """Фикстура сценария (§8). Поля `journal`/`forecast`/`recommended`
    присутствуют не во всех сценариях — держим их как свободные словари."""

    scenario_id: Literal["main", "neg", "peak"]
    as_of: str
    week: int
    nodes: list[ScenarioNode]
    journal: dict[str, Any] | None = None
    forecast: dict[str, Any] | None = None
    recommended: dict[str, Any] | None = None


# --- Чтение -------------------------------------------------------------


def _read_json(path: Path) -> Any:
    if not path.is_file():
        raise FileNotFoundError(f"Нет файла данных: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def load_graph() -> GraphPayload:
    """Граф причин (§6). Валидируется Pydantic'ом при загрузке."""
    return GraphPayload.model_validate(_read_json(DATA_DIR / "graph.json"))


@lru_cache(maxsize=1)
def load_norms() -> list[NormRecord]:
    """Нормы метрик (§5.4), 8 записей."""
    raw = _read_json(DATA_DIR / "norms.json")
    return [NormRecord.model_validate(item) for item in raw]


@lru_cache(maxsize=1)
def load_seasonality() -> list[SeasonalityWeek]:
    """Недельные коэффициенты сезонности (§5.3)."""
    raw = _read_json(DATA_DIR / "seasonality.json")
    return [SeasonalityWeek.model_validate(item) for item in raw["weeks"]]


@lru_cache(maxsize=1)
def load_facts() -> FactsPayload:
    """Факты по дням (§5.6)."""
    return FactsPayload.model_validate(_read_json(DATA_DIR / "facts.json"))


@lru_cache(maxsize=len(SCENARIO_IDS))
def load_scenario(scenario_id: str) -> Scenario:
    """Фикстура сценария `main` / `neg` / `peak` (§8)."""
    if scenario_id not in SCENARIO_IDS:
        raise KeyError(
            f"Неизвестный сценарий: {scenario_id!r}. "
            f"Допустимо: {sorted(SCENARIO_IDS)}"
        )
    return Scenario.model_validate(_read_json(SCENARIOS_DIR / f"{scenario_id}.json"))


def clear_caches() -> None:
    """Сбросить кэш лоадера (используется тестами)."""
    load_graph.cache_clear()
    load_norms.cache_clear()
    load_seasonality.cache_clear()
    load_facts.cache_clear()
    load_scenario.cache_clear()
