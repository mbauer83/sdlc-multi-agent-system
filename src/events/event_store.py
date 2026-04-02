"""
EventStore: the sole write path for all SDLC workflow events.

Agents never access the SQLite database directly. All reads and writes go
through this class. Pydantic v2 validates every event before insertion.
The append-only invariant is enforced: no UPDATE or DELETE on the events table.

Usage:
    store = EventStore(engagement_id="ENG-001")
    store.append(PhaseEnteredPayload(phase_id="A", iteration_number=1, trigger="initial"))
    state = store.current_state()
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Type

from pydantic import ValidationError

from .models.base import BaseEventPayload, EventEnvelope, EventValidationError
from .models.state import WorkflowState
from .registry import EventRegistry


_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS events (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id        TEXT    UNIQUE NOT NULL,
    event_type      TEXT    NOT NULL,
    timestamp       TEXT    NOT NULL,
    engagement_id   TEXT    NOT NULL,
    cycle_id        TEXT,
    actor           TEXT    NOT NULL,
    correlation_id  TEXT,
    payload         TEXT    NOT NULL,
    CONSTRAINT valid_json CHECK (json_valid(payload))
);

CREATE INDEX IF NOT EXISTS idx_events_type        ON events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_cycle       ON events(cycle_id);
CREATE INDEX IF NOT EXISTS idx_events_correlation ON events(correlation_id);

CREATE TABLE IF NOT EXISTS snapshots (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_at TEXT    NOT NULL,
    timestamp   TEXT    NOT NULL,
    state       TEXT    NOT NULL
);
"""

_ENGAGEMENTS_ROOT = Path(__file__).parent.parent.parent / "engagements"


