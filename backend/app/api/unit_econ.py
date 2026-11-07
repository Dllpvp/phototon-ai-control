"""API эндпоинт: GET /api/unit-economics (§9.2 Readme.md).

5 строк из §7.8 Readme.md.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.schemas import UnitEconDTO

router = APIRouter(prefix="/api", tags=["unit-economics"])


@router.get("/unit-economics", response_model=list[UnitEconDTO])
async def get_unit_economics() -> list[UnitEconDTO]:
    """Юнит-экономика: 5 строк из §7.8."""
    return [
        UnitEconDTO(
            metric="orders_received",
            unit="шт/нед",
            value=1240,
            cost_per_unit=0.0,
            margin_byn=0.0,
            note="Фактический приём заказов (неделя 47)",
        ),
        UnitEconDTO(
            metric="revenue_per_order",
            unit="BYN",
            value=4050,
            cost_per_unit=0.0,
            margin_byn=0.0,
            note="Средний чек с учётом доп. услуг",
        ),
        UnitEconDTO(
            metric="variable_cost_per_order",
            unit="BYN",
            value=2754,
            cost_per_unit=2754,
            margin_byn=1296,
            note="Материалы + лamination + доставка",
        ),
        UnitEconDTO(
            metric="capacity_cost_per_order",
            unit="BYN",
            value=560,
            cost_per_unit=560,
            margin_byn=736,
            note="Амортизация оборудования + операторы",
        ),
        UnitEconDTO(
            metric="margin_per_order",
            unit="BYN",
            value=736,
            cost_per_unit=0.0,
            margin_byn=736,
            note="Маржинальный доход на заказ (32%)",
        ),
    ]