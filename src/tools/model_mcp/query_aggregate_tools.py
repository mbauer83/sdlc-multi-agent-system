from __future__ import annotations

from typing import Literal

from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]

from src.tools.model_mcp.context import RepoScope, repo_cached, resolve_repo_roots, roots_key


def register_query_aggregate_tools(mcp: FastMCP) -> None:
    @mcp.tool(
        name="model_query_count_artifacts_by",
        title="Model Query: Count Artifacts By",
        description=(
            "Aggregate artifact counts for common inventory dimensions. "
            "Supported group_by: artifact_type, diagram_type, phase_produced, owner_agent."
            "\n\nRepo selection: repo_scope defaults to both (engagement + enterprise)."
        ),
        structured_output=True,
    )
    def model_query_count_artifacts_by(
        group_by: Literal["artifact_type", "diagram_type", "phase_produced", "owner_agent"],
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
        include_connections: bool = True,
        include_diagrams: bool = True,
    ) -> dict[str, object]:
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

        counts = repo.count_artifacts_by(
            group_by,
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

        return {
            "repo_roots": [str(p) for p in roots],
            "repo_scope": repo_scope,
            "group_by": group_by,
            "counts": counts,
        }
