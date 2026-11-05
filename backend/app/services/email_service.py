import html
import logging

import httpx

from app.core.config import settings
from app.models import Notification

logger = logging.getLogger(__name__)
RESEND_URL = "https://api.resend.com/emails"


def render_html_email(notification: Notification) -> str:
    message = html.escape(notification.message).replace("\n", "<br>")
    subject = html.escape(notification.subject)
    phone = html.escape(settings.business_phone)
    address = html.escape(settings.business_address)
    return (
        "<!doctype html><html><body style=\"margin:0;background:#f4f1eb;font-family:Arial,sans-serif;color:#202522\">"
        "<table role=\"presentation\" width=\"100%\" cellspacing=\"0\" cellpadding=\"0\"><tr><td align=\"center\" style=\"padding:32px 16px\">"
        "<table role=\"presentation\" width=\"600\" cellspacing=\"0\" cellpadding=\"0\" style=\"max-width:600px;background:#fff\">"
        "<tr><td style=\"background:#202522;padding:24px 32px;color:#fff;font-size:20px;font-weight:bold\">FORGE &amp; FORM</td></tr>"
        f"<tr><td style=\"padding:32px\"><h1 style=\"font-size:22px\">{subject}</h1><p style=\"font-size:16px;line-height:1.6\">{message}</p>"
        f"<p style=\"font-size:13px;color:#616761\">Questions? Contact {html.escape(settings.business_email)} or {phone}.<br>{address}</p>"
        "</td></tr></table></td></tr></table></body></html>"
    )


async def send_notification(notification: Notification) -> None:
    if settings.email_provider == "console":
        logger.info(
            "notification_preview",
            extra={"notification_id": str(notification.id), "notification_type": notification.notification_type},
        )
        return
    if settings.email_provider != "resend":
        raise ValueError(f"Unsupported EMAIL_PROVIDER: {settings.email_provider}")
    if not settings.email_api_key or not settings.email_from_address:
        raise RuntimeError("Resend email delivery requires EMAIL_API_KEY and EMAIL_FROM_ADDRESS")
    payload = {
        "from": settings.email_from_address,
        "to": [notification.recipient],
        "subject": notification.subject,
        "html": render_html_email(notification),
        "text": notification.message,
    }
    async with httpx.AsyncClient(timeout=httpx.Timeout(15.0)) as client:
        response = await client.post(
            RESEND_URL,
            json=payload,
            headers={
                "Authorization": f"Bearer {settings.email_api_key}",
                "Idempotency-Key": notification.idempotency_key,
            },
        )
        response.raise_for_status()
