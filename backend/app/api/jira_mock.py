from fastapi import APIRouter, Depends, HTTPException
from app.db import DecisionStore
from app.dependencies import get_db

router = APIRouter(prefix="/jira", tags=["jira_mock"])

@router.get("/{key}")
async def get_jira_ticket(
    key: str,
    db: DecisionStore = Depends(get_db),
):
    """Мок Jira: возвращает данные решения по ключу."""
    # Для целей демо ищем в БД по jira_key
    decisions = db.list_decisions()
    for d in decisions:
        if d.jira_key == key:
            return {
                "key": key,
                "decision_id": d.id,
                "type": d.type,
                "status": d.verdict,
                "summary": f"Решение {d.type} для сценария {d.scenario_id}",
                "url": f"https://jira.example.com/browse/{key}"
            }
    
    raise HTTPException(status_code=404, detail="Ticket not found")