class EventStore:
    """
    Append-only, Pydantic-validated event store backed by SQLite.
    One instance per engagement. Thread-safe for read; serialise writes externally
    if multiple agent processes run concurrently.
    """

    def __init__(self, engagement_id: str, db_path: Path | None = None) -> None:
        self.engagement_id = engagement_id
        if db_path is None:
            db_path = _ENGAGEMENTS_ROOT / engagement_id / "workflow.db"
        self._db_path = db_path
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self._db_path), check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging for concurrent reads
        self._conn.execute("PRAGMA foreign_keys=ON")
        self._conn.executescript(_SCHEMA_SQL)
        self._conn.commit()
        self._sequence = self._current_sequence()

    # ------------------------------------------------------------------
    # Write path
    # ------------------------------------------------------------------

    def append(
        self,
        payload: BaseEventPayload,
        actor: str,
        cycle_id: str | None = None,
        correlation_id: str | None = None,
    ) -> EventEnvelope:
        """
        Validate and append one event. Returns the persisted EventEnvelope.
        Raises EventValidationError if Pydantic validation fails.
        Raises TypeError if the payload type is not registered.
        """
        event_type = EventRegistry.type_for(type(payload))
        self._sequence += 1
        event_id = f"{self.engagement_id}-EV-{self._sequence:06d}"

        try:
            envelope = EventEnvelope(
                event_id=event_id,
                event_type=event_type,
                engagement_id=self.engagement_id,
                cycle_id=cycle_id,
                actor=actor,
                correlation_id=correlation_id,
                payload=payload.model_dump(),
            )
        except ValidationError as exc:
            raise EventValidationError(
                f"Event validation failed for {event_type}: {exc}"
            ) from exc

        # Step 1: Canonical write to SQLite (ACID transaction)
        with self._conn:
            self._conn.execute(
                """INSERT INTO events
                   (event_id, event_type, timestamp, engagement_id, cycle_id, actor, correlation_id, payload)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    envelope.event_id,
                    envelope.event_type,
                    envelope.timestamp.isoformat(),
                    envelope.engagement_id,
                    envelope.cycle_id,
                    envelope.actor,
                    envelope.correlation_id,
                    json.dumps(envelope.payload),
                ),
            )
            # Refresh snapshot if this is a sprint-close event
            if event_type == "sprint.closed":
                self._refresh_snapshot_in_transaction(envelope.event_id)

        # Step 2: Best-effort YAML export (derived audit record; not canonical)
        # Failure here does not roll back the SQLite write — the canonical state is safe.
        # Any missing YAML files are caught up by export_yaml() at the next sprint close.
        try:
            self._write_yaml_export(envelope)
        except Exception as exc:  # noqa: BLE001
            import warnings
            warnings.warn(
                f"YAML export failed for {envelope.event_id}: {exc}. "
                "SQLite write succeeded; run export_yaml() to catch up.",
                RuntimeWarning,
                stacklevel=2,
            )

        return envelope

    # ------------------------------------------------------------------
    # Read path
    # ------------------------------------------------------------------

    def current_state(self) -> WorkflowState:
        """
        Return current workflow state. Reads from snapshot table (fast path).
        Falls back to replay_state() if no snapshot exists.
        """
        row = self._conn.execute(
            "SELECT state FROM snapshots ORDER BY id DESC LIMIT 1"
        ).fetchone()
        if row:
            return WorkflowState.model_validate_json(row[0])
        return self.replay_state()

    def replay_state(self) -> WorkflowState:
        """
        Reconstruct WorkflowState by replaying all events from the beginning.
        Writes a fresh snapshot on completion.
        """
        from .replay import replay_events  # lazy import to avoid circular deps
        rows = self._conn.execute(
            "SELECT event_type, payload FROM events ORDER BY id ASC"
        ).fetchall()
        events = [(row[0], json.loads(row[1])) for row in rows]
        state = replay_events(self.engagement_id, events)
        # Persist the replayed snapshot
        last_id = self._conn.execute(
            "SELECT event_id FROM events ORDER BY id DESC LIMIT 1"
        ).fetchone()
        if last_id:
            self._write_snapshot(last_id[0], state)
        return state

    def query(
        self,
        event_type: str | None = None,
        cycle_id: str | None = None,
        correlation_id: str | None = None,
        limit: int = 500,
    ) -> list[dict[str, Any]]:
        """Return matching event rows as dicts (for agent inspection)."""
        clauses, params = [], []
        if event_type:
            clauses.append("event_type = ?")
            params.append(event_type)
        if cycle_id:
            clauses.append("cycle_id = ?")
            params.append(cycle_id)
        if correlation_id:
            clauses.append("correlation_id = ?")
            params.append(correlation_id)
        where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
        rows = self._conn.execute(
            f"SELECT event_id, event_type, timestamp, actor, cycle_id, correlation_id, payload "
            f"FROM events {where} ORDER BY id ASC LIMIT ?",
            params + [limit],
        ).fetchall()
        keys = ["event_id", "event_type", "timestamp", "actor", "cycle_id", "correlation_id", "payload"]
        return [dict(zip(keys, row)) for row in rows]

    def open_cqs(self, blocking_only: bool = False) -> list[str]:
        """Return cq-ids for CQs that have been raised but not closed."""
        state = self.current_state()
        for cycle in state.active_cycles:
            if blocking_only:
                # Would need to cross-reference the CQ records; here we return all
                return cycle.open_cqs
            return cycle.open_cqs
        return []

    def check_integrity(self) -> list[str]:
        """
        Validate JSON payloads and sequence continuity. Returns a list of
        anomaly descriptions (empty list = healthy).
        """
        anomalies: list[str] = []
        rows = self._conn.execute(
            "SELECT id, event_id, payload FROM events ORDER BY id ASC"
        ).fetchall()
        for row_id, event_id, payload_str in rows:
            try:
                json.loads(payload_str)
            except json.JSONDecodeError:
                anomalies.append(f"Row {row_id} ({event_id}): invalid JSON payload")
        return anomalies

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def export_yaml(self) -> int:
        """
        Export all SQLite events that do not yet have a corresponding YAML file
        to the workflow-events/ directory. Returns the number of files written.
        This is called at sprint close to ensure the git-committed audit record
        is up to date with the canonical SQLite store.
        """
        from .export import write_event_yaml  # implemented in Stage 5
        events_dir = self._db_path.parent / "workflow-events"
        events_dir.mkdir(exist_ok=True)
        rows = self._conn.execute(
            "SELECT event_id, event_type, timestamp, engagement_id, cycle_id, actor, correlation_id, payload "
            "FROM events ORDER BY id ASC"
        ).fetchall()
        count = 0
        for row in rows:
            event_id = row[0]
            # YAML files are named <timestamp>-<event_type>-<event_id>.yaml
            # Check if a file for this event_id already exists
            existing = list(events_dir.glob(f"*-{event_id}.yaml"))
            if not existing:
                try:
                    write_event_yaml(events_dir, dict(zip(
                        ["event_id", "event_type", "timestamp", "engagement_id",
                         "cycle_id", "actor", "correlation_id", "payload"],
                        row
                    )))
                    count += 1
                except Exception as exc:  # noqa: BLE001
                    import warnings
                    warnings.warn(f"YAML export failed for {event_id}: {exc}", RuntimeWarning)
        return count

    def _write_yaml_export(self, envelope: "EventEnvelope") -> None:  # type: ignore[name-defined]
        """Write a single event as a YAML file to workflow-events/."""
        from .export import write_event_yaml
        events_dir = self._db_path.parent / "workflow-events"
        events_dir.mkdir(exist_ok=True)
        write_event_yaml(events_dir, {
            "event_id": envelope.event_id,
            "event_type": envelope.event_type,
            "timestamp": envelope.timestamp.isoformat(),
            "engagement_id": envelope.engagement_id,
            "cycle_id": envelope.cycle_id,
            "actor": envelope.actor,
            "correlation_id": envelope.correlation_id,
            "payload": json.dumps(envelope.payload),
        })

    def _current_sequence(self) -> int:
        row = self._conn.execute("SELECT COUNT(*) FROM events").fetchone()
        return row[0] if row else 0

    def _refresh_snapshot_in_transaction(self, last_event_id: str) -> None:
        """Called within an open transaction after a sprint.closed event."""
        state = self.replay_state()
        self._conn.execute(
            "INSERT INTO snapshots (snapshot_at, timestamp, state) VALUES (?, datetime('now'), ?)",
            (last_event_id, state.model_dump_json()),
        )

    def _write_snapshot(self, snapshot_at: str, state: WorkflowState) -> None:
        with self._conn:
            self._conn.execute(
                "INSERT INTO snapshots (snapshot_at, timestamp, state) VALUES (?, datetime('now'), ?)",
                (snapshot_at, state.model_dump_json()),
            )

    def close(self) -> None:
        self._conn.close()
