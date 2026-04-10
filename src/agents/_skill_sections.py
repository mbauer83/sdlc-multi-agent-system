"""
Internal section-parsing helpers for SkillLoader.

Defines SectionSpec, SectionEntry, _SECTION_REGISTRY, and all parsing /
assembly / truncation logic. Not imported by anything outside skill_loader.py.
"""

from __future__ import annotations

import re
import warnings
from dataclasses import dataclass
from typing import Literal


# ---------------------------------------------------------------------------
# Token budget constants
# ---------------------------------------------------------------------------

BUDGETS: dict[str, tuple[int, int]] = {
    "simple":   (700,  840),
    "standard": (1400, 1680),
    "complex":  (2350, 2820),
}


# ---------------------------------------------------------------------------
# SectionSpec registry
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SectionSpec:
    """Describes how SkillLoader handles one H2 section type."""

    key: str                       # normalised lower-case canonical name
    aliases: frozenset[str]        # alternative heading names → same spec
    modes: frozenset[str]          # {"workflow","express"} = both; singleton = gated
    assembly_position: int         # output ordering (lower = earlier)
    truncation_priority: int       # lower = first to drop; -1 = never truncate
    truncation_strategy: str       # "omit" | "compact"


SECTION_REGISTRY: dict[str, SectionSpec] = {
    spec.key: spec
    for spec in [
        SectionSpec("common rationalizations (rejected)", frozenset(),
                    {"workflow", "express"}, 0, 7, "omit"),
        SectionSpec("inputs required", frozenset(),
                    {"workflow", "express"}, 1, 8, "omit"),
        SectionSpec("procedure", frozenset({"steps"}),
                    {"workflow", "express"}, 2, -1, "omit"),
        SectionSpec("feedback loop", frozenset(),
                    {"workflow", "express"}, 3, 6, "compact"),
        SectionSpec("red flags", frozenset(),
                    {"workflow", "express"}, 4, 4, "omit"),
        SectionSpec("algedonic triggers", frozenset(),
                    {"workflow"}, 5, 3, "compact"),
        SectionSpec("verification", frozenset(),
                    {"workflow", "express"}, 6, 5, "omit"),
        SectionSpec("outputs", frozenset(),
                    {"workflow", "express"}, 7, 2, "compact"),
        SectionSpec("end-of-skill memory close", frozenset(),
                    {"workflow"}, 8, 1, "omit"),
    ]
}

# Alias → canonical key reverse map
_ALIAS_MAP: dict[str, str] = {
    alias: spec.key
    for spec in SECTION_REGISTRY.values()
    for alias in spec.aliases
}


# ---------------------------------------------------------------------------
# Section entry
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SectionEntry:
    """A parsed section from a skill file."""

    canonical_key: str          # resolved canonical key (or raw key if unknown)
    heading_text: str           # original heading text (comment stripped)
    instance_mode: str | None   # per-instance mode override from heading comment
    body: str                   # section body
    is_stub: bool               # True when body is a "Injected at Layer 2" stub


# ---------------------------------------------------------------------------
# Regex constants
# ---------------------------------------------------------------------------

_H2_RE = re.compile(r"^## (.+)$", re.MULTILINE)
_MODE_TAG_RE = re.compile(r"\s*<!--\s*(workflow|express)\s*-->\s*$", re.IGNORECASE)
_STUB_RE = re.compile(
    r"^\s*\*[^*]*(?:injected at layer 2|step 0\.\w+ — injected at layer 2)[^*]*\*\s*$",
    re.IGNORECASE | re.MULTILINE,
)


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def parse_sections(markdown: str, skill_id: str = "") -> list[SectionEntry]:
    """
    Split markdown by ## headings and return SectionEntry list.

    Emits WARNING for unknown sections with no mode tag — they will be excluded
    from agent context in all invocation modes.
    """
    parts = _H2_RE.split(markdown)
    entries: list[SectionEntry] = []
    it = iter(parts[1:])  # skip preamble before first heading

    for heading_raw, body in zip(it, it):
        heading_raw = heading_raw.strip()
        tag_match = _MODE_TAG_RE.search(heading_raw)
        instance_mode: str | None = None
        if tag_match:
            instance_mode = tag_match.group(1).lower()
            heading_text = heading_raw[: tag_match.start()].strip()
        else:
            heading_text = heading_raw

        raw_key = heading_text.lower()
        canonical_key = _ALIAS_MAP.get(raw_key, raw_key)
        if canonical_key not in SECTION_REGISTRY:
            canonical_key = raw_key
            if instance_mode is None:
                warnings.warn(
                    f"Skill{f' {skill_id!r}' if skill_id else ''}: "
                    f"'## {heading_text}' not in SectionSpec registry and has no "
                    "mode tag — excluded from agent context. "
                    "Add <!-- workflow --> or <!-- express --> to include it.",
                    UserWarning,
                    stacklevel=3,
                )

        body_stripped = body.rstrip()
        entries.append(SectionEntry(
            canonical_key=canonical_key,
            heading_text=heading_text,
            instance_mode=instance_mode,
            body=body_stripped,
            is_stub=bool(_STUB_RE.search(body_stripped)),
        ))

    return entries


