"""The reports the user can see in the menu, plus the CSV export.

Each function builds a string with the report text and returns it.
The CSV export writes a file and returns a confirmation message.
"""

import csv
from typing import List, Tuple

from src.donation_service import DonationService


# The name of the file the CSV export writes to.
CSV_EXPORT_PATH = "donations_export.csv"


def total_donations_summary(service: DonationService) -> str:
    """Build the 'total donations' report."""
    # Count things up
    n_donations = len(service.donations)
    total_raised = sum(d.amount for d in service.donations.values())
    active = sum(1 for c in service.campaigns.values() if not c.is_closed)
    closed = sum(1 for c in service.campaigns.values() if c.is_closed)
    n_donors = len(service.donors)
    # Build the lines of the report
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
    """Build the 'top k donors' report. By default it shows the top 3."""
    # For every donor, work out how much they gave in total
    totals: List[Tuple[str, float, int]] = []
    for donor in service.donors.values():
        donor_total = sum(
            service.donations[d_id].amount
            for d_id in donor.donations
            if d_id in service.donations
        )
        # Only count donors who actually gave something
        if donor_total > 0:
            totals.append((donor.name, donor_total, len(donor.donations)))

    # Sort from biggest total to smallest, then keep only the top k
    totals.sort(key=lambda row: row[1], reverse=True)
    top_k = totals[:k]

    # Handle the case where nobody has donated yet
    if not top_k:
        return "---  Top 3 Donors  ---\n\n  (no donations recorded yet)"

    # Build the lines
    lines = ["---  Top 3 Donors  ---", ""]
    for i, (name, amount, count) in enumerate(top_k, start=1):
        # Lining up the columns so amounts are nicely on top of each other
        lines.append(
            f"  {i}.  {name:<18} £{amount:>9,.2f}   {count} donation"
            f"{'s' if count != 1 else ''}"
        )
    return "\n".join(lines)


def campaign_progress(service: DonationService) -> str:
    """Build the 'campaign progress' report with ASCII bar charts."""
    if not service.campaigns:
        return "---  Campaign Progress  ---\n\n  (no campaigns yet)"

    # The bar is 18 characters wide
    bar_width = 18
    lines = ["---  Campaign Progress  ---", ""]
    for campaign in service.campaigns.values():
        # Cap at 100% in case people donated more than the goal
        pct = min(campaign.progress_percent(), 100.0)
        # Work out how many # to draw, the rest are dots
        filled = int(round((pct / 100.0) * bar_width))
        bar = "#" * filled + "." * (bar_width - filled)
        # Show CLOSED if the campaign is closed
        status = "  CLOSED" if campaign.is_closed else ""
        lines.append(
            f"  {campaign.name:<18} [{bar}]  {pct:5.1f}%{status}"
        )
    return "\n".join(lines)


def export_donations_csv(service: DonationService, path: str = CSV_EXPORT_PATH) -> str:
    """Export every donation to a CSV file."""
    # These are the column headers in the CSV
    headers = [
        "donation_id",
        "donor_email",
        "donor_name",
        "campaign",
        "amount",
        "timestamp",
    ]
    # Open the file and write the rows
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for donation in service.donations.values():
            # Look up the donor's name from the email
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
