"""Product single-process entrypoint (Readme §3.7, §16.1, Этап 8).

Раздаёт собранный frontend/dist и API на одном порту :8000 без Vite и прокси.
main.py остаётся dev-точкой (CORS), serve.py — product-точка same-origin (CORS не нужен).
"""

import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api import router as api_router

DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"

if not DIST.is_dir():
    raise RuntimeError("Сначала выполните npm run build во frontend/")

app = FastAPI(title="FotoPrint Control — venue (dist + api)")

# 1. API-роутер тем же способом, что и в main.py (префикс /api внутри router).
app.include_router(api_router)


@app.get("/api/health")
def health_check():
    return {"ok": True, "version": "0.1.0", "status": "ok"}


# 2. SPA-fallback: StaticFiles(html=True) не отдаёт index.html для /journal, /report,
#    /decision/:id, /devkit без конечного слэша — вернёт 404. Catch-all до mount:
#    api/* → JSON 404, остальное → index.html (история-роутинг, Telegram-диплинк §9.2).
@app.get("/{full_path:path}", response_model=None)
async def spa_fallback(full_path: str):
    if full_path.startswith("api/"):
        return JSONResponse(status_code=404, content={"detail": "Not Found"})
    return FileResponse(DIST / "index.html")


# 3. Статика после роутера и catch-all — иначе /api/* перекроется.
app.mount("/", StaticFiles(directory=str(DIST), html=True), name="static")


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8000")),
    )