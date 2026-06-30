from __future__ import annotations

import json
import re
import shutil
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.kb import (
    DATA_DIR,
    DOCS_DIR,
    TAGGED_DIR,
    TAG_TYPES,
    TAG_PATTERN,
    chapter_file_stem,
    escape_html,
    iter_paragraphs,
    parse_tag,
    read_json,
)

TYPE_FILES = {
    "person": "person.html",
    "place": "place.html",
    "household": "household.html",
    "role": "role.html",
    "object": "object.html",
    "text": "text.html",
    "concept": "concept.html",
    "time": "time.html",
}
SITE_ASSET_VERSION = "20260630-strong-highlights-v1"
GRAPH_ASSET_VERSION = "20260630-cn-relations-v2"


def page(title: str, body: str, current: str = "", root_prefix: str = "") -> str:
    nav_items = [
        ("index.html", "总览"),
        ("chapters/001.html", "阅读"),
        ("entities/person.html", "实体"),
        ("graph/index.html", "图谱"),
        ("plans/2026-06-30-hongloumeng-kb.html", "计划"),
    ]
    nav = "\n".join(
        f'<a class="{"active" if label == current else ""}" href="{root_prefix}{href}">{label}</a>'
        for href, label in nav_items
    )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape_html(title)}</title>
  <link rel="stylesheet" href="{root_prefix}css/styles.css?v={SITE_ASSET_VERSION}">
</head>
<body>
  <header class="topbar">
    <a class="brand" href="{root_prefix}index.html">红楼梦知识图谱</a>
    <nav>{nav}</nav>
  </header>
  {body}
  <script>
    const toggle = document.querySelector('[data-highlight-toggle]');
    if (toggle) {{
      const saved = localStorage.getItem('hlm-highlight') !== 'off';
      document.body.classList.toggle('no-highlight', !saved);
      toggle.checked = saved;
      toggle.addEventListener('change', () => {{
        document.body.classList.toggle('no-highlight', !toggle.checked);
        localStorage.setItem('hlm-highlight', toggle.checked ? 'on' : 'off');
      }});
    }}
  </script>
</body>
</html>
"""


def render_marked_text(text: str) -> str:
    out = []
    pos = 0
    for match in TAG_PATTERN.finditer(text):
        out.append(escape_html(text[pos:match.start()]))
        tag, raw = match.group(1), match.group(2)
        surface, canonical = parse_tag(raw)
        entity_type, label, css_class = TAG_TYPES[tag]
        href = f"../entities/{TYPE_FILES[entity_type]}#{escape_html(canonical)}"
        out.append(
            f'<a class="entity {css_class}" href="{href}" title="{label}: {escape_html(canonical)}">'
            f"{escape_html(surface)}</a>"
        )
        pos = match.end()
    out.append(escape_html(text[pos:]))
    return "".join(out)


def parse_chapter_file(path: Path) -> dict:
    content = path.read_text(encoding="utf-8")
    title = path.stem.replace(".tagged", "")
    first = content.splitlines()[0] if content.splitlines() else title
    m = re.match(r"#\s+\[(\d+)\]\s+(.+)$", first)
    chapter_id = m.group(1) if m else path.name.split("_", 1)[0]
    chapter_title = m.group(2) if m else title
    return {
        "id": chapter_id,
        "title": chapter_title,
        "paragraphs": list(iter_paragraphs(content)),
    }


def render_chapter(chapter: dict, prev_id: str | None, next_id: str | None) -> str:
    lines = []
    for pid, body in chapter["paragraphs"]:
        anchor = pid.replace(".", "-")
        lines.append(
            f'<p id="p-{anchor}" class="chapter-para">'
            f'<a class="pn" href="#p-{anchor}">[{escape_html(pid)}]</a> '
            f"{render_marked_text(body)}</p>"
        )
    prev_link = f'<a href="{prev_id}.html">上一回</a>' if prev_id else "<span>上一回</span>"
    next_link = f'<a href="{next_id}.html">下一回</a>' if next_id else "<span>下一回</span>"
    body = f"""
