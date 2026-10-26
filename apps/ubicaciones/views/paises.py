import json

from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.http import HttpResponse
from django.urls import reverse
from django.apps import apps

from apps.common.utils import normalize_alphanumeric, build_breadcrumbs
from apps.common.querysets import export_queryset_to_xlsx

from apps.ubicaciones.models import Pais
from apps.ubicaciones.forms import CountryForm, CountryFiltersForm

from apps.ubicaciones.breadcrumbs import ubicaciones_breadcrumbs

# Campos habilitados para el ordenamiento, previniendo SQL injection.
ALLOWED_ORDER_FIELDS = [
    'nombre_normalizado',
    'codigo_alpha2', 'codigo_alpha3', 'codigo_numerico',
    'codigo_internacional', 'activo',
]


def filter_countries(queryset, filters):
    '''
    Aplica filtros de búsqueda y estado al queryset de países.
    '''
    
    search = filters.get('search', '').strip()
    status = filters.get('status')
    
    if search:
        normalized_search = normalize_alphanumeric(search.lower())
        queryset = queryset.filter(
            Q(nombre_normalizado__icontains=normalized_search) |
            Q(codigo_alpha2__icontains=search) |
            Q(codigo_alpha3__icontains=search) |
            Q(codigo_numerico__icontains=search) |
            Q(codigo_internacional__icontains=search)
        )
        
    if status == '1':
        queryset = queryset.filter(activo=True)
    elif status == '0':
        queryset = queryset.filter(activo=False)
    
    return queryset


def sort_countries(queryset, order_by, direction):
    '''
    Ordena el queryset solo en los campos permitidos.
    '''
    
    if order_by not in ALLOWED_ORDER_FIELDS:
        order_by = 'nombre_normalizado'
        
    prefix = '-' if direction == 'desc' else ''
    
    return queryset.order_by(f'{prefix}{order_by}')


def countries_list(request):
    '''
    Muestra los países, permitiendo el ordenamiento, 
    paginación, filtros y exportación de la información.
    '''
        
    queryset = Pais.objects.all()
    unfiltered_count = queryset.count()
        
    # Filtros.
    form = CountryFiltersForm(request.GET or None)
    form.setup_htmx(request.path)
    per_page = 10
    
    if form.is_valid():
        queryset = filter_countries(
            queryset=queryset,
            filters=form.cleaned_data
        )
        
        per_page = form.cleaned_data.get('per_page') or 10
    elif hasattr(form, 'fields') and 'per_page' in form.fields:
        # Si no hay GET, intentamos sacar el valor por defecto definido en el formulario
        per_page = form.fields['per_page'].initial or 10

    
    # Ordenamiento.
    order_by = request.GET.get('order_by', 'nombre_normalizado')
    direction = request.GET.get('direction', 'asc')
    
    queryset = sort_countries(
        queryset=queryset,
        order_by=order_by,
        direction=direction
    )
    
    # Paginación
    try:
        page_num = int(request.GET.get('page', 1))
    except (ValueError, TypeError):
        page_num = 1
        
    paginator = Paginator(queryset, per_page)
    page_obj = paginator.get_page(page_num)
    
    # Rango de páginas con elipsis.
    page_range = paginator.get_elided_page_range(
        number=page_obj.number,
        on_each_side=2,
        on_ends=1,
    )
    
    # Breadcrumbs.
    paises_breadcrumbs = build_breadcrumbs(
        ('Países', None),
    )
    
    
    # Si la petición viene de un elemento HTMX, renderiza un partial,
    # en caso contrario rederiza la platilla completa.
    if request.headers.get('HX-Request'):
        template = 'ubicaciones/paises/partials/_datatable.html'
    else:
        template = 'ubicaciones/paises/countries_list.html'

    context = {
        'pre_title': apps.get_app_config('ubicaciones').verbose_name,
        'title': Pais._meta.verbose_name_plural,
        'model_name': Pais._meta.verbose_name,
        'breadcrumbs': ubicaciones_breadcrumbs + paises_breadcrumbs,
        
        'form': form,
        'object_list': page_obj.object_list,
        
        'page_obj': page_obj,       # Ítems y metadata de la página actual.
        'paginator': paginator,     # Objeto paginador completo número y rango de páginas.
        'page_range': page_range,   # Rango con elipsis.
        
        'is_empty_database': unfiltered_count == 0,
        'order_by': order_by,
        'direction': direction,
    }
    
    return render(request, template, context)
    

def country_create(request):
    '''
    Crea un nuevo registro de un país.
    '''   
    template = 'ubicaciones/paises/country_create.html'
    
    context = {
        'url': reverse('ubicaciones:country_create'),
        'modal_title': 'Nuevo país',
        'create': True,
    }
    
    if request.method == 'POST':
        form = CountryForm(request.POST)
        if form.is_valid():
            obj = form.save()
            
            # Determina qué botón fue presionado.
            action = request.POST.get('action')
            
            # Guardar y añadir otro.
            if action == 'save_and_add_another':
                # Crea un nuevo formulario vacío.
                form = CountryForm()
                context['form'] = form
                
                # Renderiza la plantilla con el nuevo formulario.
                response = render(request, template, context)
                
                # Lanza el evento 'object_list_updated' y envía el mensaje de éxito, al toast.
                response['HX-Trigger'] = json.dumps({
                    'object_list_updated': None,
                    'show_toast': {
                        'type': 'success',
                        'message': f'El país "{obj.nombre}" se ha registrado con éxito.'
                    }
                })
                return response
            
            # Guardar.
            else:
                # Devuelve una respuesta exitosa vacía.
                # Lanza los eventos 'object_created' y show_toast, para cerrar el modal y actualizar la UI.                
                return HttpResponse(
                    status=204,
                    headers={
                        'HX-Trigger': json.dumps({
                            'object_created': None,
                            'show_toast': {
                                'type': 'success',
                                'message': f'El país "{obj.nombre}" se ha registrado con éxito.'
                            }
                        })
                    }
                )
        # Formulario no válido.
        else:
            # Si el formulario tiene errores, lo muestra nuevamente
            # indicando los campos que han producido el error
            # y envía el mensaje al toast.
            context['form'] = form
            response = render(request, template, context)
            response['HX-Trigger'] = json.dumps({
                'show_toast': {
                    'type': 'error',
                    'message': 'El formulario contiene errores. Revise la información ingresada antes de continuar.'
                }
            })
            return response
    else:
        # En caso el método sea diferente a POST
        # muestra el formulario vacío.
        form = CountryForm()
        context['form'] = form
        return render(request, template, context)
            

