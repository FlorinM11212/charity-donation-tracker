"""The main service that holds the program's data and rules.

This class is the brain of the program. Both the menu (main.py) and the
BDD tests call its methods. Every method returns two things: True/False
to say if it worked, and either the new object or an error message.
This way the menu just has to print whatever the second item is.
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
    """Holds all the donors, campaigns and donations in memory."""

    def __init__(self) -> None:
        # I use dictionaries because they let me find things fast.
        # Donors are keyed by email (in lowercase) so I can detect duplicates.
        self.donors: Dict[str, Donor] = {}
        self.campaigns: Dict[str, Campaign] = {}
        self.donations: Dict[str, Donation] = {}

    # ---- Donor methods ---------------------------------------------------

    def register_donor(self, name: str, email: str) -> Tuple[bool, object]:
        """Add a new donor. Returns (True, donor) on success."""
        # First check the name is valid
        ok_name, name_or_err = validate_name(name)
        if not ok_name:
            return False, name_or_err

        # Then check the email is valid
        ok_email, email_or_err = validate_email(email)
        if not ok_email:
            return False, email_or_err

        # Check the email is not already used (lowercase compare)
        if email_or_err in self.donors:
            return False, "A donor with this email already exists."

        # All good - make the donor and store it
        donor = Donor(name=name_or_err, email=email_or_err)
        self.donors[donor.email] = donor
        return True, donor

    def list_donors(self) -> List[Donor]:
        """Get all donors sorted by name (A to Z)."""
        return sorted(self.donors.values(), key=lambda d: d.name.lower())

    def find_donor(self, email: str) -> Optional[Donor]:
        """Find a donor by email. Returns None if no donor matches."""
        ok, cleaned = validate_email(email)
        if not ok:
            return None
        return self.donors.get(cleaned)

    # ---- Campaign methods -----------------------------------------------

    def create_campaign(self, name: str, goal_raw: object) -> Tuple[bool, object]:
        """Make a new campaign. The goal must be a positive number."""
        # Check the name first
        ok_name, name_or_err = validate_campaign_name(name)
        if not ok_name:
            return False, name_or_err

        # Make sure the name is not already used
        if name_or_err in self.campaigns:
            return False, "A campaign with this name already exists."

        # Check the goal is a positive number
        ok_goal, goal_or_err = validate_goal(goal_raw)
        if not ok_goal:
            return False, goal_or_err

        # All good - make the campaign and store it
        campaign = Campaign(name=name_or_err, goal=float(goal_or_err))
        self.campaigns[campaign.name] = campaign
        return True, campaign

    def list_campaigns(self) -> List[Campaign]:
        """Get all campaigns in the order they were added."""
        return list(self.campaigns.values())

    def close_campaign(self, name: str) -> Tuple[bool, object]:
        """Close a campaign so it cannot accept more donations."""
        cleaned = (name or "").strip()
        campaign = self.campaigns.get(cleaned)
        if campaign is None:
            return False, "No campaign with that name."
        # Don't close it twice
        if campaign.is_closed:
            return False, "Campaign is already closed."
        campaign.is_closed = True
        return True, campaign

    # ---- Donation methods -----------------------------------------------

    def record_donation(
        self, donor_email: str, campaign_name: str, amount_raw: object
    ) -> Tuple[bool, object]:
        """Record a new donation. Runs all the checks one by one."""
        # Check 1: is the email a real donor?
        ok_email, email_or_err = validate_email(donor_email)
        if not ok_email or email_or_err not in self.donors:
            return False, "Donor not registered."

        # Check 2: does the campaign exist?
        campaign = self.campaigns.get((campaign_name or "").strip())
        if campaign is None:
            return False, "Campaign not found."
        # Check 3: is the campaign still open?
        if campaign.is_closed:
            return False, "Campaign is closed."

        # Check 4: is the amount a valid number > 0 and <= 10000?
        ok_amount, amount_or_err = validate_amount(amount_raw)
        if not ok_amount:
            return False, amount_or_err

        # All checks passed - make the donation
        donation = Donation(
            donor_email=email_or_err,
            campaign_name=campaign.name,
            amount=float(amount_or_err),
        )
        # Just in case the random ID was already used, generate a new one.
        # This is very unlikely but I want to be safe.
        while donation.donation_id in self.donations:
            donation = Donation(
                donor_email=email_or_err,
                campaign_name=campaign.name,
                amount=float(amount_or_err),
            )

        # Save the donation, link it to the donor, and update the campaign total
        self.donations[donation.donation_id] = donation
        self.donors[email_or_err].donations.append(donation.donation_id)
        campaign.raised += donation.amount
        return True, donation

    def donations_for_donor(self, email: str) -> List[Donation]:
        """Get all donations for a donor, in the order they were made."""
        donor = self.find_donor(email)
        if donor is None:
            return []
        return [self.donations[d_id] for d_id in donor.donations if d_id in self.donations]
