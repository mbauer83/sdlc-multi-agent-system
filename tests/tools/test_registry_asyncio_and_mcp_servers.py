from __future__ import annotations

import asyncio
from pathlib import Path

from src.tools import mcp_framework_server, mcp_model_server, mcp_registry_server
from src.tools.mcp_registry import service as registry_service


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _tool_names(server: object) -> set[str]:
    mcp = getattr(server, "mcp")
    return {tool.name for tool in mcp._tool_manager.list_tools()}


def test_registry_service_is_safe_inside_running_event_loop(tmp_path: Path) -> None:
    _write(
        tmp_path / "agents" / "demo-agent" / "AGENT.md",
        """---
agent-id: demo-agent
name: Demo
system-prompt-identity: Test prompt
---

## 11. Personality & Behavioral Stance

### Runtime Behavioral Stance

Keep responses deterministic.
""",
    )

    async def run_check() -> None:
        await asyncio.sleep(0)
        payload = registry_service.load_agent_identity(
            "demo-agent",
            agents_root=str(tmp_path / "agents"),
            include_full_frontmatter=False,
        )
        assert payload is not None
        assert payload["agent_id"] == "demo-agent"

    # Regression target: this used to fail with nested loop errors when anyio.run
    # was called from inside an active event loop.
    asyncio.run(run_check())


def test_model_registry_framework_mcp_servers_expose_expected_tool_sets() -> None:
    model_tools = _tool_names(mcp_model_server)
    registry_tools = _tool_names(mcp_registry_server)
    framework_tools = _tool_names(mcp_framework_server)

    assert {
        "model_query_stats",
        "model_query_list_artifacts",
        "model_query_search_artifacts",
        "model_query_count_artifacts_by",
        "model_query_read_artifact",
        "model_query_find_neighbors",
    }.issubset(model_tools)

    assert {
        "list_agents",
        "load_agent_identity",
        "list_agent_skills",
        "list_skill_triggers",
        "get_skill_details",
        "check_skill_readiness",
    }.issubset(registry_tools)

    assert {
        "framework_query_stats",
        "framework_query_list_docs",
        "framework_query_list_sections",
        "framework_query_search_docs",
        "framework_query_read_doc",
        "framework_query_resolve_ref",
        "framework_query_related_docs",
        "framework_query_neighbors",
        "framework_query_path",
        "framework_query_path_batch",
        "framework_query_missing_links",
        "framework_query_validate_refs",
    }.issubset(framework_tools)


def test_framework_mcp_tools_behavior_via_registered_functions(tmp_path: Path) -> None:
    _write(
        tmp_path / "framework" / "one.md",
        """---
doc-id: one
owner: PM
---

# One

## Scope

References [@DOC:two#rules](framework/two.md#rules).
""",
    )
    _write(
        tmp_path / "framework" / "two.md",
        """---
doc-id: two
owner: SA
---

# Two

## Rules

Query-first reads only.
""",
    )

    tool_map = mcp_framework_server.mcp._tool_manager._tools

    stats = tool_map["framework_query_stats"].fn(framework_root=str(tmp_path), refresh=True)
    assert stats["docs"] == 2

    docs = tool_map["framework_query_list_docs"].fn(framework_root=str(tmp_path), owner="PM")
    assert len(docs) == 1
    assert docs[0]["doc_id"] == "one"

    hits = tool_map["framework_query_search_docs"].fn("query-first", framework_root=str(tmp_path), limit=5)
    assert hits
    assert hits[0]["doc_id"] == "two"

    sections = tool_map["framework_query_list_sections"].fn("one", framework_root=str(tmp_path))
    assert sections
    assert sections[0]["section_id"] == "one"

    by_section_id = tool_map["framework_query_read_doc"].fn(
        "one",
        framework_root=str(tmp_path),
        section_id="scope",
        mode="summary",
    )
    assert "Section: one#scope" in str(by_section_id["content"])

    missing = tool_map["framework_query_read_doc"].fn(
        "one",
        framework_root=str(tmp_path),
        section="scop",
        mode="summary",
    )
    assert "error" in missing
    assert missing["suggested_sections"]

    neighbors = tool_map["framework_query_neighbors"].fn("one", framework_root=str(tmp_path), section="scope")
    assert len(neighbors) == 1
    assert neighbors[0]["target"] == "two#rules"
