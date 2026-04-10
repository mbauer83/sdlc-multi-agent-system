"""
SkillLoader: parses a skill markdown file and extracts the runtime prompt.

Governed by framework/agent-runtime-spec.md §4 (Layer 3 injection).

Section registry and parsing logic live in _skill_sections.py.
Public API:
  SkillLoader.load(skill_id, invocation_mode)  → SkillSpec
  SkillLoader.load_instructions(skill_id, invocation_mode)  → str

invocation_mode values:
  "workflow"  — full engagement context; includes workflow-only sections
                (Algedonic Triggers, End-of-Skill Memory Close)
  "express"   — standalone invocation; workflow-only sections excluded;
                Layer 1 express override sentence injected by build_agent()

Complexity-class token budgets (soft / hard):
  simple:   700  / 840
  standard: 1400 / 1680
  complex:  2350 / 2820
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import frontmatter  # python-frontmatter

from ._skill_sections import (
    BUDGETS,
    assemble,
    budget_tokens,
    filter_by_mode,
    parse_sections,
    truncate,
)


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

class SkillNotFoundError(FileNotFoundError):
    """Raised when the skill file cannot be located."""


class SkillBudgetExceededError(ValueError):
    """
    Raised when skill content exceeds the hard token cap.
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
    invoke_when: str
    invoke_never_when: str
    content: str            # assembled runtime sections (within budget)
    token_estimate: int     # budget-aware token count


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

    def load(
        self,
        skill_id: str,
        invocation_mode: Literal["workflow", "express"] = "workflow",
    ) -> SkillSpec:
        """Load and return a SkillSpec for the given skill-id."""
        path = self._resolve_path(skill_id)
        post = frontmatter.load(str(path))
        complexity = str(post.get("complexity-class", "standard"))
        soft_cap, hard_cap = BUDGETS.get(complexity, BUDGETS["standard"])

        entries = parse_sections(post.content, skill_id)
        filtered = filter_by_mode(entries, invocation_mode)
        tokens = budget_tokens(filtered)

        if tokens > hard_cap:
            warnings.warn(
                f"Skill '{skill_id}' ({complexity}) exceeds hard cap "
                f"({tokens} > {hard_cap} estimated tokens). "
                "Consider splitting the skill file. Attempting truncation.",
                UserWarning,
                stacklevel=2,
            )
            truncated = truncate(filtered, soft_cap)
            if budget_tokens(truncated) < tokens:
                filtered = truncated
                tokens = budget_tokens(filtered)

        return SkillSpec(
            skill_id=skill_id,
            agent=str(post.get("agent", "")),
            complexity_class=complexity,
            trigger_phases=_as_list(post.get("trigger-phases", [])),
            primary_outputs=_as_list(post.get("primary-outputs", [])),
            invoke_when=str(post.get("invoke-when", "")).strip(),
            invoke_never_when=str(post.get("invoke-never-when", "")).strip(),
            content=assemble(filtered),
            token_estimate=tokens,
        )

    def load_instructions(
        self,
        skill_id: str,
        invocation_mode: Literal["workflow", "express"] = "workflow",
    ) -> str:
        """Return the runtime prompt string for Layer 3 injection."""
        if not skill_id:
            return ""
        return self.load(skill_id, invocation_mode=invocation_mode).content

    def _resolve_path(self, skill_id: str) -> Path:
        if skill_id in self._index:
            return self._index[skill_id]
        self._build_index()  # refresh for newly created files
        if skill_id in self._index:
            return self._index[skill_id]
        raise SkillNotFoundError(
            f"Skill '{skill_id}' not found under {self._root}"
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _as_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(v) for v in value]
    if isinstance(value, str):
        return [value]
    return []
