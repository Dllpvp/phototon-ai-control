import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_create_decision():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/decisions", json={
            "scenario_id": "main",
            "type": "hire",
            "params": {"operators": 2},
            "owner": "test",
            "due_date": "2026-11-10"
        })
    assert response.status_code == 200
    data = response.json()
    assert "jira_key" in data
    assert data["jira_key"].startswith("PROD-")
    assert "notification" in data
    assert data["notification"]["status"] in ["sent", "skipped_no_token", "failed"]

@pytest.mark.asyncio
async def test_jira_mock():
    # Сначала создаем, чтобы ключ существовал
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post("/api/decisions", json={
            "scenario_id": "main",
            "type": "hire",
            "params": {"operators": 2},
            "owner": "test",
            "due_date": "2026-11-10"
        })
        key = res.json()["jira_key"]
        
        response = await ac.get(f"/api/jira/{key}")
    assert response.status_code == 200
    data = response.json()
    assert data["key"] == key

@pytest.mark.asyncio
async def test_decisions_simulate():
    # Создаем решение
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post("/api/decisions", json={
            "scenario_id": "main",
            "type": "hire",
            "params": {"operators": 1},
            "owner": "test",
            "due_date": "2026-11-10"
        })
        d_id = res.json()["id"]
        
        # Симулируем
        response = await ac.post(f"/api/decisions/{d_id}/simulate", json={
            "days": 14,
            "branch": "main"
        })
    assert response.status_code == 200
    data = response.json()
    # Контракт §9.2: SimulationDTO (days, branch, effect_byn, verdict, loss_day,
    # defect_rate, downtime_h, final_snapshot, ...)
    assert data["days"] == 14
    assert data["branch"] == "main"
    assert "effect_byn" in data
    assert data["verdict"] in ["effective", "ineffective"]
    assert "loss_day" in data
    assert "defect_rate" in data
    assert "downtime_h" in data
    assert "final_snapshot" in data
    assert isinstance(data["final_snapshot"], dict)
