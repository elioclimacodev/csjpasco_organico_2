from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.crypto import constant_time_compare
from django.utils.http import base36_to_int
from django.conf import settings


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            f'{user.pk}',
            f'{user.password}',
            f'{user.is_active}',
            # f'{user.estado}',
            f'{timestamp}'
        )

    def check_token(self, user, token):
        if not user or not token:
            return False

        try:
            ts_b36, _ = token.split('-')
            timestamp = base36_to_int(ts_b36)
        except (ValueError, TypeError):
            return False

        if not constant_time_compare(
            self._make_token_with_timestamp(
                user,
                timestamp,
                self.secret,
            ),
            token,
        ):
            return False

        timeout = getattr(
            settings,
            'ACCOUNT_ACTIVATION_TIMEOUT',
            60 * 60 * 24,
        )

        if (self._num_seconds(self._now()) - timestamp) > timeout:
            return False

        return True

account_activation_token = AccountActivationTokenGenerator()