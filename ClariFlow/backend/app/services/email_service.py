"""
Email service for sending verification emails and notifications.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from ..core.config import settings
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class EmailService:
    """Service for sending emails."""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.smtp_use_tls = settings.SMTP_USE_TLS
        self.email_from = settings.EMAIL_FROM
        
    def is_configured(self) -> bool:
        """Check if email service is properly configured."""
        return all([
            self.smtp_host,
            self.smtp_username,
            self.smtp_password,
            self.email_from
        ])
    
    def send_verification_email(self, email: str, token: str, verification_url: str) -> bool:
        """
        Send email verification email.
        
        Args:
            email: Recipient email address
            token: Verification token
            verification_url: URL to verify email
            
        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.is_configured():
            logger.warning("Email service not configured, skipping verification email")
            return False
            
        try:
            subject = "Verify your ClariFlow account"
            
            html_content = f"""
            <html>
            <body>
                <h2>Welcome to ClariFlow!</h2>
                <p>Please verify your email address by clicking the link below:</p>
                <p><a href="{verification_url}?token={token}">Verify Email Address</a></p>
                <p>If the link doesn't work, copy and paste this URL into your browser:</p>
                <p>{verification_url}?token={token}</p>
                <p>This link will expire in 24 hours.</p>
                <p>If you didn't create an account, you can safely ignore this email.</p>
            </body>
            </html>
            """
            
            text_content = f"""
            Welcome to ClariFlow!
            
            Please verify your email address by visiting this link:
            {verification_url}?token={token}
            
            This link will expire in 24 hours.
            
            If you didn't create an account, you can safely ignore this email.
            """
            
            return self._send_email(email, subject, text_content, html_content)
            
        except Exception as e:
            logger.error(f"Error sending verification email to {email}: {str(e)}")
            return False
    
    def send_password_reset_email(self, email: str, token: str, reset_url: str) -> bool:
        """
        Send password reset email.
        
        Args:
            email: Recipient email address
            token: Reset token
            reset_url: URL to reset password
            
        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.is_configured():
            logger.warning("Email service not configured, skipping password reset email")
            return False
            
        try:
            subject = "Reset your ClariFlow password"
            
            html_content = f"""
            <html>
            <body>
                <h2>Password Reset Request</h2>
                <p>You requested to reset your password. Click the link below to proceed:</p>
                <p><a href=\"{reset_url}?token={token}\">Reset Password</a></p>
                <p>If the link doesn't work, copy and paste this URL into your browser:</p>
                <p>{reset_url}?token={token}</p>
                <p>This link will expire in 1 hour.</p>
                <p>If you didn't request a password reset, you can safely ignore this email.</p>
            </body>
            </html>
            """
            
            text_content = f"""
            Password Reset Request
            
            You requested to reset your password. Visit this link to proceed:
            {reset_url}?token={token}
            
            This link will expire in 1 hour.
            
            If you didn't request a password reset, you can safely ignore this email.
            """
            
            return self._send_email(email, subject, text_content, html_content)
            
        except Exception as e:
            logger.error(f"Error sending password reset email to {email}: {str(e)}")
            return False
    
    def _send_email(self, to_email: str, subject: str, text_content: str, html_content: Optional[str] = None) -> bool:
        """
        Send email using SMTP.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            text_content: Plain text content
            html_content: HTML content (optional)
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.email_from
            msg['To'] = to_email
            
            # Add text part
            text_part = MIMEText(text_content, 'plain')
            msg.attach(text_part)
            
            # Add HTML part if provided
            if html_content:
                html_part = MIMEText(html_content, 'html')
                msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.smtp_use_tls:
                    server.starttls()
                
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {str(e)}")
            return False

# Global email service instance
email_service = EmailService() 