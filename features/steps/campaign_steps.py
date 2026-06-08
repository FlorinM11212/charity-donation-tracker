"""Step definitions for campaign.feature.

The 'the error message should be ...' step is in donor_steps.py because
behave shares step definitions across all step files.
"""

from behave import given, when, then


# Default values used by these steps
DEFAULT_CAMPAIGN_NAME = "Sample Campaign"
DEFAULT_GOAL = 1000
NEGATIVE_GOAL = -100


@given("the donation system has no campaigns")
def step_given_no_campaigns(context):
    # Check the system starts with no campaigns
    assert len(context.service.campaigns) == 0


@given("an open campaign exists")
def step_given_open_campaign_exists(context):
    # Add a campaign up front as a pre-condition
    ok, payload = context.service.create_campaign(DEFAULT_CAMPAIGN_NAME, DEFAULT_GOAL)
    assert ok, f"Pre-condition failed: could not create campaign: {payload}"
    # Remember the name so later steps can use it
    context.campaign_name = DEFAULT_CAMPAIGN_NAME


@when("I create a campaign with a non-positive goal")
def step_when_create_campaign_invalid_goal(context):
    # Try to create a campaign with a goal that is not positive
    context.last_ok, context.last_payload = context.service.create_campaign(
        DEFAULT_CAMPAIGN_NAME, NEGATIVE_GOAL
    )


@then("the campaign creation should fail")
def step_then_campaign_failed(context):
    # Check the last create_campaign call failed
    assert context.last_ok is False, (
        f"Expected failure, but campaign creation succeeded with: {context.last_payload!r}"
    )


@then("the campaign creation should succeed")
def step_then_campaign_succeeded(context):
    # Check the last create_campaign call succeeded
    assert context.last_ok is True, (
        f"Expected success, got error: {context.last_payload!r}"
    )