<main class="reader-shell">
  <aside class="reader-aside">
    <div class="chapter-kicker">第 {chapter['id']} 回</div>
    <h1>{escape_html(chapter['title'])}</h1>
    <label class="switch"><input type="checkbox" data-highlight-toggle checked><span>实体高亮</span></label>
    <div class="chapter-nav">{prev_link}{next_link}</div>
    <div class="legend">
      {''.join(f'<span class="legend-item {v[2]}">{v[1]}</span>' for v in TAG_TYPES.values())}
    </div>
  </aside>
  <article class="chapter-text">
    {''.join(lines)}
  </article>
</main>
"""
    return page(f"{chapter['id']} {chapter['title']}", body, current="阅读", root_prefix="../")


def _type_label(entity_type: str) -> str:
    return next((v[1] for v in TAG_TYPES.values() if v[0] == entity_type), entity_type)


def _type_class(entity_type: str) -> str:
    return next((v[2] for v in TAG_TYPES.values() if v[0] == entity_type), entity_type)


def _entity_note(notes: dict, entity: dict) -> dict:
    return notes.get("entities", {}).get(f'{entity["type"]}:{entity["name"]}', {})


def _source_links(notes: dict, source_ids: list[str]) -> str:
    sources = notes.get("sources", {})
    items = []
    for source_id in source_ids:
        source = sources.get(source_id)
        if not source:
            continue
        label = escape_html(source["label"])
        note = escape_html(source.get("note", ""))
        url = escape_html(source["url"])
        items.append(f'<li><a href="{url}" target="_blank" rel="noreferrer">{label}</a><span>{note}</span></li>')
    if not items:
        return '<p class="muted">本条暂无外部资料说明，先以原文段落为准。</p>'
    return f'<ul class="source-list">{"".join(items)}</ul>'


def _refs(entity: dict, limit: int = 8) -> str:
    links = []
    for ref in entity["refs"][:limit]:
        chapter_html = f"../chapters/{ref['chapter']}.html#p-{ref['paragraph'].replace('.', '-')}"
        links.append(f'<a href="{chapter_html}">{escape_html(ref["chapter"])} [{escape_html(ref["paragraph"])}]</a>')
    return " ".join(links) if links else '<span class="muted">暂无段落引用</span>'


def _stat_card(value: int | str, label: str) -> str:
    return f"<div><strong>{escape_html(str(value))}</strong><span>{escape_html(label)}</span></div>"


def _detail_card(entity: dict, notes: dict) -> str:
    note = _entity_note(notes, entity)
    aliases = "、".join(entity["aliases"]) if entity["aliases"] else "无"
    chapters = sorted({ref["chapter"] for ref in entity["refs"]})
    summary = note.get(
        "summary",
        f"该条目在试点前五回出现 {entity['count']} 次，覆盖 {len(chapters)} 回。当前以原文自动标注为主，后续可继续补充研究注释。",
    )
    relation_notes = note.get(
        "relation_notes",
        ["可先从出现段落回到原文，观察它与同段人物、地点、物件或概念的共现关系。"],
    )
    relation_items = "".join(f"<li>{escape_html(item)}</li>" for item in relation_notes)
    source_block = _source_links(notes, note.get("source_ids", []))
    return f"""
<article class="entity-note-card {escape_html(_type_class(entity['type']))}" id="{escape_html(entity['name'])}">
  <div class="entity-note-top">
    <h3>{escape_html(entity['name'])}</h3>
    <span>{entity['count']} 次 / {len(chapters)} 回</span>
  </div>
  <p>{escape_html(summary)}</p>
  <dl>
    <div><dt>别名</dt><dd>{escape_html(aliases)}</dd></div>
    <div><dt>原文</dt><dd>{_refs(entity, limit=6)}</dd></div>
  </dl>
  <h4>关系提示</h4>
  <ul class="compact-list">{relation_items}</ul>
  <h4>资料依据</h4>
  {source_block}
