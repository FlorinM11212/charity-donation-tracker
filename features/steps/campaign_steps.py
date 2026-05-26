"""Step definitions for campaign.feature.

The 'the error message should be ...' step is in donor_steps.py because
behave shares step definitions across all step files.
"""

from behave import given, when, then


@given("the donation system has no campaigns")
def step_given_no_campaigns(context):
    # Check there are no campaigns at the start of the test
    assert len(context.service.campaigns) == 0


@given('a campaign "{name}" with goal {goal:g} exists')
def step_given_campaign_exists(context, name, goal):
    # Add a campaign up front - this is a pre-condition
    ok, payload = context.service.create_campaign(name, goal)
    assert ok, f"Pre-condition failed: could not create campaign: {payload}"


@when('I create a campaign "{name}" with goal {goal:g}')
def step_when_create_campaign(context, name, goal):
    # Try to create a campaign and save the result for the Then steps
    context.last_ok, context.last_payload = context.service.create_campaign(
        name, goal
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
