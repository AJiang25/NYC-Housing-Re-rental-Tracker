import json
import os
import re
import smtplib
from datetime import datetime
from email.mime.text import MIMEText

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

load_dotenv()

EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_TO = os.getenv("EMAIL_TO")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

if not all([EMAIL_FROM, EMAIL_TO, EMAIL_PASSWORD]):
    raise RuntimeError(
        "Missing EMAIL_FROM, EMAIL_TO, or EMAIL_PASSWORD in .env"
    )

AIRTABLE_URL = (
    "https://airtable.com/appsseXTOVx59HC0W/pagcVengefPFQvMZC/form"
)

STATE_FILE = "units.json"

PROJECT_COLUMN_ID = "fldoycl2AHO4EdprG"


# -----------------------------------------------------------------------------
# Utility Functions
# -----------------------------------------------------------------------------

def extract_price(unit):
    """Extract the rental price from a listing string."""

    match = re.search(r"\$(\d+(?:\.\d+)?)", unit)

    if match:
        return float(match.group(1))

    return None


def load_previous_units():
    """Load the previous snapshot."""

    try:
        with open(STATE_FILE, "r") as f:
            return set(json.load(f))

    except FileNotFoundError:
        return set()


def save_units(units):
    """Save the latest snapshot."""

    with open(STATE_FILE, "w") as f:
        json.dump(sorted(list(units)), f, indent=2)


def send_email(subject, body):
    """Send an email notification."""

    msg = MIMEText(body)

    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(
            EMAIL_FROM,
            EMAIL_PASSWORD,
        )

        server.send_message(msg)


# -----------------------------------------------------------------------------
# Airtable
# -----------------------------------------------------------------------------

def get_units():
    """Fetch all available units from the Airtable form."""

    units = set()

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)

        try:

            page = browser.new_page()

            def capture(response):

                if "listRowsMatchingNameAndFilters" not in response.url:
                    return

                data = response.json()

                rows = data["data"]["rowResults"]

                for row in rows:

                    value = (
                        row
                        .get("cellValuesByColumnId", {})
                        .get(PROJECT_COLUMN_ID)
                    )

                    if value:
                        units.add(value)

            page.on("response", capture)

            page.goto(
                AIRTABLE_URL,
                wait_until="networkidle"
            )

            with page.expect_response(
                lambda r: "listRowsMatchingNameAndFilters" in r.url
            ):
                page.get_by_text(
                    "Add unit",
                    exact=True
                ).click()

        finally:
            browser.close()

    return units


# -----------------------------------------------------------------------------
# Main Logic
# -----------------------------------------------------------------------------

def check_for_updates():

    previous = load_previous_units()
    current = get_units()

    new_units = current - previous
    removed_units = previous - current

    affordable_units = []

    if new_units:

        print("\nNEW UNITS:")

        for unit in sorted(new_units):

            print("+", unit)

            price = extract_price(unit)

            if price is not None and price < 3000:
                affordable_units.append(unit)

    if affordable_units:

        email_body = (
            "New apartments under $3000 detected!\n"
            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            + "\n".join(f"• {unit}" for unit in affordable_units)
        )

        send_email(
            "🏠 New Affordable Apartment Found",
            email_body,
        )

        print(
            f"\nEmail sent for {len(affordable_units)} affordable apartment(s)."
        )

    if removed_units:

        print("\nREMOVED UNITS:")

        for unit in sorted(removed_units):
            print("-", unit)

    if not new_units and not removed_units:
        print("No changes.")

    save_units(current)


# -----------------------------------------------------------------------------
# Entry Point
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    check_for_updates()