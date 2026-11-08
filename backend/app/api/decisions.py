"""API эндпоинты для управления решениями (§9.2 Readme.md).

Позволяет создавать, просматривать и симулировать эффект решений.
Интегрирован с SQLite (журнал), Jira (ключи) и Telegram (уведомления).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response

from app.db import DecisionStore
from app.dependencies import get_db
from app.integrations import jira, telegram
from app.schemas import DecisionDTO, SimulationDTO
from app.core.simulate import simulate as simulate_impact
from app.report.pdf import generate_executive_summary

router = APIRouter(prefix="", tags=["decisions"])


@router.post("/decisions", response_model=DecisionDTO)
async def create_decision(
    decision: DecisionDTO,
    db: DecisionStore = Depends(get_db),
) -> DecisionDTO:
    """Создаёт решение: сохраняет в БД, генерит Jira-ключ, шлёт Telegram."""
    # 1. Jira-ключ
    decision.jira_key = db.next_jira_key("PROD")

    # 2. Сохраняем в БД (ID и created_at проставит стор)
    saved = db.create_decision(decision)

    # 3. Telegram (не блокирует ответ, ошибки игнорируются внутри)
    telegram.send_message(
        chat_id="",  # Будет взят из настроек
        text=f"🚀 Новое решение: {saved.type} (Jira: {saved.jira_key})\nАвтор: {saved.owner}",
        subject="Новое решение"
    )

    return saved


@router.get("/decisions", response_model=list[DecisionDTO])
async def list_decisions(
    scenario_id: str | None = None,
    db: DecisionStore = Depends(get_db),
) -> list[DecisionDTO]:
    """Возвращает список всех решений (можно фильтровать по сценарию)."""
    return db.list_decisions(scenario_id=scenario_id)


@router.post("/decisions/{decision_id}/simulate", response_model=DecisionDTO)
async def simulate_decision(
    decision_id: str,
    db: DecisionStore = Depends(get_db),
) -> DecisionDTO:
    """Запускает симуляцию для решения и обновляет его статус в БД."""
    decision = db.get_decision(decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")

    # Вызываем ядро симуляции (§7.7)
    # Предполагаем, что params содержит нужные ключи (например, operators)
    result: SimulationDTO = simulate_impact(
        scenario_id=decision.scenario_id,
        decision_type=decision.type,
        params=decision.params
    )

    # Обновляем в БД
    db.update_decision_effect(
        decision_id=decision_id,
        effect_byn=result.effect_byn,
        verdict=result.verdict
    )

    # Возвращаем обновлённое решение
    updated = db.get_decision(decision_id)
    return updated
