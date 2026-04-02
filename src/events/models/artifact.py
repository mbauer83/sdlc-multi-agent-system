"""Artifact lifecycle event payloads."""
from __future__ import annotations
from typing import Literal
from pydantic import ConfigDict
from .base import BaseEventPayload
from ..registry import EventRegistry

EnterpriseLevel = Literal["strategic", "segment", "capability"]


class ArtifactDraftedPayload(BaseEventPayload):
    model_config = ConfigDict(frozen=True)
    artifact_id: str
    artifact_type: str
    version: str   # 0.x.x
    path: str

EventRegistry.register("artifact.drafted", ArtifactDraftedPayload)


class ArtifactBaselinedPayload(BaseEventPayload):
    model_config = ConfigDict(frozen=True)
    artifact_id: str
    version: str   # ≥ 1.0.0
    path: str

EventRegistry.register("artifact.baselined", ArtifactBaselinedPayload)


class ArtifactSupersededPayload(BaseEventPayload):
    model_config = ConfigDict(frozen=True)
    artifact_id: str
    successor_id: str

EventRegistry.register("artifact.superseded", ArtifactSupersededPayload)


class ArtifactPromotedPayload(BaseEventPayload):
    model_config = ConfigDict(frozen=True)
    artifact_id: str
    target_level: EnterpriseLevel
    target_path: str

EventRegistry.register("artifact.promoted", ArtifactPromotedPayload)
