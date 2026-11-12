"""AI-интерпретация через DeepSeek (Klinch Cloud) с кэшем, валидатором и фолбэком.

Поток:
    ctx  -> sha256(json(ctx, sort_keys)) -> data/ai_cache.json
    промах кэша + offline/AI_ENABLED=false -> fallback «source=fallback»
    онлайн -> OpenAI-совместимый API (DeepSeek, temperature=0, response_format=json_object)
           -> validate(raw, ctx): числа/сущности вне CONTEXT -> fallback + reason
           -> успех: «source=deepseek», ответ дописывается в кэш

Демо никогда не блокируется: любая ошибка сети/парсинга даёт fallback.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any

from openai import AsyncOpenAI

from app.config import settings
from app.schemas import AiDTO
from app.security.audit import log_call
from app.security.masking import mask
from app.security.sanitize import sanitize_ticket

# --- Пути и константы ---------------------------------------------------

_DEFAULT_CACHE_PATH = Path(__file__).resolve().parents[2] / "data" / "ai_cache.json"
CACHE_PATH = Path(os.environ.get("FOTOPRINT_AI_CACHE", _DEFAULT_CACHE_PATH))

TIMEOUT_S = 5.0

# Промпты §11.3 Readme.md
SYSTEM_PROMPT = (
    "Ты ассистент управленческой аналитики.\n"
    "Используй ТОЛЬКО факты CONTEXT. Числа и названия сущностей — дословно из CONTEXT.\n"
    "Ответ — строго JSON-объект. Русский язык."
)

_CTX_PASSTHROUGH = ("scene", "node_id", "chain", "delta", "cost_per_day")


# --- Кэш ----------------------------------------------------------------

def cache_key(ctx: dict[str, Any]) -> str:
    payload = json.dumps(ctx, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def load_cache() -> dict[str, Any]:
    try:
        raw = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}
    return raw if isinstance(raw, dict) else {}


def _save_cache(cache: dict[str, Any]) -> None:
    try:
        CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        pass


# --- Валидатор ----------------------------------------------------------

_NUMBER_RE = re.compile(r"\d+(?:[ \u00a0]\d{3})*(?:[.,]\d+)?")
_IDENT_RE = re.compile(r"[A-Za-zа-яА-ЯёЁ_][A-Za-zа-яА-ЯёЁ0-9_]*")

_ALLOWED_WORDS = frozenset({
    "fallback", "byn", "context", "json", "и", "или", "но", "а", "да", "не", "бы", "что", "как",
    "в", "на", "по", "с", "к", "за", "от", "до", "из", "о", "об", "под", "над", "при", "без",
    "через", "между", "у", "во", "со", "для", "про", "имеет", "маржу", "потери", "показатели",
    "узла", "узел", "узлы", "узлов", "узле", "узлах", "узлу",
    "руб", "сут", "день", "дня", "дне", "дни", "дней", "месяц", "месяца", "маржа", "маржинальность",
    "выручка", "простой", "простоя", "дефект", "дефектов", "оператор", "оператора", "операторы",
    "операторов", "смена", "смены", "смену", "смен", "линия", "линии", "линию", "линие", "линий",
    "решение", "решения", "рекомендация", "рекомендации", "причина", "причины", "причин",
    "ущерб", "ущерба", "потери", "потеря", "дать", "привести", "снизить", "увеличить", "устранить",
    "рекомендуется", "необходимо", "следует", "можно", "нанять", "заменить", "обновить", "проверить",
    "проверять", "проблема", "проблемы", "составляет", "равна", "равен", "примерно", "около",
    "динамика", "показатель", "уровень", "процент", "процентов",
    "клиент", "клиента", "клиенту", "клиентом", "клиенты", "клиентов",
    "forecast", "simulate", "main", "neg", "hr_operators_s3", "fin_margin", "имеет", "снизить",
})


def _numbers_in(text: str) -> set[str]:
    found: set[str] = set()
    for raw in _NUMBER_RE.findall(text):
        norm = raw.replace(" ", "").replace("\u00a0", "").replace(",", ".")
        norm = norm.rstrip(".")
        if not norm: continue
        if "." in norm:
            try:
                norm = str(int(float(norm))) if float(norm).is_integer() else repr(float(norm))
            except ValueError: continue
        else: norm = str(int(norm))
        found.add(norm)
    return found


def _numbers_in_object(obj: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(obj, bool): return found
    if isinstance(obj, (int, float)):
        found.add(str(int(obj)) if float(obj).is_integer() else repr(float(obj)))
    elif isinstance(obj, str): found |= _numbers_in(obj)
    elif isinstance(obj, dict):
        for k, v in obj.items(): found |= _numbers_in(str(k)) | _numbers_in_object(v)
    elif isinstance(obj, (list, tuple)):
        for v in obj: found |= _numbers_in_object(v)
    return found


def _words_in_object(obj: Any) -> set[str]:
    words: set[str] = set()
    if isinstance(obj, str): words |= {w.lower() for w in _IDENT_RE.findall(obj)}
    elif isinstance(obj, dict):
        for k, v in obj.items(): words |= _words_in_object(str(k)) | _words_in_object(v)
    elif isinstance(obj, (list, tuple)):
        for v in obj: words |= _words_in_object(v)
    return words


_TOKEN_V2_RE = re.compile(r"\[[A-Z][A-Z0-9_]*_[0-9]+\]")


def validate(
    raw: dict[str, Any],
    ctx: dict[str, Any],
    vault: dict[str, str] | None = None,
) -> tuple[bool, str | None]:
    if not isinstance(raw, dict):
        return False, "Ответ не JSON"
    for field in ("interpretation", "root_cause", "recommended_action"):
        if not raw.get(field):
            return False, f"Нет поля {field}"

    text = " ".join(
        str(raw[field]) for field in ("interpretation", "root_cause", "recommended_action")
    )
    tokens = _TOKEN_V2_RE.findall(text)
    if vault is not None:
        for token in tokens:
            if token not in vault:
                return False, f"Токен {token} отсутствует в vault"

    text = _TOKEN_V2_RE.sub(" ", text)
    context_numbers = _numbers_in_object(ctx)
    context_words = _words_in_object(ctx)
    if vault:
        for value in vault.values():
            context_numbers |= _numbers_in_object(value)
            context_words |= _words_in_object(value)

    for number in _numbers_in(text) - context_numbers:
        return False, f"Число {number} отсутствует в контексте"
    for word in _IDENT_RE.findall(text):
        if word.lower() not in (context_words | _ALLOWED_WORDS) and not word.isdigit():
            return False, f"Сущность {word} отсутствует в контексте"
    return True, None


# --- Фолбэк -------------------------------------------------------------

def fallback(ctx: dict[str, Any], reason: str | None = None) -> AiDTO:
    node_id = str(ctx.get("node_id", "unknown"))
    cost = ctx.get("cost_per_day", 0) or 0
    text = f"Узел {node_id} даёт ущерб ≈ {float(cost):,.0f} BYN/сут. Рекомендуется устранить причину."
    if reason: text += f" (фолбэк: {reason})"
    
    # Build complete data with all required fields
    data = {
        "scene": ctx.get("scene", "main"),
        "node_id": node_id,
        "chain": ctx.get("chain", []),
        "delta": ctx.get("delta", {}),
        "cost_per_day": cost,
        "interpretation": text,
    }
    return AiDTO(**data, source="fallback", cache_hit=False)


# --- API вызов ----------------------------------------------------------

async def interpret(ctx: dict[str, Any]) -> AiDTO:
    # T9f: конвейер pre-LLM — санитизация текста тикета, маскирование, кэш по masked_ctx
    clean_ctx = dict(ctx)
    ticket_text = clean_ctx.get("text") or clean_ctx.get("ticket_text")
    if isinstance(ticket_text, str) and ticket_text.strip():
        sanitized = sanitize_ticket(ticket_text)
        clean_ctx["clean_summary"] = sanitized["clean_summary"]
        clean_ctx["tags"] = sanitized["tags"]
    clean_ctx.pop("text", None)
    clean_ctx.pop("ticket_text", None)

    masked_ctx, vault = mask(clean_ctx, level=settings.mask_level)
    raw_payload_json = json.dumps(ctx, sort_keys=True, ensure_ascii=False, default=str)
    raw_sha256 = hashlib.sha256(raw_payload_json.encode("utf-8")).hexdigest()
    masked_payload_json = json.dumps(
        masked_ctx, sort_keys=True, ensure_ascii=False, default=str
    )

    key = cache_key(masked_ctx)
    cached = load_cache().get(key)
    if isinstance(cached, dict):
        data = {
            "scene": ctx.get("scene", "main"),
            "node_id": ctx.get("node_id", "unknown"),
            "chain": ctx.get("chain", []),
            "delta": ctx.get("delta", {}),
            "cost_per_day": ctx.get("cost_per_day", 0.0),
            "interpretation": cached["interpretation"],
        }
        return AiDTO(**data, source="cache", cache_hit=True)

    if not settings.ai_enabled or settings.offline_mode:
        log_call(
            backend=settings.llm_backend,
            mask_level=settings.mask_level,
            tokens_count=len(vault),
            payload_masked_json=masked_payload_json,
            payload_sha256=raw_sha256,
            verdict="rejected",
            reason="offline",
        )
        return fallback(ctx, "offline")

    try:
        client = AsyncOpenAI(api_key=settings.klinch_api_key, base_url=settings.deepseek_base_url, timeout=TIMEOUT_S)
        resp = await client.chat.completions.create(
            model=settings.deepseek_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                # T9f: в сеть уходит только замаскированный контекст
                {"role": "user", "content": f"CONTEXT = {json.dumps(masked_ctx, ensure_ascii=False)}"}
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )
        raw = json.loads(resp.choices[0].message.content)
    except Exception as exc:
        reason = f"DeepSeek ошибка: {type(exc).__name__}"
        log_call(
            backend=settings.llm_backend,
            mask_level=settings.mask_level,
            tokens_count=len(vault),
            payload_masked_json=masked_payload_json,
            payload_sha256=raw_sha256,
            verdict="rejected",
            reason=reason,
        )
        return fallback(ctx, reason)

    ok, reason = validate(raw, masked_ctx, vault)
    if not ok:
        log_call(
            backend=settings.llm_backend,
            mask_level=settings.mask_level,
            tokens_count=len(vault),
            payload_masked_json=masked_payload_json,
            payload_sha256=raw_sha256,
            verdict="rejected",
            reason=reason,
        )
        return fallback(ctx, reason)

    log_call(
        backend=settings.llm_backend,
        mask_level=settings.mask_level,
        tokens_count=len(vault),
        payload_masked_json=masked_payload_json,
        payload_sha256=raw_sha256,
        verdict="ok",
        reason=None,
    )

    cache = load_cache()
    cache[key] = raw
    _save_cache(cache)

    data = {
        "scene": ctx.get("scene", "main"),
        "node_id": ctx.get("node_id", "unknown"),
        "chain": ctx.get("chain", []),
        "delta": ctx.get("delta", {}),
        "cost_per_day": ctx.get("cost_per_day", 0.0),
        "interpretation": raw["interpretation"],
    }
    return AiDTO(**data, source="deepseek", cache_hit=False)