def country_details(request, pk):
    '''
    Muestra los datos de un país, sin posibilidad de modificación.
    '''
    obj = get_object_or_404(Pais, pk=pk)

    datagrid_items = [
        ('Nombre',          obj.nombre),
        ('Código Alpha-2',  obj.codigo_alpha2),
        ('Código Alpha-3',  obj.codigo_alpha3),
        ('Código Numérico', obj.codigo_numerico),
        ('Código de llamada internacional', obj.codigo_internacional),
        ('Estado',          obj.activo),
    ]
    
    template = 'ubicaciones/paises/country_details.html'
    
    context = {
        'url': reverse('ubicaciones:country_details', kwargs={'pk': pk}),
        'modal_title': obj.nombre,
        'obj': obj,
        'datagrid_items': datagrid_items,
    }
    return render(request, template, context)


def country_update(request, pk):
    '''
    Modifica o actualiza el registro de un País.
    '''
    obj = get_object_or_404(Pais, pk=pk)
    print(f'--> {obj.id} {obj.nombre}')

    template = 'ubicaciones/paises/country_create.html'

    context = {
        'url': reverse('ubicaciones:country_update', kwargs={'pk': pk}),
        'modal_title': f'Editar: {obj.nombre}',
        'obj': obj,
        'update': True,
    }
    
    if request.method == 'POST':
        form = CountryForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            
            response = HttpResponse(
                status=204,
                headers={
                    'HX-Trigger': json.dumps({
                        'object_updated': None,
                        'show_toast': {
                            'type': 'success',
                            'message': f'El país "{obj.nombre}" se actualizó con éxito.'
                        }
                    })
                }
            )
            return response
        else:
            context['form'] = form
            response = render(request, template, context)
            response['HX-Trigger'] = json.dumps({
                'show_toast': {
                    'type': 'error',
                    'message': 'El formulario contiene errores. Revise la información ingresada antes de continuar.'
                }
            })
            return response
    else:
        form = CountryForm(instance=obj)
        context['form'] = form
        return render(request, template, context)
            
    
def country_toggle(request, pk):
    '''
    Cambia el estado del registro de activo a inactivo y viceversa.
    '''
    
    obj = get_object_or_404(Pais, pk=pk)
    
    template = 'ubicaciones/paises/country_toggle.html'
    
    context = {
        'url': reverse('ubicaciones:country_toggle', kwargs={'pk': pk}),
        'obj': obj,
        'toggle': True,
        'modal_title': f'Cambia el estado del país {obj.nombre}',
        'modal_type': 'danger' if obj.activo else 'success',
    }    
    
    if request.method == 'POST':
        obj.activo = not obj.activo
        obj.save()
        toggle = 'activó' if obj.activo else 'desactivó'
        
        response = HttpResponse(
            status=204,
            headers={
                'HX-Trigger': json.dumps({
                    'object_updated': None,
                    'show_toast': {
                        'type': 'success',
                        'message': f'El país "{obj.nombre}" se {toggle} con éxito.',
                    }
                })
            }
        )
        return response
    
    response = render(request, template, context)
    response['HX-Modal-Size'] = 'modal-sm'
    return response


def countries_export(request):
    '''
    Exporta los datos filtrados y ordenados a formato xlsx.
    '''
    
    countries = Pais.objects.all()
    
    # Filtros.
    form = CountryFiltersForm(request.GET or None)
    form.setup_htmx(request.path)
    
    if form.is_valid():
        countries = filter_countries(
            queryset=countries,
            filters=form.cleaned_data
        )

    # Ordenamiento.
    order_by = request.GET.get('order_by', 'nombre_normalizado').strip()
    direction = request.GET.get('direction', 'asc')
    
    countries = sort_countries(
        queryset=countries,
        order_by=order_by,
        direction=direction,
    )
    
    columns = [
        {'header': 'País', 'field': 'nombre', 'with': 30, 'format': 'cell'},
        {'header': 'Código Alpha-2', 'field': 'codigo_alpha2', 'with': 5, 'format': 'cell'},
        {'header': 'Código Alpha-3', 'field': 'codigo_alpha3', 'with': 6, 'format': 'cell'},
        {'header': 'Código Numérico', 'field': 'codigo_numerico', 'with': 6, 'format': 'cell'},
        {'header': 'Código Internacional', 'field': 'codigo_internacional', 'with': 7, 'format': 'cell'},
        {'header': 'Estado', 'field': 'activo', 'width': 15, 'format': 'boolean'},        
    ]
    
    return export_queryset_to_xlsx(
        queryset=countries,
        columns_config=columns,
        filename='Países',
        sheet_name='Países',
    )
    