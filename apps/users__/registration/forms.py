from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django import forms


class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        label='Número de DNI',
        max_length=8,
        required=True,
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
                field.widget.attrs['class'] = f'{field_class} is-invalid'.strip()
                
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

