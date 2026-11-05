from uuid import uuid4

from app.models import Notification
from app.services.email_service import render_html_email


def test_email_template_escapes_user_supplied_content():
    notification = Notification(
        idempotency_key=str(uuid4()),
        recipient="customer@example.com",
        notification_type="contact.received",
        subject="<script>unsafe</script>",
        message="<img src=x onerror=alert(1)>",
    )
    html_body = render_html_email(notification)
    assert "<script>" not in html_body
    assert "&lt;script&gt;" in html_body
    assert "&lt;img" in html_body
