"""Тесты для симулятора (simulate.py).

Проверяет:
1. `test_main_branch` — позитивная ветка (branch="main"):
   - Применяет решение "нанять 2 операторов".
   - Итог: effect_byn == 22120 и verdict == "effective".
2. `test_neg_branch` — негативная ветка (branch="neg"):
   - Применяет решение "нанять 2 операторов".
   - Включает компенсатор equip_lamination_wear (износ 96%).
   - Итог: verdict == "ineffective" и compensating_cause == "equip_lamination_wear".
"""

from __future__ import annotations

import pytest

from app.core.simulate import simulate


def test_main_branch():
    """Тест позитивной ветки (нанять 2 операторов)."""
    hire_decision = {
        "type": "hire",
        "operators": 2,
        "effective_from": 0,
    }

    res = simulate(14, [hire_decision], branch="main")

    # Итог по §2.1: (1840 - 260) * 14 = 22120 BYN
    assert abs(res.effect_byn - 22120.0) < 1.0
    assert res.verdict == "effective"


def test_neg_branch():
    """Тест негативной ветки (нанять 2 операторов, но износ ламинатора 96%)."""
    hire_decision = {
        "type": "hire",
        "operators": 2,
        "effective_from": 0,
    }

    res = simulate(14, [hire_decision], branch="neg")

    # В негативной ветке износ ламинатора и брак остаются высокими
    assert res.verdict == "ineffective"
    assert res.compensating_cause == "equip_lamination_wear"
