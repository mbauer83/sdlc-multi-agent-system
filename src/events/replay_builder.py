"""
Mutable state builders for event replay.

Internal to the events package. Public entry point is replay.replay_events().

Event dispatch is data-driven: _HANDLERS maps event_type strings to lambda
expressions that forward to the appropriate StateBuilder method.  Adding a
new state-changing event type requires one entry in _HANDLERS — no match/case
branch and no changes to dispatch().
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Callable

from .models.state import ArtifactRecord, CycleState, GateRecord, WorkflowState

if TYPE_CHECKING:
    pass  # kept for potential future Protocol imports


# ---------------------------------------------------------------------------
# Mutable builder for a single ADM cycle
# ---------------------------------------------------------------------------

class _CycleBuilder:
    """Mutable scratch-pad for one ADM cycle, converted to CycleState at end."""

    __slots__ = (
        "cycle_id", "iteration_type", "parent_cycle_id",
        "current_phase", "phase_visit_counts",
        "active_sprints", "open_cqs", "open_algedonics",
    )

    def __init__(self, cycle_id: str, iteration_type: str, parent_cycle_id: str | None) -> None:
        self.cycle_id = cycle_id
        self.iteration_type = iteration_type
        self.parent_cycle_id = parent_cycle_id
        self.current_phase: str = "Prelim"
        self.phase_visit_counts: dict[str, int] = {}
        self.active_sprints: list[str] = []
        self.open_cqs: list[str] = []
        self.open_algedonics: list[str] = []

    @classmethod
    def from_state(cls, state: CycleState) -> "_CycleBuilder":
        """Reconstruct a mutable builder from a frozen CycleState snapshot."""
        builder = cls(state.cycle_id, state.iteration_type, state.parent_cycle_id)
        builder.current_phase = state.current_phase
        builder.phase_visit_counts = dict(state.phase_visit_counts)
        builder.active_sprints = list(state.active_sprints)
        builder.open_cqs = list(state.open_cqs)
        builder.open_algedonics = list(state.open_algedonics)
        return builder

    def to_cycle_state(self) -> CycleState:
        return CycleState(
            cycle_id=self.cycle_id,
            iteration_type=self.iteration_type,  # type: ignore[arg-type]
            parent_cycle_id=self.parent_cycle_id,
            current_phase=self.current_phase,
            phase_visit_counts=dict(self.phase_visit_counts),
            active_sprints=list(self.active_sprints),
            open_cqs=list(self.open_cqs),
            open_algedonics=list(self.open_algedonics),
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Handler type alias
# ---------------------------------------------------------------------------

type _HandlerFn = Callable[["StateBuilder", dict[str, Any], str | None, str], None]


def _first_cycle_id(cycles: dict[str, _CycleBuilder]) -> str | None:
    return next(iter(cycles), None)


def _remove_if_present(lst: list[str], value: str) -> None:
    try:
        lst.remove(value)
    except ValueError:
        pass


def _get_cycle(
    cycles: dict[str, _CycleBuilder], cycle_id: str | None
) -> _CycleBuilder | None:
    cid = cycle_id or _first_cycle_id(cycles)
    return cycles.get(cid) if cid else None


# ---------------------------------------------------------------------------
# Main mutable state builder
# ---------------------------------------------------------------------------

class StateBuilder:
    """Accumulates event mutations; produces a WorkflowState at end."""

    def __init__(self, engagement_id: str) -> None:
        self.engagement_id = engagement_id
        self.cycles: dict[str, _CycleBuilder] = {}
        self.gate_history: list[GateRecord] = []
        self.artifact_registry: dict[str, ArtifactRecord] = {}

    @classmethod
    def from_state(cls, state: WorkflowState) -> "StateBuilder":
        """
        Reconstruct a mutable builder from a frozen WorkflowState snapshot.
        Enables O(delta) incremental replay: seed from snapshot, then apply
        only the events that occurred after the snapshot point.
        """
        builder = cls(state.engagement_id)
        builder.cycles = {
            c.cycle_id: _CycleBuilder.from_state(c) for c in state.active_cycles
        }
        builder.gate_history = list(state.gate_history)
        builder.artifact_registry = dict(state.artifact_registry)
        return builder

    # ------------------------------------------------------------------
    # Cycle events
    # ------------------------------------------------------------------

    def on_cycle_initiated(self, p: dict[str, Any]) -> None:
        cid = p["cycle_id"]
        self.cycles[cid] = _CycleBuilder(
            cycle_id=cid,
            iteration_type=p["iteration_type"],
            parent_cycle_id=p.get("parent_cycle_id"),
        )

    def on_cycle_closed(self, p: dict[str, Any]) -> None:
        self.cycles.pop(p["cycle_id"], None)

    def on_cycle_iteration_type_changed(self, p: dict[str, Any]) -> None:
        if cycle := self.cycles.get(p["cycle_id"]):
            cycle.iteration_type = p["to_type"]

    # ------------------------------------------------------------------
    # Phase events
    # ------------------------------------------------------------------

    def on_phase_entered(self, p: dict[str, Any], cycle_id: str | None) -> None:
        if cycle := _get_cycle(self.cycles, cycle_id):
            phase = p["phase_id"]
            cycle.current_phase = phase
            cycle.phase_visit_counts[phase] = cycle.phase_visit_counts.get(phase, 0) + 1

    def on_phase_suspended(self, p: dict[str, Any], cycle_id: str | None) -> None:
        if not (cycle := _get_cycle(self.cycles, cycle_id)):
            return
        reason = p.get("reason")
        if reason == "blocking-cq" and (cq_id := p.get("blocking_cq_id")):
            if cq_id not in cycle.open_cqs:
                cycle.open_cqs.append(cq_id)
        elif reason == "algedonic-halt" and (sig := p.get("algedonic_id")):
            if sig not in cycle.open_algedonics:
                cycle.open_algedonics.append(sig)

    def on_phase_resumed(self, p: dict[str, Any], cycle_id: str | None) -> None:
        if not (cycle := _get_cycle(self.cycles, cycle_id)):
            return
        for cq_id in p.get("cq_ids_resolved", []):
            _remove_if_present(cycle.open_cqs, cq_id)
        if sig := p.get("algedonic_id_resolved"):
            _remove_if_present(cycle.open_algedonics, sig)

    # ------------------------------------------------------------------
    # Sprint events
    # ------------------------------------------------------------------

    def on_sprint_opened(self, p: dict[str, Any], cycle_id: str | None) -> None:
        if cycle := _get_cycle(self.cycles, cycle_id):
            if p["sprint_id"] not in cycle.active_sprints:
                cycle.active_sprints.append(p["sprint_id"])

    def on_sprint_closed(self, p: dict[str, Any], cycle_id: str | None) -> None:
        if cycle := _get_cycle(self.cycles, cycle_id):
            _remove_if_present(cycle.active_sprints, p["sprint_id"])

    # ------------------------------------------------------------------
    # Gate events
    # ------------------------------------------------------------------

    def on_gate_passed(self, p: dict[str, Any], event_id: str) -> None:
        self.gate_history.append(GateRecord(
            transition=p["transition"],
            status="passed",
            conditions=p.get("conditions", []),
            evaluated_at=event_id,
        ))

    def on_gate_held(self, p: dict[str, Any], event_id: str) -> None:
        self.gate_history.append(GateRecord(
            transition=p["transition"],
            status="held",
            conditions=p.get("blocking_items", []),
            evaluated_at=event_id,
        ))

    def on_gate_escalated(self, p: dict[str, Any], event_id: str) -> None:
        self.gate_history.append(GateRecord(
            transition=p["transition"],
            status="escalated",
            evaluated_at=event_id,
        ))

    # ------------------------------------------------------------------
    # Artifact events
    # ------------------------------------------------------------------

    def on_artifact_drafted(self, p: dict[str, Any]) -> None:
        aid = p["artifact_id"]
        self.artifact_registry[aid] = ArtifactRecord(
            artifact_id=aid,
            version=p["version"],
            status="draft",
            path=p["path"],
        )

    def on_artifact_baselined(self, p: dict[str, Any]) -> None:
        aid = p["artifact_id"]
        existing = self.artifact_registry.get(aid)
        self.artifact_registry[aid] = ArtifactRecord(
            artifact_id=aid,
            version=p["version"],
            status="baselined",
            path=p.get("path", existing.path if existing else ""),
            safety_relevant=existing.safety_relevant if existing else False,
            csco_sign_off=existing.csco_sign_off if existing else "not-required",
        )

    def on_artifact_superseded(self, p: dict[str, Any]) -> None:
        aid = p["artifact_id"]
        if existing := self.artifact_registry.get(aid):
            self.artifact_registry[aid] = ArtifactRecord(
                artifact_id=existing.artifact_id,
                version=existing.version,
                status="superseded",
                path=existing.path,
                safety_relevant=existing.safety_relevant,
                csco_sign_off=existing.csco_sign_off,
            )

    # ------------------------------------------------------------------
    # CQ events
    # ------------------------------------------------------------------

    def on_cq_raised(self, p: dict[str, Any], cycle_id: str | None) -> None:
        if not p.get("blocking"):
            return
        if cycle := _get_cycle(self.cycles, cycle_id):
            if p["cq_id"] not in cycle.open_cqs:
                cycle.open_cqs.append(p["cq_id"])

    def on_cq_closed(self, p: dict[str, Any]) -> None:
        for cycle in self.cycles.values():
            _remove_if_present(cycle.open_cqs, p["cq_id"])

    # ------------------------------------------------------------------
    # Algedonic events
    # ------------------------------------------------------------------

    def on_algedonic_raised(self, p: dict[str, Any], cycle_id: str | None) -> None:
        if cycle := _get_cycle(self.cycles, cycle_id):
            if p["signal_id"] not in cycle.open_algedonics:
                cycle.open_algedonics.append(p["signal_id"])

    def on_algedonic_resolved(self, p: dict[str, Any]) -> None:
        for cycle in self.cycles.values():
            _remove_if_present(cycle.open_algedonics, p["signal_id"])

    # ------------------------------------------------------------------
    # Dispatch: data-driven routing via module-level _HANDLERS table.
    # replay.py calls this in a thin loop; no dispatch logic lives there.
    # ------------------------------------------------------------------

    #: Known events that carry no WorkflowState change (audit-only).
    #: Not used for dispatch — just documents which types are intentional no-ops.
    AUDIT_ONLY: frozenset[str] = frozenset({
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

    def dispatch(
        self,
        event_type: str,
        payload: dict[str, Any],
        cycle_id: str | None,
        last_event_id: str,
    ) -> None:
        """
        Route one event to the appropriate mutation handler via _HANDLERS.
        AUDIT_ONLY events and unknown future types are both silent no-ops
        (forward-compatible).
        """
        if handler := _HANDLERS.get(event_type):
            handler(self, payload, cycle_id, last_event_id)

    # ------------------------------------------------------------------
    # Finalise
    # ------------------------------------------------------------------

    def to_workflow_state(self, last_event_id: str) -> WorkflowState:
        return WorkflowState(
            snapshot_at=last_event_id,
            timestamp=datetime.now(timezone.utc),
            engagement_id=self.engagement_id,
            active_cycles=[c.to_cycle_state() for c in self.cycles.values()],
            gate_history=list(self.gate_history),
            artifact_registry=dict(self.artifact_registry),
        )


# ---------------------------------------------------------------------------
# Handler table — the single authoritative map of event-type → mutation.
#
# Every handler has the same four-argument signature so _HANDLERS is
# homogeneously typed and dispatch() needs no per-event branching:
#
#   b  — StateBuilder   the mutable builder being updated
#   p  — dict           raw payload dict from the event envelope
#   c  — str | None     cycle_id extracted from the envelope (None if absent)
#   e  — str            last_event_id at the time of dispatch (used as
#                       the "evaluated_at" anchor for gate records)
#
# Parameters the handler method does not need are prefixed with _ (_c, _e)
# to signal intentional non-use without suppressing linter warnings.
#
# Defined after StateBuilder so the forward reference in _HandlerFn resolves.
# ---------------------------------------------------------------------------

_HANDLERS: dict[str, _HandlerFn] = {
    # Cycle lifecycle
    "cycle.initiated":              lambda b, p, _c, _e: b.on_cycle_initiated(p),
    "cycle.closed":                 lambda b, p, _c, _e: b.on_cycle_closed(p),
    "cycle.iteration-type-changed": lambda b, p, _c, _e: b.on_cycle_iteration_type_changed(p),
    # Phase lifecycle
    "phase.entered":                lambda b, p, c, _e: b.on_phase_entered(p, c),
    "phase.suspended":              lambda b, p, c, _e: b.on_phase_suspended(p, c),
    "phase.resumed":                lambda b, p, c, _e: b.on_phase_resumed(p, c),
    # Sprint lifecycle
    "sprint.opened":                lambda b, p, c, _e: b.on_sprint_opened(p, c),
    "sprint.closed":                lambda b, p, c, _e: b.on_sprint_closed(p, c),
    # Gate outcomes — record against the event_id, not the cycle_id
    "gate.passed":                  lambda b, p, _c, e: b.on_gate_passed(p, e),
    "gate.held":                    lambda b, p, _c, e: b.on_gate_held(p, e),
    "gate.escalated":               lambda b, p, _c, e: b.on_gate_escalated(p, e),
    # Artifact lifecycle
    "artifact.drafted":             lambda b, p, _c, _e: b.on_artifact_drafted(p),
    "artifact.baselined":           lambda b, p, _c, _e: b.on_artifact_baselined(p),
    "artifact.superseded":          lambda b, p, _c, _e: b.on_artifact_superseded(p),
    # Clarification questions
    "cq.raised":                    lambda b, p, c, _e: b.on_cq_raised(p, c),
    "cq.closed":                    lambda b, p, _c, _e: b.on_cq_closed(p),
    # Algedonic signals
    "algedonic.raised":             lambda b, p, c, _e: b.on_algedonic_raised(p, c),
    "algedonic.resolved":           lambda b, p, _c, _e: b.on_algedonic_resolved(p),
}
