"""Step definitions for donor.feature.

These are the Python functions that match each Given/When/Then line
in donor.feature. behave finds them by the text in the @decorators.
"""

from behave import given, when, then


@given("the donation system has no donors")
def step_given_no_donors(context):
    # The service is already empty thanks to before_scenario,
    # but I check it just to be safe.
    assert len(context.service.donors) == 0


@given('a donor "{name}" with email "{email}" is registered')
def step_given_donor_registered(context, name, email):
    # Add a donor up front - this is a pre-condition for the test
    ok, payload = context.service.register_donor(name, email)
    assert ok, f"Pre-condition failed: could not register donor: {payload}"


@when('I register "{name}" with email "{email}"')
def step_when_register_donor(context, name, email):
    # Try to register a donor and save the result for the Then steps
    context.last_ok, context.last_payload = context.service.register_donor(
        name, email
    )


@then("the registration should succeed")
def step_then_registration_success(context):
    # Check the last result was a success
    assert context.last_ok is True, (
        f"Expected success, got error: {context.last_payload!r}"
    )


@then("the registration should fail")
def step_then_registration_failure(context):
    # Check the last result was a failure
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
    # The service adds a full stop to error messages, but the feature
    # files don't include one. I strip the full stop before comparing.
    actual = str(context.last_payload).rstrip(".")
    expected = expected.rstrip(".")
    assert actual == expected, f"Expected error {expected!r}, got {actual!r}"
