import json

from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.apps import apps
from django.urls import reverse
from django.http import HttpResponse

from apps.common.querysets import export_queryset_to_xlsx
from apps.common.components import Breadcrumb

from apps.ubicaciones.models import Distrito, Provincia
from apps.ubicaciones.forms import DistritoForm, DistritoFiltersForm


ALLOWED_ORDER_FIELDS = [
    'nombre_normalizado', 'ubigeo_inei', 'ubigeo_reniec',
    'codigo_postal', 'activo',
]


def filter_districts(queryset, filters):
    '''
    Aplica los filtros de búsqueda y estado al queryset de provincias.
    '''
    search = filters.get('search', '').strip()
    status = filters.get('status')
    
    if search:
        queryset = queryset.filter(
            Q(nombre_normalizado__icontains=search) |
            Q(ubigeo_inei__icontains=search) |
            Q(ubigeo_reniec__icontains=search) |
            Q(codigo_postal__icontains=search) 
        )
    
    if status == '1':
        queryset = queryset.filter(activo=True)
    elif status == '0':
        queryset = queryset.filter(activo=False)
        
    return queryset


def sort_districts(queryset, order_by, direction):
    '''
    Ordena el queryset solo en los campos permitidos.
    '''
    
    if order_by not in ALLOWED_ORDER_FIELDS:
        order_by = 'nombre_normalizado'
        
    prefix = '-' if direction == 'desc' else ''
    
    return queryset.order_by(f'{prefix}{order_by}')


def distritos_list(request, prov_id):
    '''
    Muestra las provincias de una región, permitiendo el 
    ordenamiento, paginación, filtros y exportación de la información.
    '''
    provincia = get_object_or_404(Provincia, pk=prov_id)
    distritos = Distrito.objects.filter(provincia=provincia)
    unfiltered_distritos = distritos.count()
    
    # Filtros.
    form = DistritoFiltersForm(request.GET or None)
    form.setup_htmx(request.path)
    per_page = 10
    
    if form.is_valid():
        distritos = filter_districts(
            queryset=distritos,
            filters=form.cleaned_data
        )
    
        per_page = form.cleaned_data.get('per_page') or 10
        
    # Ordenamiento.
    order_by = request.GET.get('order_by', 'nombre_normalizado')
    direction = request.GET.get('direction', 'asc')
    
    distritos = sort_districts(
        queryset=distritos,
        order_by=order_by,
        direction=direction
    )
    
    # Paginación.
    try:
        page_num = int(request.GET.get('page', 1))
    except (ValueError, TypeError):
        page_num = 1
        
    paginator = Paginator(distritos, per_page)
    page_obj = paginator.get_page(page_num)
    
    # Rango de páginas con elipsis.
    page_range = paginator.get_elided_page_range(
        number=page_obj.number,
        on_each_side=2,
        on_ends=1
    )

    url = reverse(
        'ubicaciones:distritos_list',
        kwargs={'prov_id': provincia.pk},
    )

    context = {
        'url': url,
        'pre_title': apps.get_app_config('ubicaciones').verbose_name,
        'title': f'Distritos de {provincia.get_full_name}',
        'model_name': Distrito._meta.verbose_name,

        'form': form,

        'provincia': provincia,
        'page_obj': page_obj,
        'paginator': paginator,
        'is_empty_database': unfiltered_distritos == 0,

        'page_range': page_range,
        'order_by': order_by,
        'direction': direction,
    }
    
    # Si la petición es HTMX, renderiza una plantilla parcial.
    # Caso contrario renderiza la plantilla completa.
    if request.headers.get('HX-Request'):
        template = 'ubicaciones/distritos/partials/_datatable.html'
    else:
        template = 'ubicaciones/distritos/list.html'
        context['breadcrumbs'] = [
            Breadcrumb(
                label=apps.get_app_config('ubicaciones').verbose_name,
                url=reverse('ubicaciones:countries_list'),
            ),
            Breadcrumb(
                label='Regiones',
                url='',
            ),
            Breadcrumb(
                label=provincia.departamento.nombre,
                url='',
            ),
            Breadcrumb(
                label=provincia.nombre,
                url='',
            ),
            Breadcrumb(label='Distritos'),  # Nivel actual, sin enlace.
        ]        
    

    
    return render(request, template, context)


