
"""T22 — ИИ-монитор: инциденты по красным KPI (только черновики решений).

Монитор НЕ исполняет решения: он создаёт инцидент со статусом open и текстом-draft.
Кнопки «Принять»/«Отклонить» фиксируют выбор человека и вызывают decide().
Фоновый цикл живёт в core/monitor.py, ручной запуск — POST /api/monitor/check.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.loader import GraphPayload
from app.core.monitor import check_red_kpis
from app.dependencies import get_graph
from app.repo.incidents import IncidentsStore
from app.schemas import IncidentDTO, MonitorCheckResultDTO

router = APIRouter(tags=["monitor"])


def get_store() -> IncidentsStore:
    return IncidentsStore()


def run_monitor_cycle(graph: GraphPayload | None = None) -> MonitorCheckResultDTO:
    """Один проход монитора. Используется и фоном, и ручкой, и тестами."""
    if graph is None:
        from app.dependencies import get_graph as _get_graph
        graph = _get_graph()
    store = get_store()
    created: list[IncidentDTO] = []
    duplicated = 0
    for draft in check_red_kpis(graph):
        incident = store.create(draft)
        if incident is None:
            duplicated += 1
        else:
            created.append(incident)
    return MonitorCheckResultDTO(
        created=len(created),
        duplicated=duplicated,
        open_total=store.count_open(),
        incidents=created,
    )


@router.post("/monitor/check", response_model=MonitorCheckResultDTO)
def monitor_check(graph: GraphPayload = Depends(get_graph)) -> MonitorCheckResultDTO:
    """Ручной прогон проверки (демо без ожидания 30 секунд)."""
    return run_monitor_cycle(graph)


@router.get("/incidents", response_model=list[IncidentDTO])
def list_incidents(
    status: str | None = Query(None, description="open | acknowledged | resolved"),
) -> list[IncidentDTO]:
    if status is not None and status not in {"open", "acknowledged", "resolved"}:
        raise HTTPException(status_code=400, detail=f"Неизвестный статус: {status}")
    return get_store().list(status)


@router.post("/incidents/{incident_id}/accept", response_model=IncidentDTO)
def accept_incident(incident_id: str) -> IncidentDTO:
    """«Принять»: инцидент подтверждён. Решение оформляется человеком отдельно."""
    store = get_store()
    if store.get(incident_id) is None:
        raise HTTPException(status_code=404, detail="Инцидент не найден")
    result = store.decide(incident_id, accept=True)
    if result is None:
        raise HTTPException(status_code=400, detail="Инцидент уже обработан")
    return result


@router.post("/incidents/{incident_id}/reject", response_model=IncidentDTO)
def reject_incident(incident_id: str) -> IncidentDTO:
    """«Отклонить»: инцидент закрыт с resolution=rejected."""
    store = get_store()
    if store.get(incident_id) is None:
        raise HTTPException(status_code=404, detail="Инцидент не найден")
    result = store.decide(incident_id, accept=False)
    if result is None:
        raise HTTPException(status_code=400, detail="Инцидент уже обработан")
    return result
