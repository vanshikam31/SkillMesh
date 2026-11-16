"""Check your email settings.  Run from the project root (venv active):

    python backend/test_email.py your-email@gmail.com

It sends one test email using the SMTP_* values in backend/.env and tells you what is wrong if it fails."""
import os
import smtplib
import sys

sys.path.insert(0, os.path.dirname(__file__))

from app import config  # noqa: E402
from app.emailer import build_message, deliver, smtp_configured  # noqa: E402

if len(sys.argv) < 2:
    sys.exit(__doc__)

print(f"SMTP_HOST={config.SMTP_HOST or '(empty)'}  SMTP_PORT={config.SMTP_PORT}  SMTP_USER={config.SMTP_USER or '(empty)'}  "
      f"SMTP_PASSWORD={'set (' + str(len(config.SMTP_PASSWORD)) + ' characters)' if config.SMTP_PASSWORD else '(empty)'}")
if not smtp_configured():
    sys.exit("\nSMTP is not set up. Open backend/.env and fill SMTP_HOST, SMTP_USER and SMTP_PASSWORD (no # at the start of the lines).")
try:
    deliver(build_message(sys.argv[1], config.FRONTEND_URL + "/reset-password?token=TEST"))
    print(f"\nSUCCESS: test email sent to {sys.argv[1]}. Check the inbox and the Spam folder.")
except smtplib.SMTPAuthenticationError as e:
    print(f"\nLOGIN FAILED: {e}\nFix: Gmail does not accept your normal password. Turn on 2-Step Verification, create an App Password at "
          "https://myaccount.google.com/apppasswords and paste those 16 letters (without spaces) as SMTP_PASSWORD.")
except Exception as e:  # noqa: BLE001
    print(f"\nFAILED: {type(e).__name__}: {e}\nCheck SMTP_HOST, SMTP_PORT (587) and your internet connection.")
