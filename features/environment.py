"""behave hooks. These run before and after each test scenario.

Every scenario gets a brand new DonationService so that data from one
test does not leak into the next one.
"""

from src.donation_service import DonationService


def before_scenario(context, scenario):
    # This runs before every scenario.
    # I make a fresh service so each scenario starts with no data.
    context.service = DonationService()
    # These are used by the Then steps to check what happened.
    context.last_ok = None
    context.last_payload = None


def after_all(context):
    # This runs once at the end of all tests.
    # I don't need to clean anything because there is no database.
    return
