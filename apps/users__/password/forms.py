from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django import forms


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