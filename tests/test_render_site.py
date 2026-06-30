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