# ---------------------------------------------------------------------------
# Mode filtering, assembly, budget estimation, truncation
# ---------------------------------------------------------------------------

def section_modes(entry: SectionEntry) -> frozenset[str]:
    if entry.instance_mode is not None:
        return frozenset({entry.instance_mode})
    spec = SECTION_REGISTRY.get(entry.canonical_key)
    return spec.modes if spec is not None else frozenset()


def filter_by_mode(
    entries: list[SectionEntry],
    mode: Literal["workflow", "express"],
) -> list[SectionEntry]:
    return [e for e in entries if mode in section_modes(e)]


def _assembly_pos(entry: SectionEntry) -> int:
    spec = SECTION_REGISTRY.get(entry.canonical_key)
    return spec.assembly_position if spec is not None else 999


def assemble(entries: list[SectionEntry]) -> str:
    ordered = sorted(entries, key=_assembly_pos)
    return "\n\n".join(f"## {e.heading_text}\n{e.body}" for e in ordered)


def estimate_tokens(text: str) -> int:
    return len(text) // 4


def budget_tokens(entries: list[SectionEntry]) -> int:
    """Token estimate that treats stub bodies as near-zero cost."""
    total = 0
    for e in entries:
        heading_cost = len(f"## {e.heading_text}") // 4
        if e.is_stub:
            total += heading_cost + 5
        else:
            total += estimate_tokens(f"## {e.heading_text}\n{e.body}")
    return total


def truncate(entries: list[SectionEntry], soft_cap: int) -> list[SectionEntry]:
    """Drop / compact sections in priority order until budget ≤ soft_cap."""
    def _prio(e: SectionEntry) -> int:
        spec = SECTION_REGISTRY.get(e.canonical_key)
        return spec.truncation_priority if spec is not None else 999

    working = list(entries)
    for candidate in sorted(working, key=_prio):
        spec = SECTION_REGISTRY.get(candidate.canonical_key)
        if spec is None or spec.truncation_priority == -1:
            continue
        idx = next(
            (i for i, e in enumerate(working)
             if e.canonical_key == candidate.canonical_key),
            None,
        )
        if idx is None:
            continue
        working[idx] = _compact(working[idx], spec.truncation_strategy)
        if budget_tokens(working) <= soft_cap:
            break
    return working


def _compact(entry: SectionEntry, strategy: str) -> SectionEntry:
    if strategy == "omit":
        return SectionEntry(entry.canonical_key, entry.heading_text,
                            entry.instance_mode, "", True)
    key, body = entry.canonical_key, entry.body
    if key == "algedonic triggers":
        ids = re.findall(r"ALG-\d+", body)
        new_body = f"Triggers: {', '.join(sorted(set(ids)))}" if ids else "See algedonic-protocol.md"
    elif key == "feedback loop":
        m = re.search(r"(?i)(max\s+iterations?[^\n]*|escalation[^\n]*)", body)
        new_body = m.group(0) if m else "See skill file for feedback loop."
    elif key == "outputs":
        paths = re.findall(r"`[^`]+`", body)
        new_body = " ".join(paths) if paths else "See skill file for output paths."
    else:
        return SectionEntry(entry.canonical_key, entry.heading_text,
                            entry.instance_mode, "", True)
    return SectionEntry(entry.canonical_key, entry.heading_text,
                        entry.instance_mode, new_body, False)
