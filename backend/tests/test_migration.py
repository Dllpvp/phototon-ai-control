"""T20 — тесты Migration Layer (PLAN-V2 §22.6).

8 источников, Битрикс24=pending_access, pii_level у каждого,
demo-run: 6 шагов, completed, запись в migration_runs.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.api.migration import MigrationStore
from app.main import app

STEP_KEYS = ["extract", "pii_scan", "tokenize", "map_to_graph", "validate_anchors", "dashboard_generated"]


@pytest.fixture()
def client(tmp_path, monkeypatch) -> TestClient:
    # Изоляция БД: каждый тест со своим state.db
    monkeypatch.setenv("FOTOPRINT_DB_PATH", str(tmp_path / "test_state.db"))
    return TestClient(app)


def test_sources_eight(client):
    r = client.get("/api/migration/sources")
    assert r.status_code == 200
    assert len(r.json()) == 8


def test_bitrix_pending_access(client):
    data = client.get("/api/migration/sources").json()
    bitrix = next(s for s in data if s["system"] == "bitrix")
    assert bitrix["migration_status"] == "pending_access"


def test_pii_level_marked(client):
    data = client.get("/api/migration/sources").json()
    allowed = {"none", "personal", "commercial"}
    assert all(s["pii_level"] in allowed for s in data)
    assert any(s["pii_level"] != "none" for s in data)  # тест из §22.11


def test_source_fields(client):
    for s in client.get("/api/migration/sources").json():
        assert s["system"] and s["name"] and s["department"] and s["objects"]
        assert s["access_mode"] in {"read_api", "export", "webhook", "manual_csv"}
        assert s["migration_status"] in {"contract_ready", "emulator", "pending_access"}


def test_demo_run_completed(client):
    r = client.post("/api/migration/demo-run")
    assert r.status_code == 200
    run = r.json()
    assert run["status"] == "completed"
    assert [s["key"] for s in run["steps"]] == STEP_KEYS
    assert all(s["status"] == "completed" for s in run["steps"])


def test_demo_run_counts_from_data(client):
    sources = client.get("/api/migration/sources").json()
    run = client.post("/api/migration/demo-run").json()
    assert run["sources_count"] == len(sources)
    assert run["pii_sources"] == sum(1 for s in sources if s["pii_level"] != "none")


def test_anchor_step_is_real(client):
    run = client.post("/api/migration/demo-run").json()
    step = run["steps"][4]
    assert step["key"] == "validate_anchors"
    assert step["mode"] == "real" and step["status"] == "completed"


def test_demo_run_persisted(client):
    assert MigrationStore().count_runs() == 0
    client.post("/api/migration/demo-run")
    assert MigrationStore().count_runs() == 1
    client.post("/api/migration/demo-run")
    assert MigrationStore().count_runs() == 2  # повторный запуск — новая запись, не падает
