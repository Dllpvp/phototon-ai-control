"""Тесты AI-гарда: кэш, валидатор, фолбэк, вызов DeepSeek (Klinch Cloud).

Сеть не используется: offline_mode=True по умолчанию, а онлйн-ветка
проверяется через подмену `openai.AsyncOpenAI` фейком.
"""

from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from app.integrations import ai_provider as ai


CTX = {"margin": 32, "cost": 1840}


# --- Валидатор ----------------------------------------------------------


def test_foreign_number_rejected():
    """§15.2: число вне CONTEXT → (False, reason) с проблемным токеном."""
    raw = {
        "interpretation": "маржа 99%",
        "root_cause": "x",
        "recommended_action": "y",
    }
    ok, reason = ai.validate(raw, CTX)
    assert ok is False
    assert reason is not None
    assert "99" in reason


def test_valid_raw_accepted():
    raw = {
        "interpretation": "Маржа 32%, ущерб 1840 BYN/сут.",
        "root_cause": "Простой линии",
        "recommended_action": "Рекомендуется проверить смены операторов",
    }
    ok, reason = ai.validate(raw, CTX)
    assert ok is True, reason


def test_missing_field_rejected():
    ok, reason = ai.validate({"interpretation": "ok"}, CTX)
    assert ok is False
    assert "root_cause" in (reason or "")


def test_foreign_word_rejected():
    raw = {
        "interpretation": "Проблема в узле конкурентоспособность",
        "root_cause": "x",
        "recommended_action": "y",
    }
    ok, reason = ai.validate(raw, CTX)
    assert ok is False
    assert "конкурентоспособность" in (reason or "")


# --- Кэш ----------------------------------------------------------------


def test_cache_key_is_stable():
    assert ai.cache_key(CTX) == ai.cache_key(dict(reversed(list(CTX.items()))))
    assert ai.cache_key(CTX) != ai.cache_key({"margin": 33, "cost": 1840})


# --- Фолбэк -------------------------------------------------------------


@pytest.mark.asyncio
async def test_provider_offline_returns_fallback_without_network(monkeypatch, tmp_path):
    monkeypatch.setattr(ai, "CACHE_PATH", tmp_path / "ai_cache.json")
    monkeypatch.setattr(ai.settings, "offline_mode", True)

    def boom(*args, **kwargs):
        raise AssertionError("Сеть в offline-режиме запрещена")

    monkeypatch.setattr(ai, "AsyncOpenAI", boom)

    dto = await ai.interpret({"scene": "main", "node_id": "hr_operators_s3", "cost_per_day": 1840})
    assert dto.source == "fallback"
    assert dto.cache_hit is False
    assert "фолбэк" in dto.interpretation


@pytest.mark.asyncio
async def test_offline_does_not_write_cache(monkeypatch, tmp_path):
    cache_file = tmp_path / "ai_cache.json"
    monkeypatch.setattr(ai, "CACHE_PATH", cache_file)
    await ai.interpret({"node_id": "hr_operators_s3", "cost_per_day": 1840})
    assert not cache_file.exists()


# --- Онлйн-ветка --------------------------------------------------------


class _FakeCompletions:
    def __init__(self, content: str | Exception):
        self._content = content

    async def create(self, **kwargs):
        if isinstance(self._content, Exception):
            raise self._content
        message = SimpleNamespace(content=self._content)
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])


def _patch_client(monkeypatch, content: str | Exception):
    """Подменяет AsyncOpenAI фейком, возвращающим заданный контент ответа."""
    seen: dict = {}

    class _FakeClient:
        def __init__(self, *args, **kwargs):
            seen.update(kwargs)
            self.chat = SimpleNamespace(completions=_FakeCompletions(content))

    monkeypatch.setattr(ai, "AsyncOpenAI", _FakeClient)
    return seen


def _enable_online(monkeypatch, tmp_path):
    monkeypatch.setattr(ai, "CACHE_PATH", tmp_path / "ai_cache.json")
    monkeypatch.setattr(ai.settings, "ai_enabled", True)
    monkeypatch.setattr(ai.settings, "offline_mode", False)
    monkeypatch.setattr(ai.settings, "klinch_api_key", "fake-key")


@pytest.mark.asyncio
async def test_online_valid_answer_is_cached_and_replayed(monkeypatch, tmp_path):
    _enable_online(monkeypatch, tmp_path)
    monkeypatch.setattr(ai, "CACHE_PATH", tmp_path / "nested" / "ai_cache.json")

    text = json.dumps(
        {
            "interpretation": "Маржа 32%, ущерб 1840 BYN/сут.",
            "root_cause": "Простой линии",
            "recommended_action": "Проверить смены операторов",
        },
        ensure_ascii=False,
    )
    kwargs = _patch_client(monkeypatch, text)

    ctx = {"scene": "main", "node_id": "hr_operators_s3", "cost_per_day": 1840, "margin": 32}
    first = await ai.interpret(ctx)
    assert first.source == "deepseek"
    assert first.cache_hit is False
    assert kwargs["base_url"] == ai.settings.deepseek_base_url
    assert kwargs["api_key"] == "fake-key"

    cached = json.loads((tmp_path / "nested" / "ai_cache.json").read_text(encoding="utf-8"))
    assert len(cached) == 1

    # Повторный запрос — из кэша, без обращения к API.
    def boom(*args, **kwargs):
        raise AssertionError("Кэш-хит не должен ходить в сеть")

    monkeypatch.setattr(ai, "AsyncOpenAI", boom)
    second = await ai.interpret(ctx)
    assert second.cache_hit is True
    assert second.source == "cache"
    assert second.interpretation == first.interpretation


@pytest.mark.asyncio
async def test_online_timeout_falls_back(monkeypatch, tmp_path):
    _enable_online(monkeypatch, tmp_path)
    _patch_client(monkeypatch, TimeoutError("boom"))

    dto = await ai.interpret({"node_id": "hr_operators_s3", "cost_per_day": 1840})
    assert dto.source == "fallback"
    assert "TimeoutError" in dto.interpretation


@pytest.mark.asyncio
async def test_online_hallucination_falls_back(monkeypatch, tmp_path):
    _enable_online(monkeypatch, tmp_path)

    text = json.dumps(
        {"interpretation": "маржа 99%", "root_cause": "x", "recommended_action": "y"}
    )
    _patch_client(monkeypatch, text)

    dto = await ai.interpret({"margin": 32, "cost": 1840})
    assert dto.source == "fallback"
    assert "99" in dto.interpretation
    assert not (tmp_path / "ai_cache.json").exists()


def test_prompt_matches_spec():
    assert "ТОЛЬКО факты CONTEXT" in ai.SYSTEM_PROMPT
    assert "строго JSON" in ai.SYSTEM_PROMPT
    assert ai.TIMEOUT_S == 5.0