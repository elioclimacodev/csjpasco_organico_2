import io
import json
import xlsxwriter

from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.http import HttpResponse
from django.urls import reverse
from django.apps import apps

from apps.common.utils import normalize_alphanumeric, format_proper_name
from apps.common.querysets import export_queryset_to_xlsx

from apps.organizacion.models.distrito_judicial import DistritoJudicial
from apps.organizacion.forms import DistritoJudicialForm, DistritoJudicialFiltersForm


ORDER_FIELDS = {
    'nombre': 'nombre_normalizado',
    'siglas': 'siglas',
    'latitud': 'latitud',
    'longitud': 'longitud',
    'activo': 'activo',
}

def sort_distrito_judicial(queryset, order_by, direction):
    '''
    Ordena el queryset solo en los campos permitidos.
    '''
    field = ORDER_FIELDS.get(order_by, 'nombre_normalizado')
    
    prefix = '-' if direction == 'desc' else ''
    
    return queryset.order_by(f'{prefix}{field}')


def filter_distrito_judicial(queryset, filters):
    '''
    Aplica filtros de búsqueda y estado al queryset.
    '''
    search = filters.get('search','').strip()
    status = filters.get('status')

    if search:
        normalized_search = normalize_alphanumeric(search.lower())
        queryset = queryset.filter(
            Q(nombre_normalizado__icontains=normalized_search) |
            Q(siglas__icontains=search) |
            Q(latitud__icontains=search) |
            Q(longitud__icontains=search)
        )
    
    if status == '1':
        queryset = queryset.filter(activo=True)
    elif status == '0':
        queryset = queryset.filter(activo=False)
    
    return queryset


@permission_required(
    'organizacion.view_distritojudicial',
    raise_exception=True,
)
def distritos_judiciales_list(request):
    '''
    Muestra los Distritos Judiciales permitiendo su ordenamiento, paginación,
    filtros y exportación como archivo xlsx.
    '''
    queryset = DistritoJudicial.objects.all()
    unfiltered_count = queryset.count()

    # Filtros.
    form = DistritoJudicialFiltersForm(request.GET or None)
    form.setup_htmx(request.path)
    per_page = 10

    if form.is_valid():
        queryset = filter_distrito_judicial(
            queryset=queryset,
            filters=form.cleaned_data
        )


        per_page = form.cleaned_data.get('per_page') or 10

    # Ordenamiento.
    order_by = request.GET.get('order_by', 'nombre').strip()
    direction = request.GET.get('direction', 'asc')

    queryset = sort_distrito_judicial(
        queryset=queryset,
        order_by=order_by,
        direction=direction
    )

    # Paginación.
    try:
        page_num = int(request.GET.get('page', 1))
    except (TypeError, ValueError):
        page_num = 1

    paginator = Paginator(queryset, per_page)
    page_obj = paginator.get_page(page_num)
    page_range = paginator.get_elided_page_range(
        number=page_obj.number,
        on_each_side=2,
        on_ends=1,
    )

    # Si la petición viene de un elemento HTMX, renderiza un partial,
    # en caso contrario rederiza la platilla completa.
    if request.headers.get('HX-Request'):
        template = 'organizacion/distrito_judicial/partials/_datatable.html'
    else:
        template = 'organizacion/distrito_judicial/list.html'

    context = {
        'pre_title': apps.get_app_config('organizacion').verbose_name,
        'title': DistritoJudicial._meta.verbose_name_plural,
        'model_name': DistritoJudicial._meta.verbose_name,
        'form': form,
        'page_obj': page_obj,        
        'paginator': paginator,
        'page_range': page_range,
        'is_empty_database': unfiltered_count == 0,
        'order_by': order_by,
        'direction': direction,
    }

    return render(request, template, context)


def distrito_judicial_create(request):
    '''
    Crea el registro de un Distrito Judicial.
    '''
    template = 'organizacion/distrito_judicial/create.html'

    context = {
        'url': reverse('organizacion:distrito_judicial_create'),
        'modal_title': 'Nuevo Distrito Judicial',
        'create': True,
    }

    if request.method == 'POST':
        form = DistritoJudicialForm(request.POST)
        if form.is_valid():
            obj = form.save()
            obj_name = format_proper_name(obj.nombre)

            
            action = request.POST.get('action')

            if action == 'save_and_add_another':
                form = DistritoJudicialForm()
                context['form'] = form
                response = render(request, template, context)
                response['HX-Trigger'] = json.dumps({
                    'object_list_updated': None,
                    'show_toast': {
                        'type': 'success',
                        'message': f'Distrito Judicial "{obj_name}" creado con éxito.',
                    }
                })
                return response
            else:
                return HttpResponse(
                    status=204,
                    headers={
                        'HX-Trigger': json.dumps({
                            'object_created': None,
                            'show_toast': {
                                'type': 'success',
                                'message': f'Distrito Judicial "{obj_name}" creado con éxito.',
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
        context['form'] = DistritoJudicialForm()
        return render(request, template, context)
    

def distrito_judicial_details(request, pk):
    '''
    Muestra los detalles de un Distrito Judicial sin posibilidad de modificación.
    '''
    obj = get_object_or_404(DistritoJudicial, pk=pk)
    obj_name = format_proper_name(obj.nombre)

    template = 'organizacion/distrito_judicial/details.html'

    datagrid_items = [
        ('Distrito Judicial', obj_name),
        ('Corte'            , obj.corte),
        ('Siglas'           , obj.siglas),
        ('Latitud'          , obj.latitud),
        ('Longitud'         , obj.longitud),
        ('Estado'           , obj.activo),
    ]   

    context = {
        'url': reverse('organizacion:distrito_judicial_details', kwargs={'pk': pk}),
        'title': f'{obj_name}',
        'modal_title': f'{obj_name}',
        'obj': obj,
        'datagrid_items': datagrid_items,
    }

    return render(request, template, context)


def distrito_judicial_update(request, pk):
    '''
    Modifica o actualiza el registro de un Distrito Judicial.
    '''
    obj = get_object_or_404(DistritoJudicial, pk=pk)
    obj_name = format_proper_name(obj.nombre)

    template = 'organizacion/distrito_judicial/create.html'

    context = {
        'url': reverse('organizacion:distrito_judicial_update', kwargs={'pk': pk}),
        'modal_title': f'Editar: {obj_name}',
        'obj': obj,
    }

    if request.method == 'POST':
        form = DistritoJudicialForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()

            return HttpResponse(
                status=204,
                headers= {
                    'HX-Trigger': json.dumps({
                        'object_updated': None,
                        'show_toast': {
                            'type': 'success',
                            'message': f'El Distrito Judicial "{obj_name}" se actualizó con éxito.'
                        }
                    })
                }
            )
        else:
            context['form'] = form
            response = render(request, template, context)
            response['HX-Trigger']=json.dumps({
                'show_toast': {
                    'type': 'error',
                    'message': 'El formulario contiene errores. Revise la información ingresada antes de continuar.',
                }
            })
            return response
    else:
        context['form'] = DistritoJudicialForm(instance=obj)
        return render(request, template, context)
            

def distrito_judicial_toggle(request, pk):
    '''
    Cambia el estado del registro de activo a inactivo y viceversa.
    '''
    obj = get_object_or_404(DistritoJudicial, pk=pk)
    obj_name = format_proper_name(obj.nombre)
    
    template = 'organizacion/distrito_judicial/toggle.html'

    context = {
        'url': reverse('organizacion:distrito_judicial_toggle', kwargs={'pk': pk}),
        'modal_title': f'Cambiar el estado: {obj_name}',
        'modal_type': 'danger' if obj.activo else 'success',
        'model_name': obj._meta.verbose_name,
        'toggle': True,
        'obj': obj,
    }

    if request.method == 'POST':
        obj.activo = not obj.activo
        obj.save()
        toggle = 'activó' if obj.activo else 'desactivó'

        return HttpResponse(
            status=204,
            headers={
                'HX-Trigger': json.dumps({
                    'object_updated': None,
                    'show_toast': {
                        'type': 'success',
                        'message': f'El Distrito Judicial {obj_name} se {toggle} con éxito.',
                    }
                })
            }
        )

    response = render(request, template, context)
    response['HX-Modal-Size'] = 'modal-sm'
    return response


def distritos_judiciales_export(request):
    '''
    Exporta los datos filtrados y ordenados a un archivo xlsx.
    '''
    queryset = DistritoJudicial.objects.all()

    # 1. Filtros (Lógica de negocio específica de este modelo)
    form = DistritoJudicialFiltersForm(request.GET or None)
    form.setup_htmx(request.path)

    if form.is_valid():
        queryset = filter_distrito_judicial(queryset=queryset, filters=form.cleaned_data)

    # 2. Ordenamiento (Lógica de negocio específica de este modelo)
    order_by = request.GET.get('order_by', 'nombre_normalizado').strip()
    direction = request.GET.get('direction', 'asc')
    queryset = sort_distrito_judicial(queryset=queryset, order_by=order_by, direction=direction)

    # 3. Configuración de columnas para ESTE modelo en particular
    columns = [
        {'header': 'Distrito Judicial', 'field': 'nombre', 'width': 30, 'format': 'cell'},
        {'header': 'Siglas', 'field': 'corte', 'width': 40, 'format': 'cell'},        
        {'header': 'Siglas', 'field': 'siglas', 'width': 15, 'format': 'cell'},
        # {'header': 'Latitud', 'field': 'latitud', 'width': 15, 'format': 'cell_center'},
        # {'header': 'Longitud', 'field': 'longitud', 'width': 15, 'format': 'cell_center'},
        {'header': 'Estado', 'field': 'activo', 'width': 15, 'format': 'boolean'},
    ]

    # 4. Delegar la generación del Excel al utilitario genérico
    return export_queryset_to_xlsx(
        queryset=queryset,
        columns_config=columns,
        filename="Distritos Judiciales",
        sheet_name="Distritos Judiciales"
    )