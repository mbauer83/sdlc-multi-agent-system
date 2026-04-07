from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from typing import Literal

ReferenceDirection = Literal["out", "in", "both"]


@dataclass(frozen=True)
class FrameworkDocRecord:
    doc_id: str
    path: Path
    title: str
    owner: str
    tags: list[str]
    section_count: int
    updated_at: str


@dataclass(frozen=True)
class FrameworkSectionRecord:
    doc_id: str
    section_id: str
    heading: str
    heading_path: list[str]
    level: int
    path: Path
    line_start: int
    line_end: int
    content: str
    snippet: str

    @property
    def node_id(self) -> str:
        return f"{self.doc_id}#{self.section_id}"


@dataclass(frozen=True)
class FrameworkSearchHit:
    score: float
    section: FrameworkSectionRecord
    snippet: str


@dataclass(frozen=True)
class FrameworkReferenceEdge:
    source_doc_id: str
    source_section_id: str
    target_doc_id: str
    target_section_id: str
    target_path: str

    @property
    def source_node_id(self) -> str:
        return f"{self.source_doc_id}#{self.source_section_id}"

    @property
    def target_node_id(self) -> str:
        return f"{self.target_doc_id}#{self.target_section_id}"


@dataclass(frozen=True)
class FrameworkIndexStats:
    docs: int
    sections: int
    references: int
