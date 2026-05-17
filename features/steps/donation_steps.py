"""Step definitions for donation.feature."""

from behave import when, then


@when('"{email}" donates {amount:g} GBP to "{campaign_name}"')
def step_when_donate(context, email, amount, campaign_name):
    context.last_ok, context.last_payload = context.service.record_donation(
        email, campaign_name, amount
    )


@then("the donation should be recorded successfully")
def step_then_donation_success(context):
    assert context.last_ok is True, (
        f"Expected success, got error: {context.last_payload!r}"
    )


@then("the donation should be rejected")
def step_then_donation_rejected(context):
    assert context.last_ok is False, (
        f"Expected rejection, but donation succeeded with: {context.last_payload!r}"
    )


@then('the "{campaign_name}" total raised should be {amount:g} GBP')
def step_then_campaign_total(context, campaign_name, amount):
    campaign = context.service.campaigns.get(campaign_name)
    assert campaign is not None, f"Campaign {campaign_name!r} does not exist"
    # Use a small epsilon: amount is parsed from the feature file as a
    # float, so direct equality on monetary sums is fine here, but a
    # tolerance protects us if anyone changes the parser later.
    assert abs(campaign.raised - amount) < 1e-9, (
        f"Expected raised={amount}, got {campaign.raised}"
    )
