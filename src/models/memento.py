"""
MementoState — ephemeral continuity scratchpad for agent invocations.

Tier 2 of the five-tier memory architecture (see framework/learning-protocol.md §13).
Bridges successive `agent.run()` calls within the same phase so that key
decisions and open threads are not lost between invocations.

Content budget: ≤ 250 tokens total.
  key_decisions   max 3 items, each ≤ 30 tokens
  open_threads    max 3 items, each ≤ 20 tokens
  partial_context condensed prose digest, ≤ 100 tokens
"""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field, field_validator


class MementoState(BaseModel):
    """
    Agent's short-term continuity scratchpad for one (engagement, agent, phase).

    Stored with OVERWRITE semantics — each save replaces the previous state for
    the same (engagement_id, agent_role, phase) key.  Not an audit log; use the
    EventStore for canonical history.
    """

    phase: str
    invocation_id: str | None = None   # Links to EventStore for full history
    skill_id: str | None = None        # Active skill at time of save
    key_decisions: list[str] = Field(default_factory=list)
    open_threads: list[str] = Field(default_factory=list)
    partial_context: str = ""
    recorded_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())

    @field_validator("key_decisions")
    @classmethod
    def _cap_decisions(cls, v: list[str]) -> list[str]:
        return v[:3]

    @field_validator("open_threads")
    @classmethod
    def _cap_threads(cls, v: list[str]) -> list[str]:
        return v[:3]

    def summary(self) -> str:
        """Return a compact human-readable summary for injection into agent context."""
        parts: list[str] = [f"Prior invocation state for phase {self.phase}:"]
        if self.key_decisions:
            parts.append("Key decisions:")
            for i, d in enumerate(self.key_decisions, 1):
                parts.append(f"  {i}. {d}")
        if self.open_threads:
            parts.append("Open threads:")
            for i, t in enumerate(self.open_threads, 1):
                parts.append(f"  {i}. {t}")
        return "\n".join(parts)
