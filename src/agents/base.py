"""
build_agent(): factory function that constructs a PydanticAI Agent for a given role.

Four-layer system prompt assembly (per framework/agent-runtime-spec.md §4):
  Layer 1: system-prompt-identity from AGENT.md frontmatter (≤150 tokens)
  Layer 2: ### Runtime Behavioral Stance subsection from AGENT.md §11 (≤350 tokens)
  Layer 3: active skill content via SkillLoader (injected per-call via @agent.instructions)
  Layer 4: per-call context (workflow state summary, injected in the user prompt)

Only Layers 1+2 are static (baked into the system prompt at agent-build time).
Layer 3 is dynamic — the SkillLoader is wired as an @agent.instructions callback.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import frontmatter
from pydantic_ai import Agent

from src.models.llm_config import LLMConfig
from .deps import AgentDeps
from .skill_loader import SkillLoader

# Hard token caps for Layer 1 and Layer 2
_L1_HARD_CAP = 150  # tokens
_L2_HARD_CAP = 350  # tokens
_CHARS_PER_TOKEN = 4  # rough heuristic (same as SkillLoader)


# ---------------------------------------------------------------------------
# Agent spec loading
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AgentSpec:
    agent_id: str
    layer1: str   # system-prompt-identity verbatim
    layer2: str   # ### Runtime Behavioral Stance text


class AgentSpecError(ValueError):
    """Raised when AGENT.md cannot be parsed or a layer exceeds its cap."""


def load_agent_spec(agent_id: str, agents_root: Path) -> AgentSpec:
    """
    Parse AGENT.md for agent_id and extract Layer 1 + Layer 2 content.

    Searches for <agent_id>/AGENT.md under agents_root (case-insensitive on
    directory name so "SA" matches "solution-architect").
    """
    agent_dir = _find_agent_dir(agent_id, agents_root)
    agent_md = agent_dir / "AGENT.md"
    if not agent_md.exists():
        raise AgentSpecError(f"AGENT.md not found for agent '{agent_id}' at {agent_md}")

    post = frontmatter.load(str(agent_md))

    # --- Layer 1 ---
    layer1 = str(post.get("system-prompt-identity", "")).strip()
    if not layer1:
        raise AgentSpecError(f"AGENT.md for '{agent_id}' has no system-prompt-identity field")
    if len(layer1) // _CHARS_PER_TOKEN > _L1_HARD_CAP:
        import warnings
        warnings.warn(
            f"system-prompt-identity for '{agent_id}' exceeds {_L1_HARD_CAP} token cap "
            f"({len(layer1) // _CHARS_PER_TOKEN} estimated tokens). "
            "Consider trimming the AGENT.md field.",
            UserWarning,
            stacklevel=2,
        )

    # --- Layer 2 ---
    layer2 = _extract_runtime_behavioral_stance(post.content)
    if len(layer2) // _CHARS_PER_TOKEN > _L2_HARD_CAP:
        # Truncate at sentence boundary rather than hard-cut
        layer2 = _truncate_at_sentence(layer2, _L2_HARD_CAP * _CHARS_PER_TOKEN)

    return AgentSpec(agent_id=agent_id, layer1=layer1, layer2=layer2)


# ---------------------------------------------------------------------------
# Agent factory
# ---------------------------------------------------------------------------

def build_agent(
    agent_id: str,
    agents_root: Path,
    llm_config: LLMConfig | None = None,
    result_type: type | None = None,
) -> Any:
    """
    Build a PydanticAI Agent for the given agent_id.

    The returned agent has:
    - Static system prompt: Layer 1 + Layer 2
    - Dynamic Layer 3 via @agent.instructions (SkillLoader)
    - result_type: str by default; pass result_type=PMDecision for the PM
      supervisor node (returns structured routing decisions).

    Provider is determined by llm_config.primary_model (PydanticAI
    'provider:model-id' string).  Defaults to LLMConfig.from_env() when
    no config is supplied.
    """
    from typing import Any as _Any  # avoid re-export confusion
    cfg = llm_config or LLMConfig.from_env()
    spec = load_agent_spec(agent_id, agents_root)
    skill_loader = SkillLoader(agents_root)

    static_system_prompt = (
        f"{spec.layer1}\n\n"
        f"## Behavioral Stance\n{spec.layer2}"
        if spec.layer2
        else spec.layer1
    )

    extra: dict[str, _Any] = dict(cfg.extra_params)
    if result_type is not None:
        extra["result_type"] = result_type

    agent: Any = Agent(
        model=cfg.primary_model,
        system_prompt=static_system_prompt,
        deps_type=AgentDeps,
        retries=3,
        model_settings={"max_tokens": 8192},
        **extra,
    )

    @agent.system_prompt
    def _inject_skill(ctx: object) -> str:  # type: ignore[misc]
        """Layer 3: inject the active skill content at call time."""
        deps: AgentDeps = ctx.deps  # type: ignore[attr-defined]
        if not deps.active_skill_id:
            return ""
        try:
            return (
                "\n\n## Active Skill\n"
                + skill_loader.load_instructions(deps.active_skill_id)
            )
        except Exception as exc:  # noqa: BLE001
            return f"\n\n[Skill load failed: {exc}]"

    return agent


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_AGENT_DIR_ALIASES: dict[str, str] = {
    "SA":   "solution-architect",
    "SwA":  "software-architect",
    "PM":   "project-manager",
    "PO":   "product-owner",
    "DE":   "implementing-developer",
    "DO":   "devops-platform",
    "QA":   "qa-engineer",
    "SMM":  "sales-marketing",
    "CSCO": "csco",
}


def _find_agent_dir(agent_id: str, agents_root: Path) -> Path:
    # Canonical alias lookup first
    if dir_name := _AGENT_DIR_ALIASES.get(agent_id):
        candidate = agents_root / dir_name
        if candidate.is_dir():
            return candidate
    # Fallback: case-insensitive scan
    lower = agent_id.lower()
    for child in agents_root.iterdir():
        if child.is_dir() and (
            child.name.lower() == lower
            or child.name.lower().replace("-", "") == lower.replace("-", "")
        ):
            return child
    raise AgentSpecError(
        f"Agent directory for '{agent_id}' not found under {agents_root}. "
        f"Known aliases: {list(_AGENT_DIR_ALIASES)}"
    )


_BEHAVIORAL_STANCE_RE = re.compile(
    r"###\s+Runtime Behavioral Stance\s*\n(.*?)(?=\n###|\n##|\Z)",
    re.DOTALL,
)


def _extract_runtime_behavioral_stance(markdown: str) -> str:
    match = _BEHAVIORAL_STANCE_RE.search(markdown)
    if not match:
        return ""
    return match.group(1).strip()


def _truncate_at_sentence(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    truncated = text[:max_chars]
    last_period = truncated.rfind(". ")
    if last_period > max_chars // 2:
        return truncated[: last_period + 1]
    return truncated
