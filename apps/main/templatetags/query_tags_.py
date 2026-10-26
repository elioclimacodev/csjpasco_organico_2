from django import template
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe

register = template.Library()

# @register.simple_tag(takes_context=True)
# def url_replace(context, **kwargs):
#     '''
#     Reemplaza o añade parámetros en la querystring actual.
#     Preserva todos los parámetros existentes excepto los que 
#     se sobreescriben.
#     '''
    
#     query = context['request'].GET.copy()
#     for k, v in kwargs.items():
#         query[k] = v
#     return query.urlencode()


# @register.simple_tag(takes_context=True)
# def sort_url(context, field):
#     '''
#     Contruye el querystring para ordenar por una columna,
#     preservando todos los parámetros actuales: página, filtros,
#     búsqueda, etc.
    
#     Lógica de dirección:
#     - Si ya se ordena por 'asc' -> cambia a 'desc'.
#     - En cualquier otro caso -> ordena 'asc'.
    
#     La página NO se resetea: el total de registros no cambia
#     al reordenar, por lo que la página actual siempre sigue
#     siendo válida.
#     '''
    
#     # Generamos una copia MUTABLE del QueryDict request.GET 
#     # (query string de la URL actual).
#     query = context['request'].GET.copy()
    
#     current_sort = context.get('order_by', '')
#     current_dir = context.get('direction', '')
    
#     # Determina la nueva dirección.
#     if current_sort == field and current_dir == 'asc':
#         new_direction = 'desc'
#     else:
#         new_direction = 'asc'
        
#     # Actualizar solo los parámetros de ordenación;
#     # 'page' y el resto se conservan como están.
#     query['order_by'] = field
#     query['direction'] = new_direction
    
#     return query.urlencode()


# @register.simple_tag(takes_context=True)
# def datatable_state_inputs(context):
#     '''
#     Genera un <input type="hidden"> por cada parámetro GET activo
#     (page, order_by, direction, search, filtros, etc.).

#     Estos inputs se colocan DENTRO del innerHTML del #datatable
#     para que sean reemplazados en cada swap. HTMX los lee via
#     hx-include="[data-datatable-param]" y los envía como parte
#     del request disparado por los eventos object_updated, etc.

#     De esta forma el datatable siempre recarga con la página,
#     orden y filtros que el usuario tenía en pantalla.

#     Excluye parámetros vacíos para no ensuciar la URL.
#     '''
#     request = context['request']
#     inputs = []

#     for key, value in request.GET.items():
#         # Ignorar valores vacíos
#         if value:
#             inputs.append(
#                 f'<input type="hidden" '
#                 f'data-datatable-param '
#                 f'name="{key}" '
#                 f'value="{value}">'
#             )

#     return mark_safe('\n'.join(inputs))