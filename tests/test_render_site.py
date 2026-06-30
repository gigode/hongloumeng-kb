from pathlib import Path

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
