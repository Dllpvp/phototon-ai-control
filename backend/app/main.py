from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    ai,
    chain,
    dashboard,
    decisions,
    forecast,
    graph,
    report,
    slice,
    unit_econ,
    whatif,
)

app = FastAPI(title="FotoPrint Control API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ai.router)
app.include_router(chain.router)
app.include_router(dashboard.router)
app.include_router(decisions.router)
app.include_router(forecast.router)
app.include_router(graph.router)
app.include_router(report.router)
app.include_router(slice.router)
app.include_router(unit_econ.router)
app.include_router(whatif.router)


@app.get("/api/health")
def health_check():
    return {"ok": True, "version": "0.1.0", "status": "ok"}