
import json

from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.apps import apps
from django.urls import reverse
from django.http import HttpResponse

from apps.common.querysets import export_queryset_to_xlsx

from apps.ubicaciones.models import Departamento, Provincia
from apps.ubicaciones.forms import ProvinciaForm, ProvinciaFiltersForm


ALLOWED_ORDER_FIELDS = [
    'nombre_normalizado', 
    'ubigeo_inei', 'ubigeo_reniec',
    'codigo_postal', 'activo',
]


def filter_provincias(queryset, filters):
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


def sort_provincias(queryset, order_by, direction):
    '''
    Ordena el queryset solo en los campos permitidos.
    '''
    
    if order_by not in ALLOWED_ORDER_FIELDS:
        order_by = 'nombre_normalizado'
        
    prefix = '-' if direction == 'desc' else ''
    
    return queryset.order_by(f'{prefix}{order_by}')


@permission_required(
    'ubicaciones.view_provincia',
    raise_exception=True,
)
def provincias_list(request, dpto_id):
    '''
    Muestra las provincias de una región, permitiendo el 
    ordenamiento, paginación, filtros y exportación de la información.
    '''
    departamento = get_object_or_404(Departamento, pk=dpto_id)
    provincias = Provincia.objects.filter(departamento=departamento).select_related('departamento')
    unfiltered_count = provincias.count()
    
    # Filtros.
    form = ProvinciaFiltersForm(request.GET or None)
    form.setup_htmx(request.path)
    per_page = 10
    
    if form.is_valid():
        provincias = filter_provincias(
            queryset=provincias,
            filters=form.cleaned_data
        )
    
        per_page = form.cleaned_data.get('per_page') or 10
        
    # Ordenamiento.
    order_by = request.GET.get('order_by', 'nombre_normalizado')
    direction = request.GET.get('direction', 'asc')
    
    provincias = sort_provincias(
        queryset=provincias,
        order_by=order_by,
        direction=direction
    )
    
    # Paginación.
    try:
        page_num = int(request.GET.get('page', 1))
    except (ValueError, TypeError):
        page_num = 1
        
    paginator = Paginator(provincias, per_page)
    page_obj = paginator.get_page(page_num)
    
    # Rango de páginas con elipsis.
    page_range = paginator.get_elided_page_range(
        number=page_obj.number,
        on_each_side=2,
        on_ends=1
    )

    url = reverse(
        'ubicaciones:provincias_list', 
        kwargs={'dpto_id': departamento.pk}
    )
    
    # Si la petición es HTMX, renderiza una plantilla parcial.
    # Caso contrario renderiza la plantilla completa.
    if request.headers.get('HX-Request'):
        template = 'ubicaciones/provincias/partials/_datatable.html'
    else:
        template = 'ubicaciones/provincias/list.html'
    
    context = {
        'url': url,
        'pre_title': apps.get_app_config('ubicaciones').verbose_name,
        'title': f'Provincias de {departamento.nombre}, {departamento.pais.nombre}',
        'model_name': Provincia._meta.verbose_name,

        'form': form,

        'departamento': departamento,
        'page_obj': page_obj,
        'paginator': paginator,
        'is_empty_database': unfiltered_count == 0,

        'page_range': page_range,
        'order_by': order_by,
        'direction': direction,
    }
    
    return render(request, template, context)


@permission_required(
    'ubicaciones.add_provincia',
    raise_exception=True,
)
def provincia_create(request, dpto_id):
    '''
    Crea el registro de una provincia que pertenece a una región o departamento.
    '''
    departamento = get_object_or_404(Departamento, pk=dpto_id)

    template = 'ubicaciones/provincias/create.html'

    context = {
        'url': reverse('ubicaciones:provincia_create', kwargs={'dpto_id': departamento.pk}),
        'modal_title': f'Nueva provincia de {departamento.nombre}, {departamento.pais.nombre}',
        'departamento': departamento,
        'create': True,
    }
    
    if request.method == 'POST':
        form = ProvinciaForm(request.POST)
        if form.is_valid():
            provincia = form.save(commit=False)
            provincia.departamento = departamento
            provincia.save()
            
            # Determina qué botón fue presionado.
            action = request.GET.get('action')
            
            # Guardar y añadir otro.
            if action == 'save_and_add_another':
                # Crea un nuevo formulario vacío.
                form = ProvinciaForm()
                context['form'] = form
                
                # Renderiza la plantilla con el nuevo formulario.
                response = render(request, template, context)
            
                # Añade la cabecera HTMX (HX-Trigger) para lanzar los eventos
                # object_list_updated y show_toast.
                response['HX-Trigger'] = json.dumps({
                    'object_list_updated': None,
                    'show_toast': {
                        'type': 'success',
                        'message': f'La provincia "{provincia.nombre}", {departamento.nombre}, {departamento.pais.nombre}" se ha registrado con éxito.',
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
                                'message': f'La provincia "{provincia.nombre}", {departamento.nombre}, {departamento.pais.nombre}" se ha registrado con éxito.',
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
        form = ProvinciaForm()
        context['form'] = form
        return render(request, template, context)
    

@permission_required(
    'ubicaciones.view_provincia',
    raise_exception=True,
)
def provincia_details(request, dpto_id, pk):
    '''
    Muestra los datos de una provincia sin posibilidad de modificación.
    '''
    departamento = get_object_or_404(Departamento, pk=dpto_id)
    provincia = get_object_or_404(Provincia, pk=pk, departamento=departamento)

    template = 'ubicaciones/provincias/details.html'

    datagrid_items = [
        ('País'             , departamento.pais.nombre),
        ('Departamento'     , departamento.nombre),
        ('Provincia'        , provincia.nombre),
        ('ubigeo_inei'      , provincia.ubigeo_inei),
        ('ubigeo_reniec'    , provincia.ubigeo_reniec),
        ('codigo_postal'    , provincia.codigo_postal),
        ('Estado'           , provincia.activo),
    ]
    
    context = {
        'url': reverse(
            'ubicaciones:provincia_details', 
            kwargs={
                'dpto_id': departamento.pk,
                'pk': provincia.pk,
            }
        ),
        'modal_title': f'{provincia.get_full_name}',
        'departamento': departamento,
        'obj': provincia,
        'datagrid_items': datagrid_items,
    }

    return render(request, template, context)


@permission_required(
    'ubicaciones.change_provincia',
    raise_exception=True,
)
def provincia_update(request, dpto_id, pk):
    '''
    Modifica o actualiza el registro de una provincia.
    '''  
    departamento = get_object_or_404(Departamento, pk=dpto_id)
    provincia = get_object_or_404(Provincia, pk=pk, departamento=departamento)

    template = 'ubicaciones/provincias/create.html'

    context = {
        'url': reverse(
            'ubicaciones:provincia_update', 
            kwargs={
                'dpto_id': departamento.pk,
                'pk': provincia.pk,
            }
        ),
        'modal_title': f'Editar: {provincia.get_full_name}',
        'departamento': departamento,
        'provincia': provincia,
    }

    if request.method == 'POST':
        form = ProvinciaForm(request.POST, instance=provincia)
        if form.is_valid():
            form.save()

            return HttpResponse(
                status=204,
                headers={
                    'HX-Trigger': json.dumps({
                        'object_updated': None,
                        'show_toast': {
                            'type': 'success',
                            'message': f'{provincia.get_full_name} se actualizó con éxito.'
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
    else:
        context['form'] = ProvinciaForm(instance=provincia)
        return render(request, template, context)
    

@permission_required(
    'ubicaciones.change_provincia',
    raise_exception=True,
)
def provincia_toggle(request, dpto_id, pk):
    '''
    Cambia el estado del registro de la provincia de activo a inactivo y viceversa.
    '''
    departamento = get_object_or_404(Departamento, pk=dpto_id)
    provincia = get_object_or_404(Provincia, pk=pk, departamento=departamento.pk)

    template = 'ubicaciones/provincias/toggle.html'

    if request.method == 'POST':
        provincia.activo = not provincia.activo
        provincia.save()
        status = 'activó' if provincia.activo else 'desactivó'

        return HttpResponse(
            status=204,
            headers={
                'HX-Trigger': json.dumps({
                    'object_updated': None,
                    'show_toast': {
                        'type': 'success',
                        'message': f'La provincia de {provincia.get_full_name} se {status} con éxito.'
                    }
                })
            }
        )
    
    context = {
        'url': reverse(
            'ubicaciones:provincia_toggle', 
            kwargs={
                'dpto_id': departamento.pk,
                'pk': provincia.pk,}),
        'modal_title': f'Cambia el estado de la provincia {provincia.get_full_name}.',
        'provincia': provincia,
        'toggle': True,
    }

    response = render(request, template, context)
    response['HX-Modal-Size'] = 'modal-sm'
    return response


@permission_required(
    'ubicaciones.view_provincia',
    raise_exception=True,
)
def provincias_export(request, dpto_id):
    '''
    Exporta los datos filtrados y ordenados a un archivo xlsx.
    '''
    departamento = get_object_or_404(Departamento, pk=dpto_id)
    provincias = Provincia.objects.filter(departamento=departamento)

    # Filtros.
    form = ProvinciaFiltersForm(request.GET or None)
    form.setup_htmx(request.path)
    if form.is_valid():
        provincias = filter_provincias(
            queryset=provincias,
            filters=form.cleaned_data,
        )

    # Ordenamiento.
    order_by = request.GET.get('order_by', 'nombre_normalizado').strip()
    direction = request.GET.get('direction', 'asc')
    provincias = sort_provincias(
        queryset=provincias,
        order_by=order_by,
        direction=direction
    )

    columns = [
        {'header': 'País'           , 'field': 'pais_nombre'         , 'width': 20, 'format': 'cell'},
        {'header': 'Departamento'   , 'field': 'departamento_nombre' , 'width': 30, 'format': 'cell'},
        {'header': 'Provincia'      , 'field': 'nombre'              , 'width': 30, 'format': 'cell'},
        {'header': 'Ubigeo INEI'    , 'field': 'ubigeo_inei'         , 'width': 15, 'format': 'cell'},
        {'header': 'Ubigeo RENIEC'  , 'field': 'ubigeo_reniec'       , 'width': 15, 'format': 'cell'},
        {'header': 'Código Postal'  , 'field': 'codigo_postal'       , 'width': 15, 'format': 'cell'},
        {'header': 'Estado'         , 'field': 'activo'              , 'width': 15, 'format': 'boolean'},        
    ]

    return export_queryset_to_xlsx(
        queryset=provincias,
        columns_config=columns,
        filename=f'{'Provincias'}',
        sheet_name='Provincias',
    )