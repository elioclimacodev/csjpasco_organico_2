import json

from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.apps import apps
from django.http import HttpResponse
from django.urls import reverse

from apps.common.utils.text import normalize_alphanumeric, format_proper_name
from apps.common.querysets import export_queryset_to_xlsx

from apps.organizacion.models import MateriaJurisdiccional
from apps.organizacion.forms import MateriaJurisdiccionalForm, MateriaJurisdiccionalFiltersForm


ALLOWED_ORDER_FIELDS = ['nombre_normalizado', 'siglas', 'estado']


def filter_materia_jurisdiccional(queryset, filters):
    '''
    Aplica filtros de búsqueda y estado al queryset.
    '''
    search = filters.get('search','').strip()
    status = filters.get('status')

    if search:
        normalized_search = normalize_alphanumeric(search.lower())
        queryset = queryset.filter(
            Q(nombre_normalizado__icontains=normalized_search) |
            Q(siglas__icontains=search)
        )

    if status == '0':
        queryset = queryset.filter(activo=False)
    elif status == '1':
        queryset = queryset.filter(activo=True)

    return queryset


def sort_materia_jurisdiccional(queryset, order_by, direction):
    '''
    Ordena el queryset solo en los campos permitidos.
    '''
    if order_by not in ALLOWED_ORDER_FIELDS:
        order_by = 'nombre_normalizado'

    prefix = '-' if direction == 'desc' else ''

    return queryset.order_by(f'{prefix}{order_by}')


@permission_required(
    'organizacion.view_materiajurisdiccional',
    raise_exception=True,
)
def materias_jurisdiccionales_list(request):
    '''
    Muestra las Materias Judiciales permitiendo su ordenamiento, paginación,
    filtros y la exportación de datos como archivo xlsx.
    '''

    queryset = MateriaJurisdiccional.objects.all()
    unfiltered_count = queryset.count()

    # ── Filtros ───────────────────────────────
    form = MateriaJurisdiccionalFiltersForm(request.GET or None)
    form.setup_htmx(request.path)
    per_page = 10
    if form.is_valid():
        queryset = filter_materia_jurisdiccional(
            queryset=queryset,
            filters=form.cleaned_data
        )
        per_page = form.cleaned_data.get('per_page') or 10
    
    # ── Ordenamiento ──────────────────────────
    order_by = request.GET.get('order_by', 'nombre_normalizado').strip()
    direction = request.GET.get('direction', 'asc')
    queryset = sort_materia_jurisdiccional(
        queryset=queryset,
        order_by=order_by,
        direction=direction
    )

    # ── Paginación ────────────────────────────
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
    
    # Si la petición viene de un elemento HTMX, renderiza un partial,
    # en caso contrario, renderiza la plantilla completa.
    if request.headers.get('HX-Request'):
        template = 'organizacion/materia_jurisdiccional/partials/_datatable.html'
    else:
        template = 'organizacion/materia_jurisdiccional/list.html'

    context = {
        'pre_title': apps.get_app_config('organizacion').verbose_name,
        'title': MateriaJurisdiccional._meta.verbose_name_plural,
        'form': form,
        'page_obj': page_obj,
        'paginator': paginator,
        'page_range': page_range,
        'order_by': order_by,
        'direction': direction,
        'is_empty_database': unfiltered_count == 0,
    }
    
    return render(request, template, context)


