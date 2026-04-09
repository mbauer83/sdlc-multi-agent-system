"""
Event replay: reconstructs WorkflowState by processing events in sequence.

Both public functions delegate all event-type routing to StateBuilder.dispatch(),
which uses the data-driven _HANDLERS table in replay_builder.py.  No dispatch
logic lives here — this module is a thin loop with two initialisation strategies:

  replay_events()         — fresh StateBuilder from engagement_id  (full replay)
  apply_events_to_state() — StateBuilder seeded from a snapshot    (delta replay)
"""

from __future__ import annotations

from .models.state import WorkflowState
from .replay_builder import StateBuilder


def _run_events(
    builder: StateBuilder,
    events: list[tuple[str, dict]],
    initial_event_id: str,
) -> tuple[StateBuilder, str]:
    """
    Feed a sequence of (event_type, payload_dict) tuples through builder.dispatch().
    Returns the same builder and the last event_id seen (or initial_event_id if
    the sequence is empty).
    """
    last_event_id = initial_event_id
    for event_type, payload in events:
        last_event_id = payload.get("event_id", last_event_id)
        builder.dispatch(
            event_type=event_type,
            payload=payload,
            cycle_id=payload.get("cycle_id"),
            last_event_id=last_event_id,
        )
    return builder, last_event_id


def replay_events(engagement_id: str, events: list[tuple[str, dict]]) -> WorkflowState:
    """
    Reconstruct WorkflowState from a full sequence of (event_type, payload_dict)
    tuples in insertion order (ascending id).
    """
    builder, last_event_id = _run_events(StateBuilder(engagement_id), events, "empty")
    return builder.to_workflow_state(last_event_id)


def apply_events_to_state(
    base_state: WorkflowState,
    delta_events: list[tuple[str, dict]],
) -> WorkflowState:
    """
    Apply delta events on top of an existing WorkflowState snapshot.
    O(delta) — does not replay from the beginning.
    Returns base_state unchanged when delta_events is empty.
    """
    if not delta_events:
        return base_state
    builder, last_event_id = _run_events(
        StateBuilder.from_state(base_state), delta_events, base_state.snapshot_at
    )
    return builder.to_workflow_state(last_event_id)
