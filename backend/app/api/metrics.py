"""T18 — Каталог KPI: 33 показателя по 10 отделам (PLAN-V2 §22.4, §22.10).

Справочный слой: формула, источник, норма, отдел. Числа не хардкодим:
- node    → value_main из графа (узлы v2 появятся после мержа ветки лида);
- anchor  → ANCHORS v1 (эффект решений);
- catalog → демо-значения лекции v2.2, единственный источник — kpi_catalog.json.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.anchors import ANCHORS
from app.core.loader import GraphPayload
from app.dependencies import get_graph
from app.schemas import MetricCatalogDTO, MetricCatalogItemDTO

router = APIRouter(tags=["metrics"])

# Справочник отделов (PLAN-V2 §22.4)
DEPARTMENTS: dict[str, str] = {
    "executive": "Директор / руководство",
    "production": "Производство",
    "clients": "Клиенты и поддержка / Мэри",
    "hr": "HR и персонал",
    "finance": "Финансы",
    "accounting": "Бухгалтерия",
    "logistics": "Логистика и доставка",
    "procurement": "Закупки",
    "admin": "Администрация",
    "retail": "Розничная сеть / picPac",
}

_CATALOG_PATH = Path(__file__).resolve().parents[1] / "data" / "kpi_catalog.json"


@lru_cache(maxsize=1)
def load_catalog() -> list[dict]:
    """Каталог KPI с диска (один раз). Файл версионируется, не генерируется seed'ом."""
    raw = json.loads(_CATALOG_PATH.read_text(encoding="utf-8"))
    return raw["items"]


def _resolve_value(item: dict, nodes: dict[str, float]) -> tuple[float | None, bool]:
    """(value, available): граф → ANCHORS → каталог. Без хардкода чисел."""
    kind = item["value_kind"]
    if kind == "anchor":
        return float(ANCHORS[item["anchor_key"]]), True
    if kind == "catalog":
        return float(item["demo_value"]), True
    node_id = item["node_id"]
    if node_id in nodes:
        return nodes[node_id], True
    return None, False  # узел v2 ещё не в графе — честно отдаём «—»


@router.get("/metrics/catalog", response_model=MetricCatalogDTO)
def metrics_catalog(
    department: str | None = Query(None, description="Фильтр по отделу, см. DEPARTMENTS"),
    graph: GraphPayload = Depends(get_graph),
) -> MetricCatalogDTO:
    """Каталог KPI: 33 записи, у каждой формула / источник / норма / отдел."""
    if department is not None and department not in DEPARTMENTS:
        raise HTTPException(
            status_code=400,
            detail=f"Неизвестный отдел: {department}. Допустимые: {', '.join(DEPARTMENTS)}",
        )
    nodes = {n.id: n.value_main for n in graph.nodes}
    items: list[MetricCatalogItemDTO] = []
    for raw in load_catalog():
        if department is not None and raw["department"] != department:
            continue
        data = dict(raw)
        data.pop("demo_value", None)  # служебное поле JSON, в DTO не отдаём
        value, available = _resolve_value(raw, nodes)
        items.append(MetricCatalogItemDTO(**data, value=value, available=available))
    return MetricCatalogDTO(total=len(items), department=department, items=items)