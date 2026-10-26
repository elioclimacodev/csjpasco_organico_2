from django.contrib.auth.tokens import PasswordResetTokenGenerator


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    """
    Genera un token único basado en el usuario y la fecha.
    """
    
    def _make_hash_value(self, user, timestamp):
        return f'{user.pk}{timestamp}{user.is_active}'
    

email_verification_token = EmailVerificationTokenGenerator()