import re

from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django import forms


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label='DNI',
        max_length=8,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'x-mask': '99999999',
            }
        )
    )
    
    password = forms.CharField(
        label='Contraseña',
        max_length=50,
        required=True,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
            }
        )
    )

    remember_me = forms.BooleanField(
        label='Recuérdame en este equipo',
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                'class': 'form-check-input'
            }
        )
    )
    
    error_messages = {
        'invalid_login': 'El DNI o la contraseña que ingresaste son incorrectos. Por favor, verifica tus datos.'
    }
    
    def clean_username(self):
        """
        Valida el DNI para asegurar que el valor ingresado debe estar compuesto solo por dígitos y debe tener 
        exactamente ocho (8) dígitos.
        """
        
        username = self.cleaned_data.get('username')
        if not re.match(r'^\d{8}$', username):
            raise ValidationError('El DNI debe tener ocho (8) dígitos.')
        return username
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for name, field in self.fields.items():
            # Aplica el estilo 'is-invalid' si el campo contiene errores.
            if self.errors.get(name):
                field_class = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = field_class + ' is-invalid'
            
    class Meta:
        model = get_user_model()
        fields = ['username', 'password', 'remember_me']
      