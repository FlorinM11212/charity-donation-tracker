"""Step definitions for donor.feature.

The scenarios use general phrasing ("a donor", "a valid email"). The
real values used in the tests are kept here as defaults so the scenario
text stays readable to non-technical people.
"""

from behave import given, when, then


# Default test values kept out of the scenario text
DEFAULT_NAME = "Sample Donor"
DEFAULT_EMAIL = "donor@example.com"
OTHER_NAME = "Another Donor"


@given("the donation system has no donors")
def step_given_no_donors(context):
    # Check the system starts empty
    assert len(context.service.donors) == 0


@given("a donor is already registered")
def step_given_donor_registered(context):
    # Add a donor up front using the default name and email
    ok, payload = context.service.register_donor(DEFAULT_NAME, DEFAULT_EMAIL)
    assert ok, f"Pre-condition failed: could not register donor: {payload}"
    # Remember the email so later steps can reuse it
    context.donor_email = DEFAULT_EMAIL


@when("I register a donor with a valid name and a valid email")
def step_when_register_valid_donor(context):
    # Try to register a donor with the default values
    context.last_ok, context.last_payload = context.service.register_donor(
        DEFAULT_NAME, DEFAULT_EMAIL
    )


@when("I register a new donor using the same email")
def step_when_register_duplicate_email(context):
    # Try to register a different donor reusing the email from the Given step
    context.last_ok, context.last_payload = context.service.register_donor(
        OTHER_NAME, context.donor_email
    )


@then("the registration should succeed")
def step_then_registration_success(context):
    # Check the last registration worked
    assert context.last_ok is True, (
        f"Expected success, got error: {context.last_payload!r}"
    )


@then("the registration should fail")
def step_then_registration_failure(context):
    # Check the last registration was rejected
    assert context.last_ok is False, (
        f"Expected failure, but operation succeeded with: {context.last_payload!r}"
    )


@then("the system should contain {count:d} donor")
@then("the system should contain {count:d} donors")
def step_then_donor_count(context, count):
    # Check how many donors are in the system
    assert len(context.service.donors) == count, (
        f"Expected {count} donor(s), found {len(context.service.donors)}"
    )


@then('the error message should be "{expected}"')
def step_then_error_message(context, expected):
    # Compare without the trailing full stop
    actual = str(context.last_payload).rstrip(".")
    expected = expected.rstrip(".")
    assert actual == expected, f"Expected error {expected!r}, got {actual!r}"
