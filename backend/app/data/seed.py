"""Генератор фактов «Фотопринт·Контроль» (§5.5–5.6 Readme.md).

Команда:
    uv run python -m app.data.seed --out data

Создаёт `<out>/facts.json`: события по дням за «плохую неделю» 45
(2026-11-02 … 2026-11-08) плюс немного фоновых фактов. Вывод строго
детерминирован (`random.seed(42)`) — файл пересоздаётся байт-в-байт.

Факты — это не граф, а «доказательство для графиков» и сверка с нормами.
Сценарии (main/neg/peak) накладываются поверх отдельно (app/data/scenarios).

Также создаёт:
- `<out>/norms.json` — нормы метрик (§5.4), включая unit_econ_margin для юнит-экономики
- `<out>/unit_economics.json` — 5 строк таблицы §7.8
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


def generate_norms() -> list[dict]:
    """Нормы метрик (§5.4) + норма для юнит-экономики (§7.8).
    
    Возвращает 9 записей: 8 базовых + unit_econ_margin.
    """
    return [
        {"metric": "fin_margin", "domain": "finance", "min": 35, "max": 40, "unit": "%", "warn": 33},
        {"metric": "prod_downtime_l2", "domain": "production", "min": 0, "max": 4, "unit": "ч/сут"},
        {"metric": "quality_defect_rate", "domain": "quality", "min": 2, "max": 5, "unit": "%"},
        {"metric": "sales_sla_breach", "domain": "clients", "min": 0, "max": 5, "unit": "зак/сут"},
        {"metric": "hr_operators_s3", "domain": "hr", "min": 6, "max": 7, "unit": "чел"},
        {"metric": "hr_overtime_s3", "domain": "hr", "min": 0, "max": 6, "unit": "ч/сут"},
        {"metric": "prod_reprint_volume", "domain": "production", "min": 0, "max": 3, "unit": "тираж/сут"},
        {"metric": "sales_churn_risk_b2b7", "domain": "clients", "min": 0, "max": 20, "unit": "% (риск)"},
        # Норма для юнит-экономики (§7.8): маржа должна быть 15–45%
        {"metric": "unit_econ_margin", "domain": "finance", "min": 15, "max": 45, "unit": "%", "warn": 20},
    ]


def generate_unit_economics() -> list[dict]:
    """5 строк таблицы юнит-экономики §7.8 Readme.md.
    
    SKU/Клиент, Цена, Бумага, Печать, Переплёт, Труд, Брак, Маржа %.
    Все числа — точно из таблицы §7.8.
    """
    return [
        {
            "sku": "Фотокнига 20×20 стандарт",
            "price": 92.0,
            "paper": 21.0,
            "printing": 12.0,
            "binding": 18.0,
            "labor": 15.0,
            "defect": 2.0,
            "margin_pct": 28.3,
        },
        {
            "sku": "Фотокнига 30×30 премиум",
            "price": 210.0,
            "paper": 48.0,
            "printing": 22.0,
            "binding": 34.0,
            "labor": 28.0,
            "defect": 4.0,
            "margin_pct": 35.2,
        },
        {
            "sku": "B2B фотостудия «Луч»",
            "price": 180.0,
            "paper": 40.0,
            "printing": 20.0,
            "binding": 30.0,
            "labor": 24.0,
            "defect": 3.0,
            "margin_pct": 35.6,
        },
        {
            "sku": "B2B маркетплейс «Книга»",
            "price": 150.0,
            "paper": 36.0,
            "printing": 16.0,
            "binding": 24.0,
            "labor": 20.0,
            "defect": 2.0,
            "margin_pct": 34.7,
        },
        {
            "sku": "Клиент №7",
            "price": 140.0,
            "paper": 30.0,
            "printing": 18.0,
            "binding": 22.0,
            "labor": 25.0,
            "defect": 48.0,
            "margin_pct": -1.9,
        },
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Генератор facts.json, norms.json, unit_economics.json (детерминированный)")
    parser.add_argument(
        "--out",
        default=str(Path(__file__).resolve().parents[2] / "data"),
        help="Каталог для выходных файлов (по умолчанию backend/data)",
    )
    args = parser.parse_args(argv)

    out_dir = Path(args.out)
    if not out_dir.is_absolute():
        out_dir = Path.cwd() / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    rng = random.Random(42)

    # 1. facts.json
    payload_facts = {
        "period": {
            "from": PERIOD_FROM.isoformat(),
            "to": PERIOD_TO.isoformat(),
            "granularity": "day",
        },
        "facts": generate(rng),
    }
    out_facts = out_dir / "facts.json"
    out_facts.write_text(json.dumps(payload_facts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"facts.json: {len(payload_facts['facts'])} записей -> {out_facts}")

    # 2. norms.json
    norms = generate_norms()
    out_norms = out_dir / "norms.json"
    out_norms.write_text(json.dumps(norms, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"norms.json: {len(norms)} записей -> {out_norms}")

    # 3. unit_economics.json
    unit_econ = generate_unit_economics()
    out_unit_econ = out_dir / "unit_economics.json"
    out_unit_econ.write_text(json.dumps(unit_econ, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"unit_economics.json: {len(unit_econ)} записей -> {out_unit_econ}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())