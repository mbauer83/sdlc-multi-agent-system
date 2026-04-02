"""External source query event payloads (logged but not used for state reconstruction)."""
from __future__ import annotations
from typing import Literal
from pydantic import ConfigDict
from .base import BaseEventPayload
from ..registry import EventRegistry

SourceType = Literal["confluence", "jira", "git", "sharepoint", "api"]
QueryType = Literal["search", "fetch-by-id", "list"]


class SourceQueriedPayload(BaseEventPayload):
    model_config = ConfigDict(frozen=True)
    source_id: str
    source_type: SourceType
    query_type: QueryType
    query_summary: str   # One-line human-readable description of the query intent

EventRegistry.register("source.queried", SourceQueriedPayload)
