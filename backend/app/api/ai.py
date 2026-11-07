from fastapi import APIRouter
from app.integrations import ai_provider
from app.schemas import AiDTO
from app.config import settings

router = APIRouter(prefix="/api/ai", tags=["ai"])

@router.post("/interpret", response_model=AiDTO)
async def interpret_chain(ctx: dict):
    return await ai_provider.interpret(ctx)

@router.get("/health")
async def ai_health():
    return {
        "enabled": settings.ai_enabled,
        "model": settings.deepseek_model,
        "cache_size": len(ai_provider.load_cache()),
        "provider": "deepseek",
    }