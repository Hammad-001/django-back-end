from django.core.mail import EmailMessage
import os


class Utils:

    # for Sending Email
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            data['subject'],
            data['body'],
            os.environ.get("EMAIL_FROM"),
            data['to_email'],
        )
        email.send(fail_silently=False)
