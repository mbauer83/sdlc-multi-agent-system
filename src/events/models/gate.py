"""Phase gate event payloads."""
from __future__ import annotations
from typing import Literal
from pydantic import ConfigDict
from .base import BaseEventPayload
from ..registry import EventRegistry


class GateEvaluatedPayload(BaseEventPayload):
    model_config = ConfigDict(frozen=True)
    transition: str               # e.g. "A→B"
    checklist_results: dict[str, bool] = {}  # checklist item → passed

EventRegistry.register("gate.evaluated", GateEvaluatedPayload)


class GatePassedPayload(BaseEventPayload):
    model_config = ConfigDict(frozen=True)
    transition: str
    conditions: list[str] = []   # conditional-pass conditions, if any

EventRegistry.register("gate.passed", GatePassedPayload)


class GateHeldPayload(BaseEventPayload):
    model_config = ConfigDict(frozen=True)
    transition: str
    blocking_items: list[str]
    target_sprint: str | None = None

EventRegistry.register("gate.held", GateHeldPayload)


class GateEscalatedPayload(BaseEventPayload):
    model_config = ConfigDict(frozen=True)
    transition: str
    algedonic_id: str

EventRegistry.register("gate.escalated", GateEscalatedPayload)
