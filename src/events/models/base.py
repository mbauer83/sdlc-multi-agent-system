"""
Base event envelope and payload types for the SDLC workflow event store.

All workflow events share EventEnvelope. Each event type has a typed payload
subclass. The EventRegistry (registry.py) maps event_type strings to payload
classes to enable full round-trip serialisation and validation.

Events are immutable once created (frozen=True). The EventStore is the only
permitted write path to the SQLite database.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class BaseEventPayload(BaseModel):
    """Base class for all event-type-specific payload models."""
    model_config = ConfigDict(frozen=True)


class EventEnvelope(BaseModel):
    """
    Common envelope for all workflow events.
    Auto-generates event_id and timestamp if not provided.
    Validated by Pydantic v2 before insertion into the SQLite event store.
    """
    model_config = ConfigDict(frozen=True)

    event_id: str
    event_type: str  # Validated against EventRegistry at write time
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    engagement_id: str
    cycle_id: str | None = None
    actor: str  # canonical agent role name | "user" | "system"
    correlation_id: str | None = None  # artifact-id, sprint-id, cq-id, or algedonic-id
    payload: dict[str, Any]  # Serialised from the type-specific payload model

    @model_validator(mode="before")
    @classmethod
    def normalise_timestamp(cls, data: dict) -> dict:
        if "timestamp" not in data or data["timestamp"] is None:
            data["timestamp"] = datetime.now(timezone.utc)
        return data


class EventValidationError(ValueError):
    """Raised when an event fails Pydantic validation before DB insertion."""
