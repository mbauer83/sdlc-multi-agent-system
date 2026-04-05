from __future__ import annotations

from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]

from src.tools.model_mcp.context import RepoPreset, RepoScope, repo_cached, resolve_repo_roots, roots_key


def register_query_search_tools(mcp: FastMCP) -> None:
    @mcp.tool(
        name="model_query_search_artifacts",
        title="Model Query: Search Artifacts",
        description=(
            "Search artifacts by text query (keyword-scored; may include semantic supplement if configured). "
            "Returns ranked hits as (score + summary record). "
            "\n\nFilters: limit, layer, artifact_type, include_connections, include_diagrams." 
            "\n\nRepo selection: repo_scope defaults to both (engagement + enterprise)."
        ),
        structured_output=True,
    )
    def model_query_search_artifacts(
        query: str,
        *,
        limit: int = 10,
        layer: str | list[str] | None = None,
        artifact_type: str | list[str] | None = None,
        engagement: str | None = None,
        include_connections: bool = True,
        include_diagrams: bool = True,
        repo_root: str | None = None,
        repo_preset: RepoPreset | None = None,
        enterprise_root: str | None = None,
        repo_scope: RepoScope = "both",
        refresh: bool = False,
    ) -> dict[str, object]:
        roots = resolve_repo_roots(
            repo_scope=repo_scope,
            repo_root=repo_root,
            repo_preset=repo_preset,
            enterprise_root=enterprise_root,
        )
        key = roots_key(roots)
        repo = repo_cached(key)
        if refresh:
            repo.refresh()

        result = repo.search_artifacts(
            query,
            limit=limit,
            layer=layer,
            artifact_type=artifact_type,
            engagement=engagement,
            include_connections=include_connections,
            include_diagrams=include_diagrams,
        )

        hits: list[dict[str, object]] = []
        for h in result.hits:
            aid = getattr(h.record, "artifact_id", "")
            record_summary = repo.read_artifact(aid, mode="summary") if aid else None
            hits.append({
                "score": h.score,
                "record_type": h.record_type,
                "artifact_id": aid,
                "record": record_summary,
            })

        return {
            "repo_roots": [str(p) for p in roots],
            "repo_scope": repo_scope,
            "query": result.query,
            "hits": hits,
        }
