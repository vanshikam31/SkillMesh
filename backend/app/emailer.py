"""Sends the password reset email through any SMTP server (for example Gmail with an app password)."""
import smtplib
from email.message import EmailMessage

from . import config


def smtp_configured() -> bool:
    return bool(config.SMTP_HOST and config.SMTP_USER and config.SMTP_PASSWORD)


def send_reset_email(to: str, link: str) -> None:
    msg = EmailMessage()
    msg["Subject"] = "Reset your SkillMesh password"
    msg["From"] = config.SMTP_FROM or config.SMTP_USER
    msg["To"] = to
    msg.set_content(
        f"Hi,\n\nUse this link to set a new password. It works for {config.RESET_TOKEN_MINUTES} minutes and only once:\n{link}\n\n"
        "If you did not ask for this, you can ignore this email.\n\n- SkillMesh"
    )
    with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT, timeout=15) as server:
        server.starttls()
        server.login(config.SMTP_USER, config.SMTP_PASSWORD)
        server.send_message(msg)