</article>
"""


def render_entity_pages(entities: dict, chapters: dict[str, str], notes: dict) -> None:
    out_dir = DOCS_DIR / "entities"
    out_dir.mkdir(parents=True, exist_ok=True)
    grouped = defaultdict(list)
    for entity in entities.values():
        grouped[entity["type"]].append(entity)

    tabs = "".join(
        f'<a class="{TAG_TYPES[tag][2]}" href="{TYPE_FILES[TAG_TYPES[tag][0]]}">{TAG_TYPES[tag][1]}</a>'
        for tag in TAG_TYPES
    )

    for entity_type, html_file in TYPE_FILES.items():
        entries = sorted(grouped.get(entity_type, []), key=lambda e: (-e["count"], e["name"]))
        label = _type_label(entity_type)
        category_note = notes.get("categories", {}).get(entity_type, {})
        total_mentions = sum(entity["count"] for entity in entries)
        covered_chapters = sorted({ref["chapter"] for entity in entries for ref in entity["refs"]})
        noted = sum(1 for entity in entries if _entity_note(notes, entity))
        top_name = entries[0]["name"] if entries else "暂无"

        stat_items = "".join(
            [
                _stat_card(len(entries), "条目"),
                _stat_card(total_mentions, "高亮次数"),
                _stat_card(len(covered_chapters), "覆盖回数"),
                _stat_card(noted, "已有详注"),
                _stat_card(top_name, "最高频条目"),
            ]
        )
        lens_items = "".join(f"<li>{escape_html(item)}</li>" for item in category_note.get("relationship_lens", []))
        source_block = _source_links(notes, category_note.get("source_ids", []))

        detail_cards = "".join(_detail_card(entity, notes) for entity in entries)
        rows = []
        for entity in entries:
            aliases = "、".join(entity["aliases"]) if entity["aliases"] else "无"
            rows.append(
                f'<tr><td><a href="#{escape_html(entity["name"])}"><strong>{escape_html(entity["name"])}</strong></a>'
                f'<div class="muted">{escape_html(aliases)}</div></td><td>{entity["count"]}</td>'
                f'<td>{_refs(entity, limit=12)}</td></tr>'
            )

        body = f"""
<main class="workbench">
  <section class="section-head">
    <p class="eyebrow">实体分类 / {escape_html(entity_type)}</p>
    <h1>{escape_html(label)}</h1>
    <p>{escape_html(category_note.get("description", "该分类由前五回自动标注生成，按出现次数和段落引用整理。"))}</p>
    <div class="category-tabs">{tabs}</div>
  </section>

  <h2>分类统计</h2>
  <section class="category-stats">{stat_items}</section>

  <section class="note-panel">
    <div>
      <h2>关系读法</h2>
      <ul class="compact-list">{lens_items}</ul>
    </div>
    <div>
      <h2>资料依据</h2>
      {source_block}
    </div>
  </section>

  <section>
    <h2>详细注释</h2>
    <div class="entity-note-grid">{detail_cards}</div>
  </section>

  <section>
    <h2>索引表</h2>
    <div class="table-wrap"><table><thead><tr><th>实体</th><th>次数</th><th>引用</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div>
  </section>
</main>
"""
        (out_dir / html_file).write_text(page(f"{label}索引", body, current="实体", root_prefix="../"), encoding="utf-8")

    index_items = "".join(
        f'<a class="entity-tile {TAG_TYPES[tag][2]}" href="{TYPE_FILES[TAG_TYPES[tag][0]]}">'
        f'<span>{TAG_TYPES[tag][1]}</span><strong>{len(grouped.get(TAG_TYPES[tag][0], []))}</strong>'
        f'<em>{escape_html(notes.get("categories", {}).get(TAG_TYPES[tag][0], {}).get("title", TAG_TYPES[tag][1]))}</em></a>'
        for tag in TAG_TYPES
    )
    index_body = f"""
<main class="workbench">
  <section class="section-head">
    <p class="eyebrow">Index</p>
    <h1>实体索引</h1>
    <p>首版从前五回抽取八类实体：人物、地点、府系、身份、物件、诗文、概念、时间。每个分类页都包含统计、关系读法、详细注释和外部资料依据。</p>
  </section>
  <section class="entity-grid">{index_items}</section>
</main>
"""
    (out_dir / "index.html").write_text(page("实体索引", index_body, current="实体", root_prefix="../"), encoding="utf-8")


def render_graph_page() -> None:
    graph_dir = DOCS_DIR / "graph"
    graph_dir.mkdir(parents=True, exist_ok=True)
    body = f"""
<main class="graph-shell">
  <section class="graph-panel">
    <p class="eyebrow">Graph Explorer</p>
    <h1>前五回关系图</h1>
    <div class="controls">
      <input id="graph-search" type="search" placeholder="搜索人物、地点、事件">
      <select id="graph-filter"><option value="">全部关系</option></select>
    </div>
    <div id="graph-details" class="details">点击节点或边查看证据。</div>
  </section>
  <section class="graph-stage">
    <svg id="graph-svg" role="img" aria-label="红楼梦知识图谱"></svg>
  </section>
</main>
<script src="graph.js?v={GRAPH_ASSET_VERSION}"></script>
"""
    (graph_dir / "index.html").write_text(page("前五回关系图", body, current="图谱", root_prefix="../"), encoding="utf-8")


def render_home(chapters: list[dict], graph: dict, entities: dict) -> None:
    chapter_cards = "".join(
        f'<a class="chapter-card" href="chapters/{c["id"]}.html"><span>第 {c["id"]} 回</span><strong>{escape_html(c["title"])}</strong></a>'
        for c in chapters
    )
    stat_items = "".join(
        f'<div><strong>{value}</strong><span>{label}</span></div>'
        for value, label in [
            (len(chapters), "试点章节"),
            (len(entities), "实体"),
            (len(graph["edges"]), "图谱边"),
            (sum(1 for e in graph["nodes"] if e["type"] == "event"), "事件"),
        ]
    )
    body = f"""
<main class="home">
  <section class="console">
    <div>
      <p class="eyebrow">Dream of the Red Chamber KB</p>
      <h1>红楼梦知识图谱</h1>
      <p>一个可高亮阅读、可回链引用、可视化探索的《红楼梦》首版知识库。当前聚焦前五回，先把人物、地点、府系、身份、物件、诗文、概念、时间和事件关系跑通。</p>
      <div class="actions"><a href="chapters/001.html">开始阅读</a><a href="entities/person.html">查看分类</a><a href="graph/index.html">查看图谱</a></div>
    </div>
    <div class="mini-map" aria-hidden="true">
      <span class="node n1">宝玉</span><span class="node n2">黛玉</span><span class="node n3">贾府</span><span class="node n4">太虚幻境</span>
      <svg viewBox="0 0 320 220"><path d="M70 90 C120 30, 180 40, 245 80"/><path d="M85 115 C145 150, 210 145, 260 120"/><path d="M120 70 C135 125, 145 160, 200 185"/></svg>
    </div>
  </section>
  <section class="stats">{stat_items}</section>
  <section class="chapter-grid">{chapter_cards}</section>
</main>
"""
    (DOCS_DIR / "index.html").write_text(page("红楼梦知识图谱", body, current="总览"), encoding="utf-8")


def copy_static() -> None:
    css_dir = DOCS_DIR / "css"
    css_dir.mkdir(parents=True, exist_ok=True)
    source_css = Path(__file__).resolve().parents[1] / "site" / "styles.css"
    css_dir.joinpath("styles.css").write_text(source_css.read_text(encoding="utf-8"), encoding="utf-8")
    graph_source = Path(__file__).resolve().parents[1] / "site" / "graph.js"
    graph_dest = DOCS_DIR / "graph" / "graph.js"
    graph_dest.parent.mkdir(parents=True, exist_ok=True)
    graph_dest.write_text(graph_source.read_text(encoding="utf-8"), encoding="utf-8")
    graph_json = DATA_DIR / "graph.json"
    if graph_json.exists():
        shutil.copyfile(graph_json, DOCS_DIR / "graph" / "graph.json")


def main() -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    (DOCS_DIR / "chapters").mkdir(parents=True, exist_ok=True)
    chapters = [parse_chapter_file(path) for path in sorted(TAGGED_DIR.glob("*.tagged.md"))]
    for idx, chapter in enumerate(chapters):
        prev_id = chapters[idx - 1]["id"] if idx > 0 else None
        next_id = chapters[idx + 1]["id"] if idx + 1 < len(chapters) else None
        (DOCS_DIR / "chapters" / f"{chapter['id']}.html").write_text(
            render_chapter(chapter, prev_id, next_id),
            encoding="utf-8",
        )
    entity_payload = read_json(DATA_DIR / "entities.json", {"entities": {}})
    graph = read_json(DATA_DIR / "graph.json", {"nodes": [], "edges": []})
    notes = read_json(DATA_DIR / "notes.json", {"sources": {}, "categories": {}, "entities": {}})
    render_entity_pages(entity_payload["entities"], {c["id"]: c["title"] for c in chapters}, notes)
    render_graph_page()
    render_home(chapters, graph, entity_payload["entities"])
    copy_static()


if __name__ == "__main__":
    main()
