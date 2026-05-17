"""behave hooks. Each scenario gets its own fresh DonationService so that
state from a previous scenario can never leak in and pass/fail another.
"""

from src.donation_service import DonationService


def before_scenario(context, scenario):
    # Fresh service per scenario keeps each Given/When/Then independent.
    context.service = DonationService()
    # Slots used by Then steps to assert success/failure and the message.
    context.last_ok = None
    context.last_payload = None


def after_all(context):
    # No global teardown needed (no DB, no temp files), but the hook is
    # here as the spec lists it under features/environment.py.
    return
