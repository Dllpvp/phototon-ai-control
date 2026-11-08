"""API эндпоинты для управления решениями (§9.2 Readme.md).

Позволяет создавать, просматривать и симулировать эффект решений.
Интегрирован с SQLite (журнал), Jira (ключи) и Telegram (уведомления).
"""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.core.anchors import ANCHORS
from app.core.simulate import simulate as simulate_impact
from app.db import DecisionStore
from app.dependencies import get_db
from app.integrations import telegram
from app.schemas import DecisionDTO

router = APIRouter(prefix="", tags=["decisions"])


class SimulateRequest(BaseModel):
    """Параметры запуска симуляции решения (§7.7)."""

    days: int = Field(default=ANCHORS["sim_days"], gt=0)
    branch: Literal["main", "neg"] = "main"


def _branch_for(decision: DecisionDTO, payload: SimulateRequest | None) -> str:
    """Ветка симуляции: явно из тела запроса, иначе из сценария решения."""
    if payload is not None:
        return payload.branch
    return decision.scenario_id if decision.scenario_id in ("main", "neg") else "main"


@router.post("/decisions", response_model=DecisionDTO)
async def create_decision(
    decision: DecisionDTO,
    db: DecisionStore = Depends(get_db),
) -> DecisionDTO:
    """Создаёт решение: сохраняет в БД, генерит Jira-ключ, шлёт Telegram."""
    # 1. Jira-ключ (счётчик PROD-{n} в SQLite, §11.2)
    decision.jira_key = db.next_jira_key("PROD")

    # 2. Сохраняем в БД (ID и created_at проставит стор)
    saved = db.create_decision(decision)

    # 3. Telegram (фолбэк внутри, никогда не raise, §11.1)
    notification = telegram.send_message(
        chat_id="",
        text=(
            f"Новое решение: {saved.type} (Jira: {saved.jira_key})\n"
            f"Автор: {saved.owner}"
        ),
        subject="Новое решение",
        related_decision_id=saved.id,
    )
    saved.notification = notification
    return saved


@router.get("/decisions", response_model=list[DecisionDTO])
async def list_decisions(
    scenario_id: str | None = None,
    db: DecisionStore = Depends(get_db),
) -> list[DecisionDTO]:
    """Возвращает список всех решений (можно фильтровать по сценарию)."""
    return db.list_decisions(scenario_id=scenario_id)


@router.get("/decisions/{decision_id}", response_model=DecisionDTO)
async def get_decision(
    decision_id: str,
    db: DecisionStore = Depends(get_db),
) -> DecisionDTO:
    """Одна запись журнала решений."""
    decision = db.get_decision(decision_id)
    if decision is None:
        raise HTTPException(status_code=404, detail="Решение не найдено")
    return decision


@router.post("/decisions/{decision_id}/simulate", response_model=DecisionDTO)
async def simulate_decision(
    decision_id: str,
    payload: SimulateRequest | None = None,
    db: DecisionStore = Depends(get_db),
) -> DecisionDTO:
    """Запускает симуляцию для решения и обновляет его статус в БД."""
    decision = db.get_decision(decision_id)
    if decision is None:
        raise HTTPException(status_code=404, detail="Решение не найдено")

    days = payload.days if payload is not None else ANCHORS["sim_days"]
    branch = _branch_for(decision, payload)

    if decision.type != "hire":
        raise HTTPException(
            status_code=400,
            detail="Симуляция поддерживается только для решений типа 'hire'",
        )

    # Ядро симуляции (§7.7): decisions — список {"type": ..., ...params}
    result = simulate_impact(
        days=days,
        decisions=[{"type": decision.type, **decision.params}],
        branch=branch,
    )

    db.update_decision_effect(
        decision_id=decision_id,
        effect_byn=result.effect_byn,
        verdict=result.verdict,
    )

    updated = db.get_decision(decision_id)
    if updated is None:  # pragma: no cover — запись только что прочитана
        raise HTTPException(status_code=404, detail="Решение не найдено")
    return updated