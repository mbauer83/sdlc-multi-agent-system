Feature: MCP model writer tools
  The sdlc-model MCP server should provide deterministic writer tools
  that produce ERP v2.0-compliant entity, connection, and diagram artifacts
  with a dry-run mode and strong repo-boundary enforcement.

  Scenario: Dry-run create entity returns a valid artifact
    Given an empty engagement architecture repository
    When I dry-run create an entity
    Then the dry-run result should include a valid entity verification

  Scenario: Create connection fails when referenced entity does not exist
    Given an empty engagement architecture repository
    When I attempt to create a connection referencing unknown entities
    Then the call should fail with a helpful error

  Scenario: Create diagram infers entity and connection ids
    Given an engagement architecture repository with two entities and one connection
    When I create an archimate diagram with serving connection
    Then the diagram should verify successfully and reference the inferred ids
