"""Step definitions for donation.feature."""

from behave import when, then


@when('"{email}" donates {amount:g} GBP to "{campaign_name}"')
def step_when_donate(context, email, amount, campaign_name):
    # Try to record a donation and save the result for the Then steps
    context.last_ok, context.last_payload = context.service.record_donation(
        email, campaign_name, amount
    )


@then("the donation should be recorded successfully")
def step_then_donation_success(context):
    # Check the donation was saved
    assert context.last_ok is True, (
        f"Expected success, got error: {context.last_payload!r}"
    )


@then("the donation should be rejected")
def step_then_donation_rejected(context):
    # Check the donation was rejected
    assert context.last_ok is False, (
        f"Expected rejection, but donation succeeded with: {context.last_payload!r}"
    )


@then('the "{campaign_name}" total raised should be {amount:g} GBP')
def step_then_campaign_total(context, campaign_name, amount):
    # Look up the campaign and check the total raised matches
    campaign = context.service.campaigns.get(campaign_name)
    assert campaign is not None, f"Campaign {campaign_name!r} does not exist"
    # I use a small tolerance because floats can have tiny rounding errors.
    assert abs(campaign.raised - amount) < 1e-9, (
        f"Expected raised={amount}, got {campaign.raised}"
    )
