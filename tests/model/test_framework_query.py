from __future__ import annotations

from pathlib import Path

from src.common.framework_query import FrameworkKnowledgeIndex


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_framework_query_index_and_search(tmp_path: Path) -> None:
    _write(
        tmp_path / "framework" / "alpha.md",
        """---
doc-id: alpha
owner: PM
tags: [discovery]
---

# Alpha Doc

## Discovery Scope

This section describes scoped discovery behavior.
""",
    )
    _write(
        tmp_path / "framework" / "beta.md",
        """---
doc-id: beta
owner: SA
---

# Beta Doc

## Runtime Rules

Use query-first retrieval and section-level reads.
""",
    )

    index = FrameworkKnowledgeIndex(tmp_path)

    stats = index.stats()
    assert stats.docs == 2
    assert stats.sections >= 2

    docs = index.list_docs(owner="PM")
    assert len(docs) == 1
    assert docs[0].doc_id == "alpha"

    hits = index.search_docs("query-first retrieval", limit=5)
    assert hits
    assert hits[0].section.doc_id == "beta"


def test_framework_query_graph_neighbors_and_path(tmp_path: Path) -> None:
    _write(
        tmp_path / "framework" / "a.md",
        """---
doc-id: a
---

# A

## One

Ref to b: [@DOC:b#two](framework/b.md#two)
""",
    )
    _write(
        tmp_path / "framework" / "b.md",
        """---
doc-id: b
---

# B

## Two

Ref to c: [@DOC:c#three](framework/c.md#three)
""",
    )
    _write(
        tmp_path / "framework" / "c.md",
        """---
doc-id: c
---

# C

## Three

Terminal node.
""",
    )

    index = FrameworkKnowledgeIndex(tmp_path)
    edges = index.neighbors("a", section="one", direction="out")
    assert len(edges) == 1
    assert edges[0].target_node_id == "b#two"

    path = index.trace_path("a#one", "c#three", max_hops=4)
    assert len(path) == 2
    assert path[0].source_node_id == "a#one"
    assert path[1].target_node_id == "c#three"


def test_framework_query_read_section_modes(tmp_path: Path) -> None:
    _write(
        tmp_path / "framework" / "doc.md",
        """---
doc-id: doc
---

# Title

## Topic

Line A
Line B
Line C
""",
    )
    index = FrameworkKnowledgeIndex(tmp_path)

    summary = index.read_doc("doc", section="topic", mode="summary")
    full = index.read_doc("doc", section="topic", mode="full")

    assert "Section: doc#topic" in summary
    assert "Line A" in summary
    assert "## Topic" in full
    assert "Line C" in full


def test_framework_query_read_by_section_id_and_list_sections(tmp_path: Path) -> None:
    _write(
        tmp_path / "framework" / "doc.md",
        """---
doc-id: doc
---

# Title

## Topic: Scope & Constraints

One line.
""",
    )
    index = FrameworkKnowledgeIndex(tmp_path)

    sections = index.list_sections("doc")
    assert len(sections) >= 2
    assert sections[1].section_id == "topic-scope-constraints"

    summary = index.read_doc("doc", section_id="topic-scope-constraints", mode="summary")
    assert "Section: doc#topic-scope-constraints" in summary


def test_framework_query_unknown_section_suggests_ids(tmp_path: Path) -> None:
    _write(
        tmp_path / "framework" / "doc.md",
        """---
doc-id: doc
---

# Title

## Scope

Body.
""",
    )
    index = FrameworkKnowledgeIndex(tmp_path)

    suggestions = index.suggest_sections("doc", "scop", limit=3)
    assert suggestions
    assert suggestions[0]["section_id"] == "scope"

    try:
        index.read_doc("doc", section="scop", mode="summary")
        assert False, "Expected ValueError for unknown section"
    except ValueError as exc:
        assert "Closest section_ids" in str(exc)