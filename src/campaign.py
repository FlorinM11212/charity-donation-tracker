"""Campaign class.

This file holds the Campaign class. A campaign is a fundraising drive
with a name and a money goal. When a campaign is closed it stops
accepting new donations.
"""

from dataclasses import dataclass, field
from datetime import date


@dataclass
class Campaign:
    """A fundraising campaign."""

    # Campaign name (must be unique)
    name: str
    # Target amount in GBP (must be a positive number)
    goal: float
    # How much was raised so far - starts at 0
    raised: float = 0.0
    # True if the campaign no longer accepts donations
    is_closed: bool = False
    # The date the campaign was created
    created_on: str = field(default_factory=lambda: date.today().isoformat())

    def progress_percent(self) -> float:
        # This calculates how close we are to the goal as a percentage.
        # The if-check is just to be safe against division by zero.
        if self.goal <= 0:
            return 0.0
        return (self.raised / self.goal) * 100.0

    def to_dict(self) -> dict:
        # This turns the campaign into a dictionary so I can save it to JSON.
        return {
            "name": self.name,
            "goal": self.goal,
            "raised": self.raised,
            "is_closed": self.is_closed,
            "created_on": self.created_on,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Campaign":
        # This builds a campaign back from a dictionary loaded from JSON.
        return cls(
            name=data["name"],
            goal=float(data["goal"]),
            raised=float(data.get("raised", 0.0)),
            is_closed=bool(data.get("is_closed", False)),
            created_on=data.get("created_on", date.today().isoformat()),
        )
