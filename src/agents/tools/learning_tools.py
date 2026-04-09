"""
Learning and framework tools.

  query_learnings   — retrieve corrections/amendments/episodic entries
  record_learning   — persist a new learning entry
  search_framework_docs / read_framework_doc — framework knowledge access

Full LearningStore (LangGraph BaseStore) wired in Stage 5 MementoStore work.
MVP uses file-based scan for engagements/<id>/work-repositories/learnings/.
"""

from __future__ import annotations

import datetime
from typing import Any

from pydantic_ai import RunContext

from src.agents.deps import AgentDeps


# ---------------------------------------------------------------------------
# Learning tools
# ---------------------------------------------------------------------------

def query_learnings(
    ctx: RunContext[AgentDeps],
    phase: str | None = None,
    artifact_type: str | None = None,
    skill_id: str | None = None,
    entry_type: str | None = None,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """
    Query the learning store for corrections, skill-amendments, and episode summaries.

    phase:        ADM phase filter ("A", "B", ...)
    artifact_type: e.g. "business-architecture"
    skill_id:     exact skill-id match for skill-amendment retrieval
    entry_type:   "correction" | "skill-amendment" | "episodic"
    """
    learnings_dir = ctx.deps.engagement_path / "work-repositories" / "learnings"
    if not learnings_dir.exists():
        return []

    results: list[dict[str, Any]] = []
    for f in sorted(learnings_dir.glob("*.md"), reverse=True)[: limit * 4]:
        try:
            fm = _parse_frontmatter(f.read_text())
            if phase and fm.get("phase") not in (phase, None, ""):
                continue
            if artifact_type and fm.get("artifact-type") != artifact_type:
                continue
            if skill_id and fm.get("skill-id") != skill_id:
                continue
            if entry_type and fm.get("entry-type") != entry_type:
                continue
            results.append(fm)
        except Exception:  # noqa: BLE001
            pass
        if len(results) >= limit:
            break
    return results


def record_learning(
    ctx: RunContext[AgentDeps],
    artifact_type: str,
    entry_type: str,
    correction: str,
    importance: str = "S3",
    phase: str | None = None,
    error_type: str | None = None,
) -> str:
    """
    Record a learning entry.

    artifact_type: the PRIMARY OUTPUT artifact type of this skill (not inputs)
    entry_type:    "correction" | "skill-amendment" | "episodic"
    correction:    imperative first-person voice, ≤300 chars/sentence, ≤3 sentences
    Returns the filename of the written entry.
    """
    learnings_dir = ctx.deps.engagement_path / "work-repositories" / "learnings"
    learnings_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S")
    agent = ctx.deps.agent_id
    fname = f"{ts}-{agent}-{artifact_type[:20]}.md"
    (learnings_dir / fname).write_text(
        f"---\nagent: {agent}\nphase: {phase or ''}\n"
        f"artifact-type: {artifact_type}\nentry-type: {entry_type}\n"
        f"importance: {importance}\nerror-type: {error_type or ''}\n"
        f"skill-id: {ctx.deps.active_skill_id}\n---\n\n{correction}\n"
    )
    return fname


# ---------------------------------------------------------------------------
# Framework knowledge tools
# ---------------------------------------------------------------------------

def search_framework_docs(
    ctx: RunContext[AgentDeps],
    query: str,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """Keyword search across framework/spec sections. Returns scored snippets."""
    from src.common.framework_query import FrameworkKnowledgeIndex

    # Index root is the repo root (parent of framework/)
    idx = FrameworkKnowledgeIndex(ctx.deps.framework_path.parent)
    return [
        {
            "doc_id": h.section.doc_id,
            "section_id": h.section.section_id,
            "heading": h.section.heading,
            "snippet": h.snippet,
        }
        for h in idx.search_docs(query, limit=limit)
    ]


def read_framework_doc(
    ctx: RunContext[AgentDeps],
    doc_id: str,
    section_id: str | None = None,
    mode: str = "summary",
) -> str:
    """
    Read a framework document or specific section.
    mode="summary" returns the first 400 chars of the section (default).
    mode="full" returns the complete section text.
    """
    from src.common.framework_query import FrameworkKnowledgeIndex

    idx = FrameworkKnowledgeIndex(ctx.deps.framework_path.parent)
    return str(idx.read_doc(doc_id, section_id=section_id, mode=mode))


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

def _parse_frontmatter(text: str) -> dict[str, Any]:
    """Minimal YAML frontmatter parse."""
    import yaml

    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return yaml.safe_load(text[3:end]) or {}
    return {}
