"""Генератор фактов «Фотопринт·Контроль» (§5.5–5.6 Readme.md).

Команда:
    uv run python -m app.data.seed --out data

Создаёт `<out>/facts.json`: события по дням за «плохую неделю» 45
(2026-11-02 … 2026-11-08) плюс немного фоновых фактов. Вывод строго
детерминирован (`random.seed(42)`) — файл пересоздаётся байт-в-байт.

Факты — это не граф, а «доказательство для графиков» и сверка с нормами.
Сценарии (main/neg/peak) накладываются поверх отдельно (app/data/scenarios).
"""

from __future__ import annotations

import argparse
import json
import random
from datetime import date, timedelta
from pathlib import Path

# Окно фактов (§5.2)
PERIOD_FROM = date(2026, 1, 5)
PERIOD_TO = date(2026, 11, 8)

# «Плохая неделя» 45: as_of=2026-11-02 (Monday)
WEEK45_START = date(2026, 11, 2)
WEEK45_COEFF = 1.4
BAD_DAY = date(2026, 11, 2)

# Фоновые дни (неделя 44)
BACKGROUND_DAY = date(2026, 10, 26)


def _noise(rng: random.Random, pct: float) -> float:
    """Относительный шум в диапазоне ±pct (доля, например 0.08)."""
    return 1.0 + rng.uniform(-pct, pct)


def _fact(ts: date, domain: str, metric: str, value: float, dims: dict | None = None) -> dict:
    return {
        "ts": ts.isoformat(),
        "domain": domain,
        "metric": metric,
        "value": value,
        "dims": dims or {},
    }


def generate(rng: random.Random) -> list[dict]:
    """Возвращает детерминированный список фактов (~50 записей)."""
    facts: list[dict] = []
    c = WEEK45_COEFF

    # --- Неделя 45: ежедневные факты (6 метрик × 7 дней = 42) ---
    for offset in range(7):
        day = WEEK45_START + timedelta(days=offset)

        if day == BAD_DAY:
            # Анкорный снимок «плохой недели» (§8.1)
            facts.append(_fact(day, "production", "downtime_line2_h", 14.0, {"line": "L2", "shift": 3}))
            facts.append(_fact(day, "quality", "defect_rate", 9.0, {}))
            facts.append(_fact(day, "finance", "margin", 32.0, {}))
            facts.append(_fact(day, "clients", "orders_received", round(120 * c), {}))
            facts.append(_fact(day, "clients", "orders_delivered", round(115 * c), {}))
            facts.append(_fact(day, "finance", "revenue", round(6200 * c), {}))
            continue

        facts.append(_fact(day, "production", "downtime_line2_h",
                           round(9 + (c - 1) * 10 + rng.uniform(-1.5, 1.5), 1),
                           {"line": "L2", "shift": 3}))
        facts.append(_fact(day, "quality", "defect_rate",
                           round(4.5 + (c - 1) * 3 + rng.uniform(-0.6, 0.6), 2), {}))
        facts.append(_fact(day, "finance", "margin",
                           round(36 - 14 * 0.25 - 9 * 0.8 + rng.uniform(-0.8, 0.8), 2), {}))
        facts.append(_fact(day, "clients", "orders_received",
                           round(120 * c * _noise(rng, 0.08)), {}))
        facts.append(_fact(day, "clients", "orders_delivered",
                           round(115 * c * _noise(rng, 0.05)), {}))
        facts.append(_fact(day, "finance", "revenue",
                           round(6200 * c * _noise(rng, 0.04)), {}))

    # --- Анкорные факты 2026-11-02, дополняющие профиль недели 45 (+5) ---
    facts.append(_fact(BAD_DAY, "hr", "operators_on_shift", 4, {"shift": 3}))
    facts.append(_fact(BAD_DAY, "clients", "sla_breach", 23, {}))
    facts.append(_fact(BAD_DAY, "production", "reprint_volume", 9, {}))
    facts.append(_fact(BAD_DAY, "finance", "revenue_week", 41200, {}))
    facts.append(_fact(BAD_DAY, "production", "downtime_line2_h", 14.0, {"line": "L2", "shift": 3, "note": "anchor"}))

    # --- Фон: неделя 44 (неделя «до»), 3 метрики (+3) ---
    facts.append(_fact(BACKGROUND_DAY, "clients", "orders_received", round(120 * 1.3), {}))
    facts.append(_fact(BACKGROUND_DAY, "clients", "orders_delivered", round(115 * 1.3), {}))
    facts.append(_fact(BACKGROUND_DAY, "finance", "revenue", round(6200 * 1.3), {}))

    return facts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Генератор facts.json (детерминированный)")
    parser.add_argument(
        "--out",
        default=str(Path(__file__).resolve().parents[2] / "data"),
        help="Каталог для facts.json (по умолчанию backend/data)",
    )
    args = parser.parse_args(argv)

    out_dir = Path(args.out)
    if not out_dir.is_absolute():
        out_dir = Path.cwd() / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    rng = random.Random(42)
    payload = {
        "period": {
            "from": PERIOD_FROM.isoformat(),
            "to": PERIOD_TO.isoformat(),
            "granularity": "day",
        },
        "facts": generate(rng),
    }

    out_file = out_dir / "facts.json"
    out_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"facts.json: {len(payload['facts'])} записей -> {out_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
