"""Тесты структуры графа причин: backend/data/graph.json (§6 Readme.md)."""

import json
from pathlib import Path

import networkx as nx

GRAPH_JSON = Path(__file__).resolve().parents[1] / "data" / "graph.json"

EXPECTED_NODE_IDS = {
    "fin_margin",
    "fin_loss_day",
    "fin_revenue_week",
    "sales_sla_breach",
    "sales_b2b_orders",
    "sales_b2c_churn_risk",
    "sales_client7_margin",
    "prod_downtime_l2",
    "prod_print_queue",
    "prod_reprint_volume",
    "quality_defect_rate",
    "hr_operators_s3",
    "hr_overtime_s3",
    "hr_turnover",
    "equip_lamination_wear",
    "season_week_coeff",
    "season_peak_risk",
    "fin_ondemand_margin",
}

EXPECTED_LEAVES = {
    "hr_operators_s3",
    "equip_lamination_wear",
    "season_week_coeff",
    "hr_turnover",
    "sales_client7_margin",
}


def load_graph_payload() -> dict:
    with open(GRAPH_JSON, encoding="utf-8") as f:
        return json.load(f)


def build_digraph(payload: dict) -> nx.DiGraph:
    graph = nx.DiGraph()
    for node in payload["nodes"]:
        graph.add_node(node["id"])
    for edge in payload["edges"]:
        graph.add_edge(edge["from"], edge["to"])
    return graph


def find_leaves(graph: nx.DiGraph, payload: dict) -> list[str]:
    """Корневые причины (§6.5).

    Список §6.5 включает `hr_operators_s3` и `sales_client7_margin`, у которых по
    таблице §6.2 всё же есть входящие рёбра, поэтому корни задаются явно в
    `root_causes` и объединяются с узлами без входящих рёбер.
    """
    leaves = {node for node in graph.nodes if graph.in_degree(node) == 0}
    leaves.update(payload.get("root_causes", []))
    return sorted(leaves)


def test_graph_file_exists() -> None:
    assert GRAPH_JSON.is_file(), f"Нет файла: {GRAPH_JSON}"


def test_graph_has_18_nodes_and_17_edges() -> None:
    payload = load_graph_payload()
    graph = build_digraph(payload)
    assert len(payload["nodes"]) == 18
    assert len(payload["edges"]) == 17
    assert graph.number_of_nodes() == 18
    assert graph.number_of_edges() == 17


def test_node_ids_match_readme_section_6_1() -> None:
    payload = load_graph_payload()
    actual = {node["id"] for node in payload["nodes"]}
    assert actual == EXPECTED_NODE_IDS


def test_graph_is_dag() -> None:
    payload = load_graph_payload()
    graph = build_digraph(payload)
    assert nx.is_directed_acyclic_graph(graph) is True
    assert list(nx.topological_sort(graph))


def test_leaves_are_root_causes() -> None:
    payload = load_graph_payload()
    graph = build_digraph(payload)
    leaves = set(find_leaves(graph, payload))
    assert EXPECTED_LEAVES.issubset(leaves)


def test_edge_special_case_operators_to_downtime() -> None:
    payload = load_graph_payload()
    edge = next(
        e for e in payload["edges"]
        if e["from"] == "hr_operators_s3" and e["to"] == "prod_downtime_l2"
    )
    assert edge["weight"] == 3.0
    assert edge["curvature"] == 0.75


def test_path_hint_chain_main() -> None:
    payload = load_graph_payload()
    hints = payload["path_hints"]
    assert any(h["id"] == "chain_main" for h in hints)
    chain = next(h for h in hints if h["id"] == "chain_main")
    assert chain["path"] == [
        "fin_margin",
        "sales_sla_breach",
        "prod_downtime_l2",
        "hr_operators_s3",
    ]


def test_edges_reference_existing_nodes() -> None:
    payload = load_graph_payload()
    node_ids = {node["id"] for node in payload["nodes"]}
    for edge in payload["edges"]:
        assert edge["from"] in node_ids, f"Неизвестный узел: {edge['from']}"
        assert edge["to"] in node_ids, f"Неизвестный узел: {edge['to']}"


def test_node_required_fields() -> None:
    payload = load_graph_payload()
    required = {"id", "domain", "name", "unit", "value_main", "norm", "status_main", "cost_per_day"}
    for node in payload["nodes"]:
        missing = required - set(node.keys())
        assert not missing, f"Узел {node['id']} не имеет полей: {missing}"
        assert node["domain"] in {"finance", "clients", "production", "hr", "quality", "season"}
        assert node["status_main"] in {"red", "yellow", "green"}


def test_edge_required_fields() -> None:
    payload = load_graph_payload()
    required = {"from", "to", "sign", "weight", "lag_days", "note", "curvature"}
    for edge in payload["edges"]:
        missing = required - set(edge.keys())
        assert not missing, f"Ребро {edge['from']}->{edge['to']} не имеет полей: {missing}"
        assert edge["sign"] in (-1, 1)
        assert edge["weight"] > 0
        assert edge["lag_days"] >= 0
