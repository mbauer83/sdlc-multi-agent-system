"""Specialist invocation event payloads (PM decision layer)."""
from __future__ import annotations
from pydantic import ConfigDict
from .base import BaseEventPayload
from ..registry import EventRegistry


class SpecialistInvokedPayload(BaseEventPayload):
    model_config = ConfigDict(frozen=True)
    agent_id: str          # e.g. "SA", "SwA", "DE"
    skill_id: str          # skill frontmatter skill-id
    task: str              # natural-language task description

EventRegistry.register("specialist.invoked", SpecialistInvokedPayload)


class SpecialistCompletedPayload(BaseEventPayload):
    model_config = ConfigDict(frozen=True)
    agent_id: str
    skill_id: str
    outcome: str = "success"   # "success" | "failed" | "cq-blocked"

EventRegistry.register("specialist.completed", SpecialistCompletedPayload)
