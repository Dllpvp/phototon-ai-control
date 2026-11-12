"""Демо-RBAC для 7 ролей (§22.3 PLAN-V2).

Роль берётся из заголовка `X-Demo-Role`, департамент — из `X-Demo-Dept`.
Никакого настоящего auth/JWT: роль — демо-заголовок (AGENTS.md §12).

Единственный источник матрицы ролей → домены и типы решений.
"""

from __future__ import annotations

from fastapi import HTTPException, Request, status

from app.schemas import AlertDTO, ChainNodeDTO, DashboardDTO, KpiDTO

ROLE_DOMAIN_MAP: dict[str, set[str]] = {
    # director: все домены (None в get_allowed_domains)
    "production_head": {"production", "quality", "logistics", "hr"},
    "hr_head": {"hr", "admin"},
    "finance_head": {"finance", "accounting"},
    "support_head": {"clients", "logistics"},
    "specialist": set(),
}

# Домены head каждого департамента для department_head
DEPT_DOMAIN_MAP: dict[str, set[str]] = {
    "production": {"production", "quality", "logistics", "hr"},
    "hr": {"hr", "admin"},
    "finance": {"finance", "accounting"},
    "support": {"clients", "logistics"},
    "clients": {"clients", "logistics"},
    "quality": {"production", "quality", "logistics", "hr"},
    "logistics": {"clients", "production", "logistics", "hr"},
}

DEFAULT_DEPT = "production"
DEFAULT_ROLE = "director"

# Синонимы §22.3: repair/reglament = maintenance
DECISION_TYPE_SYNONYMS: dict[str, str] = {
    "repair": "maintenance",
    "reglament": "maintenance",
}

ROLE_ALLOWED_DECISION_TYPES: dict[str, set[str]] = {
    "director": {"hire", "maintenance", "other"},
    "production_head": {"maintenance", "hire"},
    "hr_head": {"hire"},
    "finance_head": {"maintenance", "other"},
    "support_head": {"maintenance", "other"},
    "specialist": set(),
}

HEADER_ROLE = "X-Demo-Role"
HEADER_DEPT = "X-Demo-Dept"


def get_role(request: Request) -> str:
    """Роль из заголовка X-Demo-Role; отсутствует → 'director' (фолбэк §17)."""
    value = request.headers.get(HEADER_ROLE)
    if not value or not value.strip():
        return DEFAULT_ROLE
    return value.strip()


def get_dept(request: Request) -> str | None:
    """Департамент из заголовка X-Demo-Dept (для department_head)."""
    value = request.headers.get(HEADER_DEPT)
    if not value or not value.strip():
        return None
    return value.strip()


def get_allowed_domains(role: str, dept: str | None = None) -> set[str] | None:
    """Множество разрешённых доменов; None = все (director)."""
    if role == "director":
        return None
    if role == "department_head":
        key = (dept or DEFAULT_DEPT).lower()
        return DEPT_DOMAIN_MAP.get(key, DEPT_DOMAIN_MAP[DEFAULT_DEPT])
    return ROLE_DOMAIN_MAP.get(role, set())


def effective_role(role: str, dept: str | None) -> str:
    """Возвращает реальную роль, учитывая department_head и заголовок dept.
    Если role == 'department_head', переводит в '<dept>_head' (по умолчанию production_head).
    """
    if role != "department_head":
        return role
    # map department to corresponding head role; fallback to production_head
    base = (dept or "production").lower()
    mapped = f"{base}_head"
    return mapped if mapped in ROLE_ALLOWED_DECISION_TYPES else "production_head"

def can_create_decision(role: str, decision_type: str, dept: str | None = None) -> bool:
    """Разрешено ли роли создавать решение данного типа (с учётом синонимов и department_head)."""
    real_role = effective_role(role, dept)
    norm = DECISION_TYPE_SYNONYMS.get(decision_type, decision_type)
    allowed = ROLE_ALLOWED_DECISION_TYPES.get(real_role, set())
    return decision_type in allowed or norm in allowed


def check_decision_permission(
    role: str, decision_type: str, dept: str | None = None
) -> None:
    """Raises 403, если роль не может создать решение этого типа."""
    if not can_create_decision(role, decision_type, dept):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Роль '{role}' не может создать решение типа '{decision_type}'",
        )


HIDDEN_STATUS = "hidden"


def filter_dashboard(dto: DashboardDTO, allowed: set[str] | None) -> DashboardDTO:
    """Оставляет в kpis/alerts только узлы разрешённых доменов; headline — без денег."""
    if allowed is None:
        return dto

    kpis: list[KpiDTO] = [k for k in dto.kpis if k.domain in allowed]
    alerts: list[AlertDTO] = [a for a in dto.alerts if a.node_id in {k.node_id for k in kpis}]

    # Headline: для director (allowed is None) остаётся финансовый текст (из алертов).
    # Для ограниченных ролей — департаментский заголовок по первому red-KPI
    # разрешённых доменов (деньги не показываем; кейс 10/11 T9b).
    headline = dto.headline
    red_kpis = [k for k in kpis if k.status == "red"]
    if red_kpis:
        first = red_kpis[0]
        headline = f"{first.name}: {first.value:.0f} {first.unit}"
    elif kpis:
        first = kpis[0]
        headline = f"{first.name}: {first.value:.0f} {first.unit}"
    else:
        headline = "Все показатели в норме"

    return dto.model_copy(update={"kpis": kpis, "alerts": alerts, "headline": headline})


def hide_chain_nodes(nodes: list[ChainNodeDTO], allowed: set[str] | None) -> list[ChainNodeDTO]:
    """Скрывает деньги узлов недоступных доменов, сохраняя длину цепочки."""
    if allowed is None:
        return nodes

    return [
        node
        if node.domain in allowed
        else node.model_copy(
            update={
                "value": None,
                "status": HIDDEN_STATUS,
                "cost_per_day": None,
                "delta_from_parent": None,
            }
        )
        for node in nodes
    ]


__all__ = [
    "get_role",
    "get_dept",
    "get_allowed_domains",
    "can_create_decision",
    "check_decision_permission",
    "effective_role",
    "filter_dashboard",
    "hide_chain_nodes",
    "ROLE_DOMAIN_MAP",
    "DEPT_DOMAIN_MAP",
    "ROLE_ALLOWED_DECISION_TYPES",
    "DEFAULT_ROLE",
    "DEFAULT_DEPT",
    "HEADER_ROLE",
    "HEADER_DEPT",
]