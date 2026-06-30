from pathlib import Path

from scripts.kb import RAW_DIR, TAGGED_DIR, strip_tags


def test_tagged_text_strips_back_to_raw_body():
    tagged_files = sorted(TAGGED_DIR.glob("*.tagged.md"))
    assert tagged_files
    for tagged in tagged_files:
        raw = RAW_DIR / tagged.name.replace(".tagged.md", ".md")
        assert raw.exists()
        assert strip_tags(tagged.read_text(encoding="utf-8")) == raw.read_text(encoding="utf-8")


def test_all_tagged_files_have_paragraph_ids():
    for path in sorted(TAGGED_DIR.glob("*.tagged.md")):
        text = path.read_text(encoding="utf-8")
        assert "[1]" in text
