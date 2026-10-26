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

from .services import send_activation_email
from .choices import EstadoUsuario
from .tokens import account_activation_token

from .forms import (
    GENERIC_REGISTRATION_ERROR,
    RegistrationConflictError,
    UsuarioPasswordChangeForm,
    UsuarioPasswordResetForm,
    UsuarioRegistrationForm,
    UsuarioSetPasswordForm,
    LoginForm
)


Usuario = get_user_model()


def registro(request):
    if request.user.is_authenticated:
        return redirect('home:home') # TODO: CORREGIR LA URL DE HOME.

    if request.method == 'POST':
        form = UsuarioRegistrationForm(request.POST)

        if form.is_valid():
            try:
                usuario = form.save()

            except RegistrationConflictError:
                form.add_error(
                    None,
                    GENERIC_REGISTRATION_ERROR,
                )

            else:
                try:
                    send_activation_email(
                        request=request,
                        user=usuario,
                    )

                except SMTPException:
                    request.session['registration_email_sent'] = False

                    messages.warning(
                        request,
                        (
                            'Su cuenta se ha registrado correctamente. '
                            'No obstante, no fue posible enviarle el correo '
                            'de activación. Por favor, solicite un nuevo '
                            'enlace de activación.'
                        ),
                    )

                else:
                    request.session['registration_email_sent'] = True

                return redirect(
                    'usuarios:registro_completo'
                )

    else:
        form = UsuarioRegistrationForm()

    template = 'usuarios/registro/registro.html'

    context = {
        'form': form,
        'title': 'Registro de usuarios',
        'container_size': 'narrow',
    }

    return render(
        request,
        template,
        context,
    )


def activar_cuenta(request, uidb64, token):
    context = {
        'container_size': 'tight',
    }


    try:
        uid = force_str(
            urlsafe_base64_decode(uidb64)
        )

        usuario = Usuario.objects.get(pk=uid)

    except (
        TypeError,
        ValueError,
        OverflowError,
        Usuario.DoesNotExist,
    ):
        usuario = None

    if usuario is None:
        context['title'] = 'Enlace de activación no válido'

        return render(
            request,
            'usuarios/registro/activacion_invalida.html',
            context,
        )

    if usuario.is_active:
        messages.info(
            request,
            'Su cuenta ya se encuentra activa.',
        )

        # TODO: completar el enlace, mejor confirmar la activación de la cuenta y mostrar
        # un botón para que se vaya al login.
        return redirect(
            'usuarios:iniciar_sesion'
        )

    if not account_activation_token.check_token(
        usuario,
        token,
    ):

        context['title'] = 'Enlace de activación no válido'
        return render(
            request,
            'usuarios/registro/activacion_invalida.html',
            context
        )

    usuario.is_active = True
    # usuario.estado = EstadoUsuario.ACTIVO

    usuario.save(
        update_fields=[
            'is_active',
            # 'estado',
        ]
    )

    messages.success(
        request,
        (
            'Su cuenta ha sido activada correctamente. '
            'Ya puede iniciar sesión.'
        ),
    )

    # TODO: completar el enlace
    return redirect(
        'usuarios:iniciar_sesion'
    )


def registro_completo(request):
    if request.user.is_authenticated:
        return redirect('home:home') # TODO: CORREGIR LA URL DE HOME.

    email_sent = request.session.pop(
        'registration_email_sent',
        None,
    )

    template = 'usuarios/registro/registro_completo.html'

    context = {
        'title': 'Registro de usuarios',
        'container_size': 'tight',
        'email_sent': email_sent,
    }

    return render(
        request,
        template,
        context,
    )


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

