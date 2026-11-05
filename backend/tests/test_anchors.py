"""Проверка якорей: цифры плана не разъехались (§2.3 Readme.md)."""

from app.core.anchors import ANCHORS, validate_anchors


def test_validate_anchors() -> None:
    """validate_anchors() не бросает AssertionError на согласованных якорях."""
    validate_anchors()


def test_anchors_expose_expected_keys() -> None:
    """Таблица ANCHORS содержит все ключи, которые видит фронт по API."""
    expected = {
        "downtime_h_by_ops",
        "sla_orders_by_ops",
        "revenue_week_by_ops",
        "loss_day_by_ops",
        "defect_rate_now",
        "defect_rate_after_hire",
        "defect_rate_neg",
        "loss_day_neg",
        "peak_week",
        "peak_coeff",
        "peak_forecast_orders",
        "capacity_orders",
        "peak_downtime_h",
        "peak_loss_day",
        "peak_days_ahead",
        "sim_days",
        "test_effect_14d",
    }
    assert expected <= set(ANCHORS)
