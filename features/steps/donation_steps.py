"""Step definitions for donation.feature."""

from behave import when, then


# Default values used by these steps
VALID_DONATION_AMOUNT = 50
OVER_LIMIT_AMOUNT = 25000


@when("the donor makes a valid donation to the campaign")
def step_when_valid_donation(context):
    # Use the donor email from donor_steps and the campaign name from campaign_steps
    context.donation_amount = VALID_DONATION_AMOUNT
    context.last_ok, context.last_payload = context.service.record_donation(
        context.donor_email, context.campaign_name, VALID_DONATION_AMOUNT
    )


@when("the donor tries to donate more than 10000 GBP to the campaign")
def step_when_over_limit_donation(context):
    # Try to donate an amount over the maximum allowed
    context.last_ok, context.last_payload = context.service.record_donation(
        context.donor_email, context.campaign_name, OVER_LIMIT_AMOUNT
    )


@then("the donation should be recorded successfully")
def step_then_donation_success(context):
    # Check the donation went through
    assert context.last_ok is True, (
        f"Expected success, got error: {context.last_payload!r}"
    )


@then("the donation should be rejected")
def step_then_donation_rejected(context):
    # Check the donation was rejected
    assert context.last_ok is False, (
        f"Expected rejection, but donation succeeded with: {context.last_payload!r}"
    )


@then("the campaign total raised should equal the donated amount")
def step_then_campaign_total_matches(context):
    # Check the campaign's raised total matches the amount we just donated
    campaign = context.service.campaigns.get(context.campaign_name)
    assert campaign is not None, "Campaign was not found"
    assert abs(campaign.raised - context.donation_amount) < 1e-9, (
        f"Expected raised={context.donation_amount}, got {campaign.raised}"
    )
