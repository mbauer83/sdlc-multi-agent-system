from __future__ import annotations

from typing import Literal

from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]

from src.tools.model_mcp.context import RepoPreset, RepoScope, repo_cached, resolve_repo_roots, roots_key


def register_query_graph_tools(mcp: FastMCP) -> None:
    @mcp.tool(
        name="model_query_find_connections_for",
        title="Model Query: Find Connections",
        description=(
            "Find connection records that touch a given entity_id. "
            "direction: any|outbound|inbound; optionally filter by conn_lang and conn_type." 
            "\n\nRepo selection: repo_scope defaults to both (engagement + enterprise)."
        ),
        structured_output=True,
    )
    def model_query_find_connections_for(
        entity_id: str,
        *,
        direction: Literal["any", "outbound", "inbound"] = "any",
        conn_lang: str | None = None,
        conn_type: str | None = None,
        repo_root: str | None = None,
        repo_preset: RepoPreset | None = None,
        enterprise_root: str | None = None,
        repo_scope: RepoScope = "both",
        refresh: bool = False,
    ) -> list[dict[str, object]]:
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

        conns = repo.find_connections_for(
            entity_id,
            direction=direction,
            conn_lang=conn_lang,
            conn_type=conn_type,
        )

        out: list[dict[str, object]] = []
        for c in conns:
            d = repo.read_artifact(c.artifact_id, mode="summary")
            if d is not None:
                out.append(d)
        return out

    @mcp.tool(
        name="model_query_find_neighbors",
        title="Model Query: Find Neighbors",
        description=(
            "Graph traversal: return entity_ids reachable from entity_id within max_hops using connections. "
            "Optionally restrict to a connection language (conn_lang)." 
            "\n\nRepo selection: repo_scope defaults to both (engagement + enterprise)."
        ),
        structured_output=True,
    )
    def model_query_find_neighbors(
        entity_id: str,
        *,
        max_hops: int = 1,
        conn_lang: str | None = None,
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

        neighbors = repo.find_neighbors(entity_id, max_hops=max_hops, conn_lang=conn_lang)
        normalized = {k: sorted(list(v)) for k, v in neighbors.items()}
        return {
            "repo_roots": [str(p) for p in roots],
            "repo_scope": repo_scope,
            "entity_id": entity_id,
            "max_hops": max_hops,
            "neighbors": normalized,
        }
