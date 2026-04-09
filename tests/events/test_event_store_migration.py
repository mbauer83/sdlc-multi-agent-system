"""BDD scenarios for the EventStore Alembic migration baseline.

Tests verify:
  - Schema is created correctly on empty databases.
  - Migration is idempotent on EventStore-pre-initialised databases.
  - EventStore operates correctly on Alembic-migrated databases.
  - Downgrade is clean.
  - Column set matches the EventStore contract.

Alembic is invoked programmatically (no subprocess) so tests are fast and
do not depend on the CLI being on PATH.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig
from pytest_bdd import given, parsers, scenarios, then, when

from src.events.event_store import EventStore
from src.events.models.phase import PhaseEnteredPayload

scenarios("features/event_store_migration.feature")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).parent.parent.parent


def _make_alembic_cfg(db_path: Path) -> AlembicConfig:
    """Build an AlembicConfig targeting a specific SQLite database file."""
    cfg = AlembicConfig(_REPO_ROOT / "alembic.ini")
    cfg.set_main_option("script_location", str(_REPO_ROOT / "src" / "events" / "migrations"))
    cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    return cfg


def _table_names(db_path: Path) -> set[str]:
    """Return all user-created table names in the SQLite database."""
    conn = sqlite3.connect(str(db_path))
    try:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
        return {r[0] for r in rows}
    finally:
        conn.close()


def _column_names(db_path: Path, table: str) -> set[str]:
    """Return all column names for the given table."""
    conn = sqlite3.connect(str(db_path))
    try:
        rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
        return {r[1] for r in rows}
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    return tmp_path / "workflow.db"


@pytest.fixture
def alembic_cfg(db_path: Path) -> AlembicConfig:
    return _make_alembic_cfg(db_path)


# ---------------------------------------------------------------------------
# Given steps
# ---------------------------------------------------------------------------


@given("an empty SQLite database", target_fixture="db_path")
def empty_database(db_path: Path) -> Path:
    # Just ensure the file doesn't exist yet; SQLite creates it on connect
    assert not db_path.exists()
    return db_path


@given("a database already initialised by EventStore", target_fixture="db_path")
def pre_initialised_database(db_path: Path) -> Path:
    # EventStore.__init__ runs executescript to create tables
    EventStore(engagement_id="ENG-PRE", db_path=db_path)
    assert "events" in _table_names(db_path)
    return db_path


# ---------------------------------------------------------------------------
# When steps
# ---------------------------------------------------------------------------


@when("alembic upgrade head is applied")
def upgrade_head(db_path: Path) -> None:
    alembic_command.upgrade(_make_alembic_cfg(db_path), "head")


@when("alembic downgrade base is applied")
def downgrade_base(db_path: Path) -> None:
    alembic_command.downgrade(_make_alembic_cfg(db_path), "base")


@when("EventStore is opened against the migrated database", target_fixture="store")
def open_event_store(db_path: Path) -> EventStore:
    return EventStore(engagement_id="ENG-MIGRATED", db_path=db_path)


# ---------------------------------------------------------------------------
# Then steps
# ---------------------------------------------------------------------------


@then("the events table exists")
def events_table_exists(db_path: Path) -> None:
    assert "events" in _table_names(db_path), "events table missing"


@then("the snapshots table exists")
def snapshots_table_exists(db_path: Path) -> None:
    assert "snapshots" in _table_names(db_path), "snapshots table missing"


@then(parsers.parse('the alembic_version table records revision "{rev}"'))
def alembic_version_is(db_path: Path, rev: str) -> None:
    conn = sqlite3.connect(str(db_path))
    try:
        rows = conn.execute("SELECT version_num FROM alembic_version").fetchall()
    finally:
        conn.close()
    assert rows, "alembic_version table is empty — migration was not stamped"
    assert rows[0][0] == rev, f"Expected revision '{rev}', got '{rows[0][0]}'"


@then("the events table does not exist")
def events_table_gone(db_path: Path) -> None:
    assert "events" not in _table_names(db_path), "events table should have been dropped"


@then("the snapshots table does not exist")
def snapshots_table_gone(db_path: Path) -> None:
    assert "snapshots" not in _table_names(db_path), "snapshots table should have been dropped"


@then("EventStore can append an event and retrieve it")
def store_round_trip(store: EventStore) -> None:
    envelope = store.append(
        PhaseEnteredPayload(
            phase_id="A",
            iteration_type="context",
            iteration_number=1,
            trigger="initial",
        ),
        actor="TEST",
    )
    assert envelope.event_id.startswith("ENG-MIGRATED")
    state = store.current_state()
    assert state is not None


@then(
    parsers.parse(
        "the events table has columns {cols}"
    )
)
def events_table_columns(db_path: Path, cols: str) -> None:
    expected = {c.strip() for c in cols.split(",")}
    actual = _column_names(db_path, "events")
    missing = expected - actual
    assert not missing, f"events table missing columns: {missing}"


@then(
    parsers.parse(
        "the snapshots table has columns {cols}"
    )
)
def snapshots_table_columns(db_path: Path, cols: str) -> None:
    expected = {c.strip() for c in cols.split(",")}
    actual = _column_names(db_path, "snapshots")
    missing = expected - actual
    assert not missing, f"snapshots table missing columns: {missing}"
