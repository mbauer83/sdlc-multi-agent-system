"""Artifact handoff event payloads."""
from __future__ import annotations
from typing import Literal
from pydantic import ConfigDict
from .base import BaseEventPayload
from ..registry import EventRegistry


class HandoffIssuedPayload(BaseEventPayload):
    model_config = ConfigDict(frozen=True)
    handoff_id: str
    artifact_id: str
    from_agent: str
    to_agents: list[str]

EventRegistry.register("handoff.issued", HandoffIssuedPayload)


class HandoffAcknowledgedPayload(BaseEventPayload):
    model_config = ConfigDict(frozen=True)
    handoff_id: str
    acknowledged_by: str
    retrieval_intent: Literal["summary", "full"]

EventRegistry.register("handoff.acknowledged", HandoffAcknowledgedPayload)