@permission_required(
    'organizacion.add_materiajurisdiccional',
    raise_exception=True,
)
def materia_jurisdiccional_create(request):
    '''
    Crea el registro de una Materia Judicial.
    '''
    template = 'organizacion/materia_jurisdiccional/create.html'

    context = {
        'url': reverse('organizacion:materia_jurisdiccional_create'),
        'modal_title': f'Nueva Materia',
        'create': True,
    }

    if request.method == 'POST':
        form = MateriaJurisdiccionalForm(request.POST)
        if form.is_valid():
            obj = form.save()
            obj_name = format_proper_name(obj.nombre)

            action = request.POST.get('action')

            if action == 'save_and_add_another':
                form = MateriaJurisdiccionalForm()
                context['form'] = form
                response = render(request, template, context)
                response['HX-Trigger'] = json.dumps({
                    'object_list_updated': None,
                    'show_toast': {
                        'type': 'success',
                        'message': f'Materia "{obj_name}" creado con éxito.',
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
                                'message': f'Materia "{obj_name}" creado con éxito.',
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
        context['form'] = MateriaJurisdiccionalForm()
        return render(request, template, context)
    

@permission_required(
    'organizacion.view_materiajurisdiccional',
    raise_exception=True,
)
def materia_jurisdiccional_details(request, pk):
    '''
    Muestra los detalles de una Materia Judicial sin posibilidad de modificación.
    '''
    obj = get_object_or_404(MateriaJurisdiccional, pk=pk)
    obj_name = format_proper_name(obj.nombre)


    datagrid_items = [
        ('Materia'  , obj.nombre),
        ('Siglas'   , obj.siglas),
        ('Estado'   , obj.activo),
    ]

    template = 'organizacion/materia_jurisdiccional/details.html'

    context = {
        'url': reverse('organizacion:materia_jurisdiccional_details', kwargs={'pk': pk}),
        'modal_title': f'{obj_name}',
        'obj': obj,
        'datagrid_items': datagrid_items,
    }

    return render(request, template, context)


@permission_required(
    'organizacion.change_materiajurisdiccional',
    raise_exception=True,
)
def materia_jurisdiccional_update(request, pk):
    '''
    Modifica o actualiza el registro de un Órgano Jurisdiccional.
    '''
    obj = get_object_or_404(MateriaJurisdiccional, pk=pk)
    oj_name = format_proper_name(obj.nombre)

    template = 'organizacion/materia_jurisdiccional/create.html'

    context = {
        'url': reverse('organizacion:materia_jurisdiccional_update', kwargs={'pk': pk}),
        'modal_title': f'Editar: {oj_name}',
        'update': True,
        'obj': obj,
    }

    if request.method == 'POST':
        form = MateriaJurisdiccionalForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()

            return HttpResponse(
                status=204,
                headers={
                    'HX-Trigger': json.dumps({
                        'object_updated': None,
                        'show_toast': {
                            'type': 'success',
                            'message': f'La materia "{oj_name}" se actualizó con éxito.'
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
        context['form'] = MateriaJurisdiccionalForm(instance=obj)
        return render(request, template, context)


@permission_required(
    'organizacion.change_materiajurisdiccional',
    raise_exception=True,
)
def materia_jurisdiccional_toggle(request, pk):
    '''
    Cambia el estado del registro de activo a inactivo y viceversa.
    '''
    obj = get_object_or_404(MateriaJurisdiccional, pk=pk)
    obj_name = format_proper_name(obj.nombre)

    template = 'organizacion/materia_jurisdiccional/toggle.html'

    context = {
        'url': reverse('organizacion:materia_jurisdiccional_toggle', kwargs={'pk': pk}),
        'modal_title': f'Cambiar el estado: {obj_name}',
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
                        'message': f'La materia "{obj_name}" se {toggle} con éxito.',
                    }
                })
            }
        )
    response = render(request, template, context)
    response['HX-Modal-Size'] = 'modal-sm'
    return response


@permission_required(
    'organizacion.view_materiajurisdiccional',
    raise_exception=True,
)
def materias_jurisdiccionales_export(request):
    '''
    Exporta los datos filtrados y ordenados a un archivo xlsx.
    '''
    queryset = MateriaJurisdiccional.objects.all()

    # ── Filtros ───────────────────────────────
    form = MateriaJurisdiccionalFiltersForm(request.GET or None)
    form.setup_htmx(request.path)
    if form.is_valid():
        queryset = filter_materia_jurisdiccional(
            queryset=queryset,
            filters=form.cleaned_data
        )

    # ── Ordenamiento ──────────────────────────
    order_by = request.GET.get('order_by', 'nombre_normalizado').strip()
    direction = request.GET.get('direction', 'asc')
    queryset = sort_materia_jurisdiccional(
        queryset=queryset,
        order_by=order_by,
        direction=direction
    )

    # ── Columnas ───────────────────────────
    columns = [
        {'header': 'Materia', 'field': 'nombre', 'width': 25, 'format': 'cell'},
        {'header': 'Materia', 'field': 'siglas', 'width': 15, 'format': 'cell'},
        {'header': 'Estado', 'field': 'activo', 'width': 15, 'format': 'boolean'},
    ]
    
    return export_queryset_to_xlsx(
        queryset=queryset,
        columns_config=columns,
        filename='Materia',
        sheet_name='Materia',
    )