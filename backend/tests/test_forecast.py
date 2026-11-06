"""Тесты прогноза пика forecast() (§7.6 Readme.md).

Проверяем формулы:
  base = BASE_WEEKLY_ORDERS * (1 + TREND_PER_WEEK * (week - 45))
  forecast_orders = round(base * seasonality_coeff, -1)
  capacity_orders = 6 * ORDERS_PER_OPERATOR_WEEK
  deficit = capacity_orders - forecast_orders
"""

from __future__ import annotations

import pytest

from app.core.anchors import ANCHORS
from app.core.constants import (
    BASE_WEEKLY_ORDERS,
    ORDERS_PER_OPERATOR_WEEK,
    TREND_PER_WEEK,
)
from app.core.forecast import forecast, forecast_for_week
from app.core.loader import load_seasonality


class TestForecast:
    def test_peak_week_47(self) -> None:
        """Неделя 47 (пик): forecast_orders == 1240, capacity == 1050, deficit == -190."""
        seasonality = load_seasonality()
        result = forecast(47, seasonality)
        assert result.forecast_orders == 1240
        assert result.capacity_orders == 1050
        assert result.deficit == -190

    def test_base_formula_week_47(self) -> None:
        """base = 917 * (1 + 0.002 * (47 - 45)) = 917 * 1.004 = 920.668."""
        seasonality = load_seasonality()
        result = forecast(47, seasonality)
        expected_base = BASE_WEEKLY_ORDERS * (1 + TREND_PER_WEEK * (47 - 45))
        assert result.base == pytest.approx(expected_base)

    def test_seasonality_coeff_47(self) -> None:
        """Для недели 47 коэффициент сезонности == 1.35 (якорь peak_coeff)."""
        seasonality = load_seasonality()
        result = forecast(47, seasonality)
        assert result.seasonality_coeff == 1.35
        assert result.seasonality_coeff == ANCHORS["peak_coeff"]

    def test_forecast_orders_rounding(self) -> None:
        """forecast_orders округляется до десятков: round(base * coeff, -1)."""
        seasonality = load_seasonality()
        result = forecast(47, seasonality)
        base = BASE_WEEKLY_ORDERS * (1 + TREND_PER_WEEK * (47 - 45))
        expected_rounded = round(base * 1.35, -1)
        assert result.forecast_orders == expected_rounded
        assert result.forecast_orders == 1240

    def test_capacity_formula(self) -> None:
        """capacity = 6 * ORDERS_PER_OPERATOR_WEEK = 6 * 175 = 1050."""
        seasonality = load_seasonality()
        result = forecast(47, seasonality)
        assert result.capacity_orders == 6 * ORDERS_PER_OPERATOR_WEEK
        assert result.capacity_orders == 1050

    def test_deficit_formula(self) -> None:
        """deficit = capacity - forecast = 1050 - 1240 = -190."""
        seasonality = load_seasonality()
        result = forecast(47, seasonality)
        assert result.deficit == result.capacity_orders - result.forecast_orders
        assert result.deficit == -190

    def test_forecast_matches_anchors(self) -> None:
        """Результат для недели 47 совпадает с ANCHORS."""
        seasonality = load_seasonality()
        result = forecast(47, seasonality)
        assert result.forecast_orders == ANCHORS["peak_forecast_orders"]
        assert result.capacity_orders == ANCHORS["capacity_orders"]

    def test_week_45_no_trend(self) -> None:
        """Неделя 45: тренд = 0, base = BASE_WEEKLY_ORDERS."""
        seasonality = load_seasonality()
        result = forecast(45, seasonality)
        assert result.base == pytest.approx(BASE_WEEKLY_ORDERS)

    def test_forecast_for_week_helper(self) -> None:
        """forecast_for_week(47) — обёртка, загружающая сезонность сама."""
        result = forecast_for_week(47)
        assert result.forecast_orders == 1240
        assert result.capacity_orders == 1050
        assert result.deficit == -190

    def test_loss_day_in_result(self) -> None:
        """В результате есть потери в сутки: для пика — якорь 1180 BYN."""
        seasonality = load_seasonality()
        result = forecast(47, seasonality)
        assert result.loss_day == ANCHORS["peak_loss_day"]
        assert result.loss_day == 1180

    def test_downtime_in_result(self) -> None:
        """Простой в пике — якорь 9 ч (§8.3)."""
        seasonality = load_seasonality()
        result = forecast(47, seasonality)
        assert result.downtime_h == ANCHORS["peak_downtime_h"]
        assert result.downtime_h == 9.0

    def test_constants_override(self) -> None:
        """Переопределение констант через словарь constants."""
        seasonality = load_seasonality()
        result = forecast(47, seasonality, constants={"DEFAULT_OPERATORS": 7})
        assert result.capacity_orders == 7 * ORDERS_PER_OPERATOR_WEEK

    def test_non_peak_week_estimate(self) -> None:
        """Не-пиковая неделя: простой и потери оцениваются по дефициту."""
        seasonality = load_seasonality()
        result = forecast(45, seasonality)
        # Проверяем связку: если дефицит есть, потери = downtime * COST_PER_DOWNTIME_H
        if result.deficit < 0:
            from app.core.constants import COST_PER_DOWNTIME_H

            assert result.loss_day == pytest.approx(result.downtime_h * COST_PER_DOWNTIME_H)
