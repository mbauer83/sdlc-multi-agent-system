from __future__ import annotations

import time
from pathlib import Path

from src.tools import mcp_framework_server


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_framework_auto_refresh_without_manual_refresh(tmp_path: Path) -> None:
    _write(
        tmp_path / "framework" / "alpha.md",
        """---
doc-id: alpha
---

# Alpha

## Scope

Initial text only.
""",
    )

    tool_map = mcp_framework_server.mcp._tool_manager._tools

    hits_before = tool_map["framework_query_search_docs"].fn(
        "auto-refresh-token",
        framework_root=str(tmp_path),
    )
    assert hits_before == []

    time.sleep(0.02)
    _write(
        tmp_path / "framework" / "alpha.md",
        """---
doc-id: alpha
---

# Alpha

## Scope

auto-refresh-token now present.
""",
    )

    hits_after = tool_map["framework_query_search_docs"].fn(
        "auto-refresh-token",
        framework_root=str(tmp_path),
    )
    assert hits_after
    assert hits_after[0]["doc_id"] == "alpha"


def test_framework_read_doc_exposes_freshness_metadata(tmp_path: Path) -> None:
    _write(
        tmp_path / "framework" / "doc.md",
        """---
doc-id: doc
---

# Doc

## Topic

Body.
""",
    )

    tool_map = mcp_framework_server.mcp._tool_manager._tools
    payload = tool_map["framework_query_read_doc"].fn(
        "doc",
        framework_root=str(tmp_path),
        section_id="topic",
        mode="summary",
    )

    freshness = payload["freshness"]
    assert "index_version" in freshness
    assert "last_refresh_at" in freshness
    assert "index_age_ms" in freshness
    assert "stale_detected" in freshness
    assert "auto_refreshed" in freshness


def test_framework_resolve_ref_path_diagnostics_and_batch(tmp_path: Path) -> None:
    _write(
        tmp_path / "framework" / "a.md",
        """---
doc-id: a
---

# A

## One

Ref [@DOC:b#two](framework/b.md#two).
""",
    )
    _write(
        tmp_path / "framework" / "b.md",
        """---
doc-id: b
---

# B

## Two

Ref [@DOC:c#three](framework/c.md#three).
""",
    )
    _write(
        tmp_path / "framework" / "c.md",
        """---
doc-id: c
---

# C

## Three

Terminal.
""",
    )

    tool_map = mcp_framework_server.mcp._tool_manager._tools

    resolved = tool_map["framework_query_resolve_ref"].fn(
        "a",
        "on",
        framework_root=str(tmp_path),
    )
    assert resolved["canonical_ref"] == "a#one"
    assert resolved["confidence"] > 0

    diag_ok = tool_map["framework_query_path"].fn(
        "a#one",
        "c#three",
        framework_root=str(tmp_path),
        include_diagnostics=True,
    )
    assert len(diag_ok["path"]) == 2
    assert diag_ok["diagnostics"]["reason_code"] == "OK"

    diag_missing = tool_map["framework_query_path"].fn(
        "a#one",
        "c#unknown",
        framework_root=str(tmp_path),
        include_diagnostics=True,
    )
    assert diag_missing["path"] == []
    assert diag_missing["diagnostics"]["reason_code"] == "UNKNOWN_TARGET_REF"
    assert diag_missing["diagnostics"]["suggested_target_refs"]

    batch = tool_map["framework_query_path_batch"].fn(
        [
            {"source_ref": "a#one", "target_ref": "c#three"},
            {"source_ref": "a#one", "target_ref": "c#unknown"},
        ],
        framework_root=str(tmp_path),
    )
    assert len(batch["results"]) == 2
    assert batch["results"][0]["reason_code"] == "OK"
    assert batch["results"][1]["reason_code"] == "UNKNOWN_TARGET_REF"


def test_framework_missing_links_and_validate_refs(tmp_path: Path) -> None:
    _write(
        tmp_path / "framework" / "links.md",
        """---
doc-id: links
---

# Links

## Lonely

No refs.

## Broken

Bad ref [@DOC:missing#none](framework/missing.md#none).
""",
    )

    tool_map = mcp_framework_server.mcp._tool_manager._tools

    missing_links = tool_map["framework_query_missing_links"].fn(
        "links",
        framework_root=str(tmp_path),
        max_degree=0,
    )
    section_ids = {item["section_id"] for item in missing_links["sections"]}
    assert "lonely" in section_ids

    validation = tool_map["framework_query_validate_refs"].fn(
        framework_root=str(tmp_path),
        doc_id_or_path="links",
    )
    assert validation["issue_count"] >= 1
    issues = {item["issue"] for item in validation["issues"]}
    assert "UNKNOWN_TARGET_DOC" in issues
