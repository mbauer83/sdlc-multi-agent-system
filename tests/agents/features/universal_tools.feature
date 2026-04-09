Feature: Universal agent tool adapters
  As a PydanticAI agent
  I want artifact query tools that return correct JSON-serializable structures
  So that tool results can be passed to the LLM without serialization errors

  Background:
    Given a temporary architecture repository with one entity file

  Scenario: list_artifacts returns list of plain dicts
    When list_artifacts is called with no filters
    Then the result is a list
    And each item in the list is a dict with keys artifact_id, name, status

  Scenario: list_artifacts with artifact_type filter returns matching entities only
    When list_artifacts is called with artifact_type "stakeholder"
    Then the result contains only items where artifact_type is "stakeholder"

  Scenario: list_artifacts with unknown filter returns empty list
    When list_artifacts is called with artifact_type "nonexistent-type"
    Then the result is an empty list

  Scenario: list_artifacts result dicts have no Path objects
    When list_artifacts is called with no filters
    Then each item in the list is JSON-serializable

  Scenario: search_artifacts returns list of dicts with score field
    When search_artifacts is called with query "test stakeholder"
    Then the result is a list
    And each item has keys artifact_id, name, score, record_type

  Scenario: search_artifacts result dicts have no Path objects
    When search_artifacts is called with query "stakeholder"
    Then each item in the list is JSON-serializable

  Scenario: read_artifact returns a JSON string for an existing artifact
    When read_artifact is called with the entity's artifact_id
    Then the result is a string
    And the string contains the artifact_id

  Scenario: read_artifact returns an error string for a missing artifact
    When read_artifact is called with artifact_id "DOES-NOT-EXIST"
    Then the result is a string starting with "[Artifact"

  Scenario: list_artifacts does not raise when the repo root is missing
    Given a context with a non-existent architecture repository
    When list_artifacts is called with no filters
    Then the result is an empty list

  Scenario: search_artifacts does not raise when the repo root is missing
    Given a context with a non-existent architecture repository
    When search_artifacts is called with query "anything"
    Then the result is an empty list
