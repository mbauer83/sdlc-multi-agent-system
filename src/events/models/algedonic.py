"""Algedonic signal event payloads."""
from __future__ import annotations
from typing import Literal
from pydantic import ConfigDict
from .base import BaseEventPayload
from ..registry import EventRegistry

AlgedonicSeverity = Literal["S1", "S2", "S3", "S4"]
AlgedonicCategory = Literal["SC", "RB", "TC", "GV", "IA", "KG"]


class AlgedonicRaisedPayload(BaseEventPayload):
    model_config = ConfigDict(frozen=True)
    signal_id: str
    trigger_id: str    # ALG-001 through ALG-018
    category: AlgedonicCategory
    severity: AlgedonicSeverity

EventRegistry.register("algedonic.raised", AlgedonicRaisedPayload)


class AlgedonicAcknowledgedPayload(BaseEventPayload):
    model_config = ConfigDict(frozen=True)
    signal_id: str
    acknowledged_by: str

EventRegistry.register("algedonic.acknowledged", AlgedonicAcknowledgedPayload)


class AlgedonicResolvedPayload(BaseEventPayload):
    model_config = ConfigDict(frozen=True)
    signal_id: str
    resolution: str
    artifacts_updated: list[str] = []

EventRegistry.register("algedonic.resolved", AlgedonicResolvedPayload)
