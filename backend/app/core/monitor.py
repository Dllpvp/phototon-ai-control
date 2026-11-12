
"""T22 — ИИ-монитор: красные KPI → черновики инцидентов (PLAN-V2 §22, ТЗ T22).

Чистый слой: без FastAPI, без БД, без сети. Монитор НИКОГДА не исполняет
решения автоматически — только предлагает черновик (status="draft").
Решение оформляет человек через существующий /api/decisions.
"""

from __future__ import annotations

import asyncio
import os
import sys
from dataclasses import dataclass

from app.core.loader import GraphPayload

# Служебные узлы, не являющиеся KPI отделов: внешний фактор и скрытый компенсатор
MONITOR_EXCLUDE: frozenset[str] = frozenset({"season_week_coeff", "equip_lamination_wear"})

CHECK_INTERVAL_SEC = 30  # период фоновой проверки по ТЗ T22
_MAX_ROOT_DEPTH = 4      # как drill-down v1: не глубже 4 шагов


@dataclass(frozen=True)
class IncidentDraft:
    """Черновик инцидента. cause_key — ключ дедупликации (узел графа)."""

    cause_key: str
    node_id: str
    title: str
    value: float
    unit: str
    root_cause: str
    recommendation: str
    status: str = "draft"


def root_cause_of(graph: GraphPayload, node_id: str) -> str:
    """Детерминированный обход назад по входящим рёбрам до корня (≤4 шага).

    Предпочитаем красных родителей, среди них — по алфавиту id (стабильность).
    """
    parents: dict[str, list[str]] = {}
    for e in graph.edges:
        parents.setdefault(e.to, []).append(e.from_)
    red = {n.id for n in graph.nodes if n.status_main == "red"}
    current = node_id
    for _ in range(_MAX_ROOT_DEPTH):
        candidates = sorted(parents.get(current, []))
        if not candidates:
            break
        preferred = [p for p in candidates if p in red]
        current = (preferred or candidates)[0]
    return current


def check_red_kpis(graph: GraphPayload) -> list[IncidentDraft]:
    """Красные KPI → черновики. Один узел = один cause_key = один инцидент."""
    drafts: list[IncidentDraft] = []
    for node in graph.nodes:
        if node.status_main != "red" or node.id in MONITOR_EXCLUDE:
            continue
        root = root_cause_of(graph, node.id)
        drafts.append(IncidentDraft(
            cause_key=node.id,
            node_id=node.id,
            title=f"{node.name}: {node.value_main:g} {node.unit} вне нормы",
            value=node.value_main,
            unit=node.unit,
            root_cause=root,
            recommendation=(
                f"Черновик: проверить «{root}» и оформить решение по «{node.name}». "
                f"Требуется подтверждение ответственного — автоматически не исполняется."
            ),
        ))
    return drafts


async def monitor_loop(interval_sec: int = CHECK_INTERVAL_SEC) -> None:
    """Фоновый цикл. Импорт api/repo внутри — core не зависит от них на импорте."""
    from app.api.incidents import run_monitor_cycle

    while True:
        try:
            run_monitor_cycle()
        except Exception:
            pass  # монитор не имеет права ронять приложение
        await asyncio.sleep(interval_sec)


def start_monitor() -> asyncio.Task | None:
    """Запуск фона. Выключен в тестах, при OFFLINE_MODE и MONITOR_ENABLED=false."""
    if "pytest" in sys.modules:
        return None
    if os.environ.get("MONITOR_ENABLED", "true").lower() == "false":
        return None
    if os.environ.get("OFFLINE_MODE", "false").lower() == "true":
        return None
    return asyncio.create_task(monitor_loop())
