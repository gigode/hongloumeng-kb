from pathlib import Path

from scripts.kb import TAG_TYPES
from scripts.render_site import DOCS_DIR


def test_rendered_site_files_exist():
    assert (DOCS_DIR / "index.html").exists()
    assert (DOCS_DIR / "chapters" / "001.html").exists()
    assert (DOCS_DIR / "graph" / "index.html").exists()


def test_reader_has_highlight_toggle():
    html = (DOCS_DIR / "chapters" / "001.html").read_text(encoding="utf-8")
    assert "data-highlight-toggle" in html
    assert "class=\"entity" in html


def test_graph_uses_chinese_relation_labels():
    script = (DOCS_DIR / "graph" / "graph.js").read_text(encoding="utf-8")
    html = (DOCS_DIR / "graph" / "index.html").read_text(encoding="utf-8")
    assert "父母子女" in script
    assert "人物出场于事件" in script
    assert "option.textContent = labelForRelation(type)" in script
    assert "graph.js?v=" in html


def test_entity_category_pages_have_stats_and_notes():
    for entity_type, label, _css_class in TAG_TYPES.values():
        html = (DOCS_DIR / "entities" / f"{entity_type}.html").read_text(encoding="utf-8")
        assert label in html
        assert "分类统计" in html
        assert "关系读法" in html
        assert "详细注释" in html
        assert "资料依据" in html
        assert "entity-note-card" in html
        assert "source-list" in html
