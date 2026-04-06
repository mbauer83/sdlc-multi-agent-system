from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Any

import frontmatter  # type: ignore[import-not-found]


SECTION_RE = re.compile(r"^##\s+(?P<title>[^\n]+?)\s*$", re.MULTILINE)
H3_SECTION_RE = re.compile(r"^###\s+(?P<title>[^\n]+?)\s*$", re.MULTILINE)

SKILL_RUNTIME_SECTION_ORDER: tuple[str, ...] = (
    "Inputs Required",
    "Procedure",
    "Algedonic Triggers",
    "Feedback Loop",
    "Outputs",
)


@dataclass(frozen=True)
class ParsedMarkdown:
    frontmatter: dict[str, Any]
    content: str


def normalize_newlines(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = "\n".join(line.rstrip() for line in text.split("\n"))
    return text.strip("\n") + "\n"


def parse_frontmatter(markdown: str) -> ParsedMarkdown:
    post = frontmatter.loads(markdown)
    meta: dict[str, Any] = dict(post.metadata or {})
    meta_sorted = {key: meta[key] for key in sorted(meta.keys())}
    content = normalize_newlines(post.content or "")
    return ParsedMarkdown(frontmatter=meta_sorted, content=content)


def extract_h2_section(markdown: str, *, title: str) -> str | None:
    markdown = normalize_newlines(markdown)
    matches = list(SECTION_RE.finditer(markdown))
    for index, match in enumerate(matches):
        if match.group("title").strip().lower() != title.strip().lower():
            continue
        body_start = match.end()
        body_end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        return markdown[body_start:body_end].strip("\n") + "\n"
    return None


def extract_h3_subsection(markdown: str, *, h2_title: str, h3_title: str) -> str | None:
    h2_body = extract_h2_section(markdown, title=h2_title)
    if h2_body is None:
        return None

    body_text = normalize_newlines(h2_body)
    matches = list(H3_SECTION_RE.finditer(body_text))
    for index, match in enumerate(matches):
        if match.group("title").strip().lower() != h3_title.strip().lower():
            continue
        body_start = match.end()
        body_end = matches[index + 1].start() if index + 1 < len(matches) else len(body_text)
        return body_text[body_start:body_end].strip("\n") + "\n"
    return None


def extract_skill_runtime_sections(markdown: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    for title in SKILL_RUNTIME_SECTION_ORDER:
        body = extract_h2_section(markdown, title=title)
        if body is None and title == "Procedure":
            body = extract_h2_section(markdown, title="Steps")
        if body is not None:
            sections[title] = normalize_newlines(body)
    return sections


def parse_inputs_required_table(markdown: str) -> tuple[list[str], list[dict[str, str]]]:
    section = extract_h2_section(markdown, title="Inputs Required")
    if section is None:
        return ([], [])

    lines = [line for line in normalize_newlines(section).split("\n") if line.strip()]
    header_index = next((i for i, line in enumerate(lines) if line.strip().startswith("|") and line.count("|") >= 2), None)
    if header_index is None or header_index + 1 >= len(lines):
        return ([], [])
    if "---" not in lines[header_index + 1]:
        return ([], [])

    headers = _split_markdown_row(lines[header_index])
    rows: list[dict[str, str]] = []
    required_keys: list[str] = []

    for line in lines[header_index + 2 :]:
        if not line.strip().startswith("|"):
            break
        cells = _split_markdown_row(line)
        if len(cells) < 1:
            continue
        cells = _pad_cells(cells, expected_count=len(headers))
        row_dict = {headers[i]: cells[i] for i in range(len(headers))}
        rows.append(row_dict)

        key = _normalize_key_cell(cells[0])
        if not key:
            continue

        if _row_is_optional(cells):
            continue
        required_keys.append(key)

    return (_dedupe_preserving_order(required_keys), rows)


def _split_markdown_row(row: str) -> list[str]:
    row = row.strip().strip("|")
    return [cell.strip() for cell in row.split("|")]


def _pad_cells(cells: list[str], *, expected_count: int) -> list[str]:
    if len(cells) < expected_count:
        return cells + [""] * (expected_count - len(cells))
    return cells


def _normalize_key_cell(value: str) -> str:
    key = re.sub(r"^`(.+?)`$", r"\1", value.strip())
    return re.sub(r"\*\*(.+?)\*\*", r"\1", key).strip()


def _row_is_optional(cells: list[str]) -> bool:
    return "optional" in " ".join(cells).lower()


def _dedupe_preserving_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        out.append(value)
    return out


def filter_frontmatter(meta: dict[str, Any], keys: tuple[str, ...]) -> dict[str, Any]:
    return {key: meta[key] for key in keys if key in meta}


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
