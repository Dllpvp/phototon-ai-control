"""API package — централизованный роутер (AGENTS.md).

Все роутеры подключаются сюда, main.py импортирует только app.api.router.
"""

from fastapi import APIRouter

from app.api import (
    chain,
    dashboard,
    decisions,
    forecast,
    jira_mock,
    slice,
    snapshot,
    unit_econ,
    whatif,
    ai,
    report,
)

router = APIRouter(prefix="/api")

router.include_router(snapshot.router)
router.include_router(dashboard.router)
router.include_router(chain.router)
router.include_router(slice.router)
router.include_router(whatif.router)
router.include_router(forecast.router)
router.include_router(unit_econ.router)
router.include_router(decisions.router)
router.include_router(jira_mock.router)
router.include_router(ai.router)
router.include_router(report.router)
