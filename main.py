"""Entry point for the Charity Donation Tracker.

Runs the text menu loop, dispatches user choices to the DonationService,
and persists state via storage.save() on a clean exit. Every input read
is wrapped so a typo never crashes the program — bad input prints a
clear message and re-prompts.
"""

from typing import Callable

from src import reports, storage
from src.donation_service import DonationService


# ---- Small console helpers -------------------------------------------------

# Borders defined once so the visual style is consistent everywhere.
MAIN_BORDER = "=" * 60
SUB_BORDER = "-" * 60


def _ask(prompt: str) -> str:
    """Read a line from stdin. Strips trailing newline and surrounding spaces.

    Wrapped in try/except so EOFError (e.g. piped input ending) returns "" and
    KeyboardInterrupt bubbles up to the main loop where we save and exit.
    """
    try:
        return input(prompt).strip()
    except EOFError:
        return ""


def _pause() -> None:
    """Standard 'press Enter' pause used at the end of every action."""
    try:
        input("\nPress Enter to continue...")
    except EOFError:
        # No interactive stdin (e.g. tests piping input): just continue.
        pass


def _print_success(msg: str) -> None:
    print(f"✓ {msg}")


def _print_error(msg: str) -> None:
    # Spec rule: error messages start with "✗ " and end with a full stop.
    if not msg.endswith("."):
        msg = msg + "."
    print(f"✗ {msg}")


# ---- Main and sub-menus ----------------------------------------------------


def _main_menu_screen() -> None:
    print()
    print(MAIN_BORDER)
    print("        CHARITY DONATION TRACKER  –  Main Menu")
    print(MAIN_BORDER)
    print()
    print("  1.  Donor Management")
    print("  2.  Campaign Management")
    print("  3.  Record a Donation")
    print("  4.  Reports")
    print("  5.  Export Donations to CSV")
    print("  6.  Save and Exit")
    print(SUB_BORDER)


def _menu_loop(prompt_text: str, options: dict) -> None:
    """Generic loop: print options, dispatch, repeat until "back".

    ``options`` maps the choice string ('1', '2', ...) to either:
      * a (label, callable) pair for an action, or
      * (label, None) for the back-out entry, which exits the loop.
    """
    while True:
        print()
        print(f"---  {prompt_text}  ---")
        print()
        for key in sorted(options.keys()):
            label, _ = options[key]
            print(f"  {key}.  {label}")
        choice = _ask(f"\n  Enter your choice (1-{len(options)}): ")
        entry = options.get(choice)
        if entry is None:
            _print_error("Invalid choice. Please pick a number from the menu.")
            _pause()
            continue
        _, handler = entry
        if handler is None:
            return
        handler()


# ---- Donor handlers --------------------------------------------------------


def _do_register_donor(service: DonationService) -> Callable[[], None]:
    def handler() -> None:
        print()
        name = _ask("  Full name : ")
        email = _ask("  Email     : ")
        ok, payload = service.register_donor(name, email)
        if ok:
            _print_success(f"Donor registered: {payload.name} <{payload.email}>")
        else:
            _print_error(payload)
        _pause()

    return handler


def _do_list_donors(service: DonationService) -> Callable[[], None]:
    def handler() -> None:
        donors = service.list_donors()
        print()
        if not donors:
            print("No donors registered yet.")
            _pause()
            return
        # Fixed-width columns so the table lines up across rows.
        print(f"  {'Name':<23} {'Email':<27} Donations")
        print(f"  {'-' * 23} {'-' * 27} {'-' * 9}")
        for donor in donors:
            print(
                f"  {donor.name:<23} {donor.email:<27} {len(donor.donations):>9}"
            )
        print(f"\n  (Total: {len(donors)} donor{'s' if len(donors) != 1 else ''})")
        _pause()

    return handler


def _do_lookup_donor(service: DonationService) -> Callable[[], None]:
    def handler() -> None:
        print()
        email = _ask("  Email : ")
        donor = service.find_donor(email)
        if donor is None:
            _print_error("No donor found with that email.")
            _pause()
            return
        donations = service.donations_for_donor(donor.email)
        total = sum(d.amount for d in donations)
        print()
        print(f"  Donor         : {donor.name}")
        print(f"  Email         : {donor.email}")
        print(f"  Registered on : {donor.registered_on}")
        print(f"  Donation history ({len(donations)}):")
        if not donations:
            print("    (no donations yet)")
        else:
            for d in donations:
                print(
                    f"    - {d.donation_id}  £{d.amount:>7,.2f}   "
                    f"{d.campaign_name:<18} {d.timestamp}"
                )
        print(f"\n  Total contributed: £{total:,.2f}")
        _pause()

    return handler


def _donor_menu(service: DonationService) -> None:
    _menu_loop(
        "Donor Management",
        {
            "1": ("Register a new donor", _do_register_donor(service)),
            "2": ("List all donors", _do_list_donors(service)),
            "3": ("Look up a donor by email", _do_lookup_donor(service)),
            "4": ("Back to main menu", None),
        },
    )


