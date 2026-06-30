from scripts.build_graph import build_graph


def test_graph_export_has_nodes_and_edges():
    graph = build_graph()
    assert len(graph["nodes"]) >= 30
    assert len(graph["edges"]) >= 40
    assert any(node["type"] == "event" for node in graph["nodes"])
    assert any(edge["type"] == "appears_in_event" for edge in graph["edges"])
