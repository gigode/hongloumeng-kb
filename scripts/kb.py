from __future__ import annotations

import html
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RAW_DIR = ROOT / "texts" / "raw"
TAGGED_DIR = ROOT / "texts" / "tagged"
DOCS_DIR = ROOT / "docs"

TAG_TYPES = {
    "@": ("person", "人物", "person"),
    "=": ("place", "地点", "place"),
    "&": ("household", "府系", "household"),
    "#": ("role", "身份", "role"),
    "•": ("object", "物件", "object"),
    "{": ("text", "诗文", "text"),
    "_": ("concept", "概念", "concept"),
    "%": ("time", "时间", "time"),
}

TAG_BY_TYPE = {value[0]: key for key, value in TAG_TYPES.items()}
TAG_PATTERN = re.compile(r"〖([@=&\#•\{_%])([^〖〗\n]+?)〗")
PARA_PATTERN = re.compile(r"^\[(?P<id>[0-9]+(?:\.[0-9]+)*)\]\s*(?P<body>.*)$")


def ensure_dirs() -> None:
    for path in [DATA_DIR, RAW_DIR, TAGGED_DIR, DOCS_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def read_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).strip().lower()
    value = re.sub(r"\s+", "-", value)
    value = re.sub(r"[^a-z0-9\u4e00-\u9fff:-]+", "-", value)
    return value.strip("-") or "item"


def entity_id(entity_type: str, name: str) -> str:
    return f"{entity_type}:{slugify(name)}"


def chapter_file_stem(chapter_id: str, title: str) -> str:
    short = re.sub(r"[^\w\u4e00-\u9fff]+", "", title)[:18] or f"chapter-{chapter_id}"
    return f"{chapter_id}_{short}"


def strip_tags(text: str) -> str:
    return TAG_PATTERN.sub(lambda m: m.group(2).split("|", 1)[0], text)


def parse_tag(raw: str) -> tuple[str, str]:
    if "|" in raw:
        surface, canonical = raw.split("|", 1)
        return surface.strip(), canonical.strip()
    value = raw.strip()
    return value, value


def extract_tags(text: str):
    for match in TAG_PATTERN.finditer(text):
        tag, raw = match.group(1), match.group(2)
        surface, canonical = parse_tag(raw)
        entity_type = TAG_TYPES[tag][0]
        yield {
            "type": entity_type,
            "surface": surface,
            "canonical": canonical,
            "start": match.start(),
            "end": match.end(),
        }


def iter_paragraphs(markdown: str):
    for line in markdown.splitlines():
        match = PARA_PATTERN.match(line.strip())
        if match:
            yield match.group("id"), match.group("body")


def escape_html(value: str) -> str:
    return html.escape(value, quote=True)
