Feature: Donation processing
  As a charity administrator
  I want every donation to be validated
  So that the records remain accurate and trustworthy

  Scenario: Record a valid donation from a registered donor to an open campaign
    Given a donor is already registered
    And an open campaign exists
    When the donor makes a valid donation to the campaign
    Then the donation should be recorded successfully
    And the campaign total raised should equal the donated amount

  Scenario: Reject a donation greater than the maximum allowed amount
    Given a donor is already registered
    And an open campaign exists
    When the donor tries to donate more than 10000 GBP to the campaign
    Then the donation should be rejected
    And the error message should be "Amount must not exceed 10000"
