"""
Event replay: reconstructs WorkflowState by processing events in sequence.

Called by EventStore.replay_state() when the SQLite snapshot is absent
or when a full audit replay is needed.

Unknown event types are silently skipped (forward-compatible).
State mutation logic lives in replay_builder.StateBuilder.
"""

from __future__ import annotations

from .models.state import WorkflowState
from .replay_builder import StateBuilder


#: Events that carry no WorkflowState change (audit-only).
_AUDIT_ONLY = frozenset({
    "phase.exited",
    "phase.return-triggered",
    "sprint.suspended",
    "gate.evaluated",
    "handoff.issued",
    "handoff.acknowledged",
    "source.queried",
    "artifact.promoted",
    "cq.assumption-made",
    "cq.answered",
    "algedonic.acknowledged",
})


def replay_events(engagement_id: str, events: list[tuple[str, dict]]) -> WorkflowState:
    """
    Reconstruct WorkflowState from a sequence of (event_type, payload_dict) tuples.
    Events must be in insertion order (ascending id).
    """
    builder = StateBuilder(engagement_id)
    last_event_id = "empty"

    for event_type, payload in events:
        last_event_id = payload.get("event_id", last_event_id)
        cycle_id: str | None = payload.get("cycle_id")

        match event_type:
            case "cycle.initiated":
                builder.on_cycle_initiated(payload)
            case "cycle.closed":
                builder.on_cycle_closed(payload)
            case "cycle.iteration-type-changed":
                builder.on_cycle_iteration_type_changed(payload)
            case "phase.entered":
                builder.on_phase_entered(payload, cycle_id)
            case "phase.suspended":
                builder.on_phase_suspended(payload, cycle_id)
            case "phase.resumed":
                builder.on_phase_resumed(payload, cycle_id)
            case "sprint.opened":
                builder.on_sprint_opened(payload, cycle_id)
            case "sprint.closed":
                builder.on_sprint_closed(payload, cycle_id)
            case "gate.passed":
                builder.on_gate_passed(payload, last_event_id)
            case "gate.held":
                builder.on_gate_held(payload, last_event_id)
            case "gate.escalated":
                builder.on_gate_escalated(payload, last_event_id)
            case "artifact.drafted":
                builder.on_artifact_drafted(payload)
            case "artifact.baselined":
                builder.on_artifact_baselined(payload)
            case "artifact.superseded":
                builder.on_artifact_superseded(payload)
            case "cq.raised":
                builder.on_cq_raised(payload, cycle_id)
            case "cq.closed":
                builder.on_cq_closed(payload)
            case "algedonic.raised":
                builder.on_algedonic_raised(payload, cycle_id)
            case "algedonic.resolved":
                builder.on_algedonic_resolved(payload)
            case _ if event_type in _AUDIT_ONLY:
                pass  # audit-only — no state change
            case _:
                pass  # unknown event type — forward-compatible skip

    return builder.to_workflow_state(last_event_id)
