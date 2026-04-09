"""
YAML audit export / import for the workflow event store.

write_event_yaml(): writes one event as a YAML file to workflow-events/.
                    Called by EventStore on each append (best-effort).

import_from_yaml(): reconstructs the SQLite events table from the YAML files
                    in workflow-events/. Used on fresh clone or after SQLite
                    loss (disaster recovery).

Design note (see framework/architecture-repository-design.md §4.2):
- SQLite is the CANONICAL event store (Pydantic-validated, ACID-protected).
- YAML files are the DERIVED git-tracked audit export committed at sprint
  boundaries.  Agents cannot write to workflow-events/ directly.
- On SQLite loss: import_from_yaml() rebuilds from committed YAML files;
  caller should then call EventStore.replay_state() to rebuild snapshots.
"""

from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path


def write_event_yaml(events_dir: Path, event_row: dict) -> Path:
    """
    Write one event to a YAML file in events_dir using PyYAML.

    Filename: <timestamp_slug>-<event_type_slug>-<event_id>.yaml
    The YAML structure round-trips cleanly through import_from_yaml().
    """
    import yaml  # type: ignore[import-untyped]

    slug = re.sub(r"[^a-z0-9]", "-", event_row["event_type"].lower())
    ts = event_row["timestamp"][:19].replace(":", "-").replace("T", "T")
    filename = f"{ts}-{slug}-{event_row['event_id']}.yaml"
    path = events_dir / filename

    payload = (
        json.loads(event_row["payload"])
        if isinstance(event_row["payload"], str)
        else (event_row["payload"] or {})
    )

    doc = {
        "event-id":       event_row["event_id"],
        "event-type":     event_row["event_type"],
        "timestamp":      event_row["timestamp"],
        "engagement-id":  event_row["engagement_id"],
        "cycle-id":       event_row.get("cycle_id"),
        "actor":          event_row["actor"],
        "correlation-id": event_row.get("correlation_id"),
        "payload":        payload,
    }
    path.write_text(yaml.dump(doc, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return path


def import_from_yaml(db_path: Path, events_dir: Path) -> int:
    """
    Reconstruct the SQLite events table from workflow-events/*.yaml files.

    - Files are processed in filename order (filenames embed the timestamp).
    - Events already present in the database (same event_id) are skipped.
    - The snapshots table is NOT rebuilt — caller must call
      EventStore(engagement_id, db_path=db_path).replay_state() afterward
      to regenerate snapshots.
    - Returns the number of events inserted.

    Raises ValueError if events_dir does not exist.
    """
    import yaml  # type: ignore[import-untyped]

    if not events_dir.exists():
        raise ValueError(f"events_dir does not exist: {events_dir}")

    from src.events.event_store import _SCHEMA_SQL  # lazy import — avoid circular at module level  # noqa: PLC0415

    conn = sqlite3.connect(str(db_path))
    conn.executescript(_SCHEMA_SQL)
    conn.commit()

    yaml_files = sorted(events_dir.glob("*.yaml"))
    count = 0
    for path in yaml_files:
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue  # malformed YAML — skip and warn in caller if desired
        if not isinstance(doc, dict) or "event-id" not in doc:
            continue

        # Skip duplicates
        exists = conn.execute(
            "SELECT 1 FROM events WHERE event_id = ?", (doc["event-id"],)
        ).fetchone()
        if exists:
            continue

        payload = doc.get("payload") or {}
        cycle_id = doc.get("cycle-id")
        correlation_id = doc.get("correlation-id")

        conn.execute(
            """INSERT INTO events
               (event_id, event_type, timestamp, engagement_id, cycle_id,
                actor, correlation_id, payload)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                doc["event-id"],
                doc["event-type"],
                str(doc["timestamp"]),
                doc["engagement-id"],
                cycle_id if cycle_id and cycle_id != "null" else None,
                doc.get("actor", "unknown"),
                correlation_id if correlation_id and correlation_id != "null" else None,
                json.dumps(payload),
            ),
        )
        count += 1

    conn.commit()
    conn.close()
    return count
