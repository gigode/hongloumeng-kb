from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.kb import DATA_DIR, read_json, write_json


def build_graph() -> dict:
    entity_data = read_json(DATA_DIR / "entities.json", {"entities": {}})["entities"]
    events = read_json(DATA_DIR / "events.json", {"events": []})["events"]
    relations = read_json(DATA_DIR / "relations.json", {"relations": []})["relations"]

    nodes = []
    for entity in entity_data.values():
        if entity["type"] in {"person", "place", "household", "object", "concept", "role", "text"}:
            nodes.append({
                "id": entity["id"],
                "label": entity["name"],
                "type": entity["type"],
                "count": entity["count"],
            })
    for event in events:
        nodes.append({
            "id": event["id"],
            "label": event["name"],
            "type": "event",
            "chapter": event["chapter"],
        })

    edges = []
    for relation in relations:
        edges.append({
            "id": relation["id"],
            "source": relation["source"],
            "target": relation["target"],
            "type": relation["type"],
            "confidence": relation["confidence"],
            "chapter": relation["evidence"]["chapter"],
            "quote": relation["evidence"]["quote"],
        })
    for event in events:
        for field, relation_type in [("participants", "appears_in_event"), ("objects", "object_in_event"), ("places", "place_in_event")]:
            for node_id in event.get(field, []):
                edges.append({
                    "id": f"{event['id']}:{relation_type}:{node_id}",
                    "source": node_id,
                    "target": event["id"],
                    "type": relation_type,
                    "confidence": "high",
                    "chapter": event["chapter"],
                    "quote": event["summary"],
                })
    return {"nodes": nodes, "edges": edges}


def main() -> None:
    write_json(DATA_DIR / "graph.json", build_graph())


if __name__ == "__main__":
    main()