def distrito_create(request, prov_id):
    '''
    Crea el registro de una provincia que pertenece a una región o departamento.
    '''

    provincia = get_object_or_404(Provincia, pk=prov_id)

    template = 'ubicaciones/distritos/create.html'

    context = {
        'modal_title': f'Nueva distrito de {provincia.get_full_name}',
        'provincia': provincia,
        'create': True,
        'url': reverse(
            'ubicaciones:distrito_create', 
            kwargs={'prov_id': provincia.pk}),
    }
    
    if request.method == 'POST':
        form = DistritoForm(request.POST)
        if form.is_valid():
            distrito = form.save(commit=False)
            distrito.provincia = provincia
            distrito.save()
            
            # Determina qué botón fue presionado.
            action = request.POST.get('action')
            
            # Guardar y añadir otro.
            if action == 'save_and_add_another':
                # Crea un nuevo formulario vacío.
                form = DistritoForm()
                context['form'] = form
                
                # Renderiza la plantilla con el nuevo formulario.
                response = render(request, template, context)
            
                # Añade la cabecera HTMX (HX-Trigger) para lanzar los eventos
                # object_list_updated y show_toast.
                response['HX-Trigger'] = json.dumps({
                    'object_list_updated': None,
                    'show_toast': {
                        'type': 'success',
                        'message': f'El distrito "{distrito.nombre}" se ha registrado con éxito.',
                    }
                })
                return response
            # Guardar
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
                                'message': f'El distrito "{distrito.nombre}" se ha registrado con éxito.',
                            }
                        })
                    }
                )
        else:
            # Si el formulario tiene errores, lo muestra nuevamente
            # indicando los campos que han producido el error
            # y envía el mensaje al toast.      
            context['form'] = form
            response = render(request, template, context)
            response['HX-Trigger'] = json.dumps({
                'show_toast': {
                    'type': 'error',
                    'message': 'El formulario contiene errores. Revise la información ingresada antes de continuar.',
                }
            })
            return response
    else:
        # En caso el método sea diferente a POST
        # muestra el formulario vacío.
        form = DistritoForm()
        context['form'] = form
        return render(request, template, context)
    

def distrito_details(request, prov_id, pk):
    '''
    Muestra los datos de una provincia sin posibilidad de modificación.
    '''
    
    provincia = get_object_or_404(Provincia, pk=prov_id)
    distrito = get_object_or_404(Distrito, pk=pk, provincia=provincia)

    template = 'ubicaciones/distritos/details.html'

    datagrid_items = [
        ('País'             , provincia.departamento.pais.nombre),
        ('Departamento'     , provincia.departamento.nombre),
        ('Provincia'        , provincia.nombre),
        ('Distrito'         , distrito.nombre),
        ('Ubigeo INEI'      , distrito.ubigeo_inei),
        ('ubigeo RENIEC'    , distrito.ubigeo_reniec),
        ('Estado'           , distrito.activo),
    ]
    
    context = {
        'datagrid_items': datagrid_items,
        'modal_title': f'{distrito.get_full_name}',
        'distrito': distrito,
        'url': reverse(
            'ubicaciones:distrito_details', 
            kwargs={
                'prov_id': provincia.pk,
                'pk': pk}),
    }

    return render(request, template, context)


def distrito_update(request, prov_id, pk):
    '''
    Modifica o actualiza el registro de una provincia.
    '''
    
    provincia = get_object_or_404(Provincia, pk=prov_id)
    distrito = get_object_or_404(Distrito, pk=pk, provincia=provincia)

    template = 'ubicaciones/distritos/create.html'

    context = {
        'modal_title': f'{distrito.get_full_name}',
        'provincia': provincia,
        'distrito': distrito,
        'url': reverse(
            'ubicaciones:distrito_update', 
            kwargs={
                'prov_id': provincia.pk,
                'pk': pk}),
    }

    if request.method == 'POST':
        form = DistritoForm(request.POST, instance=distrito)
        if form.is_valid():
            form.save()

            return HttpResponse(
                status=204,
                headers={
                    'HX-Trigger': json.dumps({
                        'object_updated': None,
                        'show_toast': {
                            'type': 'success',
                            'message': f'La provincia de "{distrito.nombre}" se actualizó con éxito.'
                        }
                    })
                }
            )
        else:
            context['form'] = form
            response = render(request, template, context)
            response['HX-Trigger'] = json.dumps({
                'show_toast': {
                    'type': 'error',
                    'message': 'El formulario contiene errores. Revise la información ingresada antes de continuar.',
                }
            })
            return response
    else:
        context['form'] = DistritoForm(instance=distrito)
        return render(request, template, context)
    

def distrito_toggle(request, prov_id, pk):
    '''
    Cambia el estado del registro de la provincia de activo a inactivo y viceversa.
    '''

    provincia = get_object_or_404(Provincia, pk=prov_id)
    distrito = get_object_or_404(Distrito, pk=pk, provincia=provincia)

    template = 'ubicaciones/distritos/toggle.html'

    context = {
        'modal_title': f'Cambia el estado del distrito "{distrito.get_full_name}".',
        'obj': distrito,
        'toggle': True,
        'url': reverse(
            'ubicaciones:distrito_toggle', 
            kwargs={
                'prov_id': provincia.pk,
                'pk': pk}),
    }

    if request.method == 'POST':
        distrito.activo = not distrito.activo
        distrito.save()
        status = 'activó' if distrito.activo else 'desactivó'

        response = HttpResponse(
            status=204,
            headers={
                'HX-Trigger': json.dumps({
                    'object_updated': None,
                    'show_toast': {
                        'type': 'success',
                        'message': f'La provincia de {distrito.nombre} se {status} con éxito.'
                    }
                })
            }
        )
        return response
    
    response = render(request, template, context)
    response['HX-Modal-Size'] = 'modal-sm'
    return response


def distritos_export(request, prov_id):
    '''
    Exporta los datos filtrados y ordenados a un archivo xlsx.
    '''
    distritos = Distrito.objects.filter(provincia=prov_id)

    # Filtros.
    form = DistritoFiltersForm(request.GET or None)
    form.setup_htmx(request.path)
    if form.is_valid():
        distritos = filter_districts(
            queryset=distritos,
            filters=form.cleaned_data,
        )

    # Ordenamiento.
    order_by = request.GET.get('order_by', 'nombre_normalizado').strip()
    direction = request.GET.get('direction', 'asc')
    distritos = sort_districts(
        queryset=distritos,
        order_by=order_by,
        direction=direction
    )

    columns = [
        {'header': 'País'           , 'field': 'pais_nombre'         , 'width': 20, 'format': 'cell'},
        {'header': 'Departamento'   , 'field': 'departamento_nombre' , 'width': 30, 'format': 'cell'},
        {'header': 'Provincia'      , 'field': 'provincia_nombre'    , 'width': 30, 'format': 'cell'},
        {'header': 'Distrito'       , 'field': 'nombre'              , 'width': 30, 'format': 'cell'},        
        {'header': 'Ubigeo INEI'    , 'field': 'ubigeo_inei'         , 'width': 15, 'format': 'cell'},
        {'header': 'Ubigeo RENIEC'  , 'field': 'ubigeo_reniec'       , 'width': 15, 'format': 'cell'},
        {'header': 'Código Postal'  , 'field': 'codigo_postal'       , 'width': 15, 'format': 'cell'},
        {'header': 'Estado'         , 'field': 'activo'              , 'width': 15, 'format': 'boolean'},        
    ]

    return export_queryset_to_xlsx(
        queryset=distritos,
        columns_config=columns,
        filename=f'{'Distritos'}',
        sheet_name='Distritos',
    )
