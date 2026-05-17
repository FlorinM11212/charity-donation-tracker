"""Donation domain model.

A Donation is a single contribution from a Donor to a Campaign. It carries
a short receipt ID (6 hex chars derived from uuid4) so the administrator
can read it back to a donor over the phone.
"""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


def _new_receipt_id() -> str:
    # uuid4().hex is 32 chars; first 6 uppercased gives a short, readable receipt.
    # Collisions within a single charity's lifetime are vanishingly unlikely.
    return uuid4().hex[:6].upper()


@dataclass
class Donation:
    """Plain data class for one donation.

    Attributes:
        donation_id: 6-character uppercase hex receipt ID.
        donor_email: Foreign key to Donor.email (lowercased).
        campaign_name: Foreign key to Campaign.name.
        amount: GBP amount; validators enforce 0 < amount <= 10000.
        timestamp: ISO datetime to the second.
    """

    donor_email: str
    campaign_name: str
    amount: float
    donation_id: str = field(default_factory=_new_receipt_id)
    timestamp: str = field(
        # Trim microseconds so the timestamp prints nicely in reports.
        default_factory=lambda: datetime.now().replace(microsecond=0).isoformat(sep=" ")
    )

    def to_dict(self) -> dict:
        return {
            "donation_id": self.donation_id,
            "donor_email": self.donor_email,
            "campaign_name": self.campaign_name,
            "amount": self.amount,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Donation":
        return cls(
            donor_email=data["donor_email"],
            campaign_name=data["campaign_name"],
            amount=float(data["amount"]),
            donation_id=data["donation_id"],
            timestamp=data["timestamp"],
        )