# ---- Campaign handlers -----------------------------------------------------


def _do_create_campaign(service: DonationService) -> Callable[[], None]:
    def handler() -> None:
        print()
        name = _ask("  Campaign name : ")
        goal = _ask("  Goal in GBP   : ")
        ok, payload = service.create_campaign(name, goal)
        if ok:
            _print_success(
                f"Campaign created: {payload.name} (goal: £{payload.goal:,.2f})"
            )
        else:
            _print_error(payload)
        _pause()

    return handler


def _do_list_campaigns(service: DonationService) -> Callable[[], None]:
    def handler() -> None:
        campaigns = service.list_campaigns()
        print()
        if not campaigns:
            print("No campaigns yet.")
            _pause()
            return
        print(
            f"  {'Name':<18} {'Goal':>10} {'Raised':>10} {'Progress':>9}  Status"
        )
        print(f"  {'-' * 18} {'-' * 10} {'-' * 10} {'-' * 8}  ------")
        for c in campaigns:
            status = "Closed" if c.is_closed else "Open"
            print(
                f"  {c.name:<18} £{c.goal:>9,.2f} £{c.raised:>9,.2f}"
                f" {c.progress_percent():>7.1f}%  {status}"
            )
        _pause()

    return handler


def _do_close_campaign(service: DonationService) -> Callable[[], None]:
    def handler() -> None:
        print()
        name = _ask("  Campaign name : ")
        ok, payload = service.close_campaign(name)
        if ok:
            _print_success(f"Campaign closed: {payload.name}")
        else:
            _print_error(payload)
        _pause()

    return handler


def _campaign_menu(service: DonationService) -> None:
    _menu_loop(
        "Campaign Management",
        {
            "1": ("Create a new campaign", _do_create_campaign(service)),
            "2": ("List all campaigns", _do_list_campaigns(service)),
            "3": ("Close a campaign", _do_close_campaign(service)),
            "4": ("Back to main menu", None),
        },
    )


# ---- Donation flow ---------------------------------------------------------


def _record_donation(service: DonationService) -> None:
    print()
    print("---  Record a Donation  ---")
    print()
    email = _ask("  Donor email   : ")
    campaign_name = _ask("  Campaign name : ")
    amount = _ask("  Amount in GBP : ")
    ok, payload = service.record_donation(email, campaign_name, amount)
    if not ok:
        _print_error(payload)
        _pause()
        return
    donation = payload
    donor = service.donors[donation.donor_email]
    campaign = service.campaigns[donation.campaign_name]
    print()
    _print_success("Donation recorded.")
    print(f"  Receipt: {donation.donation_id}")
    print(
        f"  {donor.name} donated £{donation.amount:,.2f} to {campaign.name}."
    )
    print(
        f"  Campaign progress: {campaign.progress_percent():.1f}% of "
        f"£{campaign.goal:,.2f}"
    )
    _pause()


# ---- Reports ---------------------------------------------------------------


def _reports_menu(service: DonationService) -> None:
    _menu_loop(
        "Reports",
        {
            "1": (
                "Total donations summary",
                lambda: (print("\n" + reports.total_donations_summary(service)), _pause()),
            ),
            "2": (
                "Top 3 donors",
                lambda: (print("\n" + reports.top_donors(service)), _pause()),
            ),
            "3": (
                "Campaign progress",
                lambda: (print("\n" + reports.campaign_progress(service)), _pause()),
            ),
            "4": ("Back to main menu", None),
        },
    )


def _export_csv(service: DonationService) -> None:
    print()
    msg = reports.export_donations_csv(service)
    print(msg)
    _pause()


# ---- Main loop -------------------------------------------------------------


def main() -> None:
    donors, campaigns, donations, warning = storage.load()
    service = DonationService()
    service.donors = donors
    service.campaigns = campaigns
    service.donations = donations

    if warning:
        # Surface storage problems on launch, before the menu, so the user
        # knows why the database looks empty.
        print()
        _print_error(warning)
        _pause()

    try:
        while True:
            _main_menu_screen()
            choice = _ask("  Enter your choice (1-6): ")
            if choice == "1":
                _donor_menu(service)
            elif choice == "2":
                _campaign_menu(service)
            elif choice == "3":
                _record_donation(service)
            elif choice == "4":
                _reports_menu(service)
            elif choice == "5":
                _export_csv(service)
            elif choice == "6":
                storage.save(service.donors, service.campaigns, service.donations)
                print()
                print("Data saved. Goodbye!")
                return
            else:
                _print_error("Invalid choice. Please pick a number from 1 to 6.")
                _pause()
    except KeyboardInterrupt:
        # Ctrl+C anywhere: still save before exiting (FR-5.3 / section 9).
        storage.save(service.donors, service.campaigns, service.donations)
        print("\n\nInterrupted. Data saved. Goodbye!")


if __name__ == "__main__":
    main()
