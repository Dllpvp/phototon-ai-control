
"""T20 — Migration Layer (PLAN-V2 §22.6): карта источников + демо-миграция.

Реальный перенос данных — после получения доступов от заказчика.
Сейчас: контракт источников (JSON) + детерминированный demo-run на 6 шагов.
Шаги PII scan / Map to graph / Validate anchors делают настоящую работу,
Extract / Tokenize / Dashboard — эмуляция (бейдж mode=emulator).
Журнал — своя таблица migration_runs (паттерн DecisionStore, db.py не трогаем).
"""

from __future__ import annotations

import json
import os
import sqlite3
import uuid
from datetime import datetime
from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, Depends

from app.core.anchors import validate_anchors
from app.core.loader import GraphPayload
from app.dependencies import get_graph
from app.schemas import MigrationRunDTO, MigrationSourceDTO, MigrationStepDTO

router = APIRouter(tags=["migration"])

_SOURCES_PATH = Path(__file__).resolve().parents[1] / "data" / "migration_sources.json"
# Тот же state.db, что у DecisionStore; путь переопределяется FOTOPRINT_DB_PATH (тесты)
_DEFAULT_DB_PATH = Path(__file__).resolve().parents[2] / "state.db"


@lru_cache(maxsize=1)
def load_sources() -> list[dict]:
    """Карта источников с диска (один раз). Файл версионируется, не генерируется."""
    raw = json.loads(_SOURCES_PATH.read_text(encoding="utf-8"))
    return raw["sources"]


class MigrationStore:
    """Журнал демо-миграций: таблица migration_runs в общем state.db."""

    def __init__(self, db_path: Path | None = None):
        self.db_path = Path(db_path or os.environ.get("FOTOPRINT_DB_PATH", _DEFAULT_DB_PATH))
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS migration_runs (
                    id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    status TEXT NOT NULL,
                    sources_count INTEGER NOT NULL,
                    pii_sources INTEGER NOT NULL,
                    steps_json TEXT NOT NULL
                )
            """)
            conn.commit()

    def save_run(self, run: MigrationRunDTO) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO migration_runs (id, created_at, status, sources_count, pii_sources, steps_json) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (run.run_id, run.created_at.isoformat(), run.status, run.sources_count,
                 run.pii_sources, json.dumps([s.model_dump() for s in run.steps], ensure_ascii=False)),
            )
            conn.commit()

    def count_runs(self) -> int:
        with sqlite3.connect(self.db_path) as conn:
            return conn.execute("SELECT COUNT(*) FROM migration_runs").fetchone()[0]


def _build_steps(sources: list[dict], graph: GraphPayload) -> list[MigrationStepDTO]:
    """6 шагов §22.6. Все счётчики выводятся из данных, не хардкодятся."""
    extracted = [s for s in sources if s["migration_status"] != "pending_access"]
    skipped = [s["name"] for s in sources if s["migration_status"] == "pending_access"]
    pii = [s for s in sources if s["pii_level"] != "none"]
    objects_total = sum(len(s["objects"]) for s in extracted)
    departments = sorted({s["department"] for s in sources})

    steps = [
        MigrationStepDTO(
            n=1, key="extract", title="Extract", status="completed", mode="emulator",
            detail=f"Извлечено {len(extracted)}/{len(sources)} источников, {objects_total} типов объектов; "
                   f"пропущены (pending_access): {', '.join(skipped) or 'нет'}",
        ),
        MigrationStepDTO(
            n=2, key="pii_scan", title="PII scan", status="completed", mode="real",
            detail=f"PII найдены в {len(pii)} источниках: {', '.join(s['name'] for s in pii)}",
        ),
        MigrationStepDTO(
            n=3, key="tokenize", title="Tokenize", status="completed", mode="emulator",
            detail=f"Токенизировано {len(pii)} источников ([CLIENT_*], [EMP_*]); vault локальный, наружу не уходит",
        ),
        MigrationStepDTO(
            n=4, key="map_to_graph", title="Map to graph", status="completed", mode="real",
            detail=f"Сопоставлено с графом причин: {len(graph.nodes)} узлов, {len(graph.edges)} рёбер",
        ),
    ]
    # Шаг 5 — настоящая проверка якорей v1, не заглушка
    try:
        validate_anchors()
        steps.append(MigrationStepDTO(
            n=5, key="validate_anchors", title="Validate anchors", status="completed", mode="real",
            detail="validate_anchors() пройден: числа v1 сходятся",
        ))
    except AssertionError as e:
        steps.append(MigrationStepDTO(
            n=5, key="validate_anchors", title="Validate anchors", status="failed", mode="real",
            detail=f"Якоря не сошлись: {e}",
        ))
    ok = all(s.status == "completed" for s in steps)
    steps.append(MigrationStepDTO(
        n=6, key="dashboard_generated", title="Dashboard generated",
        status="completed" if ok else "skipped", mode="emulator",
        detail=f"Дашборд собран по {len(departments)} отделам: {', '.join(departments)}",
    ))
    return steps


@router.get("/migration/sources", response_model=list[MigrationSourceDTO])
def migration_sources() -> list[MigrationSourceDTO]:
    """8 источников (§22.6). Битрикс24 = pending_access, у каждого указан pii_level."""
    return [MigrationSourceDTO(**s) for s in load_sources()]


@router.post("/migration/demo-run", response_model=MigrationRunDTO)
def migration_demo_run(graph: GraphPayload = Depends(get_graph)) -> MigrationRunDTO:
    """Демо-миграция: 6 шагов, детерминированно, офлайн. Запись в migration_runs."""
    sources = load_sources()
    steps = _build_steps(sources, graph)
    status = "completed" if all(s.status == "completed" for s in steps) else "failed"
    run = MigrationRunDTO(
        run_id=str(uuid.uuid4()),
        status=status,
        created_at=datetime.now(),
        sources_count=len(sources),
        pii_sources=sum(1 for s in sources if s["pii_level"] != "none"),
        steps=steps,
    )
    MigrationStore().save_run(run)
    return run
