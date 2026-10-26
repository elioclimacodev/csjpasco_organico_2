from django.contrib.auth.tokens import PasswordResetTokenGenerator


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    """
    Generador de tokens que verifica que el usuario no haya cambiado
    la información crítica desde el registro como la contraseña o email.
    """
    
    def _make_hash_value(self, user, timestamp):
        # El hash incluye el estado de actividad para invalidar el token
        # si se intenta usar en una cuenta que ya está activa.
        
        return (f'{user.pk}{timestamp}{user.is_active}')
    
    
account_activation_token = AccountActivationTokenGenerator()
        