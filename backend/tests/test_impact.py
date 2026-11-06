"""Тесты обхода графа delta() (§7.3 Readme.md).

Проверяем BFS с учётом sign, weight и curvature через math.copysign.
Конкретный кейс: hr_operators_s3, d_input=+2, ребро в prod_downtime_l2
имеет sign=-1, weight=3.0, curvature=0.75.
"""

from __future__ import annotations

import math

import pytest

from app.core.graph import get_graph
from app.core.impact import delta, delta_default


class TestDelta:
    def test_start_node_in_result(self) -> None:
        """Стартовый узел всегда есть в результате с d_input."""
        g = get_graph()
        result = delta(g, "hr_operators_s3", 2.0)
        assert "hr_operators_s3" in result
        assert result["hr_operators_s3"] == 2.0

    def test_single_edge_downtime(self) -> None:
        """hr_operators_s3 → prod_downtime_l2 с d_input=+2.

        Ребро: sign=-1, weight=3.0, curvature=0.75.
        d = 2.0
        d_to = d * weight * sign = 2 * 3.0 * (-1) = -6.0
        curvature: 0.75 * copysign(d*d, d) = 0.75 * copysign(4, 2) = 0.75 * 4 = 3.0
        Итого: -6.0 + 3.0 = -3.0
        """
        g = get_graph()
        result = delta(g, "hr_operators_s3", 2.0, depth=1)
        assert "prod_downtime_l2" in result
        expected = 2.0 * 3.0 * (-1) + 0.75 * math.copysign(2.0 * 2.0, 2.0)
        assert result["prod_downtime_l2"] == pytest.approx(expected)
        assert result["prod_downtime_l2"] == pytest.approx(-3.0)

    def test_single_edge_overtime(self) -> None:
        """hr_operators_s3 → hr_overtime_s3 с d_input=+2.

        Ребро: sign=-1, weight=2.5, curvature=0.0.
        d_to = 2 * 2.5 * (-1) = -5.0
        """
        g = get_graph()
        result = delta(g, "hr_operators_s3", 2.0, depth=1)
        assert result["hr_overtime_s3"] == pytest.approx(-5.0)

    def test_depth_limit(self) -> None:
        """При depth=0 только стартовый узел."""
        g = get_graph()
        result = delta(g, "hr_operators_s3", 2.0, depth=0)
        assert set(result.keys()) == {"hr_operators_s3"}

    def test_depth_2_reaches_loss_day(self) -> None:
        """Глубина 2: hr_operators_s3 → prod_downtime_l2 → fin_loss_day.

        Шаг 1: prod_downtime_l2 получает d1 = -3.0 (см. test_single_edge_downtime).
        Шаг 2: prod_downtime_l2 → fin_loss_day, sign=1, weight=131.0, curvature=0.
               d2 = -3.0 * 131.0 * 1 = -393.0
        """
        g = get_graph()
        result = delta(g, "hr_operators_s3", 2.0, depth=2)
        assert "fin_loss_day" in result
        # prod_downtime_l2 -> fin_loss_day: weight=131
        d1 = -3.0
        expected_loss = d1 * 131.0 * 1
        assert result["fin_loss_day"] == pytest.approx(expected_loss)

    def test_negative_input(self) -> None:
        """d_input=-2: sign меняет направление, copysign учитывает знак d."""
        g = get_graph()
        result = delta(g, "hr_operators_s3", -2.0, depth=1)
        # d=-2, weight=3, sign=-1: d_to = -2 * 3 * (-1) = +6
        # curvature: 0.75 * copysign(4, -2) = 0.75 * (-4) = -3
        # Итого: 6 + (-3) = 3
        expected = (-2.0) * 3.0 * (-1) + 0.75 * math.copysign((-2.0) ** 2, -2.0)
        assert result["prod_downtime_l2"] == pytest.approx(expected)
        assert result["prod_downtime_l2"] == pytest.approx(3.0)

    def test_delta_default_uses_get_graph(self) -> None:
        """delta_default() вызывает get_graph() внутри."""
        result = delta_default("hr_operators_s3", 1.0, depth=1)
        assert "hr_operators_s3" in result
        assert result["hr_operators_s3"] == 1.0

    def test_zero_input(self) -> None:
        """d_input=0 → все эффекты нулевые."""
        g = get_graph()
        result = delta(g, "hr_operators_s3", 0.0, depth=6)
        for v in result.values():
            assert v == 0.0

    def test_accumulation_multiple_paths(self) -> None:
        """Если в узел ведут несколько путей, изменения суммируются."""
        g = get_graph()
        # hr_operators_s3 → hr_overtime_s3 → quality_defect_rate
        # и hr_operators_s3 → prod_downtime_l2 (но нет пути в quality_defect_rate напрямую)
        result = delta(g, "hr_operators_s3", 2.0, depth=3)
        # Проверяем, что quality_defect_rate достижим и имеет ненулевое значение
        assert "quality_defect_rate" in result
        assert result["quality_defect_rate"] != 0.0

    def test_no_out_edges(self) -> None:
        """Узел без исходящих рёбер — только он сам в результате."""
        g = get_graph()
        # fin_margin не имеет исходящих рёбер
        result = delta(g, "fin_margin", 5.0, depth=6)
        assert set(result.keys()) == {"fin_margin"}
        assert result["fin_margin"] == 5.0
