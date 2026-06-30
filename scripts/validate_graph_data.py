from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.kb import DATA_DIR, read_json


def validate() -> list[str]:
    errors: list[str] = []
    entities = read_json(DATA_DIR / "entities.json", {"entities": {}})["entities"]
    events = read_json(DATA_DIR / "events.json", {"events": []})["events"]
    relations = read_json(DATA_DIR / "relations.json", {"relations": []})["relations"]
    ids = set(entities) | {event["id"] for event in events}

    for event in events:
        for field in ["participants", "objects", "places"]:
            for node_id in event.get(field, []):
                if node_id not in ids:
                    errors.append(f"Event {event['id']} references missing {field} id {node_id}")

    for relation in relations:
        if relation.get("source") not in ids:
            errors.append(f"Relation {relation.get('id')} missing source {relation.get('source')}")
        if relation.get("target") not in ids:
            errors.append(f"Relation {relation.get('id')} missing target {relation.get('target')}")
        evidence = relation.get("evidence") or {}
        if not evidence.get("chapter") or not evidence.get("paragraph") or not evidence.get("quote"):
            errors.append(f"Relation {relation.get('id')} lacks evidence")
    return errors


def main() -> None:
    errors = validate()
    if errors:
        raise SystemExit("\n".join(errors))
    print("graph data ok")


if __name__ == "__main__":
    main()
