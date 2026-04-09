"""
LearningEntry: canonical Pydantic model for agent learning records.

Governed by framework/learning-protocol.md §8 and
framework/artifact-schemas/learning-entry.schema.md.

Entry types:
  correction      — a mistake was made and corrected
  skill-amendment — a skill procedure needs updating
  episodic        — a noteworthy successful strategy to repeat
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field, field_validator


EntryType = Literal["correction", "skill-amendment", "episodic"]
Importance = Literal["S1", "S2", "S3", "S4"]
Applicability = Literal["this-engagement", "cross-engagement", "enterprise"]


class LearningEntry(BaseModel):
    """
    A single agent learning record.

    The artifact_type must be the PRIMARY OUTPUT artifact of the skill that
    produced this learning — not an input artifact reviewed or consumed.
    This is the retrieval key for query_learnings().
    """

    learning_id: str = Field(description="<ROLE>-L-NNN assigned by record()")
    agent: str = Field(description="Agent role abbreviation e.g. SA, SwA, PM")
    phase: str = Field(description="ADM phase letter(s) e.g. A, B, C")
    artifact_type: str = Field(
        description="Primary output artifact type of the skill (retrieval key)"
    )
    entry_type: EntryType
    error_type: str | None = Field(
        default=None,
        description="Category tag e.g. inference-error, boundary-violation",
    )
    importance: Importance = "S3"
    applicability: Applicability = "this-engagement"

    # Provenance
    generated_at_phase: str
    generated_at_sprint: str | None = None
    generated_at_engagement: str | None = None
    skill_id: str | None = None

    # Graph connectivity for related-entry expansion
    related: list[str] = Field(
        default_factory=list,
        description="learning_ids of related entries for graph expansion",
    )

    # Lifecycle flags
    promoted: bool = False
    synthesis_superseded: bool = False
    synthesised_from: list[str] = Field(default_factory=list)

    # Text payload
    trigger_text: str = Field(description="What triggered this learning")
    correction_text: str = Field(
        description="Imperative first-person, ≤300 chars/sentence, ≤3 sentences"
    )
    context_text: str | None = None

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @field_validator("correction_text")
    @classmethod
    def _validate_correction(cls, v: str) -> str:
        sentences = [s.strip() for s in v.split(".") if s.strip()]
        if len(sentences) > 3:
            raise ValueError("correction_text must be ≤3 sentences")
        for s in sentences:
            if len(s) > 300:
                raise ValueError(
                    f"Each correction sentence must be ≤300 chars, got {len(s)}"
                )
        return v

    def to_frontmatter_dict(self) -> dict[str, object]:
        """Return a subset suitable for YAML frontmatter in a .md file."""
        return {
            "learning-id": self.learning_id,
            "agent": self.agent,
            "phase": self.phase,
            "artifact-type": self.artifact_type,
            "entry-type": self.entry_type,
            "error-type": self.error_type,
            "importance": self.importance,
            "applicability": self.applicability,
            "skill-id": self.skill_id,
            "generated-at-phase": self.generated_at_phase,
            "generated-at-sprint": self.generated_at_sprint,
            "generated-at-engagement": self.generated_at_engagement,
            "promoted": self.promoted,
            "related": self.related,
        }
