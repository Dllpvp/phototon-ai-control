"""T9b: демо-RBAC 7 ролей из PLAN-V2 §22.3 (заголовки X-Demo-Role / X-Demo-Dept).

Кейсы 1–11 из задачи T9b. Все проверки идут через публичный HTTP-контракт
приложения (TestClient), без обращения к приватным внутренностям роутеров.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.security.rbac import DEFAULT_ROLE

client = TestClient(app)


def get_auth_headers(role: str | None = None, dept: str | None = None) -> dict[str, str]:
    headers: dict[str, str] = {}
    if role is not None:
        headers["X-Demo-Role"] = role
    if dept is not None:
        headers["X-Demo-Dept"] = dept
    return headers


def kpi_ids(headers: dict[str, str]) -> dict[str, list[str]]:
    resp = client.get("/api/dashboard", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    return {
        "ids": [k["node_id"] for k in data["kpis"]],
        "domains": [k["domain"] for k in data["kpis"]],
        "kpis": data["kpis"],
        "alerts": data["alerts"],
        "headline": data["headline"],
        "loss_counter_started_at": data["loss_counter_started_at"],
    }


def post_decision(headers: dict[str, str], decision_type: str):
    payload = {
        "scenario_id": "main",
        "type": decision_type,
        "params": {},
        "owner": "Тест T9b",
    }
    return client.post("/api/decisions", json=payload, headers=headers)


# ── Кейс 1: director видит финансовые KPI ─────────────────────────────
def test_director_sees_finance_kpis():
    data = kpi_ids(get_auth_headers("director"))
    assert "fin_loss_day" in data["ids"]
    assert "finance" in data["domains"]


# ── Кейс 2: production_head — finance скрыт, production/hr видны ──────
def test_production_head_no_finance():
    data = kpi_ids(get_auth_headers("production_head", "production"))
    assert "fin_loss_day" not in data["ids"]
    assert "finance" not in data["domains"]
    assert "hr_operators_s3" in data["ids"]


# ── Кейс 3: hr_head — finance скрыт, hr присутствует ──────────────────
def test_hr_head_domains():
    data = kpi_ids(get_auth_headers("hr_head"))
    assert "finance" not in data["domains"]
    assert "hr" in data["domains"]


# ── Кейс 4: support_head — clients присутствует, finance скрыт ────────
def test_support_head_domains():
    data = kpi_ids(get_auth_headers("support_head"))
    assert "clients" in data["domains"]
    assert "finance" not in data["domains"]


# ── Кейс 5: specialist — kpis пуст, POST решений → 403 ────────────────
def test_specialist_empty_and_forbidden():
    headers = get_auth_headers("specialist")
    data = kpi_ids(headers)
    assert data["kpis"] == []
    assert data["alerts"] == []
    resp = post_decision(headers, "hire")
    assert resp.status_code == 403


# ── Кейс 6: hr_head POST maintenance → 403; hire → 200 ────────────────
def test_hr_head_decision_types():
    headers = get_auth_headers("hr_head")
    resp = post_decision(headers, "maintenance")
    assert resp.status_code == 403
    resp = post_decision(headers, "hire")
    assert resp.status_code == 200


# ── Кейс 7: production_head GET /api/chain/fin_margin → hidden, длина 4 ──
def test_chain_filtering_production_head():
    headers = get_auth_headers("production_head")
    resp = client.get("/api/chain/fin_margin", headers=headers)
    assert resp.status_code == 200
    chain = resp.json()["chain"]
    assert len(chain) == 4
    first = chain[0]
    assert first["node_id"] == "fin_margin"
    assert first["value"] is None
    assert first["status"] == "hidden"
    # hr и production узлы остаются видимыми (production_head их домены)
    assert chain[-1]["node_id"] == "hr_operators_s3"
    assert chain[-1]["status"] != "hidden"
    assert chain[-1]["value"] is not None


# ── Кейс 8: без заголовка X-Demo-Role → поведение director ────────────
def test_no_role_header_defaults_to_director():
    resp = client.get("/api/dashboard")
    assert resp.status_code == 200
    ids = [k["node_id"] for k in resp.json()["kpis"]]
    assert "fin_loss_day" in ids  # как у director (фолбэк §17)


# ── Кейс 9: department_head с X-Demo-Dept: hr → видит hr, не finance ──
def test_department_head_dept_hr():
    headers = get_auth_headers("department_head", "hr")
    data = kpi_ids(headers)
    assert "hr" in data["domains"]
    assert "finance" not in data["domains"]


# ── Кейс 10: Headline — production_head не видит финансовый текст ────
def test_headline_no_margin_for_restricted_roles():
    headers = get_auth_headers("production_head")
    data = kpi_ids(headers)
    # финансовый текст («Выручка/маржа…») не должен попасть в headline
    assert "маржа" not in data["headline"].lower()
    # director, наоборот, видит финансовый headline (не сломали базовое поведение)
    director_data = kpi_ids(get_auth_headers("director"))
    assert "маржинальность" in director_data["headline"].lower()


# ── Кейс 11: LossCounter-таймер сохраняется для ограниченных ролей ────
def test_loss_counter_started_at_preserved():
    director_data = kpi_ids(get_auth_headers("director"))
    restricted_data = kpi_ids(get_auth_headers("production_head"))
    assert director_data.get("loss_counter_started_at")
    assert (
        restricted_data.get("loss_counter_started_at")
        == director_data["loss_counter_started_at"]
    )


# ── Доп.: синонимы §22.3 repair/reglament = maintenance ───────────────
@pytest.mark.parametrize("synonym", ["repair", "reglament"])
def test_decision_type_synonyms(synonym: str):
    # DecisionDTO Literal не пускает синонимы напрямую — проверяем логику
    # нормализации на уровне rbac (эндпоинт принимает только канонические типы).
    from app.security.rbac import can_create_decision

    assert can_create_decision("production_head", synonym)
    assert can_create_decision("hr_head", "repair") is False
    assert can_create_decision("finance_head", "reglament")


# ── Доп.: department_head без dept → production (default) ────────────
def test_department_head_default_dept_is_production():
    headers = get_auth_headers("department_head")  # без X-Demo-Dept
    data = kpi_ids(headers)
    assert "production" in data["domains"]
    assert "finance" not in data["domains"]


# ── Доп.: DEFAULT_ROLE соответствует фолбэку ──────────────────────────
def test_default_role_constant():
    assert DEFAULT_ROLE == "director"


# ── Кейсы 10/11 задачи (аудит) — реализованы в T9d ─────────────────────
# GET /api/security/audit: director 200 / production_head 403.
@pytest.mark.parametrize(
    "role,expected",
    [("director", 200), ("production_head", 403)],
)
def test_audit_endpoint_rbac(role: str, expected: int):
    resp = client.get("/api/security/audit", headers=get_auth_headers(role))
    assert resp.status_code == expected


# ── T9h: /api/snapshot не отдаёт финансы production_head ──────────────
def _snapshot_nodes(headers: dict[str, str]) -> dict[str, dict]:
    resp = client.get("/api/snapshot", headers=headers)
    assert resp.status_code == 200
    return {node["id"]: node for node in resp.json()["nodes"]}


def test_snapshot_hides_finance_for_production_head():
    nodes = _snapshot_nodes(get_auth_headers("production_head", "production"))
    fin = nodes["fin_loss_day"]
    assert fin["value"] is None
    assert fin["status"] == "hidden"


def test_snapshot_keeps_finance_for_director():
    nodes = _snapshot_nodes(get_auth_headers("director"))
    fin = nodes["fin_loss_day"]
    assert isinstance(fin["value"], (int, float))
    assert fin["status"] != "hidden"


def test_snapshot_structure_identical_across_roles():
    director = client.get("/api/snapshot", headers=get_auth_headers("director")).json()
    prod = client.get(
        "/api/snapshot", headers=get_auth_headers("production_head", "production")
    ).json()
    assert len(director["nodes"]) == len(prod["nodes"])
    assert len(director["edges"]) == len(prod["edges"])
