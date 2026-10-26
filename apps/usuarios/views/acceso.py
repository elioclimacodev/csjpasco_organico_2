from smtplib import SMTPException

from django.contrib.auth.views import (
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordChangeDoneView,
    PasswordResetDoneView,
    PasswordChangeView,
    PasswordResetView,
    LogoutView, 
    LoginView,
)

from django.contrib.auth.decorators import (
    permission_required,
    login_required,
)

from django.utils.encoding import force_str
from django.views.generic import ListView
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib import messages
from django.urls import reverse_lazy

from apps.usuarios.services import send_activation_email
from apps.usuarios.choices import EstadoUsuario
from apps.usuarios.tokens import account_activation_token

from apps.usuarios.forms.acceso import LoginForm


Usuario = get_user_model()


class UsuarioLoginView(LoginView):
    template_name = 'usuarios/acceso/iniciar_sesion.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True
    extra_context = {
        'title': 'Iniciar sesión',
        'container_size': 'tight',
    }


class UsuarioLogoutView(LogoutView):
    pass

