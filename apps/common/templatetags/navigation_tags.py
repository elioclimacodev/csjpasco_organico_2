# apps/common/templatetags/navigation_tags.py
from django import template

from apps.common.components.menu import build_sidebar

register = template.Library()


@register.simple_tag(takes_context=True)
def get_sidebar(context):
    """
    Entrega al template el menú lateral ya filtrado para el usuario actual.

    Uso: `{% get_sidebar as sidebar %}`. Devuelve None si no hay request o
    si el usuario no está autenticado, en cuyo caso el aside no se
    renderiza. El árbol solo determina lo que se muestra: no sustituye la
    autorización de cada vista (spec FR-008).
    """
    request = context.get('request')
    if request is None:
        return None
    return build_sidebar(request.user, request)
