# apps/core/templatetags/breadcrumb_tags.py
from django import template

register = template.Library()


@register.inclusion_tag('components/navigation/breadcrumbs/breadcrumbs.html')
def render_breadcrumbs(breadcrumbs, max_visible=5, start_count=2, end_count=2):
    """
    Renderiza una ruta de navegación (breadcrumbs) colapsando los niveles
    intermedios en una elipsis desplegable cuando la cantidad de niveles
    supera `max_visible` (patrón inspirado en Notion).

    :param breadcrumbs: Lista de instancias `Breadcrumb`, en orden desde
        la raíz hasta el nivel actual.
    :param max_visible: Umbral a partir del cual se activa el colapso.
    :param start_count: Cantidad de niveles a mantener siempre visibles
        al inicio de la ruta.
    :param end_count: Cantidad de niveles a mantener siempre visibles
        al final de la ruta (incluye el nivel actual).
    """
    total = len(breadcrumbs)

    # Solo colapsamos si realmente sobran niveles que ocultar; de lo
    # contrario mostramos la ruta completa sin elipsis.
    if total > max_visible and total > start_count + end_count:
        start_items = breadcrumbs[:start_count]
        end_items = breadcrumbs[-end_count:]
        hidden_items = breadcrumbs[start_count: total - end_count]
    else:
        start_items = breadcrumbs
        end_items = []
        hidden_items = []

    return {
        'start_items': start_items,
        'end_items': end_items,
        'hidden_items': hidden_items,
        'show_ellipsis': bool(hidden_items),
    }