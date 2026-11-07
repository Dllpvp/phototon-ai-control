"""SQLite-журнал решений (§4.3 Readme.md).

Таблица `decisions` — единый источник правды по принятым решениям:
кто, что, когда, эффект и статус в Jira. Счётчик Jira-ключей
живёт в таблице `jira_counters` (PROD-{n}).

Путь к БД можно переопределить переменной окружения `FOTOPRINT_DB_PATH`
(удобно для тестов, чтобы не трогать рабочую state.db).
"""

import json
import os
import sqlite3
import uuid
from datetime import date, datetime
from pathlib import Path
from typing import Optional

from app.schemas import DecisionDTO

# Путь к БД: env-переменная или backend/state.db (не зависит от cwd)
_DEFAULT_DB_PATH = Path(__file__).resolve().parents[1] / "state.db"
DB_PATH = Path(os.environ.get("FOTOPRINT_DB_PATH", _DEFAULT_DB_PATH))

# Порядок колонок таблицы decisions. Читаем всегда по этому списку:
# у БД, созданных старой версией, порядок колонок другой.
_DECISION_COLUMNS: tuple[str, ...] = (
    "id",
    "scenario_id",
    "type",
    "params_json",
    "owner",
    "due_date",
    "status",
    "jira_key",
    "expected_effect_byn",
    "actual_effect_byn",
    "notes",
    "baseline_snapshot_json",
    "created_at",
)

# Колонки, которые добавляются миграцией в уже существующие таблицы.
_COLUMN_DDL: dict[str, str] = {
    "expected_effect_byn": "expected_effect_byn REAL DEFAULT 0.0",
    "actual_effect_byn": "actual_effect_byn REAL DEFAULT 0.0",
    "notes": "notes TEXT",
    "baseline_snapshot_json": "baseline_snapshot_json TEXT",
}


