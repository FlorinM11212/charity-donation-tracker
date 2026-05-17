"""Business logic for the Charity Donation Tracker.

The service is the single source of truth for the in-memory state. The
menu (main.py) and the BDD step definitions both drive it through the
methods below — they never mutate the dictionaries directly. Each public
method returns ``(ok, payload)`` where ``payload`` is either the created
domain object on success or a human-readable error message on failure.

This shape keeps the menu code dumb (just print the message) and makes
the BDD assertions trivial: success = ok is True, and the error message
is right there when ok is False.
"""

from typing import Dict, List, Optional, Tuple

from src.campaign import Campaign
from src.donation import Donation
from src.donor import Donor
from src.validators import (
    validate_amount,
    validate_campaign_name,
    validate_email,
    validate_goal,
    validate_name,
)


class DonationService:
    """In-memory orchestrator for donors, campaigns, and donations."""

    def __init__(self) -> None:
        # All three indices are keyed for O(1) lookup. Donors by lowercased
        # email so duplicate detection is case-insensitive (FR-1.2).
        self.donors: Dict[str, Donor] = {}
        self.campaigns: Dict[str, Campaign] = {}
        self.donations: Dict[str, Donation] = {}

    # ---- Donor operations ------------------------------------------------

    def register_donor(self, name: str, email: str) -> Tuple[bool, object]:
        """Register a new donor. Returns (True, Donor) or (False, error)."""
        ok_name, name_or_err = validate_name(name)
        if not ok_name:
            return False, name_or_err

        ok_email, email_or_err = validate_email(email)
        if not ok_email:
            return False, email_or_err

        # Email lookup is case-insensitive because validate_email lowercases.
        if email_or_err in self.donors:
            return False, "A donor with this email already exists."

        donor = Donor(name=name_or_err, email=email_or_err)
        self.donors[donor.email] = donor
        return True, donor

    def list_donors(self) -> List[Donor]:
        """All donors sorted alphabetically by name (case-insensitive)."""
        return sorted(self.donors.values(), key=lambda d: d.name.lower())

    def find_donor(self, email: str) -> Optional[Donor]:
        """Look up a donor by email; returns None if not found or invalid."""
        ok, cleaned = validate_email(email)
        if not ok:
            return None
        return self.donors.get(cleaned)

    # ---- Campaign operations --------------------------------------------

    def create_campaign(self, name: str, goal_raw: object) -> Tuple[bool, object]:
        """Create a campaign. Returns (True, Campaign) or (False, error).

        ``goal_raw`` can be a string (typed at the menu) or a number (from
        BDD steps); validate_goal handles both.
        """
        ok_name, name_or_err = validate_campaign_name(name)
        if not ok_name:
            return False, name_or_err

        if name_or_err in self.campaigns:
            return False, "A campaign with this name already exists."

        ok_goal, goal_or_err = validate_goal(goal_raw)
        if not ok_goal:
            return False, goal_or_err

        campaign = Campaign(name=name_or_err, goal=float(goal_or_err))
        self.campaigns[campaign.name] = campaign
        return True, campaign

    def list_campaigns(self) -> List[Campaign]:
        """All campaigns in insertion order (so the user sees newest last)."""
        return list(self.campaigns.values())

    def close_campaign(self, name: str) -> Tuple[bool, object]:
        """Mark a campaign as closed. Idempotent guard against double-close."""
        cleaned = (name or "").strip()
        campaign = self.campaigns.get(cleaned)
        if campaign is None:
            return False, "No campaign with that name."
        if campaign.is_closed:
            return False, "Campaign is already closed."
        campaign.is_closed = True
        return True, campaign

    # ---- Donation operations --------------------------------------------

    def record_donation(
        self, donor_email: str, campaign_name: str, amount_raw: object
    ) -> Tuple[bool, object]:
        """Validate and record a donation. (True, Donation) or (False, error).

        Validation order is the spec's chain (8.7): donor, campaign, open,
        amount-is-number, amount-positive, amount<=10000. Order matters
        because each later check depends on the previous one having passed.
        """
        ok_email, email_or_err = validate_email(donor_email)
        if not ok_email or email_or_err not in self.donors:
            # Spec uses a single "Donor not registered" message for both an
            # unknown donor and an obviously-malformed email; the user is
            # being told the same thing either way.
            return False, "Donor not registered."

        campaign = self.campaigns.get((campaign_name or "").strip())
        if campaign is None:
            return False, "Campaign not found."
        if campaign.is_closed:
            return False, "Campaign is closed."

        ok_amount, amount_or_err = validate_amount(amount_raw)
        if not ok_amount:
            return False, amount_or_err

        donation = Donation(
            donor_email=email_or_err,
            campaign_name=campaign.name,
            amount=float(amount_or_err),
        )
        # Guarantee uniqueness of the 6-char receipt id within this session
        # (uuid4 collisions are extremely rare, but the cost of avoiding
        # them is one cheap loop check).
        while donation.donation_id in self.donations:
            donation = Donation(
                donor_email=email_or_err,
                campaign_name=campaign.name,
                amount=float(amount_or_err),
            )

        self.donations[donation.donation_id] = donation
        self.donors[email_or_err].donations.append(donation.donation_id)
        campaign.raised += donation.amount
        return True, donation

    def donations_for_donor(self, email: str) -> List[Donation]:
        """All donation records belonging to a donor, oldest first."""
        donor = self.find_donor(email)
        if donor is None:
            return []
        return [self.donations[d_id] for d_id in donor.donations if d_id in self.donations]
