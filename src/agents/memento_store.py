"""
MementoStore — LangGraph BaseStore wrapper for ephemeral agent continuity state.

Tier 2 of the five-tier memory architecture (framework/learning-protocol.md §13).

Storage semantics: OVERWRITE (single slot per namespace + key).
Namespace pattern: (engagement_id, agent_role, "memento")
Key:              current ADM phase, e.g. "A", "B", "C"

Differs from LearningStore (APP-003) in that:
  - State is ephemeral and can be lost without data loss (reconstructible from
    EventStore + artifacts).
  - Semantics are overwrite, not accumulate.
  - No cross-agent visibility — each agent sees only its own memento.

APP-023 in the ENG-001 architecture model.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from src.models.memento import MementoState


class MementoStore:
    """
    Persistent-but-ephemeral continuity scratchpad backed by SQLite.

    Uses a dedicated `mementos` table in the engagement's workflow.db so that
    it co-locates with the EventStore and LearningStore without an additional
    file.  The table is created on first use (CREATE TABLE IF NOT EXISTS).

    Parameters
    ----------
    engagement_id:
        Engagement identifier.
    agent_role:
        Role identifier, e.g. "SA", "SwA".  Used as namespace component.
    db_path:
        Path to the engagement's workflow.db.  If None, falls back to the
        default engagements/<engagement_id>/workflow.db path.
    """

    _CREATE_SQL = """
    CREATE TABLE IF NOT EXISTS mementos (
        engagement_id TEXT NOT NULL,
        agent_role    TEXT NOT NULL,
        phase         TEXT NOT NULL,
        state_json    TEXT NOT NULL,
        recorded_at   TEXT NOT NULL,
        PRIMARY KEY (engagement_id, agent_role, phase)
    )
    """

    def __init__(
        self,
        engagement_id: str,
        agent_role: str,
        db_path: Path | None = None,
    ) -> None:
        self._engagement_id = engagement_id
        self._agent_role = agent_role

        if db_path is None:
            db_path = (
                Path(__file__).parent.parent.parent
                / "engagements" / engagement_id / "workflow.db"
            )
        self._db_path = db_path
        self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._conn.execute(self._CREATE_SQL)
        self._conn.commit()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get(self, phase: str) -> MementoState | None:
        """
        Return the stored MementoState for (engagement_id, agent_role, phase),
        or None if no state has been saved yet for this phase.
        """
        row = self._conn.execute(
            "SELECT state_json FROM mementos "
            "WHERE engagement_id = ? AND agent_role = ? AND phase = ?",
            (self._engagement_id, self._agent_role, phase),
        ).fetchone()
        if row is None:
            return None
        return MementoState.model_validate_json(row[0])

    def save(self, state: MementoState) -> None:
        """
        Overwrite (upsert) the MementoState for (engagement_id, agent_role, phase).

        The state_json is the full Pydantic serialisation.  Overwrites any
        prior state for the same primary key.
        """
        self._conn.execute(
            """
            INSERT INTO mementos (engagement_id, agent_role, phase, state_json, recorded_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(engagement_id, agent_role, phase) DO UPDATE SET
                state_json  = excluded.state_json,
                recorded_at = excluded.recorded_at
            """,
            (
                self._engagement_id,
                self._agent_role,
                state.phase,
                state.model_dump_json(),
                state.recorded_at,
            ),
        )
        self._conn.commit()

    def clear(self, phase: str | None = None) -> None:
        """
        Delete memento state.  If phase is None, clears all phases for this
        agent in this engagement (e.g., on engagement reset).
        """
        if phase is not None:
            self._conn.execute(
                "DELETE FROM mementos WHERE engagement_id = ? AND agent_role = ? AND phase = ?",
                (self._engagement_id, self._agent_role, phase),
            )
        else:
            self._conn.execute(
                "DELETE FROM mementos WHERE engagement_id = ? AND agent_role = ?",
                (self._engagement_id, self._agent_role),
            )
        self._conn.commit()
