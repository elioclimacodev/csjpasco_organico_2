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
    login_not_required,
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

from apps.usuarios.forms.registro import (
    GENERIC_REGISTRATION_ERROR,
    RegistrationConflictError,
    UsuarioRegistrationForm,
)


Usuario = get_user_model()


@login_not_required
def registro(request):
    if request.user.is_authenticated:
        # Quien ya tiene sesión no necesita registrarse (spec 002 §Edge Cases).
        return redirect('main:index')

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


@login_not_required
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


@login_not_required
def registro_completo(request):
    if request.user.is_authenticated:
        return redirect('main:index') # TODO: CORREGIR LA URL DE HOME.

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

