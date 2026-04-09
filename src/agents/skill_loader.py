"""
SkillLoader: parses a skill markdown file and extracts the runtime prompt.

Governed by framework/agent-runtime-spec.md §4 (Layer 3 injection).

Included sections (in order):
  - Inputs Required
  - Steps  (alias: Procedure — skill files use ## Procedure)
  - Algedonic Triggers
  - Feedback Loop
  - Outputs
  - End-of-Skill Memory Close  (added in Stage 4.9j retroactive update)

Excluded sections:
  - Knowledge Adequacy Check  (authoring guidance, not runtime content)
  - Runtime Tooling Hint      (authoring guidance)

Complexity-class token budgets (soft / hard):
  simple:   600 / 720
  standard: 1200 / 1440
  complex:  2000 / 2400

Steps are never truncated. Truncation priority when soft cap is exceeded:
  1. Algedonic Triggers → compact ALG-IDs only
  2. Feedback Loop → termination conditions + iteration count only
  3. Outputs → artifact paths only
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import frontmatter  # python-frontmatter


# ---------------------------------------------------------------------------
# Token budget constants
# ---------------------------------------------------------------------------

_BUDGETS: dict[str, tuple[int, int]] = {
    "simple":   (600,  720),
    "standard": (1200, 1440),
    "complex":  (2000, 2400),
}

_INCLUDED_H2 = frozenset({
    "inputs required",
    "procedure",
    "steps",
    "algedonic triggers",
    "feedback loop",
    "outputs",
    "end-of-skill memory close",
})


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

class SkillNotFoundError(FileNotFoundError):
    """Raised when the skill file cannot be located."""


class SkillBudgetExceededError(ValueError):
    """
    Raised when the extracted skill content exceeds the hard token cap.
    Indicates the skill file needs splitting, not compressing.
    """


# ---------------------------------------------------------------------------
# Data container
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SkillSpec:
    skill_id: str
    agent: str
    complexity_class: str
    trigger_phases: list[str]
    primary_outputs: list[str]
    content: str           # extracted runtime sections (within budget)
    token_estimate: int    # approximate token count of content


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------

class SkillLoader:
    """
    Loads skill files from the agents/ directory tree.

    agents_root: path to the root agents/ directory.
    """

    def __init__(self, agents_root: Path) -> None:
        self._root = agents_root
        # Pre-build index: skill-id → path
        self._index: dict[str, Path] = {}
        self._build_index()

    def _build_index(self) -> None:
        for path in self._root.glob("*/skills/*.md"):
            try:
                post = frontmatter.load(str(path))
                if sid := post.get("skill-id"):
                    self._index[str(sid)] = path
            except Exception:
                pass  # malformed frontmatter — skip

    def load(self, skill_id: str) -> SkillSpec:
        """Load and return a SkillSpec for the given skill-id."""
        path = self._resolve_path(skill_id)
        post = frontmatter.load(str(path))
        complexity = str(post.get("complexity-class", "standard"))
        soft_cap, hard_cap = _BUDGETS.get(complexity, _BUDGETS["standard"])

        sections = _extract_included_sections(post.content)
        content = _assemble(sections)
        tokens = _estimate_tokens(content)

        if tokens > hard_cap:
            import warnings
            warnings.warn(
                f"Skill '{skill_id}' ({complexity}) exceeds hard cap "
                f"({tokens} > {hard_cap} estimated tokens). "
                "Consider splitting the skill file. Injecting full content for now.",
                UserWarning,
                stacklevel=2,
            )
            # Attempt truncation; if Steps alone exceed the cap, inject in full
            truncated = _truncate(sections, soft_cap)
            if _estimate_tokens(truncated) < tokens:
                content = truncated
                tokens = _estimate_tokens(content)

        return SkillSpec(
            skill_id=skill_id,
            agent=str(post.get("agent", "")),
            complexity_class=complexity,
            trigger_phases=_as_list(post.get("trigger-phases", [])),
            primary_outputs=_as_list(post.get("primary-outputs", [])),
            content=content,
            token_estimate=tokens,
        )

    def load_instructions(self, skill_id: str) -> str:
        """Return the runtime prompt string for Layer 3 injection."""
        return self.load(skill_id).content

    def _resolve_path(self, skill_id: str) -> Path:
        if skill_id in self._index:
            return self._index[skill_id]
        # Fallback: rebuild index (handles newly created files)
        self._build_index()
        if skill_id in self._index:
            return self._index[skill_id]
        raise SkillNotFoundError(f"Skill '{skill_id}' not found under {self._root}")


# ---------------------------------------------------------------------------
# Internal parsing helpers
# ---------------------------------------------------------------------------

_H2_RE = re.compile(r"^## (.+)$", re.MULTILINE)


def _extract_included_sections(markdown: str) -> dict[str, str]:
    """
    Split markdown by ## headings and return only included sections.
    Keys are normalised heading names (lower-case).
    """
    parts = _H2_RE.split(markdown)
    # parts: [text-before-first-h2, heading1, body1, heading2, body2, ...]
    result: dict[str, str] = {}
    it = iter(parts[1:])  # skip preamble
    for heading, body in zip(it, it):
        key = heading.strip().lower()
        if key in _INCLUDED_H2:
            result[key] = f"## {heading.strip()}\n{body.rstrip()}"
    return result


def _assemble(sections: dict[str, str]) -> str:
    """Produce the full runtime prompt in canonical section order."""
    order = [
        "inputs required",
        "procedure",
        "steps",
        "algedonic triggers",
        "feedback loop",
        "end-of-skill memory close",
        "outputs",
    ]
    parts = [sections[k] for k in order if k in sections]
    return "\n\n".join(parts)


def _estimate_tokens(text: str) -> int:
    """Rough token estimate: characters / 4 (matches tiktoken average for English prose)."""
    return len(text) // 4


def _truncate(sections: dict[str, str], soft_cap: int) -> str:
    """
    Apply truncation in priority order until content fits within soft_cap.
    Steps (procedure) are NEVER truncated.
    """
    kept = dict(sections)

    # Priority 1: Algedonic Triggers → compact list of ALG-IDs only
    if "algedonic triggers" in kept:
        ids = re.findall(r"ALG-\d+", kept["algedonic triggers"])
        kept["algedonic triggers"] = (
            "## Algedonic Triggers\n"
            + (f"Triggers: {', '.join(sorted(set(ids)))}" if ids else "See algedonic-protocol.md")
        )
        if _estimate_tokens(_assemble(kept)) <= soft_cap:
            return _assemble(kept)

    # Priority 2: Feedback Loop → termination conditions only
    if "feedback loop" in kept:
        match = re.search(r"(?i)(max\s+iterations?[^\n]*|escalation[^\n]*)", kept["feedback loop"])
        termination = match.group(0) if match else "See skill file for feedback loop."
        kept["feedback loop"] = f"## Feedback Loop\n{termination}"
        if _estimate_tokens(_assemble(kept)) <= soft_cap:
            return _assemble(kept)

    # Priority 3: Outputs → artifact paths only
    if "outputs" in kept:
        paths = re.findall(r"`[^`]+`", kept["outputs"])
        kept["outputs"] = (
            "## Outputs\n"
            + (" ".join(paths) if paths else "See skill file for output paths.")
        )

    return _assemble(kept)


def _as_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(v) for v in value]
    if isinstance(value, str):
        return [value]
    return []
