"""Unit tests for the validators module.

To run them:  pytest tests/

These tests check things that would be too messy to put in the BDD
scenarios, like every kind of bad email or the exact 10,000 cap.
"""

import pytest

from src.validators import (
    MAX_DONATION_AMOUNT,
    validate_amount,
    validate_campaign_name,
    validate_email,
    validate_goal,
    validate_name,
)


# ---- Tests for validate_name -----------------------------------------------


@pytest.mark.parametrize("good", ["Al", "Alice", "  Alice Johnson  "])
def test_validate_name_accepts_valid(good):
    # These names should all be accepted
    ok, value = validate_name(good)
    assert ok is True
    assert value == good.strip()


@pytest.mark.parametrize("bad", [None, "", " ", "a", "  x"])
def test_validate_name_rejects_short_or_empty(bad):
    # These names are too short or empty - should be rejected
    ok, msg = validate_name(bad)
    assert ok is False
    assert msg == "Name must be at least 2 characters."


# ---- Tests for validate_email ----------------------------------------------


@pytest.mark.parametrize(
    "good,expected",
    [
        ("alice@example.com", "alice@example.com"),
        ("  Alice@Example.COM  ", "alice@example.com"),
        ("a.b@c.d.org", "a.b@c.d.org"),
        ("user@example.uk", "user@example.uk"),
    ],
)
def test_validate_email_accepts_valid(good, expected):
    # These emails should pass and come back in lowercase
    ok, value = validate_email(good)
    assert ok is True
    assert value == expected


@pytest.mark.parametrize(
    "bad",
    [
        None,
        "",
        "no-at-sign.com",
        "two@@example.com",
        "spaces in@example.com",
        "trailing@dot.",
        "@nolocal.com",
        "noTLD@example",
    ],
)
def test_validate_email_rejects_malformed(bad):
    # These are all broken emails - should be rejected
    ok, msg = validate_email(bad)
    assert ok is False
    assert msg == "Invalid email format."


# ---- Tests for validate_campaign_name --------------------------------------


def test_validate_campaign_name_requires_three_chars():
    # Two-character name is too short
    ok, msg = validate_campaign_name("ab")
    assert ok is False
    assert msg == "Campaign name must be at least 3 characters."


def test_validate_campaign_name_trims_whitespace():
    # Spaces at the start and end should be removed
    ok, value = validate_campaign_name("  Winter Appeal  ")
    assert ok is True
    assert value == "Winter Appeal"


# ---- Tests for validate_goal -----------------------------------------------


@pytest.mark.parametrize("raw,expected", [("100", 100.0), (250, 250.0), ("0.5", 0.5)])
def test_validate_goal_accepts_positive(raw, expected):
    # Positive numbers (as strings or numbers) should be accepted
    ok, value = validate_goal(raw)
    assert ok is True
    assert value == expected


@pytest.mark.parametrize("bad", ["0", "-1", "-100", "abc", None, ""])
def test_validate_goal_rejects_non_positive_or_garbage(bad):
    # Zero, negative numbers, and non-numbers should all be rejected
    ok, msg = validate_goal(bad)
    assert ok is False
    assert msg == "Goal must be a positive number."


# ---- Tests for validate_amount ---------------------------------------------


def test_validate_amount_accepts_at_cap():
    # Exactly 10,000 is allowed
    ok, value = validate_amount(MAX_DONATION_AMOUNT)
    assert ok is True
    assert value == MAX_DONATION_AMOUNT


def test_validate_amount_rejects_just_above_cap():
    # One penny over the cap should be rejected
    ok, msg = validate_amount(MAX_DONATION_AMOUNT + 0.01)
    assert ok is False
    assert msg == "Amount must not exceed 10000."


@pytest.mark.parametrize("bad", ["abc", None, ""])
def test_validate_amount_rejects_non_numeric(bad):
    # Things that aren't numbers should be rejected
    ok, msg = validate_amount(bad)
    assert ok is False
    assert msg == "Amount must be a positive number."


@pytest.mark.parametrize("bad", ["0", "-0.01", "-50"])
def test_validate_amount_rejects_zero_or_negative(bad):
    # Zero or negative amounts should be rejected
    ok, msg = validate_amount(bad)
    assert ok is False
    assert msg == "Amount must be a positive number."
