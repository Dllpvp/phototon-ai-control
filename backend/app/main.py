from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import router as api_router

app = FastAPI(title="FotoPrint Control API")

# Строгое CORS для localhost:5174 (фронтенд Vite dev server)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем централизованный роутер из app.api
app.include_router(api_router)


@app.get("/api/health")
def health_check():
    return {"ok": True, "version": "0.1.0", "status": "ok"}