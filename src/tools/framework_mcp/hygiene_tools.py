from __future__ import annotations

import re

from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]

from src.common.framework_query import FrameworkKnowledgeIndex
from src.common.framework_query.parsing import REF_PATTERN

from .context import framework_index_with_freshness, resolve_framework_root


def _issues_for_match(
    index: FrameworkKnowledgeIndex,
    source_node_id: str,
    match: re.Match[str],
) -> list[dict[str, object]]:
    target_doc_id = match.group(1)
    target_section_id = match.group(2)
    target_path = match.group(3)

    try:
        target_sections = index.list_sections(target_doc_id)
    except ValueError:
        return [
            {
                "source": source_node_id,
                "target_doc_id": target_doc_id,
                "target_section_id": target_section_id or "",
                "target_path": target_path,
                "issue": "UNKNOWN_TARGET_DOC",
            }
        ]

    if not target_section_id:
        return []
    exists = any(item.section_id == target_section_id for item in target_sections)
    if exists:
        return []

    suggestions = index.suggest_sections(
        target_doc_id,
        target_section_id,
        limit=5,
    )
    return [
        {
            "source": source_node_id,
            "target_doc_id": target_doc_id,
            "target_section_id": target_section_id,
            "target_path": target_path,
            "issue": "UNKNOWN_TARGET_SECTION",
            "suggested_section_ids": [str(item["section_id"]) for item in suggestions],
        }
    ]


def _collect_ref_issues(
    index: FrameworkKnowledgeIndex,
    docs: list[str],
) -> tuple[int, list[dict[str, object]]]:
    issues: list[dict[str, object]] = []
    checked = 0
    for doc in docs:
        sections = index.list_sections(doc)
        for sec in sections:
            checked += 1
            for match in REF_PATTERN.finditer(sec.content):
                issues.extend(_issues_for_match(index, sec.node_id, match))
    return checked, issues


def register_hygiene_tools(mcp: FastMCP) -> None:
    @mcp.tool(
        name="framework_query_missing_links",
        title="Framework Query: Missing Links",
        description=(
            "Find sections in a framework/spec doc with low formal @DOC connectivity (no inbound/outbound references)."
        ),
        structured_output=True,
    )
    def framework_query_missing_links(
        doc_id_or_path: str,
        *,
        framework_root: str | None = None,
        max_degree: int = 0,
        refresh: bool = False,
    ) -> dict[str, object]:
        root = resolve_framework_root(root=framework_root)
        index, freshness = framework_index_with_freshness(root, force_refresh=refresh)
        sections = index.list_sections(doc_id_or_path)
        out: list[dict[str, object]] = []
        for sec in sections:
            outbound = index.neighbors(sec.doc_id, section=sec.section_id, direction="out")
            inbound = index.neighbors(sec.doc_id, section=sec.section_id, direction="in")
            degree = len(outbound) + len(inbound)
            if degree > max_degree:
                continue
            out.append(
                {
                    "doc_id": sec.doc_id,
                    "section_id": sec.section_id,
                    "heading": sec.heading,
                    "line_start": sec.line_start,
                    "inbound": len(inbound),
                    "outbound": len(outbound),
                    "degree": degree,
                }
            )
        return {
            "framework_root": str(root),
            "doc_id_or_path": doc_id_or_path,
            "max_degree": max_degree,
            "sections": out,
            "freshness": freshness,
        }

    @mcp.tool(
        name="framework_query_validate_refs",
        title="Framework Query: Validate Refs",
        description=(
            "Validate formal @DOC references and report unresolved doc/section targets. "
            "Can be scoped to one doc or run across the full framework/spec index."
        ),
        structured_output=True,
    )
    def framework_query_validate_refs(
        *,
        framework_root: str | None = None,
        doc_id_or_path: str | None = None,
        refresh: bool = False,
    ) -> dict[str, object]:
        root = resolve_framework_root(root=framework_root)
        index, freshness = framework_index_with_freshness(root, force_refresh=refresh)
        docs = [doc_id_or_path] if doc_id_or_path else [item.doc_id for item in index.list_docs()]
        normalized_docs = [doc for doc in docs if doc is not None]
        checked, issues = _collect_ref_issues(index, normalized_docs)

        return {
            "framework_root": str(root),
            "doc_id_or_path": doc_id_or_path,
            "checked_sections": checked,
            "issue_count": len(issues),
            "issues": issues,
            "freshness": freshness,
        }
