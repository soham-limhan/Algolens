"""app/services/email.py — Email sending service using standard library smtplib."""
from __future__ import annotations

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import settings

logger = logging.getLogger("algolens.email")

def send_account_creation_email(to_email: str, user_name: str | None = None) -> bool:
    """Send an account creation confirmation email via SMTP to the specified email address.

    Uses Python's standard `smtplib` and `email.mime` packages.
    If SMTP is disabled or connection fails, falls back to logging the email.

    Args:
        to_email: Destination email address.
        user_name: Optional name of the user to personalize the email.

    Returns:
        bool: True if email sent or logged successfully, False if error occurs.
    """
    greeting = f"Hello {user_name}," if user_name else "Hello,"
    subject = "AlgoLens - Welcome to AlgoLens! Account Created"
    text_content = (
        f"{greeting}\n\n"
        f"Your AlgoLens account has been successfully created.\n\n"
        f"You can now log in to your account using your email address and password to start analyzing and optimizing your algorithms.\n\n"
        f"Best regards,\nAlgoLens Support Team"
    )
    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background-color: #0f172a; color: #f8fafc; padding: 20px;">
        <div style="max-width: 500px; margin: 0 auto; background-color: #1e293b; border-radius: 8px; padding: 30px; border: 1px solid #334155;">
          <h2 style="color: #38bdf8; margin-top: 0;">Welcome to AlgoLens!</h2>
          <p style="color: #cbd5e1; font-size: 15px;">{greeting}</p>
          <p style="color: #cbd5e1; line-height: 1.5;">Your AlgoLens account has been successfully created. You can now log in using your registered email and password to start analyzing algorithms and benchmarking performance.</p>
          <div style="background-color: #0f172a; border-radius: 6px; padding: 15px; text-align: center; margin: 20px 0; border: 1px solid #38bdf8;">
            <span style="font-size: 16px; font-weight: bold; color: #38bdf8;">Account: {to_email}</span>
          </div>
          <p style="color: #94a3b8; font-size: 13px; margin-top: 20px;">If you did not create this account, please contact our support team immediately.</p>
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
        logger.info("[SMTP Disabled/Dev Mode] Account creation email for %s", to_email)
        print(f"[SMTP Dev Mode] Sent account creation email to {to_email}")
        return True

    try:
        username = settings.smtp_username.strip() if settings.smtp_username else ""
        password = settings.smtp_password.replace(" ", "").strip() if settings.smtp_password else ""

        if settings.smtp_port == 465 or not settings.smtp_use_tls:
            server_cls = smtplib.SMTP_SSL if settings.smtp_port == 465 else smtplib.SMTP
            with server_cls(settings.smtp_host, settings.smtp_port, timeout=10) as server:
                if username and password:
                    server.login(username, password)
                server.send_message(msg)
        else:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as server:
                server.ehlo()
                if settings.smtp_use_tls:
                    server.starttls()
                    server.ehlo()
                if username and password:
                    server.login(username, password)
                server.send_message(msg)
        logger.info("Successfully sent account creation email to %s via SMTP", to_email)
        return True
    except Exception as exc:
        logger.error("Failed to send account creation email via SMTP to %s: %s", to_email, exc)
        print(f"[SMTP Warning] Failed to send email via SMTP: {exc}. Account creation email for {to_email}")
        return False


account_creation_email = send_account_creation_email


