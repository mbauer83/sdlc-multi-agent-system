Feature: Diagram file verification
  As a Stage 5 validate_diagram tool or pre-commit hook
  I want to verify that .puml diagram files conform to ERP v2.0 and diagram-conventions.md
  So that diagrams only reference entities and connections that exist in the ModelRegistry

  Scenario: Valid ArchiMate diagram passes verification
    Given a ModelVerifier with a full registry
    And a well-formed ArchiMate diagram referencing known entities and connections
    When I verify the diagram file
    Then the result is valid
    And there are no errors

  Scenario: Missing PUML frontmatter block causes an error
    Given a ModelVerifier with a full registry
    And a .puml file with no frontmatter comment block
    When I verify the diagram file
    Then the result is invalid
    And error code "E311" is reported

  Scenario: Malformed YAML in PUML frontmatter causes an error
    Given a ModelVerifier with a full registry
    And a .puml file with invalid YAML in its frontmatter comment block
    When I verify the diagram file
    Then the result is invalid
    And error code "E312" is reported

  Scenario: Missing required frontmatter field causes an error
    Given a ModelVerifier with a full registry
    And a diagram file missing the "diagram-type" field
    When I verify the diagram file
    Then the result is invalid
    And error code "E021" is reported

  Scenario: entity-ids-used references unknown entity causes an error
    Given a ModelVerifier with a full registry
    And a diagram file whose entity-ids-used includes "APP-999"
    When I verify the diagram file
    Then the result is invalid
    And error code "E301" is reported

  Scenario: connection-ids-used references unknown connection causes an error
    Given a ModelVerifier with a full registry
    And a diagram file whose connection-ids-used includes "APP-001---APP-999"
    When I verify the diagram file
    Then the result is invalid
    And error code "E302" is reported

  Scenario: ArchiMate diagram missing _macros.puml causes an error
    Given a ModelVerifier with a full registry
    And an ArchiMate diagram that does not include _macros.puml
    When I verify the diagram file
    Then the result is invalid
    And error code "E303" is reported

  Scenario: ArchiMate diagram missing _archimate-stereotypes.puml causes a warning
    Given a ModelVerifier with a full registry
    And an ArchiMate diagram that includes _macros.puml but not _archimate-stereotypes.puml
    When I verify the diagram file
    Then the result is valid
    And warning code "W301" is reported

  Scenario: PUML file missing @startuml causes an error
    Given a ModelVerifier with a full registry
    And a diagram file without @startuml
    When I verify the diagram file
    Then the result is invalid
    And error code "E304" is reported

  Scenario: PUML file missing @enduml causes an error
    Given a ModelVerifier with a full registry
    And a diagram file without @enduml
    When I verify the diagram file
    Then the result is invalid
    And error code "E305" is reported

  Scenario: Baselined diagram referencing a draft entity causes E306
    Given a ModelVerifier with a full registry
    And a baselined diagram whose entity-ids-used includes a draft entity "APP-001"
    When I verify the diagram file
    Then the result is invalid
    And error code "E306" is reported

  Scenario: Draft diagram referencing a draft entity does not cause E306
    Given a ModelVerifier with a full registry
    And a draft diagram whose entity-ids-used includes a draft entity "APP-001"
    When I verify the diagram file
    Then the result is valid
    And there are no errors

  Scenario: Batch verify_all finds errors across entity and connection files
    Given a ModelVerifier with no registry
    And an architecture repository with one valid entity and one invalid connection
    When I run verify_all on the repository
    Then the invalid connection result has errors
    And the valid entity result has no errors
