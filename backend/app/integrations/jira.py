"""Мок-Jira: генерация ключей PROD-{n} (§4.4 Readme.md).

Реального HTTP-вызова к Jira нет — ключ формируется из счётчика
в SQLite (`DecisionStore.next_jira_key`). Этого достаточно для демо:
ключ выглядит как настоящий и уникален.
"""

from __future__ import annotations

from app.db import DecisionStore


class JiraClient:
    """Минимальный клиент Jira-мока. next_key() -> "PROD-{n}"."""

    def __init__(self, store: DecisionStore, project: str = "PROD"):
        self._store = store
        self._project = project

    def next_key(self) -> str:
        """Возвращает следующий ключ тикета, инкрементируя счётчик в БД."""
        return self._store.next_jira_key(self._project)


def get_jira_client(store: DecisionStore) -> JiraClient:
    """Фабрика для FastAPI-dependency."""
    return JiraClient(store)
