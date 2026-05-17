Feature: Campaign management
  As a charity administrator
  I want to create campaigns with realistic goals
  So that donors can contribute to specific causes

  Scenario: Reject a campaign with a non-positive goal
    Given the donation system has no campaigns
    When I create a campaign "Winter Appeal" with goal -100
    Then the campaign creation should fail
    And the error message should be "Goal must be a positive number"
