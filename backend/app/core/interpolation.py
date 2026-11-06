"""Линейная интерполяция What-If по таблицам ANCHORS (§6.3, §7.4 Readme.md).

Калибровочная кривая по трём измеренным точкам (например, для операторов:
4 → 14.0, 5 → 8.0, 6 → 2.0). Между ними делается честная линейная
интерполяция. Вне диапазона [min_x, max_x] значение экстраполируется по
крайним сегментам или ограничивается границами.
"""

from __future__ import annotations

from typing import Mapping


def interp(x: float, anchors_dict: Mapping[float | int, float]) -> float:
    """Линейная интерполяция значения `x` по словарю `anchors_dict` {x: y}.

    Строго по §6.3 / §7.4 Readme.md:
    - `anchors_dict` — словарь точек (ключи могут быть int или float).
    - Если `x` точен или меньше/больше крайних точек, обрабатывается корректно.
    """
    if not anchors_dict:
        raise ValueError("Словарь якорей пуст")

    # Сортируем пары по x
    points = sorted((float(k), float(v)) for k, v in anchors_dict.items())

    # Точное совпадение или выход за границы
    if x <= points[0][0]:
        return points[0][1]
    if x >= points[-1][0]:
        return points[-1][1]

    # Ищем соседние точки (x0, y0) и (x1, y1)
    for i in range(len(points) - 1):
        x0, y0 = points[i]
        x1, y1 = points[i + 1]
        if x0 <= x <= x1:
            if x0 == x1:
                return y0
            # Линейная интерполяция
            t = (x - x0) / (x1 - x0)
            return y0 + t * (y1 - y0)

    # На всякий случай (недостижимо при правильных проверках)
    return points[-1][1]
