"""Campaign domain model.

A Campaign is a named fundraising drive with a positive monetary goal.
Donations are attributed to a campaign by name, and a campaign can be
closed to stop accepting further donations.
"""

from dataclasses import dataclass, field
from datetime import date


@dataclass
class Campaign:
    """Plain data class for a fundraising campaign.

    Attributes:
        name: Unique campaign name (case-sensitive as displayed).
        goal: Target amount in GBP. Must be > 0 (enforced by validators).
        raised: Running total raised; starts at 0 and grows with donations.
        is_closed: True once the campaign no longer accepts donations.
        created_on: ISO date (YYYY-MM-DD) the campaign was created.
    """

    name: str
    goal: float
    raised: float = 0.0
    is_closed: bool = False
    created_on: str = field(default_factory=lambda: date.today().isoformat())

    def progress_percent(self) -> float:
        # Avoid division-by-zero: validators reject goal <= 0, but be defensive.
        if self.goal <= 0:
            return 0.0
        return (self.raised / self.goal) * 100.0

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "goal": self.goal,
            "raised": self.raised,
            "is_closed": self.is_closed,
            "created_on": self.created_on,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Campaign":
        return cls(
            name=data["name"],
            goal=float(data["goal"]),
            raised=float(data.get("raised", 0.0)),
            is_closed=bool(data.get("is_closed", False)),
            created_on=data.get("created_on", date.today().isoformat()),
        )
