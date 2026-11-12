"""API эндпоинт: GET /api/unit-economics (§9.2 Readme.md).

Строки из ядра (calc), роутер только возвращает DTO.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.core import economics as econ
from app.schemas import UnitEconDTO

router = APIRouter(tags=["unit-economics"])


@router.get("/unit-economics", response_model=list[UnitEconDTO])
async def get_unit_economics() -> list[UnitEconDTO]:
    """Юнит-экономика: 5 строк из §7.8, данные из core."""
    return econ.unit_economics()