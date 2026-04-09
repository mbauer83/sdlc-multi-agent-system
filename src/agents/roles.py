"""
Per-role agent factory functions.

Each function builds a PydanticAI Agent pre-wired with the tool set
appropriate for that role.  Concrete tool registration follows the
capability grants defined in framework/agent-runtime-spec.md §6 and
write_tools._AGENT_ALLOWED_DIRS.

Usage:
    from src.agents.roles import build_sa_agent, build_pm_agent
    agent = build_sa_agent(agents_root=Path("agents/"), llm_config=cfg)

All builders accept the same keyword arguments as build_agent().
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.agents.base import build_agent
from src.agents.tools.universal_tools import register_universal_tools
from src.agents.tools.write_tools import build_write_tool
from src.models.llm_config import LLMConfig


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

def _build(
    agent_id: str,
    agents_root: Path,
    llm_config: LLMConfig | None,
    extra_tools: list[Any] | None = None,
    register_write: bool = True,
) -> Any:
    """Shared builder: universal tools + optional write tool + extras."""
    agent = build_agent(agent_id, agents_root, llm_config)
    register_universal_tools(agent)
    if register_write:
        agent.tool(build_write_tool(agent_id))
    for fn in (extra_tools or []):
        agent.tool(fn)
    return agent


# ---------------------------------------------------------------------------
# Specialist agents (universal + write)
# ---------------------------------------------------------------------------

def build_sa_agent(
    agents_root: Path,
    llm_config: LLMConfig | None = None,
) -> Any:
    """Solution Architect — writes motivation/strategy/business layers."""
    return _build("SA", agents_root, llm_config)


def build_swa_agent(
    agents_root: Path,
    llm_config: LLMConfig | None = None,
) -> Any:
    """Software Architect — writes application layer + technology-repository."""
    return _build("SwA", agents_root, llm_config)


def build_de_agent(
    agents_root: Path,
    llm_config: LLMConfig | None = None,
) -> Any:
    """Implementing Developer — writes delivery-repository."""
    return _build("DE", agents_root, llm_config)


def build_do_agent(
    agents_root: Path,
    llm_config: LLMConfig | None = None,
) -> Any:
    """DevOps / Platform Engineer — writes devops-repository + delivery-repository."""
    return _build("DO", agents_root, llm_config)


def build_qa_agent(
    agents_root: Path,
    llm_config: LLMConfig | None = None,
) -> Any:
    """QA Engineer — writes qa-repository."""
    return _build("QA", agents_root, llm_config)


def build_po_agent(
    agents_root: Path,
    llm_config: LLMConfig | None = None,
) -> Any:
    """Product Owner — writes project-repository/requirements."""
    return _build("PO", agents_root, llm_config)


def build_smm_agent(
    agents_root: Path,
    llm_config: LLMConfig | None = None,
) -> Any:
    """Sales & Marketing Manager — writes project-repository/market-analysis."""
    return _build("SMM", agents_root, llm_config)


def build_csco_agent(
    agents_root: Path,
    llm_config: LLMConfig | None = None,
) -> Any:
    """Chief Safety & Compliance Officer — writes safety-repository."""
    return _build("CSCO", agents_root, llm_config)


# ---------------------------------------------------------------------------
# PM agent (universal + PM decision tools; no write_tool)
# ---------------------------------------------------------------------------

def build_pm_agent(
    agents_root: Path,
    llm_config: LLMConfig | None = None,
) -> Any:
    """
    Project Manager — universal tools + PM decision tools.

    PM does NOT receive a write_artifact tool; it routes work to specialists
    via invoke_specialist and persists decisions via record_decision.
    """
    from src.agents.tools.pm_tools import register_pm_tools

    agent = build_agent("PM", agents_root, llm_config)
    register_universal_tools(agent)
    register_pm_tools(agent)
    return agent
