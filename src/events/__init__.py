"""
SDLC Workflow EventStore package.

Import EventStore and payload models from here. All payload imports trigger
EventRegistry registration via the register() calls at module level in each
models/*.py file.

Usage:
    from src.events import EventStore
    from src.events.models.phase import PhaseEnteredPayload

    store = EventStore(engagement_id="ENG-001")
    store.append(PhaseEnteredPayload(phase_id="A", iteration_type="context",
                                     iteration_number=1, trigger="initial"),
                 actor="project-manager")
    state = store.current_state()
"""

# Trigger all model registrations by importing model modules
from .models import phase, cycle, gate, sprint, artifact, handoff, cq, algedonic, source  # noqa: F401

from .event_store import EventStore
from .models.base import BaseEventPayload, EventEnvelope, EventValidationError
from .models.state import WorkflowState, CycleState, GateRecord, ArtifactRecord

__all__ = [
    "EventStore",
    "BaseEventPayload",
    "EventEnvelope",
    "EventValidationError",
    "WorkflowState",
    "CycleState",
    "GateRecord",
    "ArtifactRecord",
]
