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

from apps.usuarios.forms.contrasena import (
    UsuarioPasswordChangeForm,
    UsuarioPasswordResetForm,
    UsuarioSetPasswordForm,
)

Usuario = get_user_model()


class UsuarioPasswordResetView(PasswordResetView):
    template_name = 'usuarios/contrasena/restablecer/restablecer.html'
    form_class = UsuarioPasswordResetForm

    email_template_name = 'usuarios/contrasena/restablecer/emails/mensaje.txt'
    subject_template_name = 'usuarios/contrasena/restablecer/emails/asunto.txt'
    success_url = reverse_lazy('usuarios:restablecer_contrasena_enviado')

    extra_context = {
        'title': 'Restablecer contraseña',
        'container_size': 'tight',
    }


class UsuarioPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'usuarios/contrasena/restablecer/solicitud_enviada.html'
    
    extra_context = {
        'title': 'Solicitud enviada',
        'container_size': 'tight',
    }


class UsuarioPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'usuarios/contrasena/restablecer/confirmar.html'
    form_class = UsuarioSetPasswordForm
    success_url = reverse_lazy('usuarios:restablecer_contrasena_completado')
    
    extra_context = {
        'title': 'Establecer nueva contraseña',
        'container_size': 'tight',
    }


class UsuarioPasswordResetComplete(PasswordResetCompleteView):
    template_name = 'usuarios/contrasena/restablecer/completado.html'
    form_class = UsuarioPasswordResetForm

    extra_context = {
        'title': 'Contraseña restablecida',
        'container_size': 'tight',
    }


class UsuarioPasswordChangeView(PasswordChangeView):
    template_name = 'usuarios/contrasena/cambiar/cambiar.html'
    form_class = UsuarioPasswordChangeForm
    success_url = reverse_lazy('usuarios:cambiar_contrasena_completado')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            'Su contraseña ha sido actualizada correctamente.'
        )
        return response

    extra_context = {
        'pre_title': 'Usuarios',
        'title': 'Cambiar contraseña',
    }


class UsuarioPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'usuarios/contrasena/cambiar/completado.html'
    extra_context = {
        'pre_title': 'Usuarios',
        'title': 'Contraseña actualizada',
    }

