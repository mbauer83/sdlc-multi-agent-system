"""Sprint review event payloads."""
from __future__ import annotations
from typing import Literal
from pydantic import ConfigDict
from .base import BaseEventPayload
from ..registry import EventRegistry


class ReviewPendingPayload(BaseEventPayload):
    model_config = ConfigDict(frozen=True)
    sprint_id: str
    artifact_ids: list[str] = []

EventRegistry.register("review.pending", ReviewPendingPayload)


class ReviewSprintClosedPayload(BaseEventPayload):
    model_config = ConfigDict(frozen=True)
    sprint_id: str
    approved_count: int = 0
    revision_count: int = 0
    rejected_count: int = 0

EventRegistry.register("review.sprint-closed", ReviewSprintClosedPayload)
