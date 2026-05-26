"""Validators for the inputs the user types in.

Every validator returns a tuple (ok, value_or_error). If ok is True the
value is the cleaned input (for example the email in lowercase). If ok
is False the second item is the error message to show the user.
"""

import re
from typing import Tuple

# This is the pattern I use to check emails: something@something.something
# It is simple on purpose - the full email rules would be overkill here.
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# The maximum donation allowed. The spec says no donation over 10,000 GBP.
MAX_DONATION_AMOUNT = 10_000.0


def validate_name(name: str) -> Tuple[bool, str]:
    """Check a donor name. It must be at least 2 characters."""
    if name is None:
        return False, "Name must be at least 2 characters."
    # Remove spaces at the start and end
    cleaned = name.strip()
    if len(cleaned) < 2:
        return False, "Name must be at least 2 characters."
    return True, cleaned


def validate_email(email: str) -> Tuple[bool, str]:
    """Check an email. Returns it in lowercase if it is valid."""
    if email is None:
        return False, "Invalid email format."
    # I clean spaces and make it lowercase so emails compare correctly
    cleaned = email.strip().lower()
    if not _EMAIL_RE.match(cleaned):
        return False, "Invalid email format."
    return True, cleaned


def validate_campaign_name(name: str) -> Tuple[bool, str]:
    """Check a campaign name. It must be at least 3 characters."""
    if name is None:
        return False, "Campaign name must be at least 3 characters."
    cleaned = name.strip()
    if len(cleaned) < 3:
        return False, "Campaign name must be at least 3 characters."
    return True, cleaned


def validate_goal(raw: str) -> Tuple[bool, object]:
    """Check a campaign goal. It must be a number greater than zero."""
    # I try to turn the input into a number; if it fails, it is not a number
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return False, "Goal must be a positive number."
    if value <= 0:
        return False, "Goal must be a positive number."
    return True, value


def validate_amount(raw: str) -> Tuple[bool, object]:
    """Check a donation amount.

    Three things can go wrong:
      - The input is not a number
      - The number is zero or negative
      - The number is bigger than 10,000
    """
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return False, "Amount must be a positive number."
    if value <= 0:
        return False, "Amount must be a positive number."
    if value > MAX_DONATION_AMOUNT:
        return False, "Amount must not exceed 10000."
    return True, value
