"""Тесты линейной интерполяции What-If (§6.3 / §7.4 Readme.md)."""

from __future__ import annotations

import pytest

from app.core.anchors import ANCHORS
from app.core.interpolation import interp


class TestInterp:
    def test_exact_point_4(self) -> None:
        """Точное попадание в якорь: interp(4) == 14.0."""
        assert interp(4, ANCHORS["downtime_h_by_ops"]) == 14.0

    def test_exact_point_6(self) -> None:
        """Точное попадание в якорь: interp(6) == 2.0."""
        assert interp(6, ANCHORS["downtime_h_by_ops"]) == 2.0

    def test_exact_point_5(self) -> None:
        """Точное попадание в якорь: interp(5) == 8.0."""
        assert interp(5, ANCHORS["downtime_h_by_ops"]) == 8.0

    def test_midpoint_4_5(self) -> None:
        """Середина между 4 и 5: interp(4.5) == 11.0 (14 + 8) / 2."""
        assert interp(4.5, ANCHORS["downtime_h_by_ops"]) == 11.0

    def test_midpoint_5_6(self) -> None:
        """Середина между 5 и 6: interp(5.5) == 5.0 (8 + 2) / 2."""
        assert interp(5.5, ANCHORS["downtime_h_by_ops"]) == 5.0

    def test_out_of_range_below(self) -> None:
        """Ниже минимума: возвращается значение первой точки."""
        assert interp(3, ANCHORS["downtime_h_by_ops"]) == 14.0

    def test_out_of_range_above(self) -> None:
        """Выше максимума: возвращается значение последней точки."""
        assert interp(7, ANCHORS["downtime_h_by_ops"]) == 2.0

    def test_loss_day_interpolation(self) -> None:
        """Интерполяция потерь: interp(4, loss_day) == 1840, interp(4.5) == 1410."""
        assert interp(4, ANCHORS["loss_day_by_ops"]) == 1840
        assert interp(4.5, ANCHORS["loss_day_by_ops"]) == 1410.0  # (1840+980)/2

    def test_empty_dict_raises(self) -> None:
        with pytest.raises(ValueError, match="пуст"):
            interp(1, {})

    def test_single_point(self) -> None:
        """Словарь с одной точкой — всегда возвращает её значение."""
        assert interp(5, {5: 42.0}) == 42.0
        assert interp(1, {5: 42.0}) == 42.0
        assert interp(10, {5: 42.0}) == 42.0

    def test_float_keys(self) -> None:
        """Ключи могут быть float."""
        d = {4.0: 14.0, 5.0: 8.0, 6.0: 2.0}
        assert interp(4.5, d) == 11.0

    def test_quarter_point(self) -> None:
        """Четверть между 4 и 5: interp(4.25) == 12.5 (14 - 0.25*6)."""
        assert interp(4.25, ANCHORS["downtime_h_by_ops"]) == 12.5
