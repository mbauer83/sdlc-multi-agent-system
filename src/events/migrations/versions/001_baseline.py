"""Baseline schema: events + snapshots tables.

Idempotency guarantee
---------------------
This migration uses CREATE TABLE IF NOT EXISTS / CREATE INDEX IF NOT EXISTS
throughout so it is safe to run against a database that was already
initialised by EventStore.__init__ (which executes the same DDL via
executescript).  Two valid startup sequences are therefore supported:

  1. Fresh engagement: EventStore init runs DDL → alembic upgrade head stamps
     revision "001" into alembic_version without re-executing any DDL.

  2. CI / managed deployment: alembic upgrade head runs first (empty DB) →
     EventStore init calls executescript; the IF NOT EXISTS guards are no-ops.

All subsequent migrations (002+) are also expected to be written
idempotently so that the two paths remain interchangeable.

Revision ID: 001
Create date: 2026-04-10
"""

from __future__ import annotations

from alembic import op


# revision identifiers, used by Alembic
revision = "001"
down_revision = None          # first migration
branch_labels = None
depends_on = None


def upgrade() -> None:
    # -----------------------------------------------------------------
    # events — append-only workflow event log
    # -----------------------------------------------------------------
    op.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id        TEXT    UNIQUE NOT NULL,
            event_type      TEXT    NOT NULL,
            timestamp       TEXT    NOT NULL,
            engagement_id   TEXT    NOT NULL,
            cycle_id        TEXT,
            actor           TEXT    NOT NULL,
            correlation_id  TEXT,
            payload         TEXT    NOT NULL,
            CONSTRAINT valid_json CHECK (json_valid(payload))
        )
    """)

    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_events_type        ON events(event_type)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_events_cycle       ON events(cycle_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_events_correlation ON events(correlation_id)"
    )

    # -----------------------------------------------------------------
    # snapshots — serialised WorkflowState checkpoints
    # -----------------------------------------------------------------
    op.execute("""
        CREATE TABLE IF NOT EXISTS snapshots (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            snapshot_at TEXT    NOT NULL,
            timestamp   TEXT    NOT NULL,
            state       TEXT    NOT NULL
        )
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS snapshots")
    op.execute("DROP TABLE IF EXISTS events")
