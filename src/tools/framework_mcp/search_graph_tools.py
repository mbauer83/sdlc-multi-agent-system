from __future__ import annotations

from typing import Literal

from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]

from src.tools.framework_mcp.hygiene_tools import register_hygiene_tools
from src.tools.framework_mcp.path_tools import _path_to_payload, register_path_tools
from src.tools.framework_mcp.context import (
    framework_index_with_freshness,
    resolve_framework_root,
)


def register_search_graph_tools(mcp: FastMCP) -> None:
    _register_search_tool(mcp)
    _register_neighbors_tool(mcp)
    register_path_tools(mcp)
    register_hygiene_tools(mcp)


def _register_search_tool(mcp: FastMCP) -> None:
    @mcp.tool(
        name="framework_query_search_docs",
        title="Framework Query: Search Docs",
        description=(
            "Keyword search across indexed framework/spec sections with scored snippets."
        ),
        structured_output=True,
    )
    def framework_query_search_docs(
        query: str,
        *,
        framework_root: str | None = None,
        limit: int = 10,
        doc_id: str | None = None,
        refresh: bool = False,
    ) -> list[dict[str, object]]:
        root = resolve_framework_root(root=framework_root)
        index, _ = framework_index_with_freshness(root, force_refresh=refresh)
        hits = index.search_docs(query, limit=limit, doc_id=doc_id)
        return [
            {
                "score": hit.score,
                "doc_id": hit.section.doc_id,
                "section_id": hit.section.section_id,
                "heading": hit.section.heading,
                "heading_path": hit.section.heading_path,
                "path": str(hit.section.path),
                "line_start": hit.section.line_start,
                "line_end": hit.section.line_end,
                "snippet": hit.snippet,
            }
            for hit in hits
        ]


def _register_neighbors_tool(mcp: FastMCP) -> None:
    @mcp.tool(
        name="framework_query_neighbors",
        title="Framework Query: Neighbors",
        description=(
            "Graph traversal over formal @DOC references for a doc or specific section."
        ),
        structured_output=True,
    )
    def framework_query_neighbors(
        doc_id_or_path: str,
        *,
        framework_root: str | None = None,
        section: str | None = None,
        direction: Literal["out", "in", "both"] = "both",
        refresh: bool = False,
    ) -> list[dict[str, object]]:
        root = resolve_framework_root(root=framework_root)
        index, _ = framework_index_with_freshness(root, force_refresh=refresh)
        edges = index.neighbors(doc_id_or_path, section=section, direction=direction)
        return _path_to_payload(edges)


