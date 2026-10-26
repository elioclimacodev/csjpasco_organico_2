from django.utils.safestring import mark_safe
from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    '''
    Reemplaza o añade parámetros en la querystring actual.
    Preserva todos los parámetros existentes excepto los que 
    se sobreescriben.
    '''
    
    query = context['request'].GET.copy()
    for k, v in kwargs.items():
        query[k] = v
    return query.urlencode()


@register.inclusion_tag(
    'components/datatable/displays/sortable_header.html',
    takes_context=True
)
def sortable_header(context, field, label):
    data = context.flatten()
    data.update({
        'field': field,
        'label': label,
        'order_by': context.get('order_by'),
        'direction': context.get('direction'),
    })
    return data

@register.simple_tag(takes_context=True)
def sort_url(context, field):
    '''
    Contruye el querystring para ordenar por una columna,
    preservando todos los parámetros actuales: página, filtros,
    búsqueda, etc.
    
    Lógica de dirección:
    - Si ya se ordena por 'asc' -> cambia a 'desc'.
    - En cualquier otro caso -> ordena 'asc'.
    
    La página NO se resetea: el total de registros no cambia
    al reordenar, por lo que la página actual siempre sigue
    siendo válida.
    '''
    
    # Generamos una copia MUTABLE del QueryDict request.GET 
    # (query string de la URL actual).
    query = context['request'].GET.copy()
    
    current_sort = context.get('order_by', '')
    current_dir = context.get('direction', '')
    
    # Determina la nueva dirección.
    if current_sort == field and current_dir == 'asc':
        new_direction = 'desc'
    else:
        new_direction = 'asc'
        
    # Actualizar solo los parámetros de ordenación;
    # 'page' y el resto se conservan como están.
    query['order_by'] = field
    query['direction'] = new_direction
    
    return query.urlencode()


@register.filter
def status_badge(value):
    '''
    Muestra el estado de un registro con un badge en forma de cículo
    indicando si está activo (success) o inactivo (danger).
    '''
    if value:
        return mark_safe('<span class="badge bg-success me-1"></span>')
    return mark_safe('<span class="badge bg-danger me-1"></span>')


@register.filter
def status_badge_text(value):
    '''
    Muestra el estado de un registro con un badge en forma de cículo
    indicando si está activo (success) o inactivo (danger).
    '''
    if value:
        return mark_safe('<span class="badge bg-success me-1"></span>Activo')
    return mark_safe('<span class="badge bg-danger me-1"></span>Inactivo')


@register.filter
def status_circle_outline(value):
    '''
    Muestra el estado de un registro con un círculo con un chech o x
    según su estado activo (check success) o inactivo (x danger).
    '''
    if value:
        return mark_safe(
            '''
            <div class="text-center text-success">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor" class="icon icon-tabler icons-tabler-filled icon-tabler-check"><path stroke="none" d="M0 0h24v24H0z" fill="none" /><path d="M20.707 6.293a1 1 0 0 1 0 1.414l-10 10a1 1 0 0 1 -1.414 0l-5 -5a1 1 0 0 1 1.414 -1.414l4.293 4.293l9.293 -9.293a1 1 0 0 1 1.414 0" /></svg>
            </div>            
            '''
        )
    return mark_safe(
        '''
        <div class="text-center text-danger">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor" class="icon icon-tabler icons-tabler-filled icon-tabler-x"><path stroke="none" d="M0 0h24v24H0z" fill="none" /><path d="M6.707 5.293l5.293 5.292l5.293 -5.292a1 1 0 0 1 1.414 1.414l-5.292 5.293l5.292 5.293a1 1 0 0 1 -1.414 1.414l-5.293 -5.292l-5.293 5.292a1 1 0 1 1 -1.414 -1.414l5.292 -5.293l-5.292 -5.293a1 1 0 0 1 1.414 -1.414" /></svg>
        </div> 
        '''
    )

@register.filter
def status_si_no(value):
    '''
    Muestra el estado de un registro con un círculo con un chech o x
    según su estado activo (check success) o inactivo (x danger).
    '''
    if value:
        return mark_safe(
            '''
            <div class="text-center text-success">
                Sí
            </div>            
            ''')
    return mark_safe(
        '''
        <div class="text-center text-danger">
            No
        </div> 
        ''')

@register.filter
def empty_to_dashes(value):
    '''
    Muestra el caracter definido (...) en las celdas que no tienen 
    datos (null, '')
    '''
    if value is None or value == '':
        return mark_safe('<small class="text-secondary"><em>...</em></small>')
    return value


@register.inclusion_tag('components/datatable/displays/datagrid.html')
def render_datagrid(items):
    '''
    Muestra los datos de un registro en formato datagrid de Tabler.io
    '''
    return {'items': items}

@register.inclusion_tag(
    'components/datatable/datatable.html',
    takes_context=True,
)
def render_datatable(
    context,
    table_template,
    cards_template,
    toolbar_template=None,
    # export_url=None,
):
    return {
        **context.flatten(),
        'table_template': table_template,
        'cards_template': cards_template,
        'toolbar_template': toolbar_template,
        # 'export_url': export_url,
    }
    
@register.simple_tag(takes_context=True)
def datatable_state_inputs(context):
    '''
    Genera un <input type="hidden"> por cada parámetro GET activo
    (page, order_by, direction, search, filtros, etc.).

    Estos inputs se colocan DENTRO del innerHTML del #datatable
    para que sean reemplazados en cada swap. HTMX los lee via
    hx-include="[data-datatable-param]" y los envía como parte
    del request disparado por los eventos object_updated, etc.

    De esta forma el datatable siempre recarga con la página,
    orden y filtros que el usuario tenía en pantalla.

    Excluye parámetros vacíos para no ensuciar la URL.
    '''
    request = context['request']
    inputs = []

    for key, value in request.GET.items():
        # Ignorar valores vacíos
        if value:
            inputs.append(
                f'<input type="hidden" '
                f'data-datatable-param '
                f'name="{key}" '
                f'value="{value}">'
            )

    return mark_safe('\n'.join(inputs))