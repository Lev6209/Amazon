import json
import os
import urllib.request

from django.core.mail.backends.base import BaseEmailBackend


class BrevoEmailBackend(BaseEmailBackend):

    def send_messages(self, email_messages):
        api_key = os.environ.get('BREVO_API_KEY')

        if not api_key:
            return 0

        sent_count = 0

        for message in email_messages:
            data = {
                'sender': {
                    'name': 'Amazon',
                    'email': 'amazon@ishoyev.com',
                },
                'to': [
                    {'email': email}
                    for email in message.to
                ],
                'subject': message.subject,
                'textContent': message.body,
            }

            request = urllib.request.Request(
                'https://api.brevo.com/v3/smtp/email',
                data=json.dumps(data).encode('utf-8'),
                headers={
                    'accept': 'application/json',
                    'api-key': api_key,
                    'content-type': 'application/json',
                },
                method='POST',
            )

            try:
                with urllib.request.urlopen(request):
                    sent_count += 1
            except Exception:
                if not self.fail_silently:
                    raise

        return sent_count