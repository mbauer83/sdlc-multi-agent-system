"""
YAML audit export / import for the workflow event store.

write_event_yaml(): writes a single event as a YAML file to workflow-events/
                    Called by EventStore on each append (best-effort).

export_yaml():      exports all events from SQLite that lack a corresponding
                    YAML file. Called at sprint close to ensure git audit record
                    is complete. See EventStore.export_yaml().

import_from_yaml(): reconstructs the SQLite database from the YAML files in
                    workflow-events/. Used on fresh clone or after SQLite loss.

Design note (see framework/architecture-repository-design.md §4.2):
- SQLite is the CANONICAL event store (Pydantic-validated, ACID-protected).
- YAML files are the DERIVED git-tracked audit export committed at sprint boundaries.
- Agents cannot write to workflow-events/ directly (only EventStore writes here).
- On SQLite loss: import_from_yaml() rebuilds from committed YAML files.

Stage 5 TODO: implement write_event_yaml() and import_from_yaml() with full
              YAML serialisation matching the EventEnvelope schema.
"""

from __future__ import annotations

import json
from pathlib import Path


def write_event_yaml(events_dir: Path, event_row: dict) -> Path:
    """
    Write one event to a YAML file in events_dir.
    Filename: <timestamp>-<event_type_slugified>-<event_id>.yaml

    Stage 5 TODO: replace stub with full PyYAML serialisation.
    """
    import re
    slug = re.sub(r"[^a-z0-9]", "-", event_row["event_type"].lower())
    ts = event_row["timestamp"][:19].replace(":", "-").replace("T", "T")
    filename = f"{ts}-{slug}-{event_row['event_id']}.yaml"
    path = events_dir / filename
    payload = json.loads(event_row["payload"]) if isinstance(event_row["payload"], str) else event_row["payload"]
    content_lines = [
        f"event-id: {event_row['event_id']}",
        f"event-type: {event_row['event_type']}",
        f"timestamp: {event_row['timestamp']}",
        f"engagement-id: {event_row['engagement_id']}",
        f"cycle-id: {event_row.get('cycle_id') or 'null'}",
        f"actor: {event_row['actor']}",
        f"correlation-id: {event_row.get('correlation_id') or 'null'}",
        "payload:",
    ]
    for k, v in payload.items():
        content_lines.append(f"  {k}: {v}")
    path.write_text("\n".join(content_lines) + "\n")
    return path


def import_from_yaml(db_path: Path, events_dir: Path) -> int:
    """
    Reconstruct a SQLite event store from YAML files in events_dir.
    Returns the number of events imported.

    Stage 5 TODO: implement full round-trip with proper YAML parsing
    and EventRegistry validation.
    """
    raise NotImplementedError(
        "import_from_yaml() is a Stage 5 implementation item. "
        "See framework/architecture-repository-design.md §4.2 for the design spec."
    )
