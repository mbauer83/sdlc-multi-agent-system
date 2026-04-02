"""Clarification Request (CQ) event payloads."""
from __future__ import annotations
from typing import Literal
from pydantic import ConfigDict
from .base import BaseEventPayload
from ..registry import EventRegistry


class CQRaisedPayload(BaseEventPayload):
    model_config = ConfigDict(frozen=True)
    cq_id: str
    blocking: bool
    target: str   # "user" | "pm" | agent role name
    blocks_task: str | None = None

EventRegistry.register("cq.raised", CQRaisedPayload)


class CQAnsweredPayload(BaseEventPayload):
    model_config = ConfigDict(frozen=True)
    cq_id: str
    answered_by: str

EventRegistry.register("cq.answered", CQAnsweredPayload)


class CQAssumptionMadePayload(BaseEventPayload):
    model_config = ConfigDict(frozen=True)
    cq_id: str
    assumption_text: str

EventRegistry.register("cq.assumption-made", CQAssumptionMadePayload)


class CQClosedPayload(BaseEventPayload):
    model_config = ConfigDict(frozen=True)
    cq_id: str
    resolution: Literal["answered", "withdrawn", "superseded"]

EventRegistry.register("cq.closed", CQClosedPayload)
