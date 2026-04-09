"""
LLMConfig — structured LLM provider configuration.

Replaces scattered os.getenv("SDLC_MODEL", ...) calls with a single,
validated configuration object.  Provider strings follow PydanticAI's
native ``provider:model-id`` convention so that swapping providers is
purely a config change:

  anthropic:claude-sonnet-4-6        # Anthropic (default)
  openai:gpt-4o                      # OpenAI
  ollama:llama3.1                    # Ollama (local, OpenAI-compatible)
  test                               # PydanticAI TestModel (no API key needed)

Resolution order (highest priority first):
  1. Environment variables  SDLC_PRIMARY_MODEL / SDLC_ROUTING_MODEL
  2. Per-engagement  llm:  block in engagements-config.yaml
  3. Top-level  llm:  block in engagements-config.yaml
  4. Compiled-in defaults (Anthropic Sonnet / Haiku)
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Compiled-in defaults
# ---------------------------------------------------------------------------

_DEFAULT_PRIMARY = "anthropic:claude-sonnet-4-6"
_DEFAULT_ROUTING = "anthropic:claude-haiku-4-5-20251001"


# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------

class LLMConfig(BaseModel):
    """Validated LLM provider configuration for one engagement session."""

    primary_model: str = Field(
        default=_DEFAULT_PRIMARY,
        description=(
            "PydanticAI model string for primary specialist agents. "
            "Format: 'provider:model-id' or 'test' for TestModel."
        ),
    )
    routing_model: str = Field(
        default=_DEFAULT_ROUTING,
        description=(
            "PydanticAI model string for PM routing / summarisation agents. "
            "Typically a faster / cheaper model than primary_model."
        ),
    )
    extra_params: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional keyword arguments forwarded to the PydanticAI Agent constructor.",
    )

    # ------------------------------------------------------------------
    # Constructors
    # ------------------------------------------------------------------

    @classmethod
    def from_env(cls) -> "LLMConfig":
        """Build from environment variables only (no file I/O)."""
        return cls(
            primary_model=os.getenv("SDLC_PRIMARY_MODEL", _DEFAULT_PRIMARY),
            routing_model=os.getenv("SDLC_ROUTING_MODEL", _DEFAULT_ROUTING),
        )

    @classmethod
    def load(cls, config_path: Path, engagement_id: str) -> "LLMConfig":
        """
        Load with full resolution cascade.

        Env vars always win — they are applied on top of whatever the YAML
        provides so that CI / local overrides work without editing files.
        """
        if not config_path.exists():
            return cls.from_env()

        raw: dict[str, Any] = yaml.safe_load(config_path.read_text()) or {}

        # 1. Per-engagement llm block
        eng_block = raw.get("engagements", {})
        active: list[dict] = (
            eng_block.get("active-engagements", [])
            if isinstance(eng_block, dict)
            else []
        )
        for eng in active:
            if isinstance(eng, dict) and eng.get("id") == engagement_id:
                if llm_block := eng.get("llm"):
                    return cls._from_block(llm_block)
                break  # engagement found but has no llm block — fall through

        # 2. Top-level llm block
        if llm_block := raw.get("llm"):
            return cls._from_block(llm_block)

        # 3. Env-only fallback
        return cls.from_env()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    @classmethod
    def _from_block(cls, block: dict[str, Any]) -> "LLMConfig":
        """Build from a YAML llm: block, with env vars taking precedence."""
        primary = (
            os.getenv("SDLC_PRIMARY_MODEL")
            or block.get("primary-model", _DEFAULT_PRIMARY)
        )
        routing = (
            os.getenv("SDLC_ROUTING_MODEL")
            or block.get("routing-model", _DEFAULT_ROUTING)
        )
        return cls(
            primary_model=primary,
            routing_model=routing,
            extra_params=block.get("extra-params", {}),
        )
