"""
Universal agent tools — artifact query, event query, and tool registration.

See also:
  escalation_tools.py  — emit_event, raise_cq, raise_algedonic
  learning_tools.py    — query_learnings, record_learning, framework docs

All tools are registered on an agent via register_universal_tools(agent).
"""

from __future__ import annotations

from typing import Any

from pydantic_ai import RunContext

from src.agents.deps import AgentDeps
from src.common.model_query import ModelRepository


# ---------------------------------------------------------------------------
# Artifact query tools
# ---------------------------------------------------------------------------

def read_artifact(ctx: RunContext[AgentDeps], artifact_id: str, mode: str = "summary") -> str:
    """
    Read an artifact by its artifact-id.
    mode="summary" → frontmatter + first two §content sections (default).
    mode="full"    → entire file content.
    """
    repo = _model_repo(ctx)
    result = repo.read_artifact(artifact_id, mode=mode)
    if result is None:
        return f"[Artifact '{artifact_id}' not found]"
    return result


def list_artifacts(
    ctx: RunContext[AgentDeps],
    artifact_type: str | None = None,
    status: str | None = None,
    layer: str | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """
    List artifacts with optional filters. Returns metadata only (no content bodies).

    artifact_type: e.g. "business-architecture", "value-stream", "stakeholder"
    status:        "draft" | "baselined" | "superseded"
    layer:         ArchiMate layer prefix e.g. "motivation", "business"
    """
    repo = _model_repo(ctx)
    filters: dict[str, str] = {}
    if artifact_type:
        filters["artifact_type"] = artifact_type
    if status:
        filters["status"] = status
    if layer:
        filters["layer"] = layer
    results = repo.list_artifacts(**filters)
    return [r.to_dict() for r in results[:limit]]


def search_artifacts(
    ctx: RunContext[AgentDeps],
    query: str,
    artifact_type: str | None = None,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """
    Keyword search across all artifacts. Returns ranked (metadata, snippet) pairs.
    Use when artifact type is unknown or discovery is by concept.
    """
    repo = _model_repo(ctx)
    kwargs: dict[str, Any] = {}
    if artifact_type:
        kwargs["artifact_type"] = artifact_type
    results = repo.search_artifacts(query, limit=limit, **kwargs)
    return [
        {"artifact_id": r.artifact_id, "title": r.title, "snippet": snippet}
        for r, snippet in results
    ]


# ---------------------------------------------------------------------------
# Event store query tool
# ---------------------------------------------------------------------------

def query_event_store(
    ctx: RunContext[AgentDeps],
    event_type: str | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Query recent EventStore events, optionally filtered by event_type."""
    return ctx.deps.event_store.query(event_type=event_type, limit=limit)


# ---------------------------------------------------------------------------
# Tool registration
# ---------------------------------------------------------------------------

def register_universal_tools(agent: Any) -> None:
    """Register all universal tools on a PydanticAI Agent instance."""
    from .escalation_tools import emit_event, raise_algedonic, raise_cq
    from .learning_tools import (
        query_learnings,
        read_framework_doc,
        record_learning,
        search_framework_docs,
    )

    for fn in (
        read_artifact,
        list_artifacts,
        search_artifacts,
        query_event_store,
        emit_event,
        raise_cq,
        raise_algedonic,
        query_learnings,
        record_learning,
        search_framework_docs,
        read_framework_doc,
    ):
        agent.tool(fn)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _model_repo(ctx: RunContext[AgentDeps]) -> ModelRepository:
    roots = [ctx.deps.architecture_repo_path, ctx.deps.enterprise_repo_path]
    return ModelRepository(roots=[r for r in roots if r.exists()])
