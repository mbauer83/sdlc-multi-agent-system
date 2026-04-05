Feature: Entity file verification
  As a Stage 5 write_artifact tool or pre-commit hook
  I want to verify that model-entity .md files conform to ERP v2.0 conventions
  So that the ModelRegistry can be built reliably and diagrams remain consistent

  Background:
    Given a ModelVerifier with no registry

  Scenario: Valid entity file passes verification
    Given a well-formed entity file with all required fields
    When I verify the entity file
    Then the result is valid
    And there are no errors

  Scenario: Missing frontmatter block causes an error
    Given an entity file that does not start with ---
    When I verify the entity file
    Then the result is invalid
    And error code "E011" is reported

  Scenario: Unclosed frontmatter block causes an error
    Given an entity file whose frontmatter --- is never closed
    When I verify the entity file
    Then the result is invalid
    And error code "E012" is reported

  Scenario: Malformed YAML in frontmatter causes an error
    Given an entity file with invalid YAML in the frontmatter
    When I verify the entity file
    Then the result is invalid
    And error code "E013" is reported

  Scenario: Missing required field causes an error
    Given an entity file that is missing the "safety-relevant" field
    When I verify the entity file
    Then the result is invalid
    And error code "E021" is reported

  Scenario: Invalid artifact-id format causes an error
    Given an entity file with artifact-id "app-001"
    When I verify the entity file
    Then the result is invalid
    And error code "E101" is reported

  Scenario: Unrecognised artifact-type causes an error
    Given an entity file with artifact-type "unknown-widget"
    When I verify the entity file
    Then the result is invalid
    And error code "E102" is reported

  Scenario: Non-boolean safety-relevant causes an error
    Given an entity file with safety-relevant set to the string "yes"
    When I verify the entity file
    Then the result is invalid
    And error code "E103" is reported

  Scenario: Invalid status value causes an error
    Given an entity file with status "pending"
    When I verify the entity file
    Then the result is invalid
    And error code "E022" is reported

  Scenario: Missing section content marker causes an error
    Given an entity file without a "§content" section marker
    When I verify the entity file
    Then the result is invalid
    And error code "E031" is reported

  Scenario: Missing section display marker causes an error
    Given an entity file without a "§display" section marker
    When I verify the entity file
    Then the result is invalid
    And error code "E031" is reported

  Scenario: Filename prefix mismatch causes an error
    Given an entity file whose filename does not start with its artifact-id
    When I verify the entity file
    Then the result is invalid
    And error code "E104" is reported

  Scenario: Valid entity file with friendly-name in filename passes verification
    Given a well-formed entity file with a friendly-name suffix in the filename
    When I verify the entity file
    Then the result is valid
    And there are no errors

  Scenario: Enterprise entity may omit engagement field
    Given an enterprise entity file without an "engagement" field
    When I verify the entity file
    Then the result is valid
    And there are no errors
