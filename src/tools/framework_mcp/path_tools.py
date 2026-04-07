from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]

from src.common.framework_query import FrameworkKnowledgeIndex, FrameworkReferenceEdge

from .context import framework_index_with_freshness, resolve_framework_root


def _ref_exists(index: FrameworkKnowledgeIndex, ref: str) -> bool:
    if "#" in ref:
        doc_id, section_id = ref.split("#", 1)
        try:
            sections = index.list_sections(doc_id)
        except ValueError:
            return False
        return any(sec.section_id == section_id for sec in sections)
    try:
        sections = index.list_sections(ref)
    except ValueError:
        return False
    return bool(sections)


def _suggest_refs(index: FrameworkKnowledgeIndex, ref: str) -> list[str]:
    if "#" not in ref:
        return []
    doc_id, section_hint = ref.split("#", 1)
    try:
        suggestions = index.suggest_sections(doc_id, section_hint, limit=5)
    except ValueError:
        return []
    resolved = [f"{doc_id}#{item['section_id']}" for item in suggestions]
    if resolved:
        return resolved
    try:
        sections = index.list_sections(doc_id)
    except ValueError:
        return []
    return [f"{doc_id}#{item.section_id}" for item in sections[:5]]


def _path_to_payload(edges: Sequence[FrameworkReferenceEdge]) -> list[dict[str, object]]:
    return [
        {
            "source": edge.source_node_id,
            "target": edge.target_node_id,
            "target_path": edge.target_path,
        }
        for edge in edges
    ]


def _classify_path_error(exc: ValueError) -> str:
    msg = str(exc)
    if "Unknown source ref" in msg:
        return "UNKNOWN_SOURCE_REF"
    if "Unknown target ref" in msg:
        return "UNKNOWN_TARGET_REF"
    return "ERROR"


@dataclass
class _PathStatus:
    reason_code: str
    path: list[dict[str, object]]
    source_exists: bool
    target_exists: bool
    suggested_source_refs: list[str]
    suggested_target_refs: list[str]


def _trace_with_status(
    index: FrameworkKnowledgeIndex,
    *,
    source_ref: str,
    target_ref: str,
    max_hops: int,
    stale_detected: bool,
) -> _PathStatus:
    reason_code = "OK"
    suggestions_source: list[str] = []
    suggestions_target: list[str] = []

    try:
        edges = index.trace_path(source_ref, target_ref, max_hops=max_hops)
        if not edges:
            reason_code = "DISCONNECTED_GRAPH"
    except ValueError as exc:
        reason_code = _classify_path_error(exc)
        edges = []
        if reason_code == "UNKNOWN_SOURCE_REF":
            suggestions_source = _suggest_refs(index, source_ref)
        elif reason_code == "UNKNOWN_TARGET_REF":
            suggestions_target = _suggest_refs(index, target_ref)
        else:
            raise

    if reason_code == "DISCONNECTED_GRAPH" and stale_detected:
        reason_code = "INDEX_STALE_OR_UNREFRESHED"

    return _PathStatus(
        reason_code=reason_code,
        path=_path_to_payload(edges),
        source_exists=_ref_exists(index, source_ref),
        target_exists=_ref_exists(index, target_ref),
        suggested_source_refs=suggestions_source,
        suggested_target_refs=suggestions_target,
    )


def register_path_tools(mcp: FastMCP) -> None:
    @mcp.tool(
        name="framework_query_path",
        title="Framework Query: Path",
        description=(
            "Shortest-path traversal over formal @DOC references between two section refs."
        ),
        structured_output=True,
    )
    def framework_query_path(
        source_ref: str,
        target_ref: str,
        *,
        framework_root: str | None = None,
        max_hops: int = 6,
        refresh: bool = False,
        include_diagnostics: bool = False,
    ) -> list[dict[str, object]] | dict[str, object]:
        root = resolve_framework_root(root=framework_root)
        index, freshness = framework_index_with_freshness(root, force_refresh=refresh)
        status = _trace_with_status(
            index,
            source_ref=source_ref,
            target_ref=target_ref,
            max_hops=max_hops,
            stale_detected=bool(freshness.get("stale_detected", False)),
        )

        if not include_diagnostics:
            return list(status.path)

        return {
            "framework_root": str(root),
            "source_ref": source_ref,
            "target_ref": target_ref,
            "max_hops": max_hops,
            "path": status.path,
            "diagnostics": {
                "source_exists": status.source_exists,
                "target_exists": status.target_exists,
                "reason_code": status.reason_code,
                "suggested_source_refs": status.suggested_source_refs,
                "suggested_target_refs": status.suggested_target_refs,
                "index_age_ms": freshness.get("index_age_ms", 0),
            },
            "freshness": freshness,
        }

    @mcp.tool(
        name="framework_query_path_batch",
        title="Framework Query: Path Batch",
        description=(
            "Run multiple shortest-path traversals over formal @DOC references in one call. "
            "Each item returns path + status diagnostics."
        ),
        structured_output=True,
    )
    def framework_query_path_batch(
        pairs: list[dict[str, str]],
        *,
        framework_root: str | None = None,
        max_hops: int = 6,
        refresh: bool = False,
    ) -> dict[str, object]:
        root = resolve_framework_root(root=framework_root)
        index, freshness = framework_index_with_freshness(root, force_refresh=refresh)
        stale_detected = bool(freshness.get("stale_detected", False))

        results: list[dict[str, object]] = []
        for pair in pairs:
            source_ref = str(pair.get("source_ref", ""))
            target_ref = str(pair.get("target_ref", ""))
            status = _trace_with_status(
                index,
                source_ref=source_ref,
                target_ref=target_ref,
                max_hops=max_hops,
                stale_detected=stale_detected,
            )
            results.append(
                {
                    "source_ref": source_ref,
                    "target_ref": target_ref,
                    "reason_code": status.reason_code,
                    "path": status.path,
                    "suggested_source_refs": status.suggested_source_refs,
                    "suggested_target_refs": status.suggested_target_refs,
                }
            )

        return {
            "framework_root": str(root),
            "max_hops": max_hops,
            "results": results,
            "freshness": freshness,
        }
