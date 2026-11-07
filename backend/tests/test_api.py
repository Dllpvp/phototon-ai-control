import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_whatif_anchor_points():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Тест на 4, 5, 6 операторах
        for ops, expected_loss in [(4, 1840), (5, 980), (6, 260)]:
            response = await ac.post("/api/whatif", json={"scenario": "main", "node_id": "hr_operators_s3", "value": ops})
            assert response.status_code == 200
            data = response.json()
            assert data["loss_day"] == expected_loss
            # Проверка простоя
            if ops == 4: assert data["downtime_h"] == 14.0
            if ops == 6: assert data["downtime_h"] == 2.0

@pytest.mark.asyncio
async def test_dashboard():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/dashboard?scenario=main")
        assert response.status_code == 200
        data = response.json()
        assert "loss_counter_started_at" in data
        # Проверка сортировки алертов
        costs = [a["cost_per_day"] for a in data["alerts"]]
        assert costs == sorted(costs, reverse=True)

@pytest.mark.asyncio
async def test_ai_health():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/ai/health")
        assert response.status_code == 200
        data = response.json()
        assert data["provider"] == "deepseek"
        assert data["model"] == "deepseek-flash"


@pytest.mark.asyncio
async def test_chain():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/chain/fin_margin?scenario=main")
        assert response.status_code == 200
        data = response.json()
        assert len(data["chain"]) == 4
        assert data["chain"][-1]["node_id"] == "hr_operators_s3"
