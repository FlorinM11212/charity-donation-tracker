"""Persistence layer: load and save the application state to a JSON file.

The format is a single object with three top-level lists: donors, campaigns,
and donations. If the file is corrupted on load, it is renamed out of the
way (data.json.broken.<timestamp>) so the program can start cleanly without
losing the original for forensic inspection.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Tuple

from src.donor import Donor
from src.campaign import Campaign
from src.donation import Donation


DEFAULT_DATA_FILE = "data.json"


def load(path: str = DEFAULT_DATA_FILE) -> Tuple[Dict[str, Donor], Dict[str, Campaign], Dict[str, Donation], str]:
    """Load donors, campaigns, donations from ``path``.

    Returns four values: (donors, campaigns, donations, warning).
    ``donors`` is keyed by lowercased email; ``campaigns`` by name;
    ``donations`` by 6-char receipt id. ``warning`` is "" on a clean load
    or a human-readable message when the file was missing or corrupted
    (so main.py can surface it to the user).
    """
    if not os.path.exists(path):
        # First run: empty world, no warning.
        return {}, {}, {}, ""

    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except (json.JSONDecodeError, OSError):
        # Corrupted JSON or unreadable file: move it aside and start clean
        # so the user is not stuck unable to launch the app.
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
    """Write all state atomically to ``path``.

    Writes to a temp sibling first, then renames, so a crash mid-write
    cannot leave the data file half-written and corrupt.
    """
    payload = {
        "donors": [d.to_dict() for d in donors.values()],
        "campaigns": [c.to_dict() for c in campaigns.values()],
        "donations": [d.to_dict() for d in donations.values()],
    }
    tmp_path = f"{path}.tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    os.replace(tmp_path, path)
