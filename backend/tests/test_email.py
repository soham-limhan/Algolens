"""tests/test_email.py — Unit tests for SMTP email sending service."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

from app.config import settings
from app.services.email import (
    account_creation_email,
    send_account_creation_email,
    send_otp_email,
    send_registration_otp_email,
)


def test_send_account_creation_email_dev_mode():
    """Test send_account_creation_email in dev mode (smtp_enabled=False)."""
    with patch.object(settings, "smtp_enabled", False):
        result = send_account_creation_email("user@example.com", user_name="Alice")
        assert result is True


def test_send_account_creation_email_smtp_tls():
    """Test send_account_creation_email with SMTP TLS server mocked."""
    mock_smtp = MagicMock()

    with patch.object(settings, "smtp_enabled", True), \
         patch.object(settings, "smtp_host", "smtp.example.com"), \
         patch.object(settings, "smtp_port", 587), \
         patch.object(settings, "smtp_use_tls", True), \
         patch.object(settings, "smtp_username", "smtpuser"), \
         patch.object(settings, "smtp_password", "smtppass"), \
         patch("smtplib.SMTP", return_value=mock_smtp) as mock_smtp_cls:

        mock_smtp.__enter__.return_value = mock_smtp

        result = send_account_creation_email("newuser@example.com", user_name="Bob")

        assert result is True
        mock_smtp_cls.assert_called_once_with("smtp.example.com", 587, timeout=10)
        mock_smtp.starttls.assert_called_once()
        mock_smtp.login.assert_called_once_with("smtpuser", "smtppass")
        mock_smtp.send_message.assert_called_once()

        # Inspect the message sent
        sent_msg = mock_smtp.send_message.call_args[0][0]
        assert sent_msg["To"] == "newuser@example.com"
        assert "Welcome" in sent_msg["Subject"]
        assert "Hello Bob," in str(sent_msg)


def test_account_creation_email_alias():
    """Test that account_creation_email alias functions identically."""
    with patch.object(settings, "smtp_enabled", False):
        result = account_creation_email("user@example.com")
        assert result is True


def test_send_registration_otp_email_dev_mode():
    """Test send_registration_otp_email in dev mode."""
    with patch.object(settings, "smtp_enabled", False):
        result = send_registration_otp_email("newuser@example.com", "456789", user_name="Charlie")
        assert result is True


def test_send_registration_otp_email_smtp_tls():
    """Test send_registration_otp_email with SMTP TLS."""
    mock_smtp = MagicMock()

    with patch.object(settings, "smtp_enabled", True), \
         patch.object(settings, "smtp_host", "smtp.example.com"), \
         patch.object(settings, "smtp_port", 587), \
         patch.object(settings, "smtp_use_tls", True), \
         patch.object(settings, "smtp_username", "smtpuser"), \
         patch.object(settings, "smtp_password", "smtppass"), \
         patch("smtplib.SMTP", return_value=mock_smtp) as mock_smtp_cls:

        mock_smtp.__enter__.return_value = mock_smtp

        result = send_registration_otp_email("charlie@example.com", "112233", user_name="Charlie")

        assert result is True
        mock_smtp_cls.assert_called_once_with("smtp.example.com", 587, timeout=10)
        mock_smtp.starttls.assert_called_once()
        mock_smtp.login.assert_called_once_with("smtpuser", "smtppass")
        mock_smtp.send_message.assert_called_once()

        sent_msg = mock_smtp.send_message.call_args[0][0]
        assert sent_msg["To"] == "charlie@example.com"
        assert sent_msg["Subject"] == "AlgoLens - Account Verification OTP"
        assert "112233" in str(sent_msg)


def test_send_otp_email_dev_mode():
    """Test send_otp_email in dev mode (smtp_enabled=False)."""
    with patch.object(settings, "smtp_enabled", False):
        result = send_otp_email("user@example.com", "123456")
        assert result is True


def test_send_otp_email_smtp_tls():
    """Test send_otp_email with SMTP TLS server mocked."""
    mock_smtp = MagicMock()

    with patch.object(settings, "smtp_enabled", True), \
         patch.object(settings, "smtp_host", "smtp.example.com"), \
         patch.object(settings, "smtp_port", 587), \
         patch.object(settings, "smtp_use_tls", True), \
         patch.object(settings, "smtp_username", "smtpuser"), \
         patch.object(settings, "smtp_password", "smtppass"), \
         patch("smtplib.SMTP", return_value=mock_smtp) as mock_smtp_cls:

        mock_smtp.__enter__.return_value = mock_smtp

        result = send_otp_email("recipient@example.com", "654321")

        assert result is True
        mock_smtp_cls.assert_called_once_with("smtp.example.com", 587, timeout=10)
        mock_smtp.starttls.assert_called_once()
        mock_smtp.login.assert_called_once_with("smtpuser", "smtppass")
        mock_smtp.send_message.assert_called_once()

        # Inspect the message sent
        sent_msg = mock_smtp.send_message.call_args[0][0]
        assert sent_msg["To"] == "recipient@example.com"
        assert sent_msg["Subject"] == "AlgoLens - Password Reset OTP"
        assert "654321" in str(sent_msg)


def test_send_otp_email_smtp_ssl():
    """Test send_otp_email with SMTP SSL server (port 465) mocked."""
    mock_smtp_ssl = MagicMock()

    with patch.object(settings, "smtp_enabled", True), \
         patch.object(settings, "smtp_host", "smtp.example.com"), \
         patch.object(settings, "smtp_port", 465), \
         patch("smtplib.SMTP_SSL", return_value=mock_smtp_ssl) as mock_ssl_cls:

        mock_smtp_ssl.__enter__.return_value = mock_smtp_ssl

        result = send_otp_email("ssl@example.com", "999888")

        assert result is True
        mock_ssl_cls.assert_called_once_with("smtp.example.com", 465, timeout=10)
        mock_smtp_ssl.send_message.assert_called_once()


