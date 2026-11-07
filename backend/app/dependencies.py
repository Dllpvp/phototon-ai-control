"""FastAPI-зависимости: доступ к данным приложения (§4.1 Readme.md).

Тонкий слой между роутерами `api/` и лоадером `core/loader.py`. Данные
поднимаются в память **один раз** (первое обращение) и живут в кэше
`lru_cache` внутри лоадера; чтения диска на каждый HTTP-запрос нет.

Роутеры используют это так:

    from fastapi import Depends
    from app.dependencies import get_graph, get_state, get_scenario

    @router.get("/api/snapshot")
    def snapshot(scenario: str = "main", graph=Depends(get_graph)):
        ...

`get_state()` отдаёт агрегат (`graph` + `norms` + `seasonality`) — то, что
нужно почти каждому экрану. `get_scenario(id)` — фикстуру конкретного
сценария; неверный id → `KeyError`, который роутер обязан превратить в 400
(§9.4).
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import BaseModel

from app.core.loader import (
    GraphPayload,
    NormRecord,
    Scenario,
    SeasonalityWeek,
    load_graph,
    load_norms,
    load_scenario,
    load_seasonality,
)
from app.db import DecisionStore


class AppState(BaseModel):
    """Загруженный в память справочник приложения (граф, нормы, сезонность)."""

    graph: GraphPayload
    norms: list[NormRecord]
    seasonality: list[SeasonalityWeek]


@lru_cache(maxsize=1)
def get_state() -> AppState:
    """Агрегат справочных данных, собранный один раз при старте."""
    return AppState(
        graph=load_graph(),
        norms=load_norms(),
        seasonality=load_seasonality(),
    )


def get_graph() -> GraphPayload:
    """Граф причин (§6) как FastAPI-зависимость."""
    return get_state().graph


def get_scenario(scenario_id: str) -> Scenario:
    """Фикстура сценария `main`/`neg`/`peak` (§8) как FastAPI-зависимость."""
    return load_scenario(scenario_id)


def get_db() -> DecisionStore:
    """Хранилище решений (§4.3) как FastAPI-зависимость."""
    return DecisionStore()


def clear_state() -> None:
    """Сбросить кэш агрегата (используется тестами)."""
    get_state.cache_clear()
