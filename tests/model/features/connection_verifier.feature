Feature: Connection file verification
  As a Stage 5 write_artifact tool or pre-commit hook
  I want to verify that model-connection .md files conform to ERP v2.0 conventions
  So that connection filenames, artifact-ids, and source/target references are consistent

  Scenario: Valid connection file passes verification
    Given a ModelVerifier with a registry containing "APP-001" and "APP-016"
    And a well-formed connection file referencing known entities
    When I verify the connection file
    Then the result is valid
    And there are no errors

  Scenario: artifact-id not matching filename causes an error
    Given a ModelVerifier with a registry containing "APP-001" and "APP-016"
    And a connection file whose artifact-id does not match its filename stem
    When I verify the connection file
    Then the result is invalid
    And error code "E202" is reported

  Scenario: artifact-id with invalid format causes an error
    Given a ModelVerifier with a registry containing "APP-001" and "APP-016"
    And a connection file with artifact-id "app001---app016"
    When I verify the connection file
    Then the result is invalid
    And error code "E201" is reported

  Scenario: Source referencing unknown entity causes an error
    Given a ModelVerifier with a registry containing "APP-001" and "APP-016"
    And a connection file whose source is "APP-999"
    When I verify the connection file
    Then the result is invalid
    And error code "E204" is reported

  Scenario: Target referencing unknown entity causes an error
    Given a ModelVerifier with a registry containing "APP-001" and "APP-016"
    And a connection file whose target is "APP-999"
    When I verify the connection file
    Then the result is invalid
    And error code "E204" is reported

  Scenario: Unrecognised connection type causes an error
    Given a ModelVerifier with a registry containing "APP-001" and "APP-016"
    And a connection file with artifact-type "archimate-unknown"
    When I verify the connection file
    Then the result is invalid
    And error code "E102" is reported

  Scenario: Missing display section causes an error
    Given a ModelVerifier with a registry containing "APP-001" and "APP-016"
    And a connection file without a "§display" section
    When I verify the connection file
    Then the result is invalid
    And error code "E031" is reported

  Scenario: Missing content section causes a warning only
    Given a ModelVerifier with a registry containing "APP-001" and "APP-016"
    And a connection file without a "§content" section
    When I verify the connection file
    Then the result is valid
    And warning code "W031" is reported

  Scenario: No registry skips reference checks with a warning
    Given a ModelVerifier with no registry
    And a connection file referencing "APP-001" and "APP-016"
    When I verify the connection file
    Then the result is valid
    And warning code "W001" is reported

  Scenario: Enterprise connection may omit engagement field
    Given a ModelVerifier with no registry
    And an enterprise-scope connection file without an "engagement" field
    When I verify the connection file
    Then the result is valid
    And warning code "W001" is reported

  Scenario: Enterprise connection referencing engagement entity is rejected
    Given a ModelVerifier with a unified registry containing enterprise and engagement entities
    And an enterprise-scope connection referencing an engagement entity
    When I verify the connection file
    Then the result is invalid
    And error code "E210" is reported

  Scenario: Engagement connection may reference enterprise entity
    Given a ModelVerifier with a unified registry containing enterprise and engagement entities
    And an engagement-scope connection referencing an enterprise entity
    When I verify the connection file
    Then the result is valid
    And there are no errors
