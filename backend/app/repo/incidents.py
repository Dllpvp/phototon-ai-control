
"""T22 — хранилище инцидентов (ТЗ T22). Паттерн DecisionStore, db.py не трогаем.

Дедупликация на уровне БД: частичный UNIQUE-индекс по cause_key среди открытых
инцидентов. Повторный красный KPI с тем же cause_key отклоняется SQLite.
Статусы по ТЗ: open / acknowledged / resolved. Итог обработки — resolution.
"""

from __future__ import annotations

import os
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path

from app.core.monitor import IncidentDraft
from app.schemas import IncidentDTO

_DEFAULT_DB_PATH = Path(__file__).resolve().parents[2] / "state.db"

_COLUMNS = (
    "id", "cause_key", "node_id", "title", "value", "unit", "root_cause",
    "recommendation", "status", "resolution", "created_at", "updated_at",
)


class IncidentsStore:
    """Таблица incidents в общем state.db (путь — FOTOPRINT_DB_PATH)."""

    def __init__(self, db_path: Path | None = None):
        self.db_path = Path(db_path or os.environ.get("FOTOPRINT_DB_PATH", _DEFAULT_DB_PATH))
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS incidents (
                    id TEXT PRIMARY KEY,
                    cause_key TEXT NOT NULL,
                    node_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    value REAL NOT NULL,
                    unit TEXT NOT NULL,
                    root_cause TEXT NOT NULL,
                    recommendation TEXT NOT NULL,
                    status TEXT NOT NULL,
                    resolution TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT
                )
            """)
            conn.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS ux_incidents_open_cause
                ON incidents(cause_key) WHERE status = 'open'
            """)
            conn.commit()

    def _row_to_dto(self, row: tuple) -> IncidentDTO:
        data = dict(zip(_COLUMNS, row))
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        if data["updated_at"]:
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        return IncidentDTO(**data)

    def create(self, draft: IncidentDraft) -> IncidentDTO | None:
        """Создать открытый инцидент. None → дубль cause_key, запись отклонена."""
        incident_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                "INSERT OR IGNORE INTO incidents "
                "(id, cause_key, node_id, title, value, unit, root_cause, recommendation, "
                " status, resolution, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'open', NULL, ?, NULL)",
                (incident_id, draft.cause_key, draft.node_id, draft.title, draft.value,
                 draft.unit, draft.root_cause, draft.recommendation, now),
            )
            conn.commit()
            if cur.rowcount == 0:
                return None
        return self.get(incident_id)

    def get(self, incident_id: str) -> IncidentDTO | None:
        cols = ", ".join(_COLUMNS)
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                f"SELECT {cols} FROM incidents WHERE id = ?", (incident_id,)
            ).fetchone()
        return self._row_to_dto(row) if row else None

    def list(self, status: str | None = None) -> list[IncidentDTO]:
        cols = ", ".join(_COLUMNS)
        query = f"SELECT {cols} FROM incidents"
        params: tuple = ()
        if status:
            query += " WHERE status = ?"
            params = (status,)
        query += " ORDER BY created_at DESC, cause_key"
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(query, params).fetchall()
        return [self._row_to_dto(r) for r in rows]

    def count_open(self) -> int:
        with sqlite3.connect(self.db_path) as conn:
            return conn.execute("SELECT COUNT(*) FROM incidents WHERE status = 'open'").fetchone()[0]

    def decide(self, incident_id: str, accept: bool) -> IncidentDTO | None:
        """Принять → acknowledged+accepted, отклонить → resolved+rejected.

        Только фиксация решения человека. Никакого исполнения решения здесь нет.
        """
        status = "acknowledged" if accept else "resolved"
        resolution = "accepted" if accept else "rejected"
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                "UPDATE incidents SET status = ?, resolution = ?, updated_at = ? "
                "WHERE id = ? AND status = 'open'",
                (status, resolution, now, incident_id),
            )
            conn.commit()
            if cur.rowcount == 0:
                return None
        return self.get(incident_id)
