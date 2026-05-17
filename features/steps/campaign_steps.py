"""Step definitions for campaign.feature.

The "the error message should be" Then step is shared with donor_steps.py;
behave deduplicates by step text, so we only define it in one place.
"""

from behave import given, when, then


@given("the donation system has no campaigns")
def step_given_no_campaigns(context):
    assert len(context.service.campaigns) == 0


@given('a campaign "{name}" with goal {goal:g} exists')
def step_given_campaign_exists(context, name, goal):
    ok, payload = context.service.create_campaign(name, goal)
    assert ok, f"Pre-condition failed: could not create campaign: {payload}"


@when('I create a campaign "{name}" with goal {goal:g}')
def step_when_create_campaign(context, name, goal):
    context.last_ok, context.last_payload = context.service.create_campaign(
        name, goal
    )


@then("the campaign creation should fail")
def step_then_campaign_failed(context):
    assert context.last_ok is False, (
        f"Expected failure, but campaign creation succeeded with: {context.last_payload!r}"
    )


@then("the campaign creation should succeed")
def step_then_campaign_succeeded(context):
    assert context.last_ok is True, (
        f"Expected success, got error: {context.last_payload!r}"
    )
