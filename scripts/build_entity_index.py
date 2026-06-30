from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.kb import DATA_DIR, TAG_TYPES, TAGGED_DIR, entity_id, extract_tags, iter_paragraphs, read_json, write_json


def load_aliases() -> dict[str, dict[str, str]]:
    raw = read_json(DATA_DIR / "aliases.json", {})
    aliases: dict[str, dict[str, str]] = defaultdict(dict)
    for entity_type, mapping in raw.items():
        for canonical, alias_list in mapping.items():
            aliases[entity_type][canonical] = canonical
            for alias in alias_list:
                aliases[entity_type][alias] = canonical
    return aliases


def build_entity_index() -> dict:
    aliases = load_aliases()
    entities = {}

    for file in sorted(TAGGED_DIR.glob("*.tagged.md")):
        chapter_id = file.name.split("_", 1)[0]
        content = file.read_text(encoding="utf-8")
        for paragraph_id, body in iter_paragraphs(content):
            for tag in extract_tags(body):
                entity_type = tag["type"]
                canonical = aliases.get(entity_type, {}).get(tag["canonical"], tag["canonical"])
                eid = entity_id(entity_type, canonical)
                if eid not in entities:
                    entities[eid] = {
                        "id": eid,
                        "type": entity_type,
                        "type_label": next(v[1] for v in TAG_TYPES.values() if v[0] == entity_type),
                        "name": canonical,
                        "aliases": [],
                        "refs": [],
                        "count": 0,
                    }
                if tag["surface"] != canonical and tag["surface"] not in entities[eid]["aliases"]:
                    entities[eid]["aliases"].append(tag["surface"])
                entities[eid]["refs"].append(
                    {"chapter": chapter_id, "paragraph": paragraph_id, "surface": tag["surface"]}
                )
                entities[eid]["count"] += 1

    return {
        "meta": {
            "entity_count": len(entities),
            "tagged_chapters": len(list(TAGGED_DIR.glob("*.tagged.md"))),
        },
        "entities": dict(sorted(entities.items())),
    }


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    write_json(DATA_DIR / "entities.json", build_entity_index())


if __name__ == "__main__":
    main()
