import json

from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.http import HttpResponse
from django.apps import apps
from django.urls import reverse

from apps.common.querysets import export_queryset_to_xlsx
from apps.common.utils import normalize_alphanumeric, build_breadcrumbs

from apps.ubicaciones.models import Pais, Departamento
from apps.ubicaciones.forms import DepartamentoForm, DepartamentoFiltersForm
from apps.ubicaciones.breadcrumbs import ubicaciones_breadcrumbs


# Evita SQL injection habilitando los campos que tendrán ordenamiento.
ALLOWED_ORDER_FIELDS = [
    'nombre_normalizado', 
    'ubigeo_inei', 'ubigeo_reniec',
    'codigo_postal', 'activo',
]

def filter_regions(queryset, filters):
    '''
    Aplica filtros de búsqueda y estado al queryset de regiones.
    '''    
    search = filters.get('search', '').strip()
    status = filters.get('status')
    
    if search:
        normalized_search = normalize_alphanumeric(search.lower())
        queryset = queryset.filter(            
            Q(nombre_normalizado__icontains=normalized_search) |
            Q(ubigeo_inei__icontains=search) |
            Q(ubigeo_reniec__icontains=search) |
            Q(codigo_postal__icontains=search)
        )

    if status == '0':
        queryset = queryset.filter(activo=False)
    elif status == '1':
        queryset = queryset.filter(activo=True)

    return queryset


def sort_regions(queryset, order_by, direction):
    '''
    Ordena el queryset, solo en los campos permitidos.
    '''
    
    if order_by not in ALLOWED_ORDER_FIELDS:
        order_by = 'nombre_normalizado'
        
    prefix = '-' if direction == 'desc' else ''
    
    return queryset.order_by(f'{prefix}{order_by}')


@permission_required(
    'ubicaciones.view_departamento',
    raise_exception=True,
)
def departamentos_list(request, pais_id):
    '''
    Muestra las regiones de un país, permitiendo el 
    ordenamiento, paginación, filtrado y exportación de la información.
    '''
    
    # País.    
    pais = get_object_or_404(Pais, pk=pais_id)
    
    # Queryset base.
    queryset = Departamento.objects.filter(pais=pais).select_related('pais')
    unfilteder_count = queryset.count()
    
    # Filtros: Pasamos request.GET para que tome los valores por defecto
    #          si está vacío.
    form = DepartamentoFiltersForm(request.GET or None)
    form.setup_htmx(request.path)
    per_page = 10
    
    # Si el formulario tiene datos y es válido, filtramos
    if request.GET and form.is_valid():
        queryset = filter_regions(
            queryset=queryset,
            filters=form.cleaned_data,
        )
        
        per_page = form.cleaned_data.get('per_page') or 10
    elif hasattr(form, 'fields') and 'per_page' in form.fields:
        # Si no hay GET, intentamos sacar el valor por defecto definido en el formulario
        per_page = form.fields['per_page'].initial or 10

        
    # Ordenamiento.
    order_by = request.GET.get('order_by', 'nombre_normalizado').strip()
    direction = request.GET.get('direction', 'asc').strip()
    
    queryset = sort_regions(
        queryset=queryset,
        order_by=order_by,
        direction=direction,
    )
    
    # Paginación.
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
        on_ends=1
    )
    
    # ── Breadcrumbs ──────────────────
    url = reverse('ubicaciones:departamentos_list', kwargs={'pais_id': pais.pk})
    
    departamentos_breadcrumbs = build_breadcrumbs(
        ('Países', reverse('ubicaciones:countries_list')),
        (pais.nombre, url),
        ('Departamentos', None),
    )

    # Si la petición viene de un elemento HTMX, renderiza un partial,
    # en caso contrario rederiza la platilla completa.
    if request.headers.get('HX-Request'):
        template = 'ubicaciones/departamentos/partials/_datatable.html'
    else:
        template = 'ubicaciones/departamentos/list.html'
    
    context = {
        'url': url,
        'pre_title': apps.get_app_config('ubicaciones').verbose_name,
        'title': f'Departamentos de {pais.nombre}',
        'model_name': Departamento._meta.verbose_name,
        'breadcrumbs': ubicaciones_breadcrumbs + departamentos_breadcrumbs,

        'pais': pais,

        'form': form,
        'object_list': page_obj.object_list,
        
        'paginator': paginator,
        'page_obj': page_obj,
        'page_range': page_range,
        
        'is_empty_database': unfilteder_count == 0,
        'order_by': order_by,
        'direction': direction,
    }

    return render(request, template, context)
    
    
@permission_required(
    'ubicaciones.add_departamento',
    raise_exception=True,
)
def departamento_create(request, pais_id):
    '''
    Crea el registro de una región/departamento de un país.
    '''
    
    pais = get_object_or_404(Pais, pk=pais_id)
    
    template = 'ubicaciones/departamentos/create.html'
        
    context = {
        'url': reverse('ubicaciones:departamento_create', kwargs={'pais_id': pais.pk}), # Vuelve a cargar el formulario en el modal, si se guarda y añade otro.
        'modal_title': f'Nuevo departamento de {pais.nombre}',
        'country': pais,
        'create': True,
    }
    
    if request.method == 'POST':
        form = DepartamentoForm(request.POST)
        if form.is_valid():
            departamento = form.save(commit=False)
            departamento.pais = pais
            departamento.save()
            
            # Determina qué botón fue presionado.
            action = request.POST.get('action')
            
            # Opción A: Guardar y añadir otro.
            if action == 'save_and_add_another':
                # Crea un nuevo formulario vacío.
                context['form'] = DepartamentoForm()
                
                # Renderiza la plantilla con el nuevo formulario.
                response = render(request, template, context)
            
                # Lanza el evento 'object_list_updated' y envía el mensaje de éxito, al toast.
                response['HX-Trigger'] = json.dumps({
                    'object_list_updated': None,
                    'show_toast': {
                        'type': 'success',
                        'message': f'"{departamento.nombre}, {pais.nombre}" se ha registrado con éxito.',
                    }
                })
                return response
            
            # Opción B: Guardar (cierra el modal).
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
                                'message': f'"{departamento.nombre}, {pais.nombre}" se ha registrado con éxito.',
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
        context['form'] = DepartamentoForm()
        return render(request, template, context)
            

@permission_required(
    'ubicaciones.view_departamento',
    raise_exception=True,
)
def departamento_details(request, pais_id, pk):
    '''
    Muestra los datos de una región sin posiblidad de modificación.
    '''
    
    pais = get_object_or_404(Pais, pk=pais_id)
    departamento = get_object_or_404(Departamento, pk=pk, pais=pais)
    
    
    template = 'ubicaciones/departamentos/details.html'

    datagrid_items = [
        ('País',            pais.nombre),
        ('Departamento',    departamento.nombre),
        ('ubigeo_inei',     departamento.ubigeo_inei),
        ('ubigeo_reniec',   departamento.ubigeo_reniec),
        ('codigo_postal',   departamento.codigo_postal),
        ('Estado',          departamento.activo),
    ]
    
    context = {
        'url': reverse(
            'ubicaciones:departamento_details', 
            kwargs={
                'pais_id': pais.pk, 
                'pk': departamento.pk
            }
        ),
        'modal_title': f'{departamento.nombre}, {pais.nombre}',
        'obj': departamento,
        'pais': pais,
        'datagrid_items': datagrid_items,
    }
    
    return render(request, template, context)
    
    
@permission_required(
    'ubicaciones.change_departamento',
    raise_exception=True,
)
def departamento_update(request, pais_id, pk):
    '''
    Modifica o actualiza el registro de una región.
    '''
    pais = get_object_or_404(Pais, pk=pais_id)
    departamento = get_object_or_404(Departamento, pk=pk, pais=pais)
      
    template = 'ubicaciones/departamentos/create.html'
    
    context = {
        'url': reverse(
            'ubicaciones:departamento_update', 
            kwargs={
                'pais_id': pais.pk,
                'pk': departamento.pk,
            }
        ),
        'modal_title': f'Editar: {departamento.nombre}, {pais.nombre}',
        'obj': departamento,
        'update': True,
    }
    
    if request.method == 'POST':
        form = DepartamentoForm(request.POST, instance=departamento)
        if form.is_valid():
            # obj = form.save(commit=False)
            form.save()
            
            response = HttpResponse(
                status=204,
                headers={
                    'HX-Trigger': json.dumps({
                        'object_updated': None,
                        'show_toast': {
                            'type': 'success',
                            'message': f'"{departamento.nombre}, {pais.nombre}" se actualizó con éxito.'
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
        form = DepartamentoForm(instance=departamento)
        context['form'] = form
        return render(request, template, context)
            

@permission_required(
    'ubicaciones.change_departamento',
    raise_exception=True,
)
def departamento_toggle(request, pais_id, pk):
    '''
    Cambia el estado del registro de activo a inactivo y viceversa.
    '''
    pais = get_object_or_404(Pais, pk=pais_id)
    departamento = get_object_or_404(Departamento, pk=pk, pais=pais)
    
    template = 'ubicaciones/departamentos/toggle.html'
    
    if request.method == 'POST':
        departamento.activo = not departamento.activo
        departamento.save()
        status = 'activó' if departamento.activo else 'desactivó'
        
        response = HttpResponse(
            status=204,
            headers={
                'HX-Trigger': json.dumps({
                    'object_updated': None,
                    'show_toast': {
                        'type': 'success',
                        'message': f'"{departamento.nombre}, {pais.nombre}" se {status} con éxito.'
                    }
                })
            }
        )
        return response
    
    context = {
        'url': reverse(
            'ubicaciones:departamento_toggle', 
            kwargs={
                'pais_id': pais.pk,
                'pk': departamento.pk,
            }
        ),
        'modal_title': f'Cambia el estado de {departamento.nombre}, {pais.nombre}',
        'modal_type': 'danger' if departamento.activo else 'success',
        'toggle': True,
        'obj': departamento,
    }    
    
    response = render(request, template, context)
    response['HX-Modal-Size'] = 'modal-sm'
    return response
    
        
@permission_required(
    'ubicaciones.view_departamento',
    raise_exception=True,
)
def departamento_export(request, pais_id):
    '''
    Exporta los datos filtrados y ordenados a formato xlsx.
    '''
    
    pais = get_object_or_404(Pais, pk=pais_id)
    departamentos = Departamento.objects.filter(pais=pais)
    
    # Filtros.
    form = DepartamentoFiltersForm(request.GET or None)
    form.setup_htmx(request.path)
    if request.GET and form.is_valid():
        departamentos = filter_regions(
            queryset=departamentos,
            filters=form.cleaned_data,
        )     
        
    # Ordenamiento.
    order_by = request.GET.get('order_by', 'nombre_normalizado').strip()
    direction = request.GET.get('direction', 'asc').strip()
    
    departamentos = sort_regions(
        queryset=departamentos,
        order_by=order_by,
        direction=direction,
    )
    
    columns = [
        {'header': 'País',          'field': 'pais_nombre',     'width': 20,    'format': 'cell'},
        {'header': 'Departamento',  'field': 'nombre',          'width': 30,    'format': 'cell'},
        {'header': 'Ubigeo INEI',   'field': 'ubigeo_inei',     'width': 15,    'format': 'cell'},
        {'header': 'Ubigeo RENIEC', 'field': 'ubigeo_reniec',   'width': 15,    'format': 'cell'},
        {'header': 'Código Postal', 'field': 'codigo_postal',   'width': 15,    'format': 'cell'},
        {'header': 'Estado',        'field': 'activo',          'width': 15,    'format': 'boolean'}, 
    ]
    
    return export_queryset_to_xlsx(
        queryset=departamentos,
        columns_config=columns,
        filename=f'Departamentos_{pais.nombre}',
        sheet_name='Departamentos',
    )
