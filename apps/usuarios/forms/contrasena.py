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

from apps.usuarios.models import Usuario


class UsuarioPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label="Correo electrónico",
        required=True,
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'autocomplete': 'off',
                'inputmode': 'email',
                'autofocus': True,
            }
        ),
    )    

    def clean_email(self):
        email = self.cleaned_data['email']
        return email.strip().lower()


class UsuarioSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["new_password1"].widget.attrs.update({
            "class": "form-control",
            "autocomplete": "new-password",
            "x-model": "new_password1",
            "x-bind:type": "showPassword ? 'text' : 'password'",
        })

        self.fields["new_password2"].widget.attrs.update({
            "class": "form-control",
            "autocomplete": "new-password",
            "x-model": "new_password2",
            "x-bind:type": "showPassword ? 'text' : 'password'",
            "x-bind:class": "{ 'is-invalid': mostrarErrorCoincidencia }",
            "x-bind:aria-invalid": "mostrarErrorCoincidencia ? 'true' : 'false'",
        })


class UsuarioPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field in (
            'old_password',
            'new_password1',
            'new_password2',
        ):
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'autocomplete': (
                    'current-password' if field == 'old_password' else 'new-password'
                ),
                'x-bind:type': "showPassword ? 'text' : 'password'",
            })

        self.fields['new_password1'].widget.attrs.update({
            'x-model': 'newPassword1',
        })

        self.fields['new_password2'].widget.attrs.update({
            'x-model': 'newPassword2',
            'x-bind:class': (
                "{ 'is-invalid': mostrarErrorCoincidencia }"
            ),
            'x-bind:aria-invalid': (
                "mostrarErrorCoincidencia ? 'true': 'false'"
            ),
        })


