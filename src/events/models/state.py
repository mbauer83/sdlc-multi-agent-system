"""
WorkflowState: the current computed state of an engagement's ADM workflow.

Stored as a row in the SQLite snapshots table (JSON-serialised). Reconstructed
by replaying the event log when the snapshot is absent or corrupted.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class CycleState(BaseModel):
    model_config = ConfigDict(frozen=True)

    cycle_id: str
    iteration_type: Literal["context", "definition", "transition", "governance"]
    parent_cycle_id: str | None = None
    current_phase: str  # "Prelim" | "A" | "B" | "C" | "D" | "E" | "F" | "G" | "H" | "RM"
    phase_visit_counts: dict[str, int] = {}  # {"A": 1, "B": 2, ...}
    active_sprints: list[str] = []
    open_cqs: list[str] = []        # cq-ids
    open_algedonics: list[str] = [] # signal-ids


class GateRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    transition: str  # e.g. "A→B"
    status: Literal["passed", "held", "pending", "escalated"]
    conditions: list[str] = []  # conditional-pass conditions, if any
    evaluated_at: str | None = None  # event_id of the gate.evaluated event


class ArtifactRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    artifact_id: str
    version: str
    status: Literal["draft", "baselined", "superseded", "archived"]
    path: str
    safety_relevant: bool = False
    csco_sign_off: Literal["true", "false", "not-required"] = "not-required"


class WorkflowState(BaseModel):
    """
    Current computed state of an engagement's ADM workflow.
    This is NOT mutable at rest — it is produced by replaying events or
    reading the most recent snapshot from the SQLite snapshots table.
    """
    model_config = ConfigDict(frozen=True)

    snapshot_at: str        # event_id of the last event included in this snapshot
    timestamp: datetime
    engagement_id: str
    active_cycles: list[CycleState] = []
    gate_history: list[GateRecord] = []
    artifact_registry: dict[str, ArtifactRecord] = {}

    def phase_visit_count(self, cycle_id: str, phase_id: str) -> int:
        """Return how many times a phase has been entered in a given cycle."""
        for cycle in self.active_cycles:
            if cycle.cycle_id == cycle_id:
                return cycle.phase_visit_counts.get(phase_id, 0)
        return 0

    def is_phase_revisit(self, cycle_id: str, phase_id: str) -> bool:
        """True if the phase has been entered more than once (i.e., is a revisit)."""
        return self.phase_visit_count(cycle_id, phase_id) > 1