def send_registration_otp_email(to_email: str, otp: str, user_name: str | None = None) -> bool:
    """Send an account registration verification OTP via SMTP to the specified email address.

    Uses Python's standard `smtplib` and `email.mime` packages.
    If SMTP is disabled or connection fails, falls back to logging the OTP.

    Returns:
        bool: True if email sent or logged successfully, False if error occurs.
    """
    greeting = f"Hello {user_name}," if user_name else "Hello,"
    subject = "AlgoLens - Account Verification OTP"
    text_content = (
        f"{greeting}\n\n"
        f"Thank you for signing up for AlgoLens!\n\n"
        f"Your One-Time Password (OTP) to verify your email address and create your account is: {otp}\n\n"
        f"This code is valid for 15 minutes. "
        f"If you did not request this account creation, please ignore this email.\n\n"
        f"Best regards,\nAlgoLens Support Team"
    )
    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background-color: #0f172a; color: #f8fafc; padding: 20px;">
        <div style="max-width: 500px; margin: 0 auto; background-color: #1e293b; border-radius: 8px; padding: 30px; border: 1px solid #334155;">
          <h2 style="color: #38bdf8; margin-top: 0;">Verify Your Email Address</h2>
          <p style="color: #cbd5e1; font-size: 15px;">{greeting}</p>
          <p style="color: #cbd5e1;">Thank you for signing up for AlgoLens! Please use the following 6-digit OTP code to verify your email address and complete your account creation:</p>
          <div style="background-color: #0f172a; border-radius: 6px; padding: 15px; text-align: center; margin: 20px 0; border: 1px dashed #38bdf8;">
            <span style="font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #38bdf8;">{otp}</span>
          </div>
          <p style="color: #94a3b8; font-size: 14px;">This code is valid for 15 minutes. If you did not attempt to register an AlgoLens account, you can safely ignore this email.</p>
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
        logger.info("[SMTP Disabled/Dev Mode] Registration OTP email for %s: OTP=%s", to_email, otp)
        print(f"[SMTP Dev Mode] Sent Registration OTP email to {to_email}: {otp}")
        return True

    try:
        username = settings.smtp_username.strip() if settings.smtp_username else ""
        password = settings.smtp_password.replace(" ", "").strip() if settings.smtp_password else ""

        if settings.smtp_port == 465 or not settings.smtp_use_tls:
            server_cls = smtplib.SMTP_SSL if settings.smtp_port == 465 else smtplib.SMTP
            with server_cls(settings.smtp_host, settings.smtp_port, timeout=10) as server:
                if username and password:
                    server.login(username, password)
                server.send_message(msg)
        else:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as server:
                server.ehlo()
                if settings.smtp_use_tls:
                    server.starttls()
                    server.ehlo()
                if username and password:
                    server.login(username, password)
                server.send_message(msg)
        logger.info("Successfully sent registration OTP email to %s via SMTP", to_email)
        return True
    except Exception as exc:
        logger.error("Failed to send registration OTP email via SMTP to %s: %s", to_email, exc)
        print(f"[SMTP Warning] Failed to send email via SMTP: {exc}. Registration OTP for {to_email} was: {otp}")
        return False


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
        f"This code is valid only for 15 minutes for your password reset request. "
        f"If you did not request this, please ignore this email and contact support.\n\n"
        f"Best regards,\nAlgoLens Support Team"
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
          <p style="color: #94a3b8; font-size: 14px;">This code is valid only for 15 minutes. If you did not request a password reset, please ignore this email and contact support.</p>
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
        username = settings.smtp_username.strip() if settings.smtp_username else ""
        password = settings.smtp_password.replace(" ", "").strip() if settings.smtp_password else ""

        if settings.smtp_port == 465 or not settings.smtp_use_tls:
            server_cls = smtplib.SMTP_SSL if settings.smtp_port == 465 else smtplib.SMTP
            with server_cls(settings.smtp_host, settings.smtp_port, timeout=10) as server:
                if username and password:
                    server.login(username, password)
                server.send_message(msg)
        else:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as server:
                server.ehlo()
                if settings.smtp_use_tls:
                    server.starttls()
                    server.ehlo()
                if username and password:
                    server.login(username, password)
                server.send_message(msg)
        logger.info("Successfully sent OTP email to %s via SMTP", to_email)
        return True
    except Exception as exc:
        logger.error("Failed to send OTP email via SMTP to %s: %s", to_email, exc)
        print(f"[SMTP Warning] Failed to send email via SMTP: {exc}. OTP for {to_email} was: {otp}")
        return False
