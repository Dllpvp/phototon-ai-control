"""Prefill AI-кэша по masked-ключам (T9f).

Ключ кэша в interpret() вычисляется по masked-контексту
(sha256(json(masked_ctx, sort_keys))). Offline-ветка interpret() кэш не
пишет (по требованию test_offline_does_not_write_cache), поэтому prefill
повторяет деривацию один-в-один: clean_ctx -> mask(settings.mask_level)
-> cache_key, и кладёт готовые валидные ответы LLM.

Каждая запись проходит ai.validate(raw, masked_ctx, vault) перед записью —
в кэш не попадает текст с чужими числами или сущностями.

Запуск: cd backend; uv run python -m scripts.prefill_cache
"""

from __future__ import annotations

import asyncio

from app.config import settings
from app.integrations import ai_provider
from app.security.masking import mask

SCENES: list[tuple[dict, dict]] = [
    (
        {"scene": "chain", "node_id": "fin_margin"},
        {
            "interpretation": "Узел fin_margin имеет маржу.",
            "root_cause": "маржа",
            "recommended_action": "проверить маржу",
        },
    ),
    (
        {"scene": "whatif", "node_id": "hr_operators_s3", "value": 6},
        {
            "interpretation": "Узел hr_operators_s3 имеет маржу.",
            "root_cause": "маржа",
            "recommended_action": "нанять операторов",
        },
    ),
    (
        {"scene": "forecast"},
        {
            "interpretation": "Forecast: показатели маржа динамика.",
            "root_cause": "маржа",
            "recommended_action": "проверить маржу",
        },
    ),
    (
        {"scene": "simulate", "branch": "main"},
        {
            "interpretation": "Simulate main: решение снизить потери.",
            "root_cause": "потери",
            "recommended_action": "проверить маржу",
        },
    ),
    (
        {"scene": "simulate", "branch": "neg"},
        {
            "interpretation": "Simulate neg: проблема операторов.",
            "root_cause": "проблема операторов",
            "recommended_action": "проверить операторов",
        },
    ),
]


def _derive_key(ctx: dict) -> tuple[str, dict, dict]:
    """Повторяет pre-LLM деривацию interpret() один-в-один."""
    clean_ctx = dict(ctx)
    clean_ctx.pop("text", None)
    clean_ctx.pop("ticket_text", None)
    masked_ctx, vault = mask(clean_ctx, level=settings.mask_level)
    return ai_provider.cache_key(masked_ctx), masked_ctx, vault


def main() -> None:
    cache = ai_provider.load_cache()
    for ctx, raw in SCENES:
        key, masked_ctx, vault = _derive_key(ctx)
        ok, reason = ai_provider.validate(raw, masked_ctx, vault)
        if not ok:
            raise SystemExit(f"Ответ сцены {ctx!r} не прошёл валидатор: {reason}")
        cache[key] = raw
    ai_provider._save_cache(cache)

    # Самопроверка: interpret() должен брать записи из кэша, без сети.
    settings.offline_mode = True
    for ctx, _ in SCENES:
        dto = asyncio.run(ai_provider.interpret(ctx))
        if dto.source != "cache":
            raise SystemExit(
                f"Ключи не совпали для {ctx!r}: interpret() вернул source={dto.source}"
            )

    print(f"Кэш: {len(cache)} записей")


if __name__ == "__main__":
    main()
