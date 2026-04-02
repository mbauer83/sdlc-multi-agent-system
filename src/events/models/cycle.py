"""ADM cycle lifecycle event payloads."""
from __future__ import annotations
from typing import Literal
from pydantic import ConfigDict
from .base import BaseEventPayload
from ..registry import EventRegistry

IterationType = Literal["context", "definition", "transition", "governance"]
CycleLevel = Literal["strategic", "segment", "capability"]


class CycleInitiatedPayload(BaseEventPayload):
    model_config = ConfigDict(frozen=True)
    cycle_id: str
    iteration_type: IterationType
    cycle_level: CycleLevel = "capability"
    parent_cycle_id: str | None = None  # set for child cycles

EventRegistry.register("cycle.initiated", CycleInitiatedPayload)


class CycleClosedPayload(BaseEventPayload):
    model_config = ConfigDict(frozen=True)
    cycle_id: str
    outcomes: list[str] = []
    promoted_artifacts: list[str] = []

EventRegistry.register("cycle.closed", CycleClosedPayload)


class CycleIterationTypeChangedPayload(BaseEventPayload):
    model_config = ConfigDict(frozen=True)
    cycle_id: str
    from_type: IterationType
    to_type: IterationType
    reason: str

EventRegistry.register("cycle.iteration-type-changed", CycleIterationTypeChangedPayload)
