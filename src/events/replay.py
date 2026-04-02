"""
Event replay: reconstructs WorkflowState by processing events in sequence.

Called by EventStore.replay_state() when the SQLite snapshot is absent
or when a full audit replay is needed.

Stage 5 TODO: implement the full state machine that processes each event
type and updates the relevant CycleState, GateRecord, and ArtifactRecord
fields. The stub below raises NotImplementedError so that tests fail
loudly rather than silently return wrong state.
"""

from __future__ import annotations

from .models.state import WorkflowState, CycleState
from datetime import datetime, timezone


def replay_events(engagement_id: str, events: list[tuple[str, dict]]) -> WorkflowState:
    """
    Reconstruct WorkflowState from a sequence of (event_type, payload_dict) tuples.
    Events must be in insertion order (ascending id).

    Stage 5 implementation: process each event type and mutate state accordingly.
    For now returns an empty WorkflowState so the system starts cleanly.
    """
    # Stage 5 TODO: implement event type handlers:
    # cycle.initiated → add CycleState to active_cycles
    # phase.entered   → update current_phase, increment phase_visit_counts
    # gate.passed     → add GateRecord to gate_history
    # artifact.baselined → add/update ArtifactRecord in artifact_registry
    # cq.raised       → add cq-id to relevant CycleState.open_cqs
    # cq.closed       → remove from open_cqs
    # algedonic.raised → add to open_algedonics
    # algedonic.resolved → remove from open_algedonics
    # ... etc for all event types in §4.4 of architecture-repository-design.md

    return WorkflowState(
        snapshot_at=events[-1][1].get("event_id", "unknown") if events else "empty",
        timestamp=datetime.now(timezone.utc),
        engagement_id=engagement_id,
        active_cycles=[],
        gate_history=[],
        artifact_registry={},
    )
