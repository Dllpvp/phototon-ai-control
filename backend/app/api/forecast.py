"""API эндпоинт: GET /api/forecast (§9.2, §9.3 Readme.md).

Прогноз по сценарию peak: недельные заказы, capacity, дефицит, downtime, loss.
"""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.forecast import forecast_for_week
from app.core.loader import load_scenario
from app.schemas import ForecastDTO

router = APIRouter(prefix="/api", tags=["forecast"])


@router.get("/forecast", response_model=ForecastDTO)
async def get_forecast(
    scenario: str = Query("peak", description="ID сценария: peak (для прогноза)"),
) -> ForecastDTO:
    """Прогноз пика заказов на неделю 47 (пиковая карточка)."""
    if scenario not in ("main", "neg", "peak"):
        raise HTTPException(
            status_code=400,
            detail=(
                f"Неизвестный сценарий: {scenario!r}. "
                "Допустимо: main, neg, peak"
            ),
        )

    scenario_data = load_scenario(scenario)
    # По §8: для peak используем неделю 47
    week = scenario_data.week if scenario == "peak" else 47

    result = forecast_for_week(week)

    downtime_after = None
    loss_day_after = None
    if result.deficit < 0:
        # Рекомендация: нанять 2 оператора -> downtime 8 ч (анкер 5 операторов)
        downtime_after = 8.0
        loss_day_after = 8.0 * 131.0  # COST_PER_DOWNTIME_H

    return ForecastDTO(
        week=week,
        seasonality_coeff=float(result.seasonality_coeff),
        forecast_orders=result.forecast_orders,
        capacity_orders=result.capacity_orders,
        deficit=result.deficit,
        downtime_h=result.downtime_h,
        loss_day=float(result.loss_day),
        recommended_action="нанять 2 оператора (смена 3)" if result.deficit < 0 else None,
        downtime_h_after=downtime_after,
        loss_day_after=loss_day_after,
    )
