"""Интеграционные тесты для API и внешних систем.

Проверяет связку: API -> DB -> Telegram/Jira/PDF.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.report.pdf import generate_executive_summary
import os

client = TestClient(app)

def test_create_decision():
    """Тест создания решения через API."""
    payload = {
        "scenario_id": "main",
        "type": "hire",
        "params": {"operators": 2},
        "owner": "test_user",
        "due_date": "2026-11-20",
        "verdict": "pending"
    }
    response = client.post("/api/decisions", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["jira_key"].startswith("PROD-")
    assert data["owner"] == "test_user"

def test_list_decisions():
    """Тест получения списка решений."""
    response = client.get("/api/decisions")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_pdf_gen():
    """Тест генерации PDF-отчёта."""
    pdf_bytes = generate_executive_summary("main")
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF-")

def test_health():
    """Простой хелсчек."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
