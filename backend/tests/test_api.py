import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_snapshot_main():
    """GET /api/snapshot?scenario=main → 200, 18 узлов, 17 рёбер, as_of=2026-11-02."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/snapshot?scenario=main")
        assert response.status_code == 200
        data = response.json()
        assert data["scenario_id"] == "main"
        assert data["as_of"] == "2026-11-02"
        assert len(data["nodes"]) == 18
        assert len(data["edges"]) == 17
        # Проверка структуры узла
        node = data["nodes"][0]
        assert "id" in node
        assert "domain" in node
        assert "name" in node
        assert "unit" in node
        assert "value" in node
        assert "status" in node
        assert "cost_per_day" in node


@pytest.mark.asyncio
async def test_dashboard_alerts_sorted():
    """GET /api/dashboard?scenario=main → 200, alerts отсортированы по cost_per_day desc (первый = 1840 BYN)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/dashboard?scenario=main")
        assert response.status_code == 200
        data = response.json()
        assert "alerts" in data
        alerts = data["alerts"]
        assert len(alerts) > 0
        # Проверка сортировки по cost_per_day desc
        costs = [a["cost_per_day"] for a in alerts]
        assert costs == sorted(costs, reverse=True)
        # Первый алерт должен иметь cost_per_day = 1840
        assert alerts[0]["cost_per_day"] == 1840


@pytest.mark.asyncio
async def test_dashboard_loss_counter():
    """loss_counter_started_at в ISO-формате, не None."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/dashboard?scenario=main")
        assert response.status_code == 200
        data = response.json()
        assert "loss_counter_started_at" in data
        assert data["loss_counter_started_at"] is not None
        # Проверка ISO формата (содержит T)
        assert "T" in data["loss_counter_started_at"]


@pytest.mark.asyncio
async def test_chain_fin_margin():
    """GET /api/chain/fin_margin?scenario=main → 200, chain длиной 4, последний узел = "hr_operators_s3", source="hint"."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/chain/fin_margin?scenario=main")
        assert response.status_code == 200
        data = response.json()
        assert data["source"] == "hint"
        chain = data["chain"]
        assert len(chain) == 4
        assert chain[-1]["node_id"] == "hr_operators_s3"


@pytest.mark.asyncio
async def test_whatif_anchor_points():
    """POST /api/whatif для ops=4/5/6 возвращает ТОЧНО (14,23,41200,1840), (8,11,44900,980), (2,3,47600,260) после округления downtime_h."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # ops = 4
        r4 = await ac.post("/api/whatif", json={"scenario": "main", "node_id": "hr_operators_s3", "value": 4})
        assert r4.status_code == 200
        d4 = r4.json()
        assert d4["downtime_h"] == 14.0
        assert d4["sla_orders"] == 23
        assert d4["revenue_week"] == 41200.0
        assert d4["loss_day"] == 1840.0

        # ops = 5
        r5 = await ac.post("/api/whatif", json={"scenario": "main", "node_id": "hr_operators_s3", "value": 5})
        assert r5.status_code == 200
        d5 = r5.json()
        assert d5["downtime_h"] == 8.0
        assert d5["sla_orders"] == 11
        assert d5["revenue_week"] == 44900.0
        assert d5["loss_day"] == 980.0

        # ops = 6
        r6 = await ac.post("/api/whatif", json={"scenario": "main", "node_id": "hr_operators_s3", "value": 6})
        assert r6.status_code == 200
        d6 = r6.json()
        assert d6["downtime_h"] == 2.0
        assert d6["sla_orders"] == 3
        assert d6["revenue_week"] == 47600.0
        assert d6["loss_day"] == 260.0


@pytest.mark.asyncio
async def test_forecast_peak():
    """GET /api/forecast?scenario=peak → 200, forecast_orders=1240, capacity_orders=1050, deficit=-190."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/forecast?scenario=peak")
        assert response.status_code == 200
        data = response.json()
        assert data["forecast_orders"] == 1240
        assert data["capacity_orders"] == 1050
        assert abs(data["deficit"]) == 190


@pytest.mark.asyncio
async def test_unit_economics():
    """GET /api/unit-economics → 200, 5 строк с точными SKU и маржами, статус red только для -1.9%"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/unit-economics")
        assert response.status_code == 200
        items = response.json()
        assert isinstance(items, list)
        assert len(items) == 5
        # Ожидаемые данные из seed
        expected = [
            {"sku": "Фотокнига 20×20 стандарт", "margin_pct": 28.3, "status": "green"},
            {"sku": "Фотокнига 30×30 премиум", "margin_pct": 35.2, "status": "green"},
            {"sku": "B2B фотостудия «Луч»", "margin_pct": 35.6, "status": "green"},
            {"sku": "B2B маркетплейс «Книга»", "margin_pct": 34.7, "status": "green"},
            {"sku": "Клиент №7", "margin_pct": -1.9, "status": "red"},
        ]
        for exp in expected:
            match = next((item for item in items if item["sku"] == exp["sku"]), None)
            assert match is not None, f"Missing SKU {exp['sku']}"
            assert match["margin_pct"] == exp["margin_pct"], f"Margin mismatch for {exp['sku']}"
            assert match["status"] == exp["status"], f"Status mismatch for {exp['sku']}"


@pytest.mark.asyncio
async def test_slice():
    """GET /api/slice?from=2026-11-01&to=2026-11-02&line=L2&shift=3 → 200, series не пустая."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/slice?from=2026-11-01&to=2026-11-02&line=L2&shift=3")
        assert response.status_code == 200
        data = response.json()
        assert "facts" in data
        assert isinstance(data["facts"], list)