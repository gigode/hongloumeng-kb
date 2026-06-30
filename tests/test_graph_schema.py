from scripts.validate_graph_data import validate


def test_graph_data_validates():
    assert validate() == []
