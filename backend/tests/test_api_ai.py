import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.integrations import ai_provider


@pytest.mark.asyncio
async def test_api_interpret_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Тестируем fallback (по умолчанию offline_mode=True в тестах)
        response = await ac.post("/api/ai/interpret", json={"node_id": "test", "cost_per_day": 100})
        assert response.status_code == 200
        data = response.json()
        assert data["source"] == "fallback"
        assert "interpretation" in data


@pytest.mark.asyncio
async def test_api_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/ai/health")
        assert response.status_code == 200
        data = response.json()
        assert "enabled" in data
        assert "model" in data
        assert "cache_size" in data
        assert data["provider"] == "klinch-deepseek"
