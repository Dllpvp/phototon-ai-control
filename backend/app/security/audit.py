"""Журнал аудита ИИ-вызовов (T9d, PLAN-V2 §6.5).

Таблица ai_audit хранит только маскированные payload'ы и sha256 сырого входа.
Сырой payload функция НЕ принимает и НЕ сохраняет.
"""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from app.config import settings
from app.schemas import AuditDTO

# Путь к БД (тот же, что decisions) — env или backend/state.db
_DEFAULT_DB_PATH = Path(__file__).resolve().parents[1] / "state.db"
DB_PATH = Path(os.environ.get("FOTOPRINT_DB_PATH", _DEFAULT_DB_PATH))


def _init_ai_audit_table(conn: sqlite3.Connection) -> None:
    """Создаёт таблицу ai_audit, если её нет. Идемпотентно."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ai_audit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            backend TEXT NOT NULL,
            mask_level TEXT NOT NULL,
            tokens_count INTEGER NOT NULL,
            payload_masked_json TEXT NOT NULL,
            payload_sha256 TEXT NOT NULL,
            verdict TEXT NOT NULL,
            reason TEXT
        )
    """)


def _get_conn() -> sqlite3.Connection:
    """Открывает соединение к БД, гарантирует наличие таблицы."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    _init_ai_audit_table(conn)
    return conn


def _default_mask_level() -> str:
    """Возвращает mask_level из settings (MASK_LEVEL, T9e) или 'strict' как фолбэк."""
    try:
        return settings.mask_level
    except AttributeError:
        return "strict"


def log_call(
    backend: str,
    mask_level: Optional[str] = None,
    tokens_count: int = 0,
    payload_masked_json: str = "",
    payload_sha256: str = "",
    verdict: str = "allow",
    reason: Optional[str] = None,
) -> int:
    """
    Записывает строку аудита. Возвращает id вставленной записи.

    Параметры:
    - backend: "deepseek" | "fallback" | "cache"
    - mask_level: "strict" | "standard" | "full" | "none" | "partial"
    - tokens_count: количество токенов в запросе
    - payload_masked_json: УЖЕ замаскированный JSON-стринг (сырого текста здесь нет)
    - payload_sha256: sha256 от сырого payload (hex, 64 символа) — хэш передаёт вызывающий
    - verdict: "allow" | "deny" | "error" | "fallback"
    - reason: опционально, детали (например, "rate_limit", "invalid_json", "injection detected")

    Функция НЕ логирует сырой текст в stdout/stderr.
    """
    ts = datetime.now(timezone.utc).isoformat()
    level = mask_level if mask_level is not None else _default_mask_level()

    with _get_conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO ai_audit (ts, backend, mask_level, tokens_count,
                                  payload_masked_json, payload_sha256, verdict, reason)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (ts, backend, level, tokens_count, payload_masked_json, payload_sha256, verdict, reason),
        )
        conn.commit()
        return cur.lastrowid


def list_last(limit: int = 10) -> list[AuditDTO]:
    """Возвращает последние `limit` записей аудита по убыванию id (новые — первые)."""
    if limit <= 0:
        return []
    with _get_conn() as conn:
        cur = conn.execute(
            """
            SELECT id, ts, backend, mask_level, tokens_count,
                   payload_masked_json, payload_sha256, verdict, reason
            FROM ai_audit
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = cur.fetchall()

    result = []
    for row in rows:
        result.append(
            AuditDTO(
                id=row["id"],
                ts=datetime.fromisoformat(row["ts"].replace("Z", "+00:00")),
                backend=row["backend"],
                mask_level=row["mask_level"],
                tokens_count=row["tokens_count"],
                payload_masked_json=row["payload_masked_json"],
                payload_sha256=row["payload_sha256"],
                verdict=row["verdict"],
                reason=row["reason"],
            )
        )
    return result


def compute_sha256(data: str) -> str:
    """Утилита для вызывающих: sha256 hex от строки."""
    return hashlib.sha256(data.encode("utf-8")).hexdigest()