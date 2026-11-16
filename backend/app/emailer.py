"""Sends the password reset email through any SMTP server (for example Gmail with an App Password)."""
import logging
import smtplib
import ssl
from email.message import EmailMessage

from . import config

log = logging.getLogger("uvicorn.error")


def smtp_configured() -> bool:
    return bool(config.SMTP_HOST and config.SMTP_USER and config.SMTP_PASSWORD)


def build_message(to: str, link: str) -> EmailMessage:
    msg = EmailMessage()
    msg["Subject"] = "Reset your SkillMesh password"
    msg["From"] = config.SMTP_FROM or config.SMTP_USER
    msg["To"] = to
    msg.set_content(
        f"Hi,\n\nUse this link to set a new password. It works for {config.RESET_TOKEN_MINUTES} minutes and only once:\n{link}\n\n"
        "If you did not ask for this, you can ignore this email.\n\n- SkillMesh"
    )
    return msg


def deliver(msg: EmailMessage) -> None:
    """Sends the message and raises an error if anything goes wrong (used by test_email.py)."""
    ctx = ssl.create_default_context()
    if config.SMTP_PORT == 465:                                   # SSL from the start
        with smtplib.SMTP_SSL(config.SMTP_HOST, config.SMTP_PORT, timeout=20, context=ctx) as server:
            server.login(config.SMTP_USER, config.SMTP_PASSWORD)
            server.send_message(msg)
    else:                                                         # port 587: start plain, then upgrade with STARTTLS
        with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT, timeout=20) as server:
            server.ehlo()
            server.starttls(context=ctx)
            server.ehlo()
            server.login(config.SMTP_USER, config.SMTP_PASSWORD)
            server.send_message(msg)


def send_reset_email(to: str, link: str) -> None:
    """Runs in the background after the API answered, so it must never crash: it writes the problem to the backend terminal instead."""
    try:
        deliver(build_message(to, link))
        log.info("Password reset email sent to %s", to)
    except Exception as e:  # noqa: BLE001
        log.error("COULD NOT SEND the reset email to %s: %s: %s  (run: python backend/test_email.py YOUR-EMAIL)", to, type(e).__name__, e)
