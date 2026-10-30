"""
Respuestas únicas ante una denegación de acceso o un fallo de verificación
anti-falsificación (CSRF), para páginas completas y fragmentos HTMX
(contracts/respuestas-acceso.md §2 y §2b; research R3).

Son el único `handler403` y la única `CSRF_FAILURE_VIEW` del proyecto
(constitución, Principio IV).
"""
import json

from django.http import HttpResponse
from django.shortcuts import render
from django.views.csrf import csrf_failure
from django.views.defaults import permission_denied


MENSAJE_SIN_PERMISO = 'No tiene permiso para realizar esta operación.'


def es_htmx(request):
    return request.headers.get('HX-Request') == 'true'


def permiso_denegado(request, exception=None):
    """
    `handler403`. La denegación llega como `PermissionDenied` nativo, ya
    visible para `process_exception` (punto de enganche de la futura auditoría).

    - Página completa: `403.html` (spec 001 FR-008b).
    - Ventana (`HX-Target: modal_content`): aviso "Acceso denegado" con "Cerrar".
    - Otro fragmento (tablas): notificación flotante de error, sin alterar el contenido.
    """
    if not es_htmx(request):
        return permission_denied(request, exception)

    if request.headers.get('HX-Target') == 'modal_content':
        return render(request, 'components/modals/modal_denegado.html', status=403)

    respuesta = HttpResponse(status=403)
    respuesta['HX-Reswap'] = 'none'
    # `json.dumps` escapa los caracteres no ASCII: las cabeceras HTTP solo admiten Latin-1.
    respuesta['HX-Trigger'] = json.dumps({'show_toast': {'type': 'error', 'message': MENSAJE_SIN_PERMISO}})
    return respuesta


def fallo_csrf(request, reason=''):
    """
    `CSRF_FAILURE_VIEW`. En HTMX pide recargar la página completa para obtener
    un token válido (o ir al inicio de sesión si no hay sesión), en lugar de
    incrustar la página de error en la ventana (decisión CHK025). En peticiones
    normales muestra `403_csrf.html`.
    """
    if not es_htmx(request):
        return csrf_failure(request, reason)

    respuesta = HttpResponse(status=403)
    respuesta['HX-Refresh'] = 'true'
    return respuesta
