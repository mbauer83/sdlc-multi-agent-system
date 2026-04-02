"""
Phase lifecycle event payloads.

These events track phase entries, revisitations, suspensions (blocking CQs),
and exits. The iteration_type and trigger fields support the ADM's non-linear,
iterative nature: phases can be entered multiple times within a cycle.
"""

from __future__ import annotations

from typing import Literal

from pydantic import ConfigDict

from .base import BaseEventPayload
from ..registry import EventRegistry

ADMPhase = Literal["Prelim", "A", "B", "C", "D", "E", "F", "G", "H", "RM"]

IterationType = Literal[
    "context",       # Architecture Context iteration: Prelim + A
    "definition",    # Architecture Definition iteration: B–D (+ E/F optional)
    "transition",    # Transition Planning iteration: E–F
    "governance",    # Architecture Governance iteration: G + H
]

PhaseEntryTrigger = Literal[
    "initial",           # First entry into this phase in this cycle
    "revisit",           # Phase revisited within the same iteration (e.g., refinement)
    "phase-h-return",    # Phase H change impact assessment triggers return here
    "requirements-change", # Requirements Management change triggers return here
    "gate-rejection",    # Phase gate held; returning to complete outstanding items
    "parent-cycle",      # Initiated by a parent ADM cycle
]


class PhaseEnteredPayload(BaseEventPayload):
    model_config = ConfigDict(frozen=True)
    phase_id: ADMPhase
    iteration_type: IterationType
    iteration_number: int           # 1-based; increments with each revisit
    trigger: PhaseEntryTrigger
    source_event_id: str | None = None  # If trigger is phase-h-return or requirements-change,
                                         # the event_id of the change record or CQ that caused it

EventRegistry.register("phase.entered", PhaseEnteredPayload)


class PhaseSuspendedPayload(BaseEventPayload):
    model_config = ConfigDict(frozen=True)
    phase_id: ADMPhase
    reason: Literal["blocking-cq", "algedonic-halt", "dependency-wait"]
    blocking_cq_id: str | None = None   # set when reason is blocking-cq
    algedonic_id: str | None = None     # set when reason is algedonic-halt

EventRegistry.register("phase.suspended", PhaseSuspendedPayload)


class PhaseResumedPayload(BaseEventPayload):
    model_config = ConfigDict(frozen=True)
    phase_id: ADMPhase
    cq_ids_resolved: list[str] = []
    algedonic_id_resolved: str | None = None

EventRegistry.register("phase.resumed", PhaseResumedPayload)


class PhaseExitedPayload(BaseEventPayload):
    model_config = ConfigDict(frozen=True)
    phase_id: ADMPhase
    artifacts_produced: list[str]  # artifact-ids baselined in this phase entry

EventRegistry.register("phase.exited", PhaseExitedPayload)


class PhaseReturnTriggeredPayload(BaseEventPayload):
    """
    Emitted when a Phase H change impact assessment or a requirements change
    determines that an earlier phase must be re-entered. The actual re-entry
    is recorded via a subsequent PhaseEnteredPayload.
    """
    model_config = ConfigDict(frozen=True)
    target_phase: ADMPhase          # Phase to return to
    trigger_source: Literal["phase-h", "requirements-change", "algedonic"]
    change_record_id: str | None = None   # CR artifact-id if trigger is phase-h
    cq_id: str | None = None             # CQ-id if trigger is requirements-change
    affected_artifacts: list[str] = []   # artifact-ids that need revision

EventRegistry.register("phase.return-triggered", PhaseReturnTriggeredPayload)
