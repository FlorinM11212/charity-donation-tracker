"""Step definitions for donor.feature.

Names match the spec's Step-Definition Mapping table (section 11).
"""

from behave import given, when, then


@given("the donation system has no donors")
def step_given_no_donors(context):
    # before_scenario already gives us a fresh service; assert the
    # invariant rather than re-creating one, so a future hook change
    # doesn't silently mask state leakage.
    assert len(context.service.donors) == 0


@given('a donor "{name}" with email "{email}" is registered')
def step_given_donor_registered(context, name, email):
    ok, payload = context.service.register_donor(name, email)
    assert ok, f"Pre-condition failed: could not register donor: {payload}"


@when('I register "{name}" with email "{email}"')
def step_when_register_donor(context, name, email):
    context.last_ok, context.last_payload = context.service.register_donor(
        name, email
    )


@then("the registration should succeed")
def step_then_registration_success(context):
    assert context.last_ok is True, (
        f"Expected success, got error: {context.last_payload!r}"
    )


@then("the registration should fail")
def step_then_registration_failure(context):
    assert context.last_ok is False, (
        f"Expected failure, but operation succeeded with: {context.last_payload!r}"
    )


@then("the system should contain {count:d} donor")
@then("the system should contain {count:d} donors")
def step_then_donor_count(context, count):
    assert len(context.service.donors) == count, (
        f"Expected {count} donor(s), found {len(context.service.donors)}"
    )


@then('the error message should be "{expected}"')
def step_then_error_message(context, expected):
    # Service-level error strings end in a full stop; feature files don't
    # bother with that, so compare without trailing punctuation either way.
    actual = str(context.last_payload).rstrip(".")
    expected = expected.rstrip(".")
    assert actual == expected, f"Expected error {expected!r}, got {actual!r}"
