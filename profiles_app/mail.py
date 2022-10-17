from django.conf import settings
from urllib3.packages import six # noqa

from patches.tokens import TokenGenerator


class EmailConfirmationTokenGenerator(TokenGenerator):
    def __init__(self):
        super().__init__()
        self.timeout = settings.EMAIL_CONFIRMATION_TIMEOUT

    def _make_hash_value(self, user, timestamp):
        return (
                six.text_type(user.pk) + six.text_type(timestamp) +
                six.text_type(user.is_email_confirmed)
        )


class ResetPasswordTokenGenerator(TokenGenerator):
    pass
