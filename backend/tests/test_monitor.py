
"""T22 — тесты ИИ-монитора.

Приёмка: красный KPI → один инцидент; повторный с тем же cause_key отклоняется.
Монитор не исполняет решения — только черновик.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.core.loader import load_graph
from app.core.monitor import MONITOR_EXCLUDE, check_red_kpis
from app.main import app
from app.repo.incidents import IncidentsStore


@pytest.fixture()
def client(tmp_path, monkeypatch) -> TestClient:
    monkeypatch.setenv("FOTOPRINT_DB_PATH", str(tmp_path / "test_state.db"))
    return TestClient(app)


def test_drafts_for_red_kpis_only():
    graph = load_graph()
    drafts = check_red_kpis(graph)
    red = {n.id for n in graph.nodes if n.status_main == "red"} - MONITOR_EXCLUDE
    assert {d.cause_key for d in drafts} == red
    assert all(d.status == "draft" for d in drafts)


def test_cause_keys_unique():
    drafts = check_red_kpis(load_graph())
    keys = [d.cause_key for d in drafts]
    assert len(keys) == len(set(keys))


def test_root_cause_is_leaf():
    graph = load_graph()
    has_parent = {e.to for e in graph.edges}
    for draft in check_red_kpis(graph):
        assert draft.root_cause not in has_parent


def test_no_auto_execution():
    for draft in check_red_kpis(load_graph()):
        assert draft.status == "draft"
        assert "автоматически не исполняется" in draft.recommendation


def test_check_creates_incidents(client):
    r = client.post("/api/monitor/check")
    assert r.status_code == 200
    data = r.json()
    expected = len(check_red_kpis(load_graph()))
    assert data["created"] == expected
    assert data["duplicated"] == 0
    assert data["open_total"] == expected
    assert all(i["status"] == "open" for i in data["incidents"])


def test_repeat_same_cause_key_rejected(client):
    first = client.post("/api/monitor/check").json()
    second = client.post("/api/monitor/check").json()
    assert second["created"] == 0
    assert second["duplicated"] == first["created"]
    assert second["open_total"] == first["created"]


def test_store_dedup_direct(client):
    store = IncidentsStore()
    draft = check_red_kpis(load_graph())[0]
    assert store.create(draft) is not None
    assert store.create(draft) is None
    assert store.count_open() == 1


def test_list_and_filter(client):
    client.post("/api/monitor/check")
    assert len(client.get("/api/incidents").json()) > 0
    assert len(client.get("/api/incidents", params={"status": "open"}).json()) > 0
    assert client.get("/api/incidents", params={"status": "resolved"}).json() == []
    assert client.get("/api/incidents", params={"status": "junk"}).status_code == 400


def test_accept_and_reject(client):
    created = client.post("/api/monitor/check").json()["incidents"]
    a = client.post(f"/api/incidents/{created[0]['id']}/accept")
    assert a.status_code == 200
    assert a.json()["status"] == "acknowledged"
    assert a.json()["resolution"] == "accepted"
    b = client.post(f"/api/incidents/{created[1]['id']}/reject")
    assert b.json()["status"] == "resolved"
    assert b.json()["resolution"] == "rejected"
    assert client.post(f"/api/incidents/{created[0]['id']}/accept").status_code == 400


def test_unknown_incident_404(client):
    assert client.post("/api/incidents/no-such-id/accept").status_code == 404


def test_acknowledged_frees_cause_key(client):
    created = client.post("/api/monitor/check").json()["incidents"]
    client.post(f"/api/incidents/{created[0]['id']}/reject")
    again = client.post("/api/monitor/check").json()
    assert again["created"] == 1