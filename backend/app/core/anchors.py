"""Якоря — единственный источник «красивых» чисел плана (§2.3 Readme.md).

Все числа, которые жюри видит на экранах (14 ч, 23 заказа, 41 200 BYN/нед,
1 840 / 260 BYN/сут, 22 120 BYN, пик 1 180 BYN/сут), живут здесь и
проверяются `validate_anchors()`. Красный тест = цифры разъехались — это
видно до запуска UI.
"""

ANCHORS: dict = {
    # What-If: операторы смены №3 (факт = 4)
    "downtime_h_by_ops": {4: 14.0, 5: 8.0, 6: 2.0},
    "sla_orders_by_ops": {4: 23, 5: 11, 6: 3},
    "revenue_week_by_ops": {4: 41200, 5: 44900, 6: 47600},
    "loss_day_by_ops": {4: 1840, 5: 980, 6: 260},

    # Качество
    "defect_rate_now": 9.0,          # % (main)
    "defect_rate_after_hire": 4.0,   # % (позитивная ветка)
    "defect_rate_neg": 11.0,         # % (негативная ветка, износ ламинатора)
    "loss_day_neg": 2170,            # BYN/сут (негативная ветка)

    # Превентив (неделя 47)
    "peak_week": 47,
    "peak_coeff": 1.35,
    "peak_forecast_orders": 1240,
    "capacity_orders": 1050,
    "peak_downtime_h": 9.0,
    "peak_loss_day": 1180,
    "peak_days_ahead": 14,

    # Эффект решения
    "sim_days": 14,
    "test_effect_14d": 22120,   # (1840 − 260) × 14, проверяется assert'ом
}


def validate_anchors() -> None:
    a = ANCHORS
    assert a["loss_day_by_ops"][4] - a["loss_day_by_ops"][6] == 1580
    assert (a["loss_day_by_ops"][4] - a["loss_day_by_ops"][6]) * a["sim_days"] == a["test_effect_14d"]
    assert a["capacity_orders"] == 6 * 175              # 6 операторов × 175 заказов/нед
    assert a["peak_forecast_orders"] - a["capacity_orders"] == 190  # ≈ 2 оператора дефицита
    for key in ("downtime_h_by_ops", "loss_day_by_ops"):
        v = [a[key][k] for k in (4, 5, 6)]
        assert v[0] > v[1] > v[2], key                 # строго убывает
    v = [a["revenue_week_by_ops"][k] for k in (4, 5, 6)]
    assert v[0] < v[1] < v[2]
    assert a["sla_orders_by_ops"][6] <= 5               # норма 0–5
    assert 1240 <= a["peak_forecast_orders"] <= 1250
    # 131 BYN/ч согласует три точки плана
    assert abs(a["loss_day_by_ops"][4] / 14 - 131) < 1
    assert abs(a["loss_day_by_ops"][6] / 2 - 131) < 2
    assert abs(a["peak_loss_day"] / a["peak_downtime_h"] - 131) < 2
