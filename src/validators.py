"""Input validators for donor names, email addresses, campaign names,
campaign goals, and donation amounts.

Each validator returns ``(ok, normalised_value_or_error_message)`` so the
service layer can both reject bad input and use the cleaned-up value
without re-doing the work (e.g. lowercased email).
"""

import re
from typing import Tuple

# Email pattern from the spec: local@domain.tld with no whitespace and no
# stray @ signs. Deliberately simple — full RFC 5322 is overkill for a CLI
# admin tool, and the spec lists this exact regex.
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# Donation hard cap (FR-3.5). Kept as a module constant so tests can import it.
MAX_DONATION_AMOUNT = 10_000.0


def validate_name(name: str) -> Tuple[bool, str]:
    """Validate a donor name. Trims whitespace; requires at least 2 chars."""
    if name is None:
        return False, "Name must be at least 2 characters."
    cleaned = name.strip()
    if len(cleaned) < 2:
        return False, "Name must be at least 2 characters."
    return True, cleaned


def validate_email(email: str) -> Tuple[bool, str]:
    """Validate an email address. Returns the lowercased form on success."""
    if email is None:
        return False, "Invalid email format."
    cleaned = email.strip().lower()
    if not _EMAIL_RE.match(cleaned):
        return False, "Invalid email format."
    return True, cleaned


def validate_campaign_name(name: str) -> Tuple[bool, str]:
    """Validate a campaign name. Trims whitespace; requires at least 3 chars."""
    if name is None:
        return False, "Campaign name must be at least 3 characters."
    cleaned = name.strip()
    if len(cleaned) < 3:
        return False, "Campaign name must be at least 3 characters."
    return True, cleaned


def validate_goal(raw: str) -> Tuple[bool, object]:
    """Validate a campaign goal entered as a raw string.

    Accepts ``str`` or numeric input. Returns the parsed float on success or
    the canonical "Goal must be a positive number." message on failure.
    """
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return False, "Goal must be a positive number."
    if value <= 0:
        return False, "Goal must be a positive number."
    return True, value


def validate_amount(raw: str) -> Tuple[bool, object]:
    """Validate a donation amount entered as a raw string.

    Returns the parsed float on success, or one of the spec's exact error
    messages on failure. Three distinct failure modes:
      * non-numeric input        -> "Amount must be a positive number."
      * zero or negative         -> "Amount must be a positive number."
      * above the 10,000 cap     -> "Amount must not exceed 10000."
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
