import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from jinja2 import Template
import structlog
from app.core.config import settings

logger = structlog.get_logger(__name__)


class EmailProvider:
    """Provider abstraction wrapping Brevo / SMTP email dispatching with Jinja2 templates."""

    def __init__(self):
        self.enabled = settings.emails_enabled
        self.template_dir = Path(__file__).parent.parent.parent / "email_templates"

    def _render_template(self, template_name: str, context: dict) -> str:
        template_file = self.template_dir / template_name
        if not template_file.exists():
            logger.error("Email template not found", template_name=template_name)
            return f"<p>{context.get('message', '')}</p>"
        
        template_str = template_file.read_text(encoding="utf-8")
        return Template(template_str).render(context)

    def send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        if not self.enabled:
            logger.warning(
                "Email provider disabled or unconfigured. Skipping email dispatch.",
                to_email=to_email,
                subject=subject,
            )
            return False

        try:
            msg = MIMEMultipart()
            msg["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
            msg["To"] = to_email
            msg["Subject"] = subject
            msg.attach(MIMEText(html_content, "html"))

            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                if settings.SMTP_TLS:
                    server.starttls()
                if settings.SMTP_USER and settings.SMTP_PASSWORD:
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)

            logger.info("Email sent successfully", to_email=to_email, subject=subject)
            return True
        except Exception as e:
            logger.error("Failed to send email", to_email=to_email, error=str(e))
            return False

    def send_verification_email(self, to_email: str, token: str) -> bool:
        link = f"{settings.FRONTEND_HOST}/verify-email?token={token}"
        subject = f"{settings.PROJECT_NAME} - Verify your email address"
        html = self._render_template(
            "account_verification.html",
            {
                "project_name": settings.PROJECT_NAME,
                "email": to_email,
                "link": link,
            },
        )
        return self.send_email(to_email, subject, html)

    def send_password_reset_email(self, to_email: str, token: str) -> bool:
        link = f"{settings.FRONTEND_HOST}/reset-password?token={token}"
        subject = f"{settings.PROJECT_NAME} - Password Reset Request"
        html = self._render_template(
            "reset_password.html",
            {
                "project_name": settings.PROJECT_NAME,
                "email": to_email,
                "link": link,
            },
        )
        return self.send_email(to_email, subject, html)
