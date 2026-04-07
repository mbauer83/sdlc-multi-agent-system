from __future__ import annotations

from dataclasses import asdict
from typing import Literal

from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]

from src.tools.model_mcp.context import RepoScope, repo_cached, resolve_repo_roots, roots_key


def _project(record: dict[str, object], fields: list[str] | None) -> dict[str, object]:
    if not fields:
        return record
    return {field: record[field] for field in fields if field in record}


def register_query_list_read_tools(mcp: FastMCP) -> None:
    @mcp.tool(
        name="model_query_list_artifacts",
        title="Model Query: List Artifacts",
        description=(
            "List artifacts (metadata-only) using framework-aligned filters (AND semantics). "
            "Returns lightweight summaries without loading full bodies. "
            "\n\nKey filters: artifact_type, layer, owner_agent, phase_produced, status, safety_relevant, engagement. "
            "\n\nSet include_connections/include_diagrams if you want non-entity results." 
            "\n\nRepo selection: repo_scope defaults to both (engagement + enterprise)."
        ),
        structured_output=True,
    )
    def model_query_list_artifacts(
        *,
        repo_root: str | None = None,
        repo_scope: RepoScope = "both",
        refresh: bool = False,
        artifact_type: str | list[str] | None = None,
        layer: str | list[str] | None = None,
        owner_agent: str | list[str] | None = None,
        phase_produced: str | list[str] | None = None,
        status: str | list[str] | None = None,
        safety_relevant: bool | None = None,
        engagement: str | None = None,
        include_connections: bool = False,
        include_diagrams: bool = False,
        fields: list[str] | None = None,
    ) -> list[dict[str, object]]:  # noqa: PLR0913
        roots = resolve_repo_roots(
            repo_scope=repo_scope,
            repo_root=repo_root,
            repo_preset=None,
            enterprise_root=None,
        )
        key = roots_key(roots)
        repo = repo_cached(key)
        if refresh:
            repo.refresh()
        summaries = repo.list_artifacts(
            artifact_type=artifact_type,
            layer=layer,
            owner_agent=owner_agent,
            phase_produced=phase_produced,
            status=status,
            safety_relevant=safety_relevant,
            engagement=engagement,
            include_connections=include_connections,
            include_diagrams=include_diagrams,
        )
        out: list[dict[str, object]] = []
        for s in summaries:
            d = asdict(s)
            d["path"] = str(s.path)
            d["repo_scope"] = repo_scope
            out.append(_project(d, fields))
        return out

    @mcp.tool(
        name="model_query_read_artifact",
        title="Model Query: Read Artifact",
        description=(
            "Read one artifact by artifact_id. "
            "mode='summary' returns frontmatter + a short content snippet; mode='full' returns full content and display blocks."
            "\n\nRepo selection: repo_scope defaults to both (engagement + enterprise)."
        ),
        structured_output=True,
    )
    def model_query_read_artifact(
        artifact_id: str,
        *,
        mode: Literal["summary", "full"] = "summary",
        repo_root: str | None = None,
        repo_scope: RepoScope = "both",
        refresh: bool = False,
    ) -> dict[str, object] | None:
        roots = resolve_repo_roots(
            repo_scope=repo_scope,
            repo_root=repo_root,
            repo_preset=None,
            enterprise_root=None,
        )
        key = roots_key(roots)
        repo = repo_cached(key)
        if refresh:
            repo.refresh()
        result = repo.read_artifact(artifact_id, mode=mode)
        if result is None:
            return None
        result["repo_roots"] = [str(p) for p in roots]
        result["repo_scope"] = repo_scope
        return result
