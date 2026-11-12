"""API эндпоинт для генерации Executive Summary PDF (§9.2, §11.4 Readme.md).

Возвращает PDF в виде StreamingResponse (application/pdf).
"""

from __future__ import annotations

import io

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

from app.report.pdf import generate_executive_summary

router = APIRouter(prefix="/report", tags=["report"])


@router.get("/executive.pdf", response_class=StreamingResponse)
async def get_executive_summary_pdf(
    scenario: str = Query("main", description="ID сценария: main|neg|peak"),
) -> StreamingResponse:
    """Генерирует и отдаёт Executive Summary PDF для указанного сценария."""
    pdf_bytes = generate_executive_summary(scenario_id=scenario)
    
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=Executive_Summary_{scenario}.pdf"
        },
    )
