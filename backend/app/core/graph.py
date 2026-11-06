"""Интерфейс доступа к графу причин из core/ (§4.1, §6 Readme.md).

Чистая обёртка над `loader.load_graph()`: предоставляет `out_edges(node_id)`
и `in_edges(node_id)` для обхода графа в `impact.py` и других модулях ядра.
Не содержит математики — только навигация по рёбрам.
"""

from __future__ import annotations

from collections import defaultdict

from app.core.loader import GraphEdgePayload, GraphPayload, load_graph


class GraphView:
    """Удобный доступ к рёбрам графа: out_edges / in_edges по id узла."""

    def __init__(self, payload: GraphPayload) -> None:
        self._payload = payload
        self._out: dict[str, list[GraphEdgePayload]] = defaultdict(list)
        self._in: dict[str, list[GraphEdgePayload]] = defaultdict(list)
        for edge in payload.edges:
            self._out[edge.from_].append(edge)
            self._in[edge.to].append(edge)

    @property
    def payload(self) -> GraphPayload:
        return self._payload

    def out_edges(self, node_id: str) -> list[GraphEdgePayload]:
        """Все исходящие рёбра из узла `node_id`."""
        return self._out.get(node_id, [])

    def in_edges(self, node_id: str) -> list[GraphEdgePayload]:
        """Все входящие рёбра в узел `node_id`."""
        return self._in.get(node_id, [])

    def node_ids(self) -> list[str]:
        return [n.id for n in self._payload.nodes]

    def get_node(self, node_id: str):
        """Узел по id или None."""
        for n in self._payload.nodes:
            if n.id == node_id:
                return n
        return None


_graph_view: GraphView | None = None


def get_graph() -> GraphView:
    """Ленивая инициализация единственного экземпляра GraphView."""
    global _graph_view
    if _graph_view is None:
        _graph_view = GraphView(load_graph())
    return _graph_view
