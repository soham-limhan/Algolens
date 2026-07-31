"""app/services/email.py — Email sending service using standard library smtplib."""
from __future__ import annotations

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import settings

logger = logging.getLogger("algolens.email")


def send_otp_email(to_email: str, otp: str) -> bool:
    """Send an OTP code via SMTP to the specified email address.

    Uses Python's standard `smtplib` and `email.mime` packages.
    If SMTP is disabled or connection fails, falls back to logging the OTP.

    Returns:
        bool: True if email sent or logged successfully, False if error occurs.
    """
    subject = "AlgoLens - Password Reset OTP"
    text_content = (
        f"Hello,\n\n"
        f"Your One-Time Password (OTP) for resetting your AlgoLens password is: {otp}\n\n"
        f"This code is valid for your password reset request. "
        f"If you did not request this, please ignore this email.\n\n"
        f"Best regards,\nAlgoLens Team"
    )
    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background-color: #0f172a; color: #f8fafc; padding: 20px;">
        <div style="max-width: 500px; margin: 0 auto; background-color: #1e293b; border-radius: 8px; padding: 30px; border: 1px solid #334155;">
          <h2 style="color: #38bdf8; margin-top: 0;">AlgoLens Password Reset</h2>
          <p style="color: #cbd5e1;">You requested a password reset. Use the following 6-digit OTP code to verify your request:</p>
          <div style="background-color: #0f172a; border-radius: 6px; padding: 15px; text-align: center; margin: 20px 0; border: 1px dashed #38bdf8;">
            <span style="font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #38bdf8;">{otp}</span>
          </div>
          <p style="color: #94a3b8; font-size: 14px;">If you did not request a password reset, please ignore this email.</p>
        </div>
      </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.smtp_from_email
    msg["To"] = to_email

    msg.attach(MIMEText(text_content, "plain"))
    msg.attach(MIMEText(html_content, "html"))

    if not settings.smtp_enabled or not settings.smtp_host:
        logger.info("[SMTP Disabled/Dev Mode] OTP email for %s: OTP=%s", to_email, otp)
        print(f"[SMTP Dev Mode] Sent OTP email to {to_email}: {otp}")
        return True

    try:
        if settings.smtp_port == 465 or not settings.smtp_use_tls:
            server_cls = smtplib.SMTP_SSL if settings.smtp_port == 465 else smtplib.SMTP
            with server_cls(settings.smtp_host, settings.smtp_port, timeout=10) as server:
                if settings.smtp_username and settings.smtp_password:
                    server.login(settings.smtp_username, settings.smtp_password)
                server.send_message(msg)
        else:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as server:
                server.ehlo()
                if settings.smtp_use_tls:
                    server.starttls()
                    server.ehlo()
                if settings.smtp_username and settings.smtp_password:
                    server.login(settings.smtp_username, settings.smtp_password)
                server.send_message(msg)
        logger.info("Successfully sent OTP email to %s via SMTP", to_email)
        return True
    except Exception as exc:
        logger.error("Failed to send OTP email via SMTP to %s: %s", to_email, exc)
        print(f"[SMTP Warning] Failed to send email via SMTP: {exc}. OTP for {to_email} was: {otp}")
        return False
