"""Тесты настроек T9e (PLAN-V2 §6.6, ADR-0005).

Проверяем дефолты новых полей LLM_BACKEND / OLLAMA / MASK_LEVEL / GATEWAY_SECRET
и их переопределение переменными окружения.
"""

from app.config import Settings


def test_defaults() -> None:
    """Дефолты: klinch-бэкенд, локальный Ollama, strict-маскировка."""
    s = Settings()
    assert s.llm_backend == "klinch"
    assert s.ollama_base_url == "http://localhost:11434/v1"
    assert s.ollama_model == "qwen2.5:7b"
    assert s.mask_level == "strict"
    assert s.gateway_secret == "demo-secret"


def test_env_override(monkeypatch) -> None:
    """Env-переменные переопределяют поля при перезагрузке Settings."""
    monkeypatch.setenv("LLM_BACKEND", "ollama")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://127.0.0.1:9999/v1")
    monkeypatch.setenv("OLLAMA_MODEL", "llama3:8b")
    monkeypatch.setenv("MASK_LEVEL", "standard")
    s = Settings()
    assert s.llm_backend == "ollama"
    assert s.ollama_base_url == "http://127.0.0.1:9999/v1"
    assert s.ollama_model == "llama3:8b"
    assert s.mask_level == "standard"


def test_gateway_secret_override(monkeypatch) -> None:
    """GATEWAY_SECRET: дефолт demo-secret, переопределяется env."""
    assert Settings().gateway_secret == "demo-secret"
    monkeypatch.setenv("GATEWAY_SECRET", "super-secret")
    assert Settings().gateway_secret == "super-secret"


def test_llm_backend_enum(monkeypatch) -> None:
    """Недопустимый LLM_BACKEND отклоняется валидацией pydantic."""
    import pytest
    from pydantic import ValidationError

    monkeypatch.setenv("LLM_BACKEND", "yandex")
    with pytest.raises(ValidationError):
        Settings()


def test_default_mask_level_reads_settings() -> None:
    """_default_mask_level возвращает значение из settings (фолбэк — strict)."""
    from app.security.audit import _default_mask_level

    assert _default_mask_level() == settings_mask_level()


def settings_mask_level() -> str:
    from app.config import settings

    return settings.mask_level
