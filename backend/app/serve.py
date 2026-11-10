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
from starlette.exceptions import HTTPException as StarletteHTTPException

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


# 2. SPA-fallback через exception_handler: StaticFiles(html=True) не отдаёт index.html
#    для /journal, /report, /decision/:id, /devkit без конечного слэша — вернёт 404.
#    Статику (/assets/*.js, /favicon.ico) НЕ перехватываем: отсутствующий файл с точкой
#    в последнем сегменте должен вернуть 404 JSON, а не index.html.
@app.exception_handler(StarletteHTTPException)
async def spa_fallback(request, exc):
    if exc.status_code != 404:
        return JSONResponse(
            status_code=exc.status_code, content={"detail": exc.detail}
        )
    path = request.url.path
    if path.startswith("/api/"):
        return JSONResponse(status_code=404, content={"detail": "Not Found"})
    if request.method != "GET":
        return JSONResponse(status_code=404, content={"detail": "Not Found"})
    last_segment = path.rstrip("/").rsplit("/", 1)[-1]
    if "." in last_segment:
        return JSONResponse(status_code=404, content={"detail": "Not Found"})
    return FileResponse(DIST / "index.html")


# 3. Статика после роутера — иначе /api/* перекроется.
app.mount("/", StaticFiles(directory=str(DIST), html=True), name="static")


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8000")),
    )