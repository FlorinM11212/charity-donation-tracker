"""Reporting: aggregate views over the service state and CSV export.

Functions in this module return strings (or, for export, write a file and
return a status string). Keeping them pure makes them straightforward to
unit-test without a full menu loop driving them.
"""

import csv
from typing import List, Tuple

from src.donation_service import DonationService


CSV_EXPORT_PATH = "donations_export.csv"


def total_donations_summary(service: DonationService) -> str:
    """FR-4.1: how many donations, total raised, and counts by category."""
    n_donations = len(service.donations)
    total_raised = sum(d.amount for d in service.donations.values())
    active = sum(1 for c in service.campaigns.values() if not c.is_closed)
    closed = sum(1 for c in service.campaigns.values() if c.is_closed)
    n_donors = len(service.donors)
    lines = [
        "---  Total Donations Summary  ---",
        "",
        f"  Number of donations : {n_donations}",
        f"  Total raised        : £{total_raised:,.2f}",
        f"  Active campaigns    : {active}",
        f"  Closed campaigns    : {closed}",
        f"  Registered donors   : {n_donors}",
    ]
    return "\n".join(lines)


def top_donors(service: DonationService, k: int = 3) -> str:
    """FR-4.2: top ``k`` donors by total contribution."""
    # Pre-compute per-donor totals once instead of per-comparator call.
    totals: List[Tuple[str, float, int]] = []
    for donor in service.donors.values():
        donor_total = sum(
            service.donations[d_id].amount
            for d_id in donor.donations
            if d_id in service.donations
        )
        if donor_total > 0:
            totals.append((donor.name, donor_total, len(donor.donations)))

    totals.sort(key=lambda row: row[1], reverse=True)
    top_k = totals[:k]

    if not top_k:
        return "---  Top 3 Donors  ---\n\n  (no donations recorded yet)"

    lines = ["---  Top 3 Donors  ---", ""]
    for i, (name, amount, count) in enumerate(top_k, start=1):
        # Padded name (18) plus right-aligned amount keeps the columns tidy
        # even when one donor has given much more than the others.
        lines.append(
            f"  {i}.  {name:<18} £{amount:>9,.2f}   {count} donation"
            f"{'s' if count != 1 else ''}"
        )
    return "\n".join(lines)


def campaign_progress(service: DonationService) -> str:
    """FR-4.3: ascii bar chart of progress per campaign."""
    if not service.campaigns:
        return "---  Campaign Progress  ---\n\n  (no campaigns yet)"

    bar_width = 18  # characters reserved for the [###...] segment
    lines = ["---  Campaign Progress  ---", ""]
    for campaign in service.campaigns.values():
        pct = min(campaign.progress_percent(), 100.0)
        filled = int(round((pct / 100.0) * bar_width))
        bar = "#" * filled + "." * (bar_width - filled)
        status = "  CLOSED" if campaign.is_closed else ""
        lines.append(
            f"  {campaign.name:<18} [{bar}]  {pct:5.1f}%{status}"
        )
    return "\n".join(lines)


def export_donations_csv(service: DonationService, path: str = CSV_EXPORT_PATH) -> str:
    """FR-4.4: dump every donation to a CSV. Returns a confirmation string.

    The donor_name column is denormalised in (looked up via donor_email)
    so the CSV is useful even if opened separately from the program.
    """
    headers = [
        "donation_id",
        "donor_email",
        "donor_name",
        "campaign",
        "amount",
        "timestamp",
    ]
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for donation in service.donations.values():
            donor = service.donors.get(donation.donor_email)
            donor_name = donor.name if donor else ""
            writer.writerow(
                [
                    donation.donation_id,
                    donation.donor_email,
                    donor_name,
                    donation.campaign_name,
                    f"{donation.amount:.2f}",
                    donation.timestamp,
                ]
            )
    return f"✓ Exported {len(service.donations)} donations to {path}"
