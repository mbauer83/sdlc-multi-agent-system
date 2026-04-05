from __future__ import annotations

from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]

from src.tools.model_mcp.context import RepoPreset, RepoScope, repo_cached, resolve_repo_roots, roots_key


def register_query_stats_tools(mcp: FastMCP) -> None:
    @mcp.tool(
        name="model_query_stats",
        title="Model Query: Stats",
        description=(
            "Return index stats for a repository: entity/connection/diagram counts and breakdowns. "
            "Use this first to confirm the server is pointed at the expected repo." 
            "\n\nRepo selection: repo_scope defaults to both (engagement + enterprise)."
        ),
        structured_output=True,
    )
    def model_query_stats(
        *,
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
        stats = repo.stats()
        stats["repo_roots"] = [str(p) for p in roots]
        stats["repo_scope"] = repo_scope
        return stats
