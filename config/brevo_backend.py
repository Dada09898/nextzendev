import requests
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings

class BrevoEmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        sent = 0
        for msg in email_messages:
            try:
                payload = {
                    "sender": {
                        "name": "NextZen IT Solutions",
                        "email": "connect@nextzendev.in"
                    },
                    "to": [{"email": addr} for addr in msg.to],
                    "subject": msg.subject,
                    "textContent": msg.body,
                }

                # ── Fix: EmailMessage content_subtype='html' handle karo ──
                if getattr(msg, 'content_subtype', None) == 'html':
                    payload['htmlContent'] = msg.body
                    payload['textContent'] = 'Please view this email in an HTML-supported email client.'

                # ── EmailMultiAlternatives ke liye (appointment etc.) ──
                elif hasattr(msg, 'alternatives'):
                    for content, mimetype in msg.alternatives:
                        if mimetype == 'text/html':
                            payload['htmlContent'] = content

                response = requests.post(
                    "https://api.brevo.com/v3/smtp/email",
                    headers={
                        "api-key": settings.BREVO_API_KEY,
                        "Content-Type": "application/json",
                    },
                    json=payload,
                    timeout=10
                )

                if response.status_code == 201:
                    sent += 1
                else:
                    print(f"Brevo error: {response.status_code} - {response.text}")

            except Exception as e:
                print(f"Email send failed: {e}")
                if not self.fail_silently:
                    raise
        return sent