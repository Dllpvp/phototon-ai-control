"""API эндпоинт: GET /api/unit-economics (§9.2 Readme.md).

5 строк из §7.8 Readme.md.
"""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.schemas import UnitEconDTO

router = APIRouter(tags=["unit-economics"])


@router.get("/unit-economics", response_model=list[UnitEconDTO])
async def get_unit_economics() -> list[UnitEconDTO]:
    """Юнит-экономика: 5 строк из §7.8."""
    return [
        UnitEconDTO(
            sku="orders_received",
            price=0.0,
            paper=0.0,
            printing=0.0,
            binding=0.0,
            labor=0.0,
            defect=0.0,
            margin_pct=0.0,
        ),
        UnitEconDTO(
            sku="revenue_per_order",
            price=4050.0,
            paper=0.0,
            printing=0.0,
            binding=0.0,
            labor=0.0,
            defect=0.0,
            margin_pct=0.0,
        ),
        UnitEconDTO(
            sku="variable_cost_per_order",
            price=2754.0,
            paper=0.0,
            printing=0.0,
            binding=0.0,
            labor=0.0,
            defect=0.0,
            margin_pct=0.0,
        ),
        UnitEconDTO(
            sku="capacity_cost_per_order",
            price=560.0,
            paper=0.0,
            printing=0.0,
            binding=0.0,
            labor=0.0,
            defect=0.0,
            margin_pct=0.0,
        ),
        UnitEconDTO(
            sku="margin_per_order",
            price=736.0,
            paper=0.0,
            printing=0.0,
            binding=0.0,
            labor=0.0,
            defect=0.0,
            margin_pct=0.32,
        ),
    ]