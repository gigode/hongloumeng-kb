from scripts.build_entity_index import build_entity_index
from scripts.kb import extract_tags


def test_extract_person_tag():
    tags = list(extract_tags("〖@宝玉|贾宝玉〗见〖@黛玉|林黛玉〗"))
    assert tags[0]["type"] == "person"
    assert tags[0]["surface"] == "宝玉"
    assert tags[0]["canonical"] == "贾宝玉"
    assert tags[1]["canonical"] == "林黛玉"


def test_build_entity_index_has_core_people():
    data = build_entity_index()
    entities = data["entities"]
    assert "person:贾宝玉" in entities
    assert "person:林黛玉" in entities
    assert entities["person:贾宝玉"]["count"] > 0
