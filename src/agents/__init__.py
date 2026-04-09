"""
Agent package — AGENT_REGISTRY and convenience accessors.

AGENT_REGISTRY is lazily populated on first access via get_agent().
Agents are built against the default agents/ root and LLMConfig.from_env().
For custom roots or configs use the per-role builders in src.agents.roles directly.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.models.llm_config import LLMConfig

# Canonical agent role identifiers
AGENT_IDS: tuple[str, ...] = (
    "PM", "SA", "SwA", "DE", "DO", "QA", "PO", "SMM", "CSCO",
)

_REGISTRY: dict[str, Any] = {}
_DEFAULT_AGENTS_ROOT = Path(__file__).parent.parent.parent / "agents"


def get_agent(
    agent_id: str,
    agents_root: Path | None = None,
    llm_config: LLMConfig | None = None,
) -> Any:
    """
    Return a pre-built PydanticAI Agent for agent_id.

    Agents are cached after first build (singleton per agent_id when using
    default root + config).  Pass explicit agents_root or llm_config to
    bypass the cache and build a fresh instance.
    """
    if agent_id not in AGENT_IDS:
        raise KeyError(
            f"Unknown agent_id '{agent_id}'. Known agents: {AGENT_IDS}"
        )

    use_cache = agents_root is None and llm_config is None
    if use_cache and agent_id in _REGISTRY:
        return _REGISTRY[agent_id]

    root = agents_root or _DEFAULT_AGENTS_ROOT
    agent = _build_for_id(agent_id, root, llm_config)

    if use_cache:
        _REGISTRY[agent_id] = agent
    return agent


def _build_for_id(
    agent_id: str,
    agents_root: Path,
    llm_config: LLMConfig | None,
) -> Any:
    from src.agents.roles import (
        build_csco_agent,
        build_de_agent,
        build_do_agent,
        build_pm_agent,
        build_po_agent,
        build_qa_agent,
        build_sa_agent,
        build_smm_agent,
        build_swa_agent,
    )

    builders = {
        "PM":   build_pm_agent,
        "SA":   build_sa_agent,
        "SwA":  build_swa_agent,
        "DE":   build_de_agent,
        "DO":   build_do_agent,
        "QA":   build_qa_agent,
        "PO":   build_po_agent,
        "SMM":  build_smm_agent,
        "CSCO": build_csco_agent,
    }
    return builders[agent_id](agents_root=agents_root, llm_config=llm_config)
