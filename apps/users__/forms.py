import re

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django import forms

class UserRegisterForm(UserCreationForm):
# class UserRegisterForm(SignupForm):
    username = forms.CharField(
        label='Número de DNI',
        max_length=8,
        required=True,
        # help_text='Su número de DNI será su nombre de usuario.',
        widget=forms.TextInput(
            attrs={
                'autocomplete': 'off',
                'class': 'form-control',
                'placeholder': 'Ejemplo: 12345678',
            }
        )
    )
    email = forms.EmailField(
        label='Correo electrónico',
        required=True,
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: usuario@dominio.com',
            }
        )
    )
    nombres = forms.CharField(
        label='Nombres',
        required = True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
            }
        )
    )
    apellido_paterno = forms.CharField(
        label='Apellido paterno',
        required = True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
            }
        )
    )
    apellido_materno = forms.CharField(
        label='Apellido materno',
        required = True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
            }
        )
    )
    password1 = forms.CharField(
        label='Contraseña',
        required=True,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Mínimo 8 caracteres',
            }
        )
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        required=True,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Repita la contraseña',
            }
        )
    )
    terminos = forms.BooleanField(
        label='Acepto los términos y condiciones.',
        required=True,
        widget=forms.CheckboxInput(
            attrs={
                'class': 'form-check-input'
            }
        )
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
               
        for name, field in self.fields.items():
            # Aplica estilos a campos password, en caso django-allauth 
            # persiste al aplicar los estilos.
            if isinstance(field.widget, forms.PasswordInput):
                field.widget.attrs.setdefault('class', 'form-control')
            
            # Aplica el estilo 'is-invalid' si el campo contiene errores.
            if self.errors.get(name):
                field_class = field.widget.attrs.get('class','')
                field.widget.attrs['class'] = field_class + ' is-invalid'
                
            # Aplica label como placeholder en todos los campos.
            if hasattr(field.widget, 'attrs'):
                # if 'placeholder' not in field.widget.attrs:
                field.widget.attrs['placeholder'] = field.label
                        
    class Meta:
        model = get_user_model()
        fields = [
            'username',
            'nombres',
            'apellido_paterno', 'apellido_materno',
            'email',
            'password1', 'password2',
            'terminos',
        ]


class LoginForm(AuthenticationForm):
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
        

class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label='Correo electrónico',
        max_length=250,
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese su correo electrónico'
            }
        )
    )
    

class CustomSetPasswordForm(SetPasswordForm):
    """
    Personaliza el formulario para integrar 
    """
    
    new_password1 = forms.CharField(
        label='Nueva contraseña', 
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese su nueva contraseña',
            }
        )
    )
    
    new_password2 = forms.CharField(
        label='Confirme su contraseña', 
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Repita su nueva contraseña',
            }
        )
    )