"""Donor domain model.

A Donor represents a person who has registered with the charity. Donors are
identified uniquely by their (lowercased) email address. Each donor keeps a
list of donation IDs that point at Donation records owned by the service.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import List


@dataclass
class Donor:
    """Plain data class for a registered donor.

    Attributes:
        name: Donor's full name (already trimmed by the caller).
        email: Lowercased, unique identifier.
        donations: Receipt IDs of donations this donor has made.
        registered_on: ISO date (YYYY-MM-DD) of registration.
    """

    name: str
    email: str
    donations: List[str] = field(default_factory=list)
    registered_on: str = field(default_factory=lambda: date.today().isoformat())

    def to_dict(self) -> dict:
        # Serialise to a plain dict so storage.py can dump it as JSON.
        return {
            "name": self.name,
            "email": self.email,
            "donations": list(self.donations),
            "registered_on": self.registered_on,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Donor":
        # Reconstruct a Donor from JSON. Default donations to [] if missing
        # so older data files (without the field) still load cleanly.
        return cls(
            name=data["name"],
            email=data["email"],
            donations=list(data.get("donations", [])),
            registered_on=data.get("registered_on", date.today().isoformat()),
        )
