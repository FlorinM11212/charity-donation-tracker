Feature: Donation processing
  As a charity administrator
  I want every donation to be validated
  So that the records remain accurate and trustworthy

  Scenario: Successful donation by a registered donor to an open campaign
    Given a donor "Alice Johnson" with email "alice@example.com" is registered
    And a campaign "Winter Appeal" with goal 1000 exists
    When "alice@example.com" donates 50 GBP to "Winter Appeal"
    Then the donation should be recorded successfully
    And the "Winter Appeal" total raised should be 50 GBP

  Scenario: Reject a donation greater than 10000 GBP
    Given a donor "Alice Johnson" with email "alice@example.com" is registered
    And a campaign "Winter Appeal" with goal 50000 exists
    When "alice@example.com" donates 25000 GBP to "Winter Appeal"
    Then the donation should be rejected
    And the error message should be "Amount must not exceed 10000"
