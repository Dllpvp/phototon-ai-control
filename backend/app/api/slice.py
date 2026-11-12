"""API эндпоинт: GET /api/slice (§9.2 Readme.md).

Кросс-фильтр: серия фактов по дням с фильтрами from, to, line, shift.
"""

from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.core.loader import FactRecord, FactsPayload, load_facts
from app.schemas import SliceDTO, SliceFactDTO

router = APIRouter(tags=["slice"])


@router.get("/slice", response_model=SliceDTO)
async def get_slice(
    from_: date = Query(..., alias="from", description="Начальная дата (YYYY-MM-DD)"),
    to: date = Query(..., description="Конечная дата (YYYY-MM-DD)"),
    line: Optional[str] = Query(None, description="Фильтр по линии (line1, line2)"),
    shift: Optional[int] = Query(None, description="Фильтр по смене (1, 2, 3)"),
    facts: FactsPayload = Depends(lambda: load_facts()),
) -> SliceDTO:
    """Серия фактов по дням с кросс-фильтрацией."""
    filtered_facts: list[SliceFactDTO] = []
    
    for f in facts.facts:
        fact_date = date.fromisoformat(f.ts.split("T")[0])
        
        if fact_date < from_ or fact_date > to:
            continue
        
        if line is not None and f.dims.get("line") != line:
            continue
        
        if shift is not None and f.dims.get("shift") != str(shift):
            continue
        
        filtered_facts.append(SliceFactDTO(
            ts=fact_date,
            domain=f.domain,
            metric=f.metric,
            value=f.value,
            dims={k: str(v) for k, v in f.dims.items()},
        ))
    
    # Сортируем по дате
    filtered_facts.sort(key=lambda f: f.ts)
    
    return SliceDTO(
        **{"from": from_},
        to=to,
        line=line,
        shift=shift,
        facts=filtered_facts,
    )