# Hongloumeng KB Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a small, publishable knowledge graph and reading site for 《红楼梦》, starting with a 5-chapter pilot that can later scale to all 120 chapters.

**Architecture:** Follow the useful shape of `baojie/shiji-kb`, but keep the first version much smaller: annotated Markdown as the human-readable source of truth, JSON indexes as the machine-readable graph layer, and a static GitHub Pages site as the user interface. Avoid Neo4j, complex agent loops, full wiki generation, or large-scale inferred relations in the MVP.

**Tech Stack:** Python 3.11+, Markdown/JSON, pytest, BeautifulSoup or MediaWiki API for source import, static HTML/CSS/JavaScript, Cytoscape.js or Sigma.js for graph visualization, GitHub Pages for publishing.

---

## Lessons From `baojie/shiji-kb`

Keep:
- `chapter_md/*.tagged.md` style annotated source files.
- Stable paragraph numbers for precise citations.
- JSON entity indexes with references back to chapter and paragraph.
- Static `docs/` output for GitHub Pages.
- Simple Python scripts that can be inspected and rerun.

Do not copy yet:
- 22 entity and verb classes.
- Event chronology inference and multi-round reflection loops.
- 20,000-page wiki generation.
- Metro-map app, game app, RDF/OWL export, Butler agent.

Adapt for fiction:
- Replace historical chronology emphasis with character, household, residence, object, poem, dream, and episode relations.
- Store every extracted relation with evidence: chapter id, paragraph id, quote, confidence.
- Mark interpretive relations as low/medium confidence unless directly stated.

## MVP Scope

The first published version should contain:
- Raw text metadata for all 120 chapters if source import is easy.
- Fully annotated pilot for chapters 1-5 only.
- Core entity types: person, place, household/clan, role/status, object, poem/text, concept/motif, time.
- Entity index pages.
- A chapter reader with syntax highlighting and paragraph anchors.
- A graph page showing person, place, household, object, and event links from the pilot.
- A short README explaining source, scope, known limits, and how to regenerate.

Suggested base text:
- Wikisource `紅樓夢`, 120 chapters, no commentary, with first 80 chapters based on 庚辰本 and last 40 based on 程甲本.
- Keep source metadata in the repo so later edition choices are visible.

## Annotation Syntax

Use a reduced tag set compatible with the `shiji-kb` visual style:

```text
〖@人物〗       person
〖=地点〗       place
〖&家族/府系〗   household
〖#身份/角色〗   role
〖•物件〗       object
〖{诗文/书名〗   text
〖_概念/母题〗   concept
〖%时间〗       time
```

Examples:

```markdown
[1.1] 〖@甄士隐〗梦中见一僧一道，携着〖•通灵宝玉〗，说起〖_梦幻〗因缘。

[3.2] 〖@林黛玉〗进〖=荣国府〗，拜见〖@贾母〗，众人皆称她为〖#姑娘〗。
```

## Data Model

Create these source and derived files:

```text
texts/raw/001.md
texts/tagged/001_甄士隐梦幻识通灵.tagged.md
data/chapters.json
data/entities.json
data/aliases.json
data/events.json
data/relations.json
data/graph.json
docs/index.html
docs/chapters/001.html
docs/entities/person.html
docs/graph/index.html
```

Entity shape:

```json
{
  "id": "person:jia-baoyu",
  "type": "person",
  "name": "贾宝玉",
  "aliases": ["宝玉", "宝二爷"],
  "refs": [
    {"chapter": "003", "paragraph": "3.4", "surface": "宝玉"}
  ]
}
```

Relation shape:

```json
{
  "id": "rel-0001",
  "source": "person:lin-daiyu",
  "target": "person:jia-baoyu",
  "type": "cousin",
  "confidence": "high",
  "evidence": {
    "chapter": "003",
    "paragraph": "3.9",
    "quote": "..."
  }
}
```

Event shape:

```json
{
  "id": "event-001-001",
  "name": "甄士隐梦幻识通灵",
  "type": "dream_frame",
  "chapter": "001",
  "paragraphs": ["1.1", "1.2"],
  "participants": ["person:zhen-shiyin"],
  "objects": ["object:tongling-baoyu"],
  "places": [],
  "summary": "甄士隐梦中见一僧一道携通灵宝玉，引出全书梦幻框架。"
}
```

## Task 1: Project Scaffold

**Files:**
- Create: `README.md`
- Create: `pyproject.toml`
- Create: `.gitignore`
- Create: `docs/.nojekyll`
- Create: `scripts/__init__.py`
- Create: `tests/__init__.py`

**Step 1: Initialize git**

Run:

```powershell
cd "C:\Users\zm_ji\Documents\New project\hongloumeng-kb"
git init
```

Expected: repository initialized.

**Step 2: Add package and test tooling**

Create `pyproject.toml` with Python dependencies:

```toml
[project]
name = "hongloumeng-kb"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
  "beautifulsoup4>=4.12",
  "requests>=2.32",
  "pypinyin>=0.51"
]

[project.optional-dependencies]
dev = ["pytest>=8.0", "jsonschema>=4.0"]
```

**Step 3: Commit**

```powershell
git add README.md pyproject.toml .gitignore docs/.nojekyll scripts tests
git commit -m "chore: scaffold hongloumeng knowledge graph"
```

## Task 2: Source Import

**Files:**
- Create: `scripts/fetch_wikisource.py`
- Create: `scripts/segment_text.py`
- Create: `texts/raw/`
- Create: `data/chapters.json`
- Test: `tests/test_source_import.py`

**Step 1: Write import tests**

Test that a chapter has a title, non-empty body, and stable id:

```python
def test_chapter_metadata_shape():
    chapter = {"id": "001", "title": "甄士隐梦幻识通灵"}
    assert chapter["id"] == "001"
    assert chapter["title"]
```

**Step 2: Implement source fetcher**

Fetch from Wikisource or store manually downloaded text. Normalize:
- Traditional or simplified choice recorded in metadata.
- One chapter per file.
- Remove navigation, edit links, and unrelated page chrome.
- Preserve chapter titles.

**Step 3: Segment paragraphs**

Generate paragraph ids:

```text
[1]
[1.1]
[1.2]
```

Use stable numbering so future annotations and evidence remain valid.

**Step 4: Validate**

Run:

```powershell
pytest tests/test_source_import.py -v
```

Expected: PASS.

**Step 5: Commit**

```powershell
git add scripts/fetch_wikisource.py scripts/segment_text.py texts/raw data/chapters.json tests/test_source_import.py
git commit -m "feat: import and segment hongloumeng source text"
```

## Task 3: Annotation Spec And Pilot Text

**Files:**
- Create: `docs/spec/annotation.md`
- Create: `texts/tagged/001_*.tagged.md` through `005_*.tagged.md`
- Test: `tests/test_annotation_integrity.py`

**Step 1: Write integrity tests**

Test stripping tags returns original text content for each pilot chapter.

**Step 2: Draft annotation spec**

Define each tag, examples, and boundaries. Keep special notes for:
- aliases: 宝玉 vs 贾宝玉
- family labels: 贾府, 荣国府, 宁国府
- role labels: 丫鬟, 奶娘, 王妃
- objects: 通灵宝玉, 风月宝鉴, 金锁
- concepts: 梦, 情, 空, 色, 太虚幻境

**Step 3: Annotate chapters 1-5**

Start with high-value tags only. Do not mark every possible noun.

**Step 4: Validate**

Run:

```powershell
pytest tests/test_annotation_integrity.py -v
```

Expected: PASS.

**Step 5: Commit**

```powershell
git add docs/spec/annotation.md texts/tagged tests/test_annotation_integrity.py
git commit -m "feat: add pilot annotations for first five chapters"
```

## Task 4: Entity Index Builder

**Files:**
- Create: `scripts/build_entity_index.py`
- Create: `data/aliases.json`
- Generate: `data/entities.json`
- Test: `tests/test_entity_index.py`

**Step 1: Write parser tests**

```python
def test_extract_person_tag():
    text = "〖@贾宝玉〗见〖@林黛玉〗"
    entities = extract_entities(text)
    assert ("person", "贾宝玉") in entities
    assert ("person", "林黛玉") in entities
```

**Step 2: Implement parser**

Use regex per tag type. Parse inline alias form later only if needed:

```text
〖@宝玉|贾宝玉〗
```

**Step 3: Build `entities.json`**

For each canonical entity, store:
- id
- type
- name
- aliases
- refs
- count

**Step 4: Validate**

Run:

```powershell
pytest tests/test_entity_index.py -v
python scripts/build_entity_index.py
```

Expected: PASS and `data/entities.json` generated.

**Step 5: Commit**

```powershell
git add scripts/build_entity_index.py data/aliases.json data/entities.json tests/test_entity_index.py
git commit -m "feat: build entity index from tagged chapters"
```

## Task 5: Events And Relations

**Files:**
- Create: `docs/spec/events-relations.md`
- Create: `data/events.json`
- Create: `data/relations.json`
- Create: `scripts/validate_graph_data.py`
- Test: `tests/test_graph_schema.py`

**Step 1: Define relation types**

Start with:
- `family_parent_child`
- `family_spouse`
- `family_sibling`
- `kinship_cousin`
- `household_member`
- `serves`
- `resides_at`
- `owns_or_carries`
- `appears_in_event`
- `co_occurs`

**Step 2: Enter pilot relations manually**

Manual entry is acceptable for first 5 chapters because it gives cleaner examples and prevents over-inference.

**Step 3: Validate schema**

Check every edge source/target exists in `entities.json` or `events.json`, and every relation has evidence.

**Step 4: Commit**

```powershell
git add docs/spec/events-relations.md data/events.json data/relations.json scripts/validate_graph_data.py tests/test_graph_schema.py
git commit -m "feat: add pilot events and relations"
```

## Task 6: Static Reader And Entity Pages

**Files:**
- Create: `scripts/render_site.py`
- Create: `site/templates/base.html`
- Create: `site/templates/chapter.html`
- Create: `site/templates/entity_index.html`
- Create: `docs/css/styles.css`
- Generate: `docs/chapters/*.html`
- Generate: `docs/entities/*.html`
- Test: `tests/test_render_site.py`

**Step 1: Render tag spans**

Convert annotations to HTML spans:

```html
<span class="entity person" data-entity="贾宝玉">贾宝玉</span>
```

**Step 2: Add paragraph anchors**

Each paragraph should render with an id:

```html
<p id="p-1-1"><a class="pn" href="#p-1-1">[1.1]</a>...</p>
```

**Step 3: Generate entity pages**

Each entity page lists references back to chapter anchors.

**Step 4: Commit**

```powershell
git add scripts/render_site.py site docs tests/test_render_site.py
git commit -m "feat: render static reader and entity pages"
```

## Task 7: Graph Explorer

**Files:**
- Create: `scripts/build_graph.py`
- Generate: `data/graph.json`
- Create: `docs/graph/index.html`
- Create: `docs/graph/graph.js`
- Create: `docs/graph/graph.css`
- Test: `tests/test_graph_export.py`

**Step 1: Build graph export**

Nodes:
- people
- places
- households
- objects
- events

Edges:
- relations from `data/relations.json`
- `appears_in_event` edges from `data/events.json`

**Step 2: Implement browser graph**

Use Cytoscape.js or Sigma.js. Required controls:
- search entity
- filter by relation type
- filter by chapter
- click node to show references

**Step 3: Validate**

Run:

```powershell
pytest tests/test_graph_export.py -v
python scripts/build_graph.py
```

Expected: graph JSON has nodes and edges, and all ids resolve.

**Step 4: Commit**

```powershell
git add scripts/build_graph.py data/graph.json docs/graph tests/test_graph_export.py
git commit -m "feat: add interactive graph explorer"
```

## Task 8: README And Publishing

**Files:**
- Modify: `README.md`
- Create: `.github/workflows/pages.yml` only if using GitHub Actions instead of Pages from branch

**Step 1: README**

Include:
- What this project is.
- Source text and edition note.
- MVP scope: first 5 chapters.
- How to regenerate data and site.
- Known limitations.
- License note.

**Step 2: Local smoke test**

Run:

```powershell
python scripts/build_entity_index.py
python scripts/validate_graph_data.py
python scripts/build_graph.py
python scripts/render_site.py
pytest -v
```

Expected: all pass.

**Step 3: Publish to GitHub**

Before publishing, confirm:
- GitHub repo name: recommended `hongloumeng-kb`
- Visibility: public or private
- GitHub Pages source: `docs/` on `main`

Then:

```powershell
git remote add origin https://github.com/<user>/hongloumeng-kb.git
git push -u origin main
```

Enable GitHub Pages from `main` / `docs`.

**Step 4: Commit**

```powershell
git add README.md .github
git commit -m "docs: document pilot scope and publishing"
```

## First-Version Success Criteria

- `pytest -v` passes.
- `data/entities.json`, `data/events.json`, `data/relations.json`, and `data/graph.json` are valid.
- Removing annotation tags from the 5 tagged chapters preserves the raw text.
- `docs/index.html` opens locally.
- The graph page shows at least 30 nodes and 40 edges from chapters 1-5.
- Every relation edge has evidence.
- The GitHub repo is pushed and GitHub Pages is enabled.

## Later Expansion

After the 5-chapter pilot works:
- Annotate chapters 6-20.
- Add the 金陵十二钗专题 page.
- Add residence graph for 大观园.
- Add poem/判词 index.
- Add relation confidence review.
- Add export formats: CSV and GraphML.
- Consider Neo4j only after the static graph becomes too small for the questions we want to ask.
