"""This is the main file. I run the program by typing: python main.py

It shows a text menu, asks the user what they want to do, and calls
the right method on the DonationService. When the user picks "Save and
Exit" it saves everything to data.json.
"""

import sys
from typing import Callable

from src import reports, storage
from src.donation_service import DonationService


# On Windows the console sometimes can't print special characters like
# ✓ ✗ £ and –. This function tells Python to use UTF-8 so those work.
def _force_utf8_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            # If something goes wrong, just skip it
            pass


# Run the UTF-8 fix right away when the program starts
_force_utf8_stdio()


# ---- Small helpers for printing and asking ---------------------------------

# I print these borders around the menus to make them look nicer
MAIN_BORDER = "=" * 60
SUB_BORDER = "-" * 60


def _ask(prompt: str) -> str:
    """Ask the user a question and return the answer with spaces removed."""
    return input(prompt).strip()


def _pause() -> None:
    """Pause until the user presses Enter."""
    # If the input is piped (like from a test), skip the pause - otherwise
    # the program would get stuck waiting forever.
    if not sys.stdin.isatty():
        return
    try:
        input("\nPress Enter to continue...")
    except EOFError:
        pass


def _print_success(msg: str) -> None:
    # All success messages start with a tick
    print(f"✓ {msg}")


def _print_error(msg: str) -> None:
    # All error messages start with a cross and end with a full stop
    if not msg.endswith("."):
        msg = msg + "."
    print(f"✗ {msg}")


# ---- The menus -------------------------------------------------------------


def _main_menu_screen() -> None:
    # Print the main menu screen
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
    """Show a sub-menu and keep asking until the user picks 'Back'.

    options is a dictionary like {"1": ("label", handler_function), ...}
    If handler_function is None, that option means 'go back'.
    """
    while True:
        print()
        print(f"---  {prompt_text}  ---")
        print()
        # Print each option in order
        for key in sorted(options.keys()):
            label, _ = options[key]
            print(f"  {key}.  {label}")
        # Ask the user what they want
        choice = _ask(f"\n  Enter your choice (1-{len(options)}): ")
        entry = options.get(choice)
        if entry is None:
            _print_error("Invalid choice. Please pick a number from the menu.")
            _pause()
            continue
        _, handler = entry
        # If handler is None, that means 'go back to the main menu'
        if handler is None:
            return
        # Otherwise call the function for that option
        handler()


# ---- Donor menu actions ----------------------------------------------------


def _do_register_donor(service: DonationService) -> Callable[[], None]:
    # I return a function that does the actual work. This way I can
    # pass it into the menu loop and let it call it when needed.
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
        # Print the table header with fixed-width columns so it lines up
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
        # Got the donor - now show their donation history
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
    # Show the Donor Management sub-menu
    _menu_loop(
        "Donor Management",
        {
            "1": ("Register a new donor", _do_register_donor(service)),
            "2": ("List all donors", _do_list_donors(service)),
            "3": ("Look up a donor by email", _do_lookup_donor(service)),
            "4": ("Back to main menu", None),
        },
    )


# ---- Campaign menu actions -------------------------------------------------


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
        # Print the table header
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
    # Show the Campaign Management sub-menu
    _menu_loop(
        "Campaign Management",
        {
            "1": ("Create a new campaign", _do_create_campaign(service)),
            "2": ("List all campaigns", _do_list_campaigns(service)),
            "3": ("Close a campaign", _do_close_campaign(service)),
            "4": ("Back to main menu", None),
        },
    )


# ---- Recording a donation --------------------------------------------------


def _record_donation(service: DonationService) -> None:
    # This is the flow for option 3 in the main menu - asks 3 questions
    # one by one and then tries to record the donation.
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
    # The donation was saved - show the receipt and the updated progress
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


# ---- Reports menu ----------------------------------------------------------


def _reports_menu(service: DonationService) -> None:
    # Show the Reports sub-menu. Each option just prints a report.
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
    # Run the CSV export and show the result
    print()
    msg = reports.export_donations_csv(service)
    print(msg)
    _pause()


# ---- The main loop ---------------------------------------------------------


def main() -> None:
    # Load the saved data when the program starts
    donors, campaigns, donations, warning = storage.load()
    service = DonationService()
    service.donors = donors
    service.campaigns = campaigns
    service.donations = donations

    # If the data file was broken, tell the user before showing the menu
    if warning:
        print()
        _print_error(warning)
        _pause()

    try:
        # Keep showing the main menu forever, until the user picks 6
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
                # Save everything and quit
                storage.save(service.donors, service.campaigns, service.donations)
                print()
                print("Data saved. Goodbye!")
                return
            else:
                _print_error("Invalid choice. Please pick a number from 1 to 6.")
                _pause()
    except KeyboardInterrupt:
        # If the user presses Ctrl+C, still save before exiting
        storage.save(service.donors, service.campaigns, service.donations)
        print("\n\nInterrupted. Data saved. Goodbye!")
    except EOFError:
        # If the input ends suddenly (no terminal), also save and exit
        storage.save(service.donors, service.campaigns, service.donations)
        print("\n\nInput stream closed. Data saved. Goodbye!")


# Only run main() if this file is executed directly (not imported)
if __name__ == "__main__":
    main()
