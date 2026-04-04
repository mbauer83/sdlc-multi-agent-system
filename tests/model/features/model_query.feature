Feature: Model repository query and search
  As a Stage 5 agent tool or developer exploring the ENG-001 model
  I want to filter, query, and search indexed entity/connection/diagram records
  So that discovery scans return the right artifacts without walking directories

  Background:
    Given a populated model repository with test fixtures

  # -----------------------------------------------------------------------
  # Basic listing and filtering
  # -----------------------------------------------------------------------

  Scenario: Listing all entities returns all indexed records
    When I list all entities
    Then I get 4 entity results

  Scenario: Filtering entities by layer
    When I list entities in the "business" layer
    Then I get 2 entity results

  Scenario: Filtering entities by artifact type
    When I list entities with type "application-component"
    Then I get 1 entity result

  Scenario: Filtering entities by owner agent
    When I list entities owned by "SA"
    Then I get 2 entity results

  Scenario: Filtering entities by phase
    When I list entities produced in phase "B"
    Then I get 2 entity results

  Scenario: Filtering entities by status
    When I list entities with status "baselined"
    Then I get 1 entity result

  Scenario: Filtering entities by safety_relevant flag
    When I list entities that are safety relevant
    Then I get 1 entity result

  Scenario: Combining multiple filters returns intersection
    When I list entities in the "business" layer owned by "SA"
    Then I get 2 entity results

  Scenario: Empty result when no entities match filters
    When I list entities in the "technology" layer
    Then I get 0 entity results

  # -----------------------------------------------------------------------
  # Connections
  # -----------------------------------------------------------------------

  Scenario: Listing all connections
    When I list all connections
    Then I get 3 connection results

  Scenario: Filtering connections by language
    When I list connections with language "archimate"
    Then I get 2 connection results

  Scenario: Filtering connections by source
    When I list connections from source "APP-001"
    Then I get 2 connection results

  Scenario: Filtering connections by target
    When I list connections targeting "BSV-001"
    Then I get 1 connection result

  # -----------------------------------------------------------------------
  # Diagrams
  # -----------------------------------------------------------------------

  Scenario: Listing diagrams returns indexed puml files
    When I list all diagrams
    Then I get 1 diagram result

  Scenario: Filtering diagrams by type
    When I list diagrams of type "archimate-business"
    Then I get 1 diagram result

  # -----------------------------------------------------------------------
  # Direct lookup
  # -----------------------------------------------------------------------

  Scenario: Getting an entity by id returns the full record
    When I get artifact "APP-001"
    Then the artifact name is "EventStore"
    And the artifact type is "application-component"
    And the artifact layer is "application"
    And the content text is non-empty

  Scenario: Getting a connection by id returns the record
    When I get artifact "APP-001---BSV-001"
    Then the artifact type is "archimate-realization"

  Scenario: Getting an unknown id returns None
    When I get artifact "UNKNOWN-999"
    Then no artifact is found

  # -----------------------------------------------------------------------
  # Graph traversal
  # -----------------------------------------------------------------------

  Scenario: Find outbound connections for an entity
    When I find outbound connections for "APP-001"
    Then I get 2 connection results

  Scenario: Find inbound connections for an entity
    When I find inbound connections for "BSV-001"
    Then I get 1 connection result

  Scenario: Find all connections for an entity
    When I find all connections for "APP-001"
    Then I get 2 connection results

  Scenario: One-hop neighbors of an entity
    When I find 1-hop neighbors of "APP-001"
    Then hop "1" contains "BSV-001"

  Scenario: Entity with no connections has empty neighbors
    When I find 1-hop neighbors of "BPR-001"
    Then the neighbor map is empty

  # -----------------------------------------------------------------------
  # framework-aligned list_artifacts interface
  # -----------------------------------------------------------------------

  Scenario: list_artifacts returns ArtifactSummary objects
    When I call list_artifacts with layer "application"
    Then I get 2 artifact summaries
    And each summary has an artifact_id

  Scenario: list_artifacts with multi-value layer filter
    When I call list_artifacts with layers "business" and "strategy"
    Then I get 2 artifact summaries

  Scenario: list_artifacts excludes connections by default
    When I call list_artifacts with no filters
    Then connections are not included in results

  Scenario: list_artifacts includes connections when requested
    When I call list_artifacts with include_connections true
    Then connections are included in results

  # -----------------------------------------------------------------------
  # read_artifact interface
  # -----------------------------------------------------------------------

  Scenario: read_artifact summary mode returns metadata and snippet
    When I read artifact "APP-001" in summary mode
    Then the result contains field "artifact_id" with value "APP-001"
    And the result contains field "record_type" with value "entity"
    And the result contains field "content_snippet"
    And the result does not contain field "content_text"

  Scenario: read_artifact full mode returns complete content
    When I read artifact "APP-001" in full mode
    Then the result contains field "content_text"
    And the result contains field "display_blocks"

  Scenario: read_artifact returns None for unknown id
    When I read artifact "MISSING-000" in summary mode
    Then read_artifact returns None

  # -----------------------------------------------------------------------
  # Keyword search
  # -----------------------------------------------------------------------

  Scenario: Search returns relevant entities ranked by score
    When I search for "append-only event log sqlite"
    Then "APP-001" appears in the search results
    And "APP-001" is the top result

  Scenario: Search scores name matches higher than content
    When I search for "sprint"
    Then "BPR-001" appears in the search results

  Scenario: Search with no matches returns empty hits
    When I search for "xyzzy quux nonexistent"
    Then the search result has 0 hits

  Scenario: Search limit caps the number of returned hits
    When I search for "application" with limit 1
    Then the search result has 1 hits

  Scenario: search_artifacts framework alias works the same as search
    When I call search_artifacts for "event store"
    Then "APP-001" appears in the search results

  # -----------------------------------------------------------------------
  # Stats
  # -----------------------------------------------------------------------

  Scenario: Stats returns counts and layer breakdown
    When I get repository stats
    Then stats entities count is 4
    And stats connections count is 3
    And stats layer "application" count is 2
