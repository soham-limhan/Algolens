"""tests/test_email.py — Unit tests for SMTP email sending service."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

from app.config import settings
from app.services.email import send_otp_email


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
