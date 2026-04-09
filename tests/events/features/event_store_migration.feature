Feature: EventStore Alembic migration baseline
  The Alembic baseline migration must create the correct schema, be idempotent
  when applied to a database already initialised by EventStore.__init__, and
  leave the database in a state where EventStore can operate normally.

  Scenario: Baseline migration creates events table on an empty database
    Given an empty SQLite database
    When alembic upgrade head is applied
    Then the events table exists
    And the snapshots table exists
    And the alembic_version table records revision "001"

  Scenario: Baseline migration is idempotent on a pre-initialised database
    Given a database already initialised by EventStore
    When alembic upgrade head is applied
    Then the events table exists
    And the snapshots table exists
    And the alembic_version table records revision "001"

  Scenario: EventStore operates correctly on a database migrated by Alembic
    Given an empty SQLite database
    When alembic upgrade head is applied
    And EventStore is opened against the migrated database
    Then EventStore can append an event and retrieve it

  Scenario: Downgrade removes both tables
    Given an empty SQLite database
    When alembic upgrade head is applied
    And alembic downgrade base is applied
    Then the events table does not exist
    And the snapshots table does not exist

  Scenario: Baseline migration columns match the EventStore schema contract
    Given an empty SQLite database
    When alembic upgrade head is applied
    Then the events table has columns event_id, event_type, timestamp, engagement_id, cycle_id, actor, correlation_id, payload
    And the snapshots table has columns snapshot_at, timestamp, state
