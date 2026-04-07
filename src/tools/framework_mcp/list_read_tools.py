from __future__ import annotations

from typing import Literal

from src.common.framework_query import FrameworkKnowledgeIndex
from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]

from .context import framework_index_with_freshness, resolve_framework_root


def register_list_read_tools(mcp: FastMCP) -> None:
    _register_discovery_read_tools(mcp)
    _register_resolve_ref_tool(mcp)


def _register_discovery_read_tools(mcp: FastMCP) -> None:
    @mcp.tool(
        name="framework_query_list_docs",
        title="Framework Query: List Docs",
        description=(
            "List framework/spec documents using metadata filters. "
            "Primary discovery step before search/read."
        ),
        structured_output=True,
    )
    def framework_query_list_docs(
        *,
        framework_root: str | None = None,
        owner: str | None = None,
        tag: str | None = None,
        path_prefix: str | None = None,
        refresh: bool = False,
    ) -> list[dict[str, object]]:
        root = resolve_framework_root(root=framework_root)
        index, _ = framework_index_with_freshness(root, force_refresh=refresh)
        recs = index.list_docs(owner=owner, tag=tag, path_prefix=path_prefix)
        return [
            {
                "doc_id": rec.doc_id,
                "path": str(rec.path),
                "title": rec.title,
                "owner": rec.owner,
                "tags": rec.tags,
                "section_count": rec.section_count,
                "updated_at": rec.updated_at,
            }
            for rec in recs
        ]


def _find_section_match(
    index: FrameworkKnowledgeIndex,
    doc_id_or_path: str,
    section_hint: str,
) -> tuple[str, float, list[dict[str, object]]]:
    sections = index.list_sections(doc_id_or_path)
    doc_id = sections[0].doc_id if sections else str(doc_id_or_path)

    target = next((sec for sec in sections if sec.section_id == section_hint), None)
    if target is None:
        target = next((sec for sec in sections if sec.heading == section_hint), None)
    if target is None:
        lowered = section_hint.strip().lower()
        target = next((sec for sec in sections if sec.heading.lower() == lowered), None)
    if target is not None:
        return f"{target.doc_id}#{target.section_id}", 1.0, []

    suggestions = index.suggest_sections(doc_id_or_path, section_hint, limit=5)
    alternatives: list[dict[str, object]] = [
        {
            "canonical_ref": f"{doc_id}#{item['section_id']}",
            "heading": item["heading"],
            "line_start": item["line_start"],
            "similarity": item["similarity"],
        }
        for item in suggestions
    ]
    if not alternatives:
        return "", 0.0, []

    first = alternatives[0]
    canonical_ref = str(first["canonical_ref"])
    raw_similarity = first.get("similarity", 0.0)
    if isinstance(raw_similarity, (float, int)):
        similarity = float(raw_similarity)
    else:
        similarity = 0.0
    return canonical_ref, similarity, alternatives


def _register_resolve_ref_tool(mcp: FastMCP) -> None:

    @mcp.tool(
        name="framework_query_read_doc",
        title="Framework Query: Read Doc",
        description=(
            "Read framework/spec content by doc id or path with optional section scoping. "
            "Use mode='summary' by default; mode='full' for escalation only."
        ),
        structured_output=True,
    )
    def framework_query_read_doc(
        doc_id_or_path: str,
        *,
        framework_root: str | None = None,
        section: str | None = None,
        section_id: str | None = None,
        mode: str = "summary",
        refresh: bool = False,
    ) -> dict[str, object]:
        root = resolve_framework_root(root=framework_root)
        index, freshness = framework_index_with_freshness(root, force_refresh=refresh)
        normalized_mode: Literal["summary", "full"] = "full" if mode == "full" else "summary"
        try:
            content = index.read_doc(
                doc_id_or_path,
                section=section,
                section_id=section_id,
                mode=normalized_mode,
            )
        except ValueError as exc:
            section_query = section_id or section
            suggestions = (
                index.suggest_sections(doc_id_or_path, section_query, limit=5)
                if section_query is not None
                else []
            )
            return {
                "framework_root": str(root),
                "doc_id_or_path": doc_id_or_path,
                "section": section,
                "section_id": section_id,
                "mode": normalized_mode,
                "error": str(exc),
                "suggested_sections": suggestions,
                "freshness": freshness,
                "content": "",
            }
        return {
            "framework_root": str(root),
            "doc_id_or_path": doc_id_or_path,
            "section": section,
            "section_id": section_id,
            "mode": normalized_mode,
            "freshness": freshness,
            "content": content,
        }

    @mcp.tool(
        name="framework_query_list_sections",
        title="Framework Query: List Sections",
        description=(
            "List all sections for a framework/spec doc, returning stable section ids and line starts."
        ),
        structured_output=True,
    )
    def framework_query_list_sections(
        doc_id_or_path: str,
        *,
        framework_root: str | None = None,
        refresh: bool = False,
    ) -> list[dict[str, object]]:
        root = resolve_framework_root(root=framework_root)
        index, _ = framework_index_with_freshness(root, force_refresh=refresh)
        sections = index.list_sections(doc_id_or_path)
        return [
            {
                "doc_id": sec.doc_id,
                "section_id": sec.section_id,
                "heading": sec.heading,
                "line_start": sec.line_start,
                "line_end": sec.line_end,
                "level": sec.level,
                "path": str(sec.path),
            }
            for sec in sections
        ]

    @mcp.tool(
        name="framework_query_related_docs",
        title="Framework Query: Related Docs",
        description=(
            "Return docs related by formal cross-references (inbound + outbound weighted count)."
        ),
        structured_output=True,
    )
    def framework_query_related_docs(
        doc_id_or_path: str,
        *,
        framework_root: str | None = None,
        limit: int = 5,
        refresh: bool = False,
    ) -> list[dict[str, object]]:
        root = resolve_framework_root(root=framework_root)
        index, _ = framework_index_with_freshness(root, force_refresh=refresh)
        recs = index.related_docs(doc_id_or_path, limit=limit)
        return [
            {
                "doc_id": rec.doc_id,
                "path": str(rec.path),
                "title": rec.title,
                "owner": rec.owner,
                "tags": rec.tags,
                "section_count": rec.section_count,
                "updated_at": rec.updated_at,
            }
            for rec in recs
        ]

    @mcp.tool(
        name="framework_query_resolve_ref",
        title="Framework Query: Resolve Ref",
        description=(
            "Resolve a doc/section reference hint to a canonical section ref (doc#section_id). "
            "Useful before path traversals when section ids are uncertain."
        ),
        structured_output=True,
    )
    def framework_query_resolve_ref(
        doc_id_or_path: str,
        ref_hint: str,
        *,
        framework_root: str | None = None,
        refresh: bool = False,
        limit: int = 5,
    ) -> dict[str, object]:
        root = resolve_framework_root(root=framework_root)
        index, freshness = framework_index_with_freshness(root, force_refresh=refresh)
        section_hint = ref_hint.split("#", 1)[1] if "#" in ref_hint else ref_hint
        canonical_ref, confidence, alternatives = _find_section_match(index, doc_id_or_path, section_hint)

        if alternatives:
            alternatives = alternatives[: max(limit, 0)]

        return {
            "framework_root": str(root),
            "doc_id_or_path": doc_id_or_path,
            "ref_hint": ref_hint,
            "canonical_ref": canonical_ref,
            "confidence": confidence,
            "alternatives": alternatives,
            "freshness": freshness,
        }
