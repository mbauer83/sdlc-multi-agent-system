from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]

from .types import FrameworkReferenceEdge, FrameworkSectionRecord

REF_PATTERN = re.compile(r"\[@DOC:([A-Za-z0-9_.-]+)(?:#([A-Za-z0-9_.-]+))?\]\(([^)]+)\)")
WORD_PATTERN = re.compile(r"[A-Za-z0-9]+")
HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    fm_text = text[4:end]
    body = text[end + 5 :]
    parsed = yaml.safe_load(fm_text) or {}
    if not isinstance(parsed, dict):
        return {}, body
    normalized: dict[str, Any] = {str(k): v for k, v in parsed.items()}
    return normalized, body


def doc_id_for(path: Path, frontmatter: dict[str, Any]) -> str:
    if "doc-id" in frontmatter and isinstance(frontmatter["doc-id"], str):
        return frontmatter["doc-id"]
    return path.stem


def coerce_str_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(v) for v in value]
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return []


def slugify(value: str) -> str:
    words = WORD_PATTERN.findall(value.lower())
    return "-".join(words) if words else "section"


def summarize_text(text: str, *, max_len: int = 180) -> str:
    compact = " ".join(text.split())
    if len(compact) <= max_len:
        return compact
    return f"{compact[: max_len - 3]}..."


def parse_sections(doc_id: str, path: Path, body: str) -> list[FrameworkSectionRecord]:
    lines = body.splitlines()
    headers: list[tuple[int, int, str]] = []
    for idx, line in enumerate(lines, start=1):
        match = HEADING_PATTERN.match(line)
        if match is None:
            continue
        level = len(match.group(1))
        heading = match.group(2).strip()
        headers.append((idx, level, heading))

    if not headers:
        return [
            FrameworkSectionRecord(
                doc_id=doc_id,
                section_id="document",
                heading=path.stem,
                heading_path=[path.stem],
                level=1,
                path=path,
                line_start=1,
                line_end=max(len(lines), 1),
                content=body,
                snippet=summarize_text(body),
            )
        ]

    sections: list[FrameworkSectionRecord] = []
    stack: list[str] = []
    for i, (line_start, level, heading) in enumerate(headers):
        while len(stack) >= level:
            stack.pop()
        stack.append(heading)
        line_end = headers[i + 1][0] - 1 if i + 1 < len(headers) else len(lines)
        content = "\n".join(lines[line_start:line_end])
        sections.append(
            FrameworkSectionRecord(
                doc_id=doc_id,
                section_id=slugify(heading),
                heading=heading,
                heading_path=list(stack),
                level=level,
                path=path,
                line_start=line_start,
                line_end=line_end,
                content=content,
                snippet=summarize_text(content),
            )
        )
    return sections


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in WORD_PATTERN.findall(text) if token]


def score_section(section: FrameworkSectionRecord, tokens: list[str]) -> float:
    heading = section.heading.lower()
    content = section.content.lower()
    score = 0.0
    for token in tokens:
        score += (heading.count(token) * 3.0) + (content.count(token) * 1.0)
    return score


def extract_snippet(content: str, tokens: list[str], *, width: int = 220) -> str:
    lowered = content.lower()
    index = -1
    for token in tokens:
        idx = lowered.find(token)
        if idx != -1:
            index = idx
            break
    if index == -1:
        return summarize_text(content, max_len=width)
    start = max(index - 60, 0)
    end = min(index + width, len(content))
    return content[start:end].replace("\n", " ").strip()


def resolve_section(
    sections: list[FrameworkSectionRecord],
    section: str,
) -> FrameworkSectionRecord | None:
    for sec in sections:
        if sec.section_id == section:
            return sec
    lowered = section.strip().lower()
    slug = slugify(lowered)
    for sec in sections:
        if sec.section_id == slug:
            return sec
    for sec in sections:
        if sec.heading.lower() == lowered:
            return sec
    return None


def first_section_id(sections: list[FrameworkSectionRecord]) -> str | None:
    if not sections:
        return None
    return sections[0].section_id


def render_section(section: FrameworkSectionRecord, *, mode: str) -> str:
    if mode == "full":
        return f"## {section.heading}\n\n{section.content}".rstrip()
    summary_lines = section.content.splitlines()[:20]
    summary_body = "\n".join(summary_lines).strip()
    return (
        f"## {section.heading}\n"
        f"Section: {section.doc_id}#{section.section_id}\n"
        f"Lines: {section.line_start}-{section.line_end}\n\n"
        f"{summary_body}"
    ).rstrip()


def build_ref_edge(
    source_section: FrameworkSectionRecord,
    target_doc_id: str,
    target_section_id: str,
    target_path: str,
) -> FrameworkReferenceEdge:
    return FrameworkReferenceEdge(
        source_doc_id=source_section.doc_id,
        source_section_id=source_section.section_id,
        target_doc_id=target_doc_id,
        target_section_id=target_section_id,
        target_path=target_path,
    )
