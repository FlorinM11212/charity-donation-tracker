"""Donor class.

This file holds the Donor class. A donor is a person who registered
in the system. I use the email as the unique ID.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import List


@dataclass
class Donor:
    """A registered donor."""

    # The donor's full name
    name: str
    # The donor's email - used as the unique ID
    email: str
    # List of donation IDs this donor has made
    donations: List[str] = field(default_factory=list)
    # The date the donor was added (today by default)
    registered_on: str = field(default_factory=lambda: date.today().isoformat())

    def to_dict(self) -> dict:
        # This turns the donor into a dictionary so I can save it to JSON.
        return {
            "name": self.name,
            "email": self.email,
            "donations": list(self.donations),
            "registered_on": self.registered_on,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Donor":
        # This builds a donor back from a dictionary loaded from JSON.
        return cls(
            name=data["name"],
            email=data["email"],
            donations=list(data.get("donations", [])),
            registered_on=data.get("registered_on", date.today().isoformat()),
        )
