"""
Universal agent tools — artifact query, event query, memento state, and registration.

See also:
  escalation_tools.py  — emit_event, raise_cq, raise_algedonic
  learning_tools.py    — query_learnings, record_learning, framework docs

All tools are registered on an agent via register_universal_tools(agent).
"""

from __future__ import annotations

import json
import logging
from typing import Any

from pydantic_ai import RunContext

from src.agents.deps import AgentDeps
from src.common.model_query import ModelRepository

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Artifact query tools
# ---------------------------------------------------------------------------

def read_artifact(ctx: RunContext[AgentDeps], artifact_id: str, mode: str = "summary") -> str:
    """
    Read an artifact by its artifact-id.
    mode="summary" → frontmatter + first two §content sections (default).
    mode="full"    → entire file content.
    """
    try:
        repo = _model_repo(ctx)
        result = repo.read_artifact(artifact_id, mode=mode)
        if result is None:
            return f"[Artifact '{artifact_id}' not found]"
        # result is dict[str, object]; serialize to JSON string for the model
        return json.dumps(result, default=str)
    except Exception as exc:  # noqa: BLE001
        log.warning("read_artifact(%s) failed: %s", artifact_id, exc)
        return f"[Error reading artifact '{artifact_id}': {exc}]"


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
    try:
        repo = _model_repo(ctx)
        filters: dict[str, str] = {}
        if artifact_type:
            filters["artifact_type"] = artifact_type
        if status:
            filters["status"] = status
        if layer:
            filters["layer"] = layer
        results = repo.list_artifacts(**filters)
        return [
            {
                "artifact_id": r.artifact_id,
                "artifact_type": r.artifact_type,
                "name": r.name,
                "version": r.version,
                "status": r.status,
                "phase_produced": r.phase_produced,
                "owner_agent": r.owner_agent,
                "engagement": r.engagement,
                "record_type": r.record_type,
            }
            for r in results[:limit]
        ]
    except Exception as exc:  # noqa: BLE001
        log.warning("list_artifacts() failed: %s", exc)
        return []


def search_artifacts(
    ctx: RunContext[AgentDeps],
    query: str,
    artifact_type: str | None = None,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """
    Keyword search across all artifacts. Returns ranked results with scores.
    Use when artifact type is unknown or discovery is by concept.
    """
    try:
        repo = _model_repo(ctx)
        kwargs: dict[str, Any] = {}
        if artifact_type:
            kwargs["artifact_type"] = artifact_type
        results = repo.search_artifacts(query, limit=limit, **kwargs)
        return [
            {
                "artifact_id": hit.record.artifact_id,
                "name": getattr(hit.record, "name", hit.record.artifact_id),
                "score": hit.score,
                "record_type": hit.record_type,
            }
            for hit in results.hits
        ]
    except Exception as exc:  # noqa: BLE001
        log.warning("search_artifacts(%r) failed: %s", query, exc)
        return []


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
# Memento state tools (Tier 2 of the five-tier memory architecture)
# ---------------------------------------------------------------------------

def get_memento_state(
    ctx: RunContext[AgentDeps],
    phase: str,
) -> dict[str, Any] | None:
    """
    Read ephemeral continuity state for the current (agent, phase).

    Returns the MementoState as a dict (key_decisions, open_threads,
    partial_context, skill_id, recorded_at), or None on first invocation
    for this phase.

    Call as Step 0.M immediately after Step 0.L (learnings lookup).
    Governed by framework/learning-protocol.md §13.
    """
    from src.agents.memento_store import MementoStore

    store = MementoStore(
        engagement_id=ctx.deps.engagement_id,
        agent_role=ctx.deps.agent_id,
        db_path=ctx.deps.engagement_path / "workflow.db",
    )
    state = store.get(phase)
    if state is None:
        return None
    return state.model_dump()


def save_memento_state(
    ctx: RunContext[AgentDeps],
    phase: str,
    key_decisions: list[str],
    open_threads: list[str],
    partial_context: str = "",
) -> None:
    """
    Overwrite the MementoState slot for the current (agent, phase).

    key_decisions: max 3 items summarising decisions made this invocation.
    open_threads:  max 3 items flagging unresolved questions or dependencies.
    partial_context: optional condensed prose digest (≤ 100 tokens).

    Call at the end of every skill execution before learning checks.
    Governed by framework/learning-protocol.md §13.3.
    """
    from src.agents.memento_store import MementoStore
    from src.models.memento import MementoState

    state = MementoState(
        phase=phase,
        invocation_id=ctx.deps.engagement_id,
        skill_id=ctx.deps.active_skill_id,
        key_decisions=key_decisions,
        open_threads=open_threads,
        partial_context=partial_context,
    )
    store = MementoStore(
        engagement_id=ctx.deps.engagement_id,
        agent_role=ctx.deps.agent_id,
        db_path=ctx.deps.engagement_path / "workflow.db",
    )
    store.save(state)


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
        get_memento_state,
        save_memento_state,
    ):
        agent.tool(fn)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _model_repo(ctx: RunContext[AgentDeps]) -> ModelRepository:
    roots = [ctx.deps.architecture_repo_path, ctx.deps.enterprise_repo_path]
    existing = [r for r in roots if r.exists()]
    if not existing:
        existing = [ctx.deps.architecture_repo_path]  # let ModelRepository report missing root
    return ModelRepository(repo_root=existing)
