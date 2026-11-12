"""Тесты T9d: аудит ИИ-вызовов (PLAN-V2 §6.5)."""

import json
import hashlib
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.security.audit import log_call, list_last
from app.schemas import AuditDTO


client = TestClient(app)


def test_log_call_basic() -> None:
    """Базовая запись: log_call → запись в БД, list_last возвращает её."""
    payload = {"prompt": "Test prompt", "context": "some context"}
    payload_json = json.dumps(payload, ensure_ascii=False)
    sha = hashlib.sha256(payload_json.encode("utf-8")).hexdigest()

    log_call(
        backend="deepseek",
        mask_level="full",
        tokens_count=123,
        payload_masked_json=payload_json,
        payload_sha256=sha,
        verdict="allow",
        reason=None,
    )

    audits = list_last(1)
    assert len(audits) == 1
    audit = audits[0]
    assert audit.backend == "deepseek"
    assert audit.mask_level == "full"
    assert audit.tokens_count == 123
    assert audit.payload_sha256 == sha
    assert audit.verdict == "allow"
    assert audit.reason is None


def test_log_call_with_reason() -> None:
    """Запись с reason (deny)."""
    payload = {"prompt": "Inject me"}
    payload_json = json.dumps(payload)
    sha = hashlib.sha256(payload_json.encode()).hexdigest()

    log_call(
        backend="deepseek",
        mask_level="full",
        tokens_count=50,
        payload_masked_json=payload_json,
        payload_sha256=sha,
        verdict="deny",
        reason="injection detected",
    )

    audits = list_last(1)
    assert audits[0].verdict == "deny"
    assert audits[0].reason == "injection detected"


def test_list_last_order() -> None:
    """Порядок: новые сверху (DESC по id)."""
    for i in range(5):
        payload = {"idx": i}
        payload_json = json.dumps(payload)
        sha = hashlib.sha256(payload_json.encode()).hexdigest()
        log_call(
            backend="test",
            mask_level="none",
            tokens_count=i,
            payload_masked_json=payload_json,
            payload_sha256=sha,
            verdict="allow",
            reason=None,
        )

    audits = list_last(5)
    assert len(audits) == 5
    # Проверяем, что возвращается в порядке убывания (новые — первыми)
    assert audits[0].tokens_count == 4
    assert audits[-1].tokens_count == 0


def test_list_last_limit() -> None:
    """Ограничение last: если просим 3, возвращается 3."""
    for i in range(10):
        payload = {"idx": i}
        payload_json = json.dumps(payload)
        sha = hashlib.sha256(payload_json.encode()).hexdigest()
        log_call(
            backend="test",
            mask_level="none",
            tokens_count=i,
            payload_masked_json=payload_json,
            payload_sha256=sha,
            verdict="allow",
            reason=None,
        )

    audits = list_last(3)
    assert len(audits) == 3


def test_audit_dto_schema() -> None:
    """AuditDTO валидируется корректно."""
    audit = AuditDTO(
        id=1,
        ts=datetime.now(timezone.utc).isoformat(),
        backend="test",
        mask_level="full",
        tokens_count=100,
        payload_masked_json='{"a": 1}',
        payload_sha256="abc123",
        verdict="allow",
        reason=None,
    )
    assert audit.verdict == "allow"
    # payload_masked_json — строка JSON, не распарсенный dict
    assert isinstance(audit.payload_masked_json, str)


def test_log_call_persists_across_calls() -> None:
    """Несколько вызовов log_call накапливаются в БД."""
    for i in range(3):
        payload = {"call": i}
        payload_json = json.dumps(payload)
        sha = hashlib.sha256(payload_json.encode()).hexdigest()
        log_call(
            backend="persist",
            mask_level="partial",
            tokens_count=10 * i,
            payload_masked_json=payload_json,
            payload_sha256=sha,
            verdict="allow",
            reason=None,
        )

    audits = list_last(10)
    # Должно быть как минимум 3 новые + что было до этого
    persist_audits = [a for a in audits if a.backend == "persist"]
    assert len(persist_audits) >= 3


# --- RBAC tests for /api/security/audit ---

def test_audit_endpoint_requires_director_role() -> None:
    """Эндпоинт /api/security/audit требует роль director (403 для других)."""
    # Без заголовка — фолбэк director → 200
    resp = client.get("/api/security/audit?last=5")
    assert resp.status_code == 200

    # production_head → 403
    resp = client.get("/api/security/audit?last=5", headers={"X-Demo-Role": "production_head"})
    assert resp.status_code == 403

    # finance_head → 403
    resp = client.get("/api/security/audit?last=5", headers={"X-Demo-Role": "finance_head"})
    assert resp.status_code == 403

    # specialist → 403
    resp = client.get("/api/security/audit?last=5", headers={"X-Demo-Role": "specialist"})
    assert resp.status_code == 403


def test_audit_endpoint_director_ok() -> None:
    """Director получает 200 и список."""
    resp = client.get("/api/security/audit?last=5", headers={"X-Demo-Role": "director"})
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    # Проверяем структуру элементов
    if data:
        item = data[0]
        assert "id" in item
        assert "ts" in item
        assert "backend" in item
        assert "mask_level" in item
        assert "tokens_count" in item
        assert "payload_masked_json" in item
        assert "payload_sha256" in item
        assert "verdict" in item
        assert "reason" in item


def test_audit_endpoint_last_param() -> None:
    """Параметр last работает."""
    resp = client.get("/api/security/audit?last=2", headers={"X-Demo-Role": "director"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) <= 2


def test_audit_endpoint_last_clamped() -> None:
    """last > 100 обрезается до 100."""
    resp = client.get("/api/security/audit?last=200", headers={"X-Demo-Role": "director"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) <= 100


def test_audit_endpoint_invalid_last() -> None:
    """last <= 0 возвращает пустой список."""
    resp = client.get("/api/security/audit?last=0", headers={"X-Demo-Role": "director"})
    assert resp.status_code == 200
    assert resp.json() == []

    resp = client.get("/api/security/audit?last=-5", headers={"X-Demo-Role": "director"})
    assert resp.status_code == 200
    assert resp.json() == []