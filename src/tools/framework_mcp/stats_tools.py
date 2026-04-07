from __future__ import annotations

from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]

from .context import framework_index_with_freshness, resolve_framework_root


def register_stats_tools(mcp: FastMCP) -> None:
    @mcp.tool(
        name="framework_query_stats",
        title="Framework Query: Stats",
        description=(
            "Return index stats for framework/spec knowledge: doc, section, and reference counts. "
            "Use first to verify root selection and index freshness."
        ),
        structured_output=True,
    )
    def framework_query_stats(
        *,
        framework_root: str | None = None,
        refresh: bool = False,
    ) -> dict[str, object]:
        root = resolve_framework_root(root=framework_root)
        index, freshness = framework_index_with_freshness(root, force_refresh=refresh)
        stats = index.stats()
        return {
            "framework_root": str(root),
            "docs": stats.docs,
            "sections": stats.sections,
            "references": stats.references,
            "freshness": freshness,
        }
