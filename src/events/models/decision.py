"""PM decision record event payload."""
from __future__ import annotations
from typing import Literal
from pydantic import ConfigDict
from .base import BaseEventPayload
from ..registry import EventRegistry


class DecisionRecordedPayload(BaseEventPayload):
    model_config = ConfigDict(frozen=True)
    decision_id: str
    decision_type: Literal["routing", "gate", "escalation", "cq-resolution"]
    rationale: str
    artifact_id: str | None = None

EventRegistry.register("decision.recorded", DecisionRecordedPayload)
