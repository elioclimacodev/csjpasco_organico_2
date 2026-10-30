"""
Exigencia de sesión en todo el sistema (denegación por defecto).

Toda vista exige sesión salvo las declaradas con `login_not_required`
(contracts/vistas-y-permisos.md §1). Es el único middleware de acceso del
proyecto (constitución, Principios II y IV; research R1–R2).
"""
from urllib.parse import urlencode, urlsplit

from django.conf import settings
from django.contrib.auth.middleware import LoginRequiredMiddleware as LoginRequiredMiddlewareBase
from django.http import HttpResponse
from django.shortcuts import resolve_url
from django.utils.http import url_has_allowed_host_and_scheme


class LoginRequiredMiddleware(LoginRequiredMiddlewareBase):
    """
    `LoginRequiredMiddleware` de Django con respuesta propia para HTMX.

    Una petición normal sin sesión se redirige al inicio de sesión con el
    comportamiento nativo. Una petición HTMX recibe `401` con la cabecera
    `HX-Redirect`, para que la página completa (no solo la ventana o la
    tabla) vaya al inicio de sesión y vuelva después a la página en la que
    estaba el usuario (spec FR-012; contracts/respuestas-acceso.md §1).
    """

    def handle_no_permission(self, request, view_func):
        if request.headers.get('HX-Request') != 'true':
            return super().handle_no_permission(request, view_func)

        respuesta = HttpResponse(status=401)
        respuesta['HX-Redirect'] = (
            f"{resolve_url(settings.LOGIN_URL)}?{urlencode({'next': self.ruta_de_retorno(request)})}"
        )
        return respuesta

    @staticmethod
    def ruta_de_retorno(request):
        """
        Ruta de la página en la que estaba el usuario (`HX-Current-URL`),
        solo si pertenece a este mismo sitio; si no, la página de inicio.
        """
        actual = request.headers.get('HX-Current-URL', '')
        if actual and url_has_allowed_host_and_scheme(
            actual,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            partes = urlsplit(actual)
            return f'{partes.path}?{partes.query}' if partes.query else partes.path
        return resolve_url(settings.LOGIN_REDIRECT_URL)
