"""
Send emails (OTPs) over SMTP with Python's built-in smtplib (same job as nodemailer in Node).
All SMTP settings come from backend/.env.
"""
import smtplib
from email.message import EmailMessage

from app import config


class MailError(Exception):
    pass


def send_email(to: str, subject: str, body: str) -> None:
    if not config.SMTP_HOST:
        if config.DEV_PRINT_OTP:  # development only: no SMTP yet, show the mail in the server log
            print(f"[DEV EMAIL] to={to} subject={subject}\n{body}", flush=True)
            return
        raise MailError("Email is not configured on the server (SMTP_HOST)")

    msg = EmailMessage()
    msg["From"] = config.SMTP_FROM or config.SMTP_USER
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)
    try:
        if config.SMTP_PORT == 465:  # SSL from the start
            with smtplib.SMTP_SSL(config.SMTP_HOST, config.SMTP_PORT, timeout=20) as smtp:
                smtp.login(config.SMTP_USER, config.SMTP_PASSWORD)
                smtp.send_message(msg)
        else:  # 587: plain connection upgraded with STARTTLS
            with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT, timeout=20) as smtp:
                smtp.starttls()
                smtp.login(config.SMTP_USER, config.SMTP_PASSWORD)
                smtp.send_message(msg)
    except (smtplib.SMTPException, OSError) as e:
        raise MailError(f"Could not send email: {e}") from e
