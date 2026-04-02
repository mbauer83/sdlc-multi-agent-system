"""Sprint lifecycle event payloads."""
from __future__ import annotations
from typing import Literal
from pydantic import ConfigDict
from .base import BaseEventPayload
from ..registry import EventRegistry

SprintStream = Literal["architecture", "business", "implementation"]


class SprintOpenedPayload(BaseEventPayload):
    model_config = ConfigDict(frozen=True)
    sprint_id: str
    stream: SprintStream
    scope: str  # Brief description of sprint scope

EventRegistry.register("sprint.opened", SprintOpenedPayload)


class SprintSuspendedPayload(BaseEventPayload):
    model_config = ConfigDict(frozen=True)
    sprint_id: str
    reason: str

EventRegistry.register("sprint.suspended", SprintSuspendedPayload)


class SprintClosedPayload(BaseEventPayload):
    model_config = ConfigDict(frozen=True)
    sprint_id: str
    artifacts_produced: list[str] = []
    open_items: list[str] = []

EventRegistry.register("sprint.closed", SprintClosedPayload)
