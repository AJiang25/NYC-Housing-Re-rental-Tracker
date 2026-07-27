import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_TO = os.getenv("EMAIL_TO")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


def send_email(subject, body):

    msg = MIMEText(body)

    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO

    with smtplib.SMTP_SSL(
        "smtp.gmail.com",
        465
    ) as server:

        server.login(
            EMAIL_FROM,
            EMAIL_PASSWORD
        )

        server.send_message(msg)


if __name__ == "__main__":

    print("Testing email...")
    print("From:", EMAIL_FROM)
    print("To:", EMAIL_TO)

    send_email(
        "Airtable Tracker Test",
        """
This is a test email from the Reside Tracker.

If you received this, email notifications are working.
"""
    )

    print("Email sent!")