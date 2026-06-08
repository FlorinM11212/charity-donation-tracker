"""Donation class.

This file holds the Donation class. A donation is one payment from a
donor to a campaign. Each donation gets a short 6-character receipt
ID so I can tell the donor "your receipt is XXXXXX".
"""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


def _new_receipt_id() -> str:
    # This makes a random 6-character receipt ID.
    # I take the first 6 characters of a uuid4 and make them uppercase.
    return uuid4().hex[:6].upper()


@dataclass
class Donation:
    """One donation made by a donor to a campaign."""

    # Email of the donor who made the donation
    donor_email: str
    # Name of the campaign the donation goes to
    campaign_name: str
    # How much money was donated, in GBP
    amount: float
    # The 6-character receipt ID (generated automatically)
    donation_id: str = field(default_factory=_new_receipt_id)
    # When the donation was recorded
    timestamp: str = field(
        # I cut off the microseconds so the time prints nicely in reports.
        default_factory=lambda: datetime.now().replace(microsecond=0).isoformat(sep=" ")
    )

    def to_dict(self) -> dict:
        # This turns the donation into a dictionary so I can save it to JSON.
        return {
            "donation_id": self.donation_id,
            "donor_email": self.donor_email,
            "campaign_name": self.campaign_name,
            "amount": self.amount,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Donation":
        # This builds a donation back from a dictionary loaded from JSON.
        return cls(
            donor_email=data["donor_email"],
            campaign_name=data["campaign_name"],
            amount=float(data["amount"]),
            donation_id=data["donation_id"],
            timestamp=data["timestamp"],
        )
