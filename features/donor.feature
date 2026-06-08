Feature: Donor registration
  As a charity administrator
  I want to register donors with valid details
  So that I can attribute donations correctly

  Scenario: Register a new donor with valid details
    Given the donation system has no donors
    When I register a donor with a valid name and a valid email
    Then the registration should succeed
    And the system should contain 1 donor

  Scenario: Reject a donor whose email is already registered
    Given a donor is already registered
    When I register a new donor using the same email
    Then the registration should fail
    And the error message should be "A donor with this email already exists"
