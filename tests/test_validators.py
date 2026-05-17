"""Optional pytest unit tests for the validators module.

Run with:  pytest tests/

These complement the BDD scenarios — they cover edge cases at the unit
level (exotic inputs, the exact regex, the cap value) that would clutter
the Gherkin if expressed there.
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


# ---- validate_name ---------------------------------------------------------


@pytest.mark.parametrize("good", ["Al", "Alice", "  Alice Johnson  "])
def test_validate_name_accepts_valid(good):
    ok, value = validate_name(good)
    assert ok is True
    assert value == good.strip()


@pytest.mark.parametrize("bad", [None, "", " ", "a", "  x"])
def test_validate_name_rejects_short_or_empty(bad):
    ok, msg = validate_name(bad)
    assert ok is False
    assert msg == "Name must be at least 2 characters."


# ---- validate_email --------------------------------------------------------


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
    ok, msg = validate_email(bad)
    assert ok is False
    assert msg == "Invalid email format."


# ---- validate_campaign_name -----------------------------------------------


def test_validate_campaign_name_requires_three_chars():
    ok, msg = validate_campaign_name("ab")
    assert ok is False
    assert msg == "Campaign name must be at least 3 characters."


def test_validate_campaign_name_trims_whitespace():
    ok, value = validate_campaign_name("  Winter Appeal  ")
    assert ok is True
    assert value == "Winter Appeal"


# ---- validate_goal ---------------------------------------------------------


@pytest.mark.parametrize("raw,expected", [("100", 100.0), (250, 250.0), ("0.5", 0.5)])
def test_validate_goal_accepts_positive(raw, expected):
    ok, value = validate_goal(raw)
    assert ok is True
    assert value == expected


@pytest.mark.parametrize("bad", ["0", "-1", "-100", "abc", None, ""])
def test_validate_goal_rejects_non_positive_or_garbage(bad):
    ok, msg = validate_goal(bad)
    assert ok is False
    assert msg == "Goal must be a positive number."


# ---- validate_amount ------------------------------------------------------


def test_validate_amount_accepts_at_cap():
    ok, value = validate_amount(MAX_DONATION_AMOUNT)
    assert ok is True
    assert value == MAX_DONATION_AMOUNT


def test_validate_amount_rejects_just_above_cap():
    ok, msg = validate_amount(MAX_DONATION_AMOUNT + 0.01)
    assert ok is False
    assert msg == "Amount must not exceed 10000."


@pytest.mark.parametrize("bad", ["abc", None, ""])
def test_validate_amount_rejects_non_numeric(bad):
    ok, msg = validate_amount(bad)
    assert ok is False
    assert msg == "Amount must be a positive number."


@pytest.mark.parametrize("bad", ["0", "-0.01", "-50"])
def test_validate_amount_rejects_zero_or_negative(bad):
    ok, msg = validate_amount(bad)
    assert ok is False
    assert msg == "Amount must be a positive number."
