from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Literal

from .parsing import (
    REF_PATTERN,
    build_ref_edge,
    coerce_str_list,
    doc_id_for,
    extract_snippet,
    first_section_id,
    parse_sections,
    render_section,
    resolve_section,
    score_section,
    split_frontmatter,
    tokenize,
)
from .types import (
    FrameworkDocRecord,
    FrameworkIndexStats,
    FrameworkReferenceEdge,
    FrameworkSearchHit,
    FrameworkSectionRecord,
    ReferenceDirection,
)


@dataclass
class _DocData:
    record: FrameworkDocRecord
    frontmatter: dict[str, Any]
    body: str


@dataclass
class FrameworkKnowledgeIndex:
    root: Path
    _docs: dict[str, _DocData] = field(default_factory=dict)
    _sections: dict[str, FrameworkSectionRecord] = field(default_factory=dict)
    _doc_sections: dict[str, list[FrameworkSectionRecord]] = field(default_factory=dict)
    _edges: list[FrameworkReferenceEdge] = field(default_factory=list)
    _outbound: dict[str, list[FrameworkReferenceEdge]] = field(default_factory=dict)
    _inbound: dict[str, list[FrameworkReferenceEdge]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.refresh()

    def refresh(self) -> None:
        self._docs.clear()
        self._sections.clear()
        self._doc_sections.clear()
        self._edges.clear()
        self._outbound.clear()
        self._inbound.clear()

        for path in self._iter_doc_paths():
            text = path.read_text(encoding="utf-8")
            frontmatter, body = split_frontmatter(text)
            doc_id = doc_id_for(path, frontmatter)
            sections = parse_sections(doc_id=doc_id, path=path, body=body)
            title = sections[0].heading if sections else path.stem
            owner = str(frontmatter.get("owner", ""))
            tags = coerce_str_list(frontmatter.get("tags"))
            updated_at = str(frontmatter.get("last-updated", ""))

            self._docs[doc_id] = _DocData(
                record=FrameworkDocRecord(
                    doc_id=doc_id,
                    path=path,
                    title=title,
                    owner=owner,
                    tags=tags,
                    section_count=len(sections),
                    updated_at=updated_at,
                ),
                frontmatter=frontmatter,
                body=body,
            )
            self._doc_sections[doc_id] = sections
            for section in sections:
                self._sections[section.node_id] = section

        self._build_reference_graph()

    def stats(self) -> FrameworkIndexStats:
        return FrameworkIndexStats(
            docs=len(self._docs),
            sections=len(self._sections),
            references=len(self._edges),
        )

    def list_docs(
        self,
        *,
        owner: str | None = None,
        tag: str | None = None,
        path_prefix: str | None = None,
    ) -> list[FrameworkDocRecord]:
        records = [doc.record for doc in self._docs.values()]
        out = [
            rec
            for rec in records
            if (owner is None or rec.owner == owner)
            and (tag is None or tag in rec.tags)
            and (path_prefix is None or str(rec.path.relative_to(self.root)).startswith(path_prefix))
        ]
        return sorted(out, key=lambda x: (str(x.path), x.doc_id))

    def search_docs(
        self,
        query: str,
        *,
        limit: int = 10,
        doc_id: str | None = None,
    ) -> list[FrameworkSearchHit]:
        tokens = tokenize(query)
        if not tokens:
            return []
        hits: list[FrameworkSearchHit] = []
        for section in self._sections.values():
            if doc_id is not None and section.doc_id != doc_id:
                continue
            score = score_section(section, tokens)
            if score <= 0:
                continue
            hits.append(
                FrameworkSearchHit(
                    score=score,
                    section=section,
                    snippet=extract_snippet(section.content, tokens),
                )
            )
        hits.sort(key=lambda x: (x.score, -x.section.level, x.section.node_id), reverse=True)
        return hits[: max(limit, 0)]

    def read_doc(
        self,
        doc_id_or_path: str,
        *,
        section: str | None = None,
        section_id: str | None = None,
        mode: Literal["summary", "full"] = "summary",
    ) -> str:
        doc = self._resolve_doc(doc_id_or_path)
        if doc is None:
            raise ValueError(f"Unknown framework doc: {doc_id_or_path}")
        sections = self._doc_sections.get(doc.record.doc_id, [])
        selected_section = section_id or section
        if selected_section is not None:
            sec = resolve_section(sections, selected_section)
            if sec is None:
                suggestions = self.suggest_sections(doc.record.doc_id, selected_section, limit=5)
                hints = ", ".join(str(s["section_id"]) for s in suggestions)
                if hints:
                    raise ValueError(
                        f"Unknown section '{selected_section}' in doc '{doc.record.doc_id}'. "
                        f"Closest section_ids: {hints}"
                    )
                raise ValueError(f"Unknown section '{selected_section}' in doc '{doc.record.doc_id}'")
            return render_section(sec, mode=mode)
        if mode == "full":
            return doc.body
        heading_lines = [f"- {sec.heading} ({sec.section_id})" for sec in sections[:12]]
        front = "\n".join(f"{k}: {v}" for k, v in doc.frontmatter.items())
        return (
            f"Document: {doc.record.doc_id}\n"
            f"Path: {doc.record.path.relative_to(self.root)}\n"
            f"Title: {doc.record.title}\n"
            f"Sections: {doc.record.section_count}\n\n"
            f"Frontmatter:\n{front or '(none)'}\n\n"
            f"Top Sections:\n" + ("\n".join(heading_lines) if heading_lines else "(none)")
        )

    def list_sections(self, doc_id_or_path: str) -> list[FrameworkSectionRecord]:
        doc = self._resolve_doc(doc_id_or_path)
        if doc is None:
            raise ValueError(f"Unknown framework doc: {doc_id_or_path}")
        sections = self._doc_sections.get(doc.record.doc_id, [])
        return sorted(sections, key=lambda s: (s.line_start, s.section_id))

    def suggest_sections(
        self,
        doc_id_or_path: str,
        query: str,
        *,
        limit: int = 5,
    ) -> list[dict[str, object]]:
        doc = self._resolve_doc(doc_id_or_path)
        if doc is None:
            return []
        query_lc = query.strip().lower()
        scored: list[tuple[float, FrameworkSectionRecord]] = []
        for section in self._doc_sections.get(doc.record.doc_id, []):
            score_id = SequenceMatcher(None, query_lc, section.section_id.lower()).ratio()
            score_heading = SequenceMatcher(None, query_lc, section.heading.lower()).ratio()
            score = max(score_id, score_heading)
            if score <= 0:
                continue
            scored.append((score, section))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [
            {
                "section_id": sec.section_id,
                "heading": sec.heading,
                "line_start": sec.line_start,
                "similarity": round(score, 3),
            }
            for score, sec in scored[: max(limit, 0)]
        ]

    def related_docs(self, doc_id_or_path: str, *, limit: int = 5) -> list[FrameworkDocRecord]:
        doc = self._resolve_doc(doc_id_or_path)
        if doc is None:
            raise ValueError(f"Unknown framework doc: {doc_id_or_path}")
        target_id = doc.record.doc_id
        counts: dict[str, int] = {}
        for edge in self._edges:
            if edge.source_doc_id == target_id and edge.target_doc_id != target_id:
                counts[edge.target_doc_id] = counts.get(edge.target_doc_id, 0) + 1
            if edge.target_doc_id == target_id and edge.source_doc_id != target_id:
                counts[edge.source_doc_id] = counts.get(edge.source_doc_id, 0) + 1

        ranked = sorted(counts.items(), key=lambda x: (x[1], x[0]), reverse=True)
        out: list[FrameworkDocRecord] = []
        for related_doc_id, _ in ranked[: max(limit, 0)]:
            rec = self._docs.get(related_doc_id)
            if rec is not None:
                out.append(rec.record)
        return out

    def neighbors(
        self,
        doc_id_or_path: str,
        *,
        section: str | None = None,
        direction: ReferenceDirection = "both",
    ) -> list[FrameworkReferenceEdge]:
        doc = self._resolve_doc(doc_id_or_path)
        if doc is None:
            raise ValueError(f"Unknown framework doc: {doc_id_or_path}")
        nodes = self._nodes_for(doc.record.doc_id, section)
        edges: list[FrameworkReferenceEdge] = []
        for node in nodes:
            if direction in ("out", "both"):
                edges.extend(self._outbound.get(node, []))
            if direction in ("in", "both"):
                edges.extend(self._inbound.get(node, []))
        unique: dict[tuple[str, str], FrameworkReferenceEdge] = {}
        for edge in edges:
            unique[(edge.source_node_id, edge.target_node_id)] = edge
        return sorted(unique.values(), key=lambda x: (x.source_node_id, x.target_node_id))

    def trace_path(self, source_ref: str, target_ref: str, *, max_hops: int = 6) -> list[FrameworkReferenceEdge]:
        source_node = self._resolve_node_ref(source_ref)
        target_node = self._resolve_node_ref(target_ref)
        if source_node is None:
            raise ValueError(f"Unknown source ref: {source_ref}")
        if target_node is None:
            raise ValueError(f"Unknown target ref: {target_ref}")
        if source_node == target_node:
            return []

        queue: deque[str] = deque([source_node])
        visited: set[str] = {source_node}
        parent: dict[str, FrameworkReferenceEdge] = {}
        depth: dict[str, int] = {source_node: 0}

        while queue:
            node = queue.popleft()
            if depth[node] >= max_hops:
                continue
            for edge in self._outbound.get(node, []):
                nxt = edge.target_node_id
                if nxt in visited:
                    continue
                visited.add(nxt)
                parent[nxt] = edge
                depth[nxt] = depth[node] + 1
                if nxt == target_node:
                    return _reconstruct_path(parent, source_node=source_node, target_node=target_node)
                queue.append(nxt)
        return []

    def _iter_doc_paths(self) -> list[Path]:
        paths: list[Path] = []
        framework_root = self.root / "framework"
        if framework_root.exists():
            paths.extend(sorted(framework_root.rglob("*.md")))
        for path in [
            self.root / "specs" / "IMPLEMENTATION_PLAN.md",
            self.root / "README.md",
            self.root / "CLAUDE.md",
        ]:
            if path.exists():
                paths.append(path)
        unique: dict[str, Path] = {str(path.resolve()): path for path in paths}
        return sorted(unique.values(), key=lambda p: str(p))

    def _build_reference_graph(self) -> None:
        self._edges = []
        self._outbound = {}
        self._inbound = {}
        for section in self._sections.values():
            for match in REF_PATTERN.finditer(section.content):
                target_doc_id = match.group(1)
                target_section_id = match.group(2) or ""
                target_path = match.group(3)
                if not target_section_id:
                    target_section_id = first_section_id(self._doc_sections.get(target_doc_id, [])) or ""
                if not target_section_id:
                    continue
                edge = build_ref_edge(section, target_doc_id, target_section_id, target_path)
                self._edges.append(edge)
                self._outbound.setdefault(edge.source_node_id, []).append(edge)
                self._inbound.setdefault(edge.target_node_id, []).append(edge)

    def _resolve_doc(self, doc_id_or_path: str) -> _DocData | None:
        by_id = self._docs.get(doc_id_or_path)
        if by_id is not None:
            return by_id
        raw = Path(doc_id_or_path)
        candidate = (self.root / raw).resolve() if not raw.is_absolute() else raw.resolve()
        for doc in self._docs.values():
            if doc.record.path.resolve() == candidate:
                return doc
        return None

    def _nodes_for(self, doc_id: str, section: str | None) -> list[str]:
        sections = self._doc_sections.get(doc_id, [])
        if section is None:
            return [sec.node_id for sec in sections]
        sec = resolve_section(sections, section)
        if sec is None:
            raise ValueError(f"Unknown section '{section}' in doc '{doc_id}'")
        return [sec.node_id]

    def _resolve_node_ref(self, ref: str) -> str | None:
        if "#" in ref:
            doc_id, section_id = ref.split("#", 1)
            node = f"{doc_id}#{section_id}"
            return node if node in self._sections else None
        doc = self._resolve_doc(ref)
        if doc is None:
            return None
        first = first_section_id(self._doc_sections.get(doc.record.doc_id, []))
        if first is None:
            return None
        node = f"{doc.record.doc_id}#{first}"
        return node if node in self._sections else None


def _reconstruct_path(
    parent: dict[str, FrameworkReferenceEdge],
    *,
    source_node: str,
    target_node: str,
) -> list[FrameworkReferenceEdge]:
    edges: list[FrameworkReferenceEdge] = []
    current = target_node
    while current != source_node:
        edge = parent.get(current)
        if edge is None:
            return []
        edges.append(edge)
        current = edge.source_node_id
    edges.reverse()
    return edges
