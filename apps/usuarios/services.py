from email.mime.image import MIMEImage

from django.conf import settings
from django.contrib.staticfiles import finders
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .tokens import account_activation_token


def send_activation_email(request, user):
    uid = urlsafe_base64_encode(
        force_bytes(user.pk)
    )

    token = account_activation_token.make_token(
        user
    )

    activation_path = reverse(
        'usuarios:activar_cuenta',
        kwargs={
            'uidb64': uid,
            'token': token,
        },
    )

    activation_url = request.build_absolute_uri(
        activation_path
    )

    context = {
        'user': user,
        'activation_url': activation_url,
        'expiration_hours': 24,
    }

    text_content = render_to_string(
        'usuarios/emails/activacion_cuenta.txt',
        context,
    )

    html_content = render_to_string(
        'usuarios/emails/activacion_cuenta.html',
        context,
    )

    email = EmailMultiAlternatives(
        subject='Active su cuenta de usuario',
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )

    email.attach_alternative(
        html_content,
        'text/html',
    )

    logo_path = finders.find(
        'img/logo_pj_96x96.png'
    )

    if logo_path is None:
        raise FileNotFoundError(
            'No se encontró el archivo '
            'img/logo_pj_96x96.png'
        )

    with open(logo_path, 'rb') as file:
        logo = MIMEImage(
            file.read(),
            _subtype='png',
        )

    logo.add_header(
        'Content-ID',
        '<logo_poder_judicial>',
    )

    logo.add_header(
        'Content-Disposition',
        'inline',
        filename='logo.png',
    )

    email.mixed_subtype = 'related'

    email.attach(logo)

    email.send(
        fail_silently=False,
    )