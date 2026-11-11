"""T18 — тесты каталога KPI: 33 записи, 10 отделов, 10 лекционных карт.

Правило 11 AGENTS.md: каждое новое число → тест. Каталог — единственный
источник лекционных демо-значений; графовые значения сверяются с графом.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.api.metrics import DEPARTMENTS
from app.core.anchors import ANCHORS
from app.core.loader import load_graph
from app.main import app


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


# 10 лекционных карт из ТЗ T18 (PLAN-V2.2)
LECTURE_IDS = {
    "exec_cross_alerts", "exec_effect_14d", "prod_reprint_volume",
    "clients_answer_1min_pct", "clients_bot_share_pct", "clients_nezabory_pvz",
    "hr_satisfaction", "fin_ondemand_margin", "proc_supply_risk_pct",
    "retail_abandoned_designs",
}

# Новые числа лекции: id → (демо-значение, норма lo, норма hi)
LECTURE_NUMBERS = {
    "exec_cross_alerts": (5, 0, 2),
    "clients_answer_1min_pct": (38, 70, None),
    "clients_bot_share_pct": (45, 80, None),
    "clients_nezabory_pvz": (18, 0, 5),
    "hr_satisfaction": (7.8, 7, 10),
    "proc_supply_risk_pct": (62, 0, 20),
    "retail_abandoned_designs": (120, 0, 50),
}


def _catalog(client: TestClient) -> dict:
    r = client.get("/api/metrics/catalog")
    assert r.status_code == 200
    return r.json()


def test_catalog_has_33_items(client):
    data = _catalog(client)
    assert data["total"] == 33
    assert len(data["items"]) == 33


def test_ids_unique(client):
    ids = [i["id"] for i in _catalog(client)["items"]]
    assert len(set(ids)) == 33


def test_required_fields(client):
    for item in _catalog(client)["items"]:
        assert item["name"] and item["unit"] and item["formula"]
        assert item["source_system"] and item["norm"] is not None
        assert item["department"] in DEPARTMENTS
        assert item["formula_status"] in ("confirmed", "assumption")
        assert item["origin"] in ("v1", "v2", "lecture_v22")


def test_all_ten_departments_covered(client):
    depts = {i["department"] for i in _catalog(client)["items"]}
    assert depts == set(DEPARTMENTS)


def test_lecture_ten_present(client):
    ids = {i["id"] for i in _catalog(client)["items"]}
    assert LECTURE_IDS <= ids


@pytest.mark.parametrize("metric_id", sorted(LECTURE_NUMBERS))
def test_lecture_numbers(client, metric_id):
    expected, lo, hi = LECTURE_NUMBERS[metric_id]
    item = next(i for i in _catalog(client)["items"] if i["id"] == metric_id)
    assert item["value"] == pytest.approx(expected)
    assert item["available"] is True
    assert item["norm"]["lo"] == lo and item["norm"]["hi"] == hi
    # формулы новых лекционных метрик заказчиком не подтверждены → «допущение»
    assert item["formula_status"] == "assumption"


def test_effect_14d_from_anchors(client):
    item = next(i for i in _catalog(client)["items"] if i["id"] == "exec_effect_14d")
    assert item["value"] == ANCHORS["test_effect_14d"] == 22120
    assert item["formula_status"] == "confirmed"


@pytest.mark.parametrize("metric_id,lo,hi", [
    ("sales_claims_day", 0, 8),
    ("sales_frt_min", 0, 15),          # ANCHORS_V2: 15 мин (в §22.4 опечатка 4.5)
    ("prod_cycle_h", 0, 22.87),        # норматив 22 ч 52 мин
    ("log_ontime_pct", 95, None),
    ("proc_paper_stock_days", 14, None),
])
def test_v2_norms(client, metric_id, lo, hi):
    item = next(i for i in _catalog(client)["items"] if i["id"] == metric_id)
    assert item["norm"]["lo"] == lo and item["norm"]["hi"] == hi


def test_percent_and_score_bounds(client):
    for item in _catalog(client)["items"]:
        if item["value"] is None:
            continue
        if item["unit"] == "%":
            assert -100 <= item["value"] <= 100  # маржа клиента бывает отрицательной
        if item["unit"] == "/10":
            assert 0 <= item["value"] <= 10


def test_norms_ordered(client):
    for item in _catalog(client)["items"]:
        lo, hi = item["norm"]["lo"], item["norm"]["hi"]
        if lo is not None and hi is not None:
            assert lo <= hi


def test_v1_node_values_match_graph(client):
    graph_values = {n.id: n.value_main for n in load_graph().nodes}
    for item in _catalog(client)["items"]:
        if item["value_kind"] == "node" and item["node_id"] in graph_values:
            assert item["available"] is True
            assert item["value"] == pytest.approx(graph_values[item["node_id"]])


def test_v2_nodes_graceful_before_merge(client):
    """До мержа графа v2 узлы отсутствуют → value=None, available=False, не падаем."""
    graph_ids = {n.id for n in load_graph().nodes}
    for item in _catalog(client)["items"]:
        if item["value_kind"] == "node" and item["node_id"] not in graph_ids:
            assert item["value"] is None and item["available"] is False


def test_department_filter(client):
    r = client.get("/api/metrics/catalog", params={"department": "clients"})
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 10
    assert all(i["department"] == "clients" for i in data["items"])
    r2 = client.get("/api/metrics/catalog", params={"department": "production"})
    assert r2.json()["total"] == 4


def test_unknown_department_400(client):
    r = client.get("/api/metrics/catalog", params={"department": "marketing"})
    assert r.status_code == 400
    assert "detail" in r.json()