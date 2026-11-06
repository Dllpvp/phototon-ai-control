"""Прогноз пика заказов vs мощность (§7.6 Readme.md).

Формулы строго по §7.6 + уточнениям §2.4:
    base(w)           = BASE_WEEKLY_ORDERS * (1 + TREND_PER_WEEK * (w - 45))
    forecast_orders   = round(base * seasonality_coeff, -1)   # до десятков
    capacity_orders   = 6 * ORDERS_PER_OPERATOR_WEEK           # 6 операторов
    deficit           = capacity_orders - forecast_orders

Константы — из `constants.py`.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.core.anchors import ANCHORS
from app.core.constants import (
    BASE_WEEKLY_ORDERS,
    COST_PER_DOWNTIME_H,
    ORDERS_PER_OPERATOR_WEEK,
    TREND_PER_WEEK,
)
from app.core.loader import SeasonalityWeek, load_seasonality

# Неделя, от которой строится тренд (базовая неделя = 45, «сейчас»)
BASELINE_WEEK = 45

# Количество операторов в смене по умолчанию (для расчёта мощности)
DEFAULT_OPERATORS = 6


@dataclass
class ForecastResult:
    """Результат прогноза на неделю."""

    week: int
    seasonality_coeff: float
    base: float
    forecast_orders: int
    capacity_orders: int
    deficit: int
    downtime_h: float
    loss_day: float


def _seasonality_coeff(week: int, seasonality_data: list[SeasonalityWeek]) -> float:
    """Коэффициент сезонности для недели `week`.

    Ищем запись, где `week_from <= week <= week_to`. Если не найдено —
    берём ближайшую (или 1.0 как фолбэк).
    """
    for rec in seasonality_data:
        if rec.week <= week <= rec.week_to:
            return rec.coeff
    # Фолбэк: ближайшая нижняя граница
    best: SeasonalityWeek | None = None
    for rec in seasonality_data:
        if rec.week <= week and (best is None or rec.week > best.week):
            best = rec
    if best is not None:
        return best.coeff
    return 1.0


def forecast(
    week: int,
    seasonality_data: list[SeasonalityWeek],
    constants: dict | None = None,
) -> ForecastResult:
    """Прогноз на неделю `week` строго по формулам §7.6.

    Параметры:
        week             — номер недели (например, 47).
        seasonality_data — список SeasonalityWeek из seasonality.json.
        constants        — необязательный словарь переопределений констант.

    Возвращает ForecastResult.
    """
    base_weekly = constants.get("BASE_WEEKLY_ORDERS", BASE_WEEKLY_ORDERS) if constants else BASE_WEEKLY_ORDERS
    trend = constants.get("TREND_PER_WEEK", TREND_PER_WEEK) if constants else TREND_PER_WEEK
    ops_per_op = constants.get("ORDERS_PER_OPERATOR_WEEK", ORDERS_PER_OPERATOR_WEEK) if constants else ORDERS_PER_OPERATOR_WEEK
    baseline = constants.get("BASELINE_WEEK", BASELINE_WEEK) if constants else BASELINE_WEEK
    operators = constants.get("DEFAULT_OPERATORS", DEFAULT_OPERATORS) if constants else DEFAULT_OPERATORS

    coeff = _seasonality_coeff(week, seasonality_data)

    # База с трендом: base = BASE_WEEKLY_ORDERS * (1 + TREND_PER_WEEK * (week - baseline))
    base = base_weekly * (1.0 + trend * (week - baseline))

    # Прогноз заказов с округлением до десятков
    forecast_orders = round(base * coeff, -1)

    # Мощность: operators * ORDERS_PER_OPERATOR_WEEK
    capacity_orders = operators * ops_per_op

    # Дефицит (отрицательный = нехватка мощности)
    deficit = capacity_orders - forecast_orders

    # Простой и потери в пике (из ANCHORS для week 47, иначе оценочно)
    # По §8.3: downtime 9 ч, loss = 9 * 131 ≈ 1180 BYN
    if week == ANCHORS["peak_week"]:
        downtime_h = ANCHORS["peak_downtime_h"]
        loss_day_val = float(ANCHORS["peak_loss_day"])
    else:
        # Оценка: простой пропорционален дефициту
        downtime_h = max(0.0, -deficit / 100.0) if deficit < 0 else 0.0
        loss_day_val = downtime_h * COST_PER_DOWNTIME_H

    return ForecastResult(
        week=week,
        seasonality_coeff=coeff,
        base=base,
        forecast_orders=int(forecast_orders),
        capacity_orders=int(capacity_orders),
        deficit=int(deficit),
        downtime_h=downtime_h,
        loss_day=loss_day_val,
    )


def forecast_for_week(week: int) -> ForecastResult:
    """Прогноз на неделю с автозагрузкой сезонности из seasonality.json."""
    return forecast(week, load_seasonality())
