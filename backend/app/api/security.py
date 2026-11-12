"""API эндпоинты безопасности: журнал аудита ИИ-вызовов (T9d, PLAN-V2 §6.5).

Доступ: только director (RBAC через X-Demo-Role).
"""

from fastapi import APIRouter, Depends, Request, status, HTTPException

from app.schemas import AuditDTO
from app.security.audit import list_last
from app.security.rbac import get_role, DEFAULT_ROLE

router = APIRouter(prefix="/security", tags=["security"])


async def require_director(request: Request) -> str:
    """Зависимость: проверяет, что роль — director."""
    role = get_role(request)
    if role != "director":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Доступ только для director, текущая роль: {role}",
        )
    return role


@router.get(
    "/audit",
    response_model=list[AuditDTO],
    summary="Последние записи аудита ИИ-вызовов",
    description="Возвращает последние N записей из таблицы ai_audit. Только для роли director.",
)
async def get_audit(
    request: Request,
    last: int = 10,
    _: str = Depends(require_director),
) -> list[AuditDTO]:
    """
    GET /api/security/audit?last=10

    - **last**: сколько последних записей вернуть (по умолчанию 10, макс. 100)
    - Доступ: только director (X-Demo-Role: director)
    - Возвращает: список AuditDTO (id, ts, backend, mask_level, tokens_count,
      payload_masked_json, payload_sha256, verdict, reason)
    """
    if last <= 0:
        return []
    if last > 100:
        last = 100
    return list_last(last)