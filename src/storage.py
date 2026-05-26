"""Save and load the program data to a JSON file.

I keep everything in one file called data.json. It has three lists
inside: donors, campaigns and donations. If the file gets broken,
I rename it and start fresh so the program does not crash.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Tuple

from src.donor import Donor
from src.campaign import Campaign
from src.donation import Donation


# This is the name of the file I save the data into.
DEFAULT_DATA_FILE = "data.json"


def load(path: str = DEFAULT_DATA_FILE) -> Tuple[Dict[str, Donor], Dict[str, Campaign], Dict[str, Donation], str]:
    """Load the data from the JSON file.

    Returns 4 things: donors, campaigns, donations, and a warning.
    The warning is an empty string if everything was fine, or a message
    if the file was broken.
    """
    # If the file does not exist yet, this is the first run.
    if not os.path.exists(path):
        return {}, {}, {}, ""

    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except (json.JSONDecodeError, OSError):
        # The file is broken or can't be read. I rename it so I can keep
        # a copy for later and then start with empty data.
        backup = f"{path}.broken.{datetime.now().strftime('%Y%m%d%H%M%S')}"
        try:
            os.rename(path, backup)
        except OSError:
            backup = "<could not rename>"
        return (
            {},
            {},
            {},
            f"data.json was corrupted; moved to {backup} and starting fresh.",
        )

    # Turn each list from the JSON back into my classes.
    # I use the email/name/id as the key so I can find things fast.
    donors = {d["email"].lower(): Donor.from_dict(d) for d in raw.get("donors", [])}
    campaigns = {c["name"]: Campaign.from_dict(c) for c in raw.get("campaigns", [])}
    donations = {
        rec["donation_id"]: Donation.from_dict(rec) for rec in raw.get("donations", [])
    }
    return donors, campaigns, donations, ""


def save(
    donors: Dict[str, Donor],
    campaigns: Dict[str, Campaign],
    donations: Dict[str, Donation],
    path: str = DEFAULT_DATA_FILE,
) -> None:
    """Save all the data to the JSON file.

    I write to a temp file first and then rename it, so if the program
    crashes in the middle the real file is not broken.
    """
    # Build the dictionary I want to save
    payload = {
        "donors": [d.to_dict() for d in donors.values()],
        "campaigns": [c.to_dict() for c in campaigns.values()],
        "donations": [d.to_dict() for d in donations.values()],
    }
    # First write to a temp file
    tmp_path = f"{path}.tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    # Then rename the temp file to the real name (this is atomic on Windows)
    os.replace(tmp_path, path)
