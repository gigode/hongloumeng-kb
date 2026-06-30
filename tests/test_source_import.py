import json

from scripts.kb import DATA_DIR, RAW_DIR


def test_chapter_metadata_shape():
    chapters = json.loads((DATA_DIR / "chapters.json").read_text(encoding="utf-8"))
    assert len(chapters) >= 5
    assert chapters[0]["id"] == "001"
    assert chapters[0]["title"]
    assert chapters[0]["paragraph_count"] >= 5


def test_raw_chapters_exist():
    chapters = json.loads((DATA_DIR / "chapters.json").read_text(encoding="utf-8"))
    for chapter in chapters[:5]:
        path = RAW_DIR.parents[1] / chapter["raw_path"]
        assert path.exists()
        assert path.read_text(encoding="utf-8").startswith("# ")
