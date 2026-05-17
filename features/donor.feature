Feature: Donor registration
  As a charity administrator
  I want to register donors with valid details
  So that I can attribute donations correctly

  Scenario: Register a new donor with valid details
    Given the donation system has no donors
    When I register "Alice Johnson" with email "alice@example.com"
    Then the registration should succeed
    And the system should contain 1 donor

  Scenario: Reject duplicate donor email
    Given a donor "Alice Johnson" with email "alice@example.com" is registered
    When I register "Alice Clone" with email "alice@example.com"
    Then the registration should fail
    And the error message should be "A donor with this email already exists"