class DecisionStore:
    """Хранилище решений поверх SQLite. Таблицы: decisions, jira_counters."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = Path(db_path or os.environ.get("FOTOPRINT_DB_PATH", _DEFAULT_DB_PATH))
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS decisions (
                    id TEXT PRIMARY KEY,
                    scenario_id TEXT NOT NULL,
                    type TEXT NOT NULL,
                    params_json TEXT NOT NULL,
                    owner TEXT NOT NULL,
                    due_date TEXT NOT NULL,
                    status TEXT NOT NULL,
                    jira_key TEXT,
                    expected_effect_byn REAL DEFAULT 0.0,
                    actual_effect_byn REAL DEFAULT 0.0,
                    notes TEXT,
                    baseline_snapshot_json TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS jira_counters (
                    name TEXT PRIMARY KEY,
                    value INTEGER NOT NULL
                )
            """)
            self._migrate_decisions(conn)
            conn.commit()

    def _migrate_decisions(self, conn: sqlite3.Connection) -> None:
        """Добавляет отсутствующие колонки в существующие таблицы decisions.

        Идемпотентно: у старых БД колонки дописываются в конец таблицы, поэтому
        читать строки нужно только через список `_COLUMNS`, а не через `SELECT *`.
        """
        existing = {row[1] for row in conn.execute("PRAGMA table_info(decisions)")}
        for name, ddl in _COLUMN_DDL.items():
            if name not in existing:
                conn.execute(f"ALTER TABLE decisions ADD COLUMN {ddl}")

    # ── Jira-счётчик (PROD-{n}) ──────────────────────────────────────

    def next_jira_key(self, project: str = "PROD") -> str:
        """Инкрементирует счётчик `project` и возвращает ключ вида PROD-{n}."""
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                "SELECT value FROM jira_counters WHERE name = ?", (project,)
            )
            row = cur.fetchone()
            next_value = (row[0] + 1) if row else 1
            if row:
                conn.execute(
                    "UPDATE jira_counters SET value = ? WHERE name = ?",
                    (next_value, project),
                )
            else:
                conn.execute(
                    "INSERT INTO jira_counters (name, value) VALUES (?, ?)",
                    (project, next_value),
                )
            conn.commit()
        return f"{project}-{next_value}"

    # ── CRUD решений ─────────────────────────────────────────────────

    def create_decision(self, decision: DecisionDTO) -> DecisionDTO:
        """Сохраняет решение в БД, проставляет id и created_at."""
        decision_id = str(uuid.uuid4())
        params = json.dumps(decision.params)
        created = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO decisions (id, scenario_id, type, params_json, owner, due_date, status, jira_key, expected_effect_byn, actual_effect_byn, notes, baseline_snapshot_json, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (decision_id, decision.scenario_id, decision.type, params,
                 decision.owner, (decision.due_date.isoformat() if decision.due_date else ""), decision.verdict,
                 decision.jira_key, decision.expected_effect_byn, decision.actual_effect_byn,
                 decision.notes, json.dumps(decision.baseline_snapshot) if decision.baseline_snapshot else None,
                 created)
            )
            conn.commit()
        decision.id = decision_id
        decision.created_at = datetime.fromisoformat(created)
        return decision

    def get_decision(self, decision_id: str) -> Optional[DecisionDTO]:
        columns = ",".join(_DECISION_COLUMNS)
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(f"SELECT {columns} FROM decisions WHERE id = ?", (decision_id,))
            row = cur.fetchone()
            if not row:
                return None
            id_, scenario_id, type_, params_json, owner, due_date, status, jira_key, expected_effect, actual_effect, notes, baseline_snapshot_json, created_at = row
            return DecisionDTO(
                id=id_,
                scenario_id=scenario_id,
                type=type_,
                params=json.loads(params_json),
                owner=owner,
                due_date=date.fromisoformat(due_date) if due_date else None,
                verdict=status,
                jira_key=jira_key,
                expected_effect_byn=expected_effect,
                actual_effect_byn=actual_effect,
                notes=notes,
                baseline_snapshot=json.loads(baseline_snapshot_json) if baseline_snapshot_json else None,
                created_at=datetime.fromisoformat(created_at)
            )

    def list_decisions(self, scenario_id: Optional[str] = None) -> list[DecisionDTO]:
        columns = ",".join(_DECISION_COLUMNS)
        with sqlite3.connect(self.db_path) as conn:
            query = f"SELECT {columns} FROM decisions"
            params = []
            if scenario_id:
                query += " WHERE scenario_id = ?"
                params.append(scenario_id)
            cur = conn.execute(query, tuple(params))
            rows = cur.fetchall()
            decisions = []
            for row in rows:
                id_, sid, type_, params_json, owner, due_date, status, jira_key, expected_effect, actual_effect, notes, baseline_snapshot_json, created_at = row
                decisions.append(DecisionDTO(
                    id=id_,
                    scenario_id=sid,
                    type=type_,
                    params=json.loads(params_json),
                    owner=owner,
                    due_date=date.fromisoformat(due_date) if due_date else None,
                    verdict=status,
                    jira_key=jira_key,
                    expected_effect_byn=expected_effect,
                    actual_effect_byn=actual_effect,
                    notes=notes,
                    baseline_snapshot=json.loads(baseline_snapshot_json) if baseline_snapshot_json else None,
                    created_at=datetime.fromisoformat(created_at)
                ))
            return decisions

    def update_jira_key(self, decision_id: str, jira_key: str) -> None:
        """Проставляет jira_key после создания тикета."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE decisions SET jira_key = ? WHERE id = ?",
                (jira_key, decision_id),
            )
            conn.commit()

    def update_decision_effect(self, decision_id: str, effect_byn: float, verdict: str) -> None:
        """Обновляет фактический эффект и вердикт после симуляции."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE decisions SET actual_effect_byn = ?, status = ? WHERE id = ?",
                (effect_byn, verdict, decision_id)
            )
            conn.commit()