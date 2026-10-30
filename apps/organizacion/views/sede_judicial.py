import io
import json
import xlsxwriter

from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.apps import apps
from django.http import HttpResponse
from django.urls import reverse

from apps.common.querysets import (
    sort_queryset, filter_by_status, search_queryset,
    export_queryset_to_xlsx
)

from apps.common.utils import format_proper_name
from apps.common.utils import build_breadcrumbs

from apps.organizacion.models import DistritoJudicial, SedeJudicial
from apps.organizacion.forms import SedeJudicialForm, SedeJudicialFiltersForm


ALLOWED_ORDER_FIELDS = ['nombre_normalizado', 'sede_superior', 'siglas']

ORDER_FIELDS = {
    'nombre'        : 'nombre_normalizado',
    'sede_superior' : 'sede_superior',
    'siglas'        : 'siglas',
}

SEARCH_FIELDS = ['siglas']

NORMALIZED_FIELDS = ['nombre_normalizado']


@permission_required(
    'organizacion.view_sedejudicial',
    raise_exception=True,
)
def sedes_list(request, dj_id):
    '''
    Muestra las sedes y subsedes permitiendo su ordenamiento, paginación,
    filtros y la exportación de datos como archivo xlsx.
    '''
    queryset = SedeJudicial.objects.filter(distrito_judicial=dj_id)
    unfiltered_count = queryset.count()

    dj = get_object_or_404(DistritoJudicial, pk=dj_id)
    corte = format_proper_name(dj.corte)


    # ── Filtros y búsqueda ───────────
    form = SedeJudicialFiltersForm(
        request.GET or None,
        request_path=request.path,
    )

    per_page = 10

    if form.is_valid():
        # Búsqueda.
        search = form.cleaned_data.get('search', '').strip()
        queryset = search_queryset(
            queryset=queryset,
            search=search,
            search_fields=SEARCH_FIELDS,
            normalized_fields=NORMALIZED_FIELDS,
        )

        # Filtros.
        status = form.cleaned_data.get('status')
        queryset = filter_by_status(
            queryset=queryset,
            status=status,
            status_field='activo'
        )

        per_page = form.cleaned_data.get('per_page') or 10
    
    # ── Ordenamiento ──────────────────
    order_by = request.GET.get('order_by', 'nombre_normalizado').strip()
    direction = request.GET.get('direction', 'asc')
    queryset = sort_queryset(
        queryset=queryset,
        order_by=order_by,
        direction=direction,
        order_fields=ORDER_FIELDS,
        default_field='nombre_normalizado'
    )

    # ── Paginación ───────────────────
    try:
        page_num = int(request.GET.get('page', 1))
    except (ValueError, TypeError):
        page_num = 1

    paginator = Paginator(queryset, per_page)
    page_obj = paginator.get_page(page_num)
    page_range = paginator.get_elided_page_range(
        number=page_obj.number,
        on_each_side=2,
        on_ends=1
    )

    # ── Breadcrumbs ──────────────────
    breadcrumbs = build_breadcrumbs(
        ('Inicio', '/'),
        ('Distritos Judiciales', reverse('organizacion:distritos_judiciales_list')),
        (dj.nombre, None)
    )
    
    # Si la petición viene de un elemento HTMX, renderiza un partial,
    # en caso contrario, renderiza la plantilla completa.
    if request.headers.get('HX-Request'):
        template = 'organizacion/sede_judicial/partials/_datatable.html'
    else:
        template = 'organizacion/sede_judicial/list.html'

    context = {
        'pre_title': apps.get_app_config('organizacion').verbose_name,
        'title': f'Sedes Judiciales',
        'distrito_judicial': dj,

        'form': form,
        
        'paginator': paginator,
        'page_obj': page_obj,
        'page_range': page_range,

        'is_empty_database': unfiltered_count == 0,
        'order_by': order_by,
        'direction': direction,

        'breadcrumbs': breadcrumbs,
    }
    
    return render(request, template, context)


@permission_required(
    'organizacion.add_sedejudicial',
    raise_exception=True,
)
def sede_create(request, dj_id):
    '''
    Crea el registro de una Sede o subsede judicial.
    '''
    dj = get_object_or_404(DistritoJudicial, pk=dj_id)
    corte = format_proper_name(dj.corte)

    template = 'organizacion/sede_judicial/create.html'

    context = {
        'url': reverse('organizacion:sede_create', kwargs={'dj_id': dj.pk}),
        'modal_title': f'Nueva Sede Judicial - {corte}',
        'create': True,
    }

    if request.method == 'POST':
        form = SedeJudicialForm(request.POST)
        if form.is_valid():
            sede = form.save(commit=False)
            sede.distrito_judicial = dj
            sede.save()
            sede_nombre = format_proper_name(sede.nombre)

            action = request.POST.get('action')

            if action == 'save_and_add_another':
                form = SedeJudicialForm()
                context['form'] = form
                response = render(request, template, context)
                response['HX-Trigger'] = json.dumps({
                    'object_list_updated': None,
                    'show_toast': {
                        'type': 'success',
                        'message': f'Sede Judicial "{sede_nombre}" creado con éxito.',
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
                                'message': f'Sede Judicial "{sede_nombre}" creado con éxito.',
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
        context['form'] = SedeJudicialForm()
        return render(request, template, context)
    

@permission_required(
    'organizacion.view_sedejudicial',
    raise_exception=True,
)
def sede_details(request, pk):
    '''
    Muestra los detalles de una Sede Judicial sin posibilidad de modificación.
    '''
    sede = get_object_or_404(SedeJudicial, pk=pk)
    distrito_judicial = format_proper_name(sede.distrito_judicial.nombre)
    corte = format_proper_name(sede.distrito_judicial.corte)
    sede_nombre = format_proper_name(sede.nombre)

    datagrid_items = [
        ('Distrito Judicial' , distrito_judicial),
        ('Corte'             , corte),
        ('Nombre de la sede' , sede_nombre),
        ('Sede superior'     , sede.sede_superior),

        ('Siglas'            , sede.siglas),
        ('Estado'            , sede.activo),
    ]

    template = 'organizacion/sede_judicial/details.html'

    context = {
        'url': reverse('organizacion:sede_details', kwargs={'pk': pk}),
        'modal_title': f'{sede_nombre} - {corte}',
        'obj': sede,
        'datagrid_items': datagrid_items,
    }

    return render(request, template, context)


@permission_required(
    'organizacion.change_sedejudicial',
    raise_exception=True,
)
def sede_update(request, pk):
    '''
    Modifica o actualiza el registro de una Sede Judicial.
    '''
    sede = get_object_or_404(SedeJudicial, pk=pk)
    sede_nombre = format_proper_name(sede.nombre)
    corte_nombre = format_proper_name(sede.distrito_judicial.corte)

    template = 'organizacion/sede_judicial/create.html'

    context = {
        'url': reverse('organizacion:sede_update', kwargs={'pk': pk}),
        'modal_title': f'Editar: {sede_nombre} - {corte_nombre}',
        'update': True,
        'obj': sede,
    }

    if request.method == 'POST':
        form = SedeJudicialForm(request.POST, instance=sede)
        if form.is_valid():
            form.save()

            return HttpResponse(
                status=204,
                headers={
                    'HX-Trigger': json.dumps({
                        'object_updated': None,
                        'show_toast': {
                            'type': 'success',
                            'message': f'La Sede Judicial "{sede_nombre}" se actualizó con éxito.'
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
        context['form'] = SedeJudicialForm(instance=sede)
        return render(request, template, context)


@permission_required(
    'organizacion.change_sedejudicial',
    raise_exception=True,
)
def sede_toggle(request, pk):
    '''
    Cambia el estado del registro de activo a inactivo y viceversa.
    '''
    sede = get_object_or_404(SedeJudicial, pk=pk)
    sede_nombre = format_proper_name(sede.nombre)
    corte_nombre = format_proper_name(sede.distrito_judicial.corte)

    template = 'organizacion/sede_judicial/toggle.html'

    context = {
        'url': reverse('organizacion:sede_toggle', kwargs={'pk': pk}),
        'modal_title': f'Cambiar el estado: {sede_nombre} - {corte_nombre}',
        'toggle': True,
        'obj': sede,
    }

    if request.method == 'POST':
        sede.activo = not sede.activo
        sede.save()

        toggle = 'activó' if sede.activo else 'desactivó'

        return HttpResponse(
            status=204,
            headers={
                'HX-Trigger': json.dumps({
                    'object_updated': None,
                    'show_toast': {
                        'type': 'success',
                        'message': f'La {sede_nombre}, {corte_nombre} se {toggle} con éxito.',
                    }
                })
            }
        )
    response = render(request, template, context)
    response['HX-Modal-Size'] = 'modal-sm'
    return response


@permission_required(
    'organizacion.view_sedejudicial',
    raise_exception=True,
)
def sedes_export(request, dj_id):
    '''
    Exporta los datos filtrados y ordenados a un archivo xlsx.
    '''
    dj = get_object_or_404(DistritoJudicial, pk=dj_id)
    queryset = SedeJudicial.objects.filter(
        Q(distrito_judicial=dj)
    )

    # ── Filtros y búsqueda ───────────────────────────────
    form = SedeJudicialFiltersForm(
        request.GET or None,
        request_path=request.path
    )

    if form.is_valid():
        # Búsqueda.
        search = form.cleaned_data.get('search','').strip()
        queryset = search_queryset(
            queryset=queryset,
            search=search,
            search_fields=SEARCH_FIELDS,
            normalized_fields=NORMALIZED_FIELDS,
        )

        # Filtros.
        status = form.cleaned_data.get('status')
        queryset = filter_by_status(
            queryset=queryset,
            status=status,
            status_field='activo',
        )

    #── Ordenamiento ─────────────────
    order_by = request.GET.get('order_by', 'nombre_normalizado').strip()
    direction = request.GET.get('direction', 'asc')

    queryset = sort_queryset(
        queryset=queryset,
        order_by=order_by,
        direction=direction,
        order_fields=ORDER_FIELDS,
        default_field='nombre_normalizado',
    )

    # ── Columnas ───────────────────────────
    columns = [
        {'header': 'Distrito Judicial', 'field': 'distrito_judicial_nombre', 'width': 25, 'format': 'cell'},
        {'header': 'Corte', 'field': 'corte_nombre', 'width': 40, 'format': 'cell'},
        {'header': 'Sede', 'field': 'nombre', 'width': 30, 'format': 'cell'},
        {'header': 'Inmediato Superior', 'field': 'sede_superior_nombre', 'width': 30, 'format': 'cell'},
        {'header': 'Siglas', 'field': 'siglas', 'width': 15, 'format': 'cell'},
        {'header': 'Estado', 'field': 'activo', 'width': 15, 'format': 'boolean'},
    ]

    return export_queryset_to_xlsx(
        queryset=queryset,
        columns_config=columns,
        filename='Sedes Judiciales',
        sheet_name='Sedes Judiciales',
    )