from abc import ABCMeta
from datetime import datetime, time

from django.contrib.auth.tokens import PasswordResetTokenGenerator

from django.conf import settings
from django.utils.crypto import constant_time_compare
from django.utils.http import base36_to_int


class _Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(_Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

    @property
    def instance(cls):
        if cls not in cls._instances:
            return cls.__call__()
        return cls._instances[cls]


class TokenGeneratorMeta(ABCMeta, _Singleton):
    pass


class TokenGenerator(PasswordResetTokenGenerator, metaclass=TokenGeneratorMeta):

    def __init__(self):
        super().__init__()
        self.timeout = settings.PASSWORD_RESET_TIMEOUT

    def check_token(self, obj, token):
        """
        Check that a password reset token is correct for a given user.
        """
        if not (obj and token):
            return False
        # Parse the token
        try:
            ts_b36, _ = token.split("-")
            # RemovedInDjango40Warning.
            legacy_token = len(ts_b36) < 4
        except ValueError:
            return False

        try:
            ts = base36_to_int(ts_b36)
        except ValueError:
            return False

        # Check that the timestamp/uid has not been tampered with
        if not constant_time_compare(self._make_token_with_timestamp(obj, ts), token):
            # RemovedInDjango40Warning: when the deprecation ends, replace
            # with:
            #   return False
            if not constant_time_compare(
                    self._make_token_with_timestamp(obj, ts, legacy=True),
                    token,
            ):
                return False

        # RemovedInDjango40Warning: convert days to seconds and round to
        # midnight (server time) for pre-Django 3.1 tokens.
        now = self._now()
        if legacy_token:
            ts *= 24 * 60 * 60
            ts += int((now - datetime.combine(now.date(), time.min)).total_seconds())
        # Check the timestamp is within limit.
        if (self._num_seconds(now) - ts) > self.timeout:
            return False

        return True
