from django.contrib.auth.forms import (
    BaseUserCreationForm, 
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
)

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django import forms

from apps.personas.choices import (
    TipoDocumento,
    EstadoCivil,
    Genero,
)

from apps.personas.validators import validate_id_number
from apps.personas.models import Persona
from apps.personas.utils import normalize_id_number


class LoginForm(AuthenticationForm):
    error_messages = {
        'invalid_login': (
            'El número de documento o la contraseña son incorrectos.'
        ),
    }

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].label = 'Número de documento'
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'autocomplete': 'off',
            'autofocus': True,
        })

        self.fields['password'].label = 'Contraseña'
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'autocomplete': 'off',
            'x-bind:type': "showPassword ? 'text': 'password'" ,
        })


