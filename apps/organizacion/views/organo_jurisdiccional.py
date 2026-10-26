import json

from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.apps import apps
from django.http import HttpResponse
from django.urls import reverse

from apps.common.utils.text import normalize_alphanumeric, format_proper_name
from apps.common.querysets import export_queryset_to_xlsx

from apps.organizacion.models import OrganoJurisdiccional
from apps.organizacion.forms import OrganoJurisdiccionalForm, OrganoJurisdiccionalFiltersForm


ALLOWED_ORDER_FIELDS = ['nombre_normalizado', 'siglas', 'estado']


def filter_organos_jurisdiccionales(queryset, filters):
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
        queryset = queryset.filters(activo=False)
    elif status == '1':
        queryset = queryset.filters(activo=True)

    return queryset


def sort_organos_jurisdiccionales(queryset, order_by, direction):
    '''
    Ordena el queryset solo en los campos permitidos.
    '''
    if order_by not in ALLOWED_ORDER_FIELDS:
        order_by = 'nombre_normalizado'

    prefix = '-' if direction == 'desc' else ''

    return queryset.order_by(f'{prefix}{order_by}')


def organos_jurisdiccionales_list(request):
    '''
    Muestra los Órganos Jurisdiccionales permitiendo su ordenamiento, paginación,
    filtros y la exportación de datos como archivo xlsx.
    '''

    queryset = OrganoJurisdiccional.objects.all()
    unfiltered_count = queryset.count()

    # ── Filtros ───────────────────────────────
    form = OrganoJurisdiccionalFiltersForm(request.GET or None)
    form.setup_htmx(request.path)
    per_page = 10
    if form.is_valid():
        queryset = filter_organos_jurisdiccionales(
            queryset=queryset,
            filters=form.cleaned_data
        )
        per_page = form.cleaned_data.get('per_page') or 10
    
    # ── Ordenamiento ──────────────────────────
    order_by = request.GET.get('order_by', 'nombre_normalizado').strip()
    direction = request.GET.get('direction', 'asc')
    queryset = sort_organos_jurisdiccionales(
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
        template = 'organizacion/organo_jurisdiccional/partials/_datatable.html'
    else:
        template = 'organizacion/organo_jurisdiccional/list.html'

    context = {
        'pre_title': apps.get_app_config('organizacion').verbose_name,
        'title': OrganoJurisdiccional._meta.verbose_name_plural,
        'form': form,
        'page_obj': page_obj,
        'paginator': paginator,
        'page_range': page_range,
        'order_by': order_by,
        'direction': direction,
        'is_empty_database': unfiltered_count == 0,
    }
    
    return render(request, template, context)


def organo_jurisdiccional_create(request):
    '''
    Crea el registro de un Órgano Jurisdiccional.
    '''
    template = 'organizacion/organo_jurisdiccional/create.html'

    context = {
        'url': reverse('organizacion:organo_jurisdiccional_create'),
        'modal_title': f'Nuevo Órgano Jurisdiccional',
        'create': True,
    }

    if request.method == 'POST':
        form = OrganoJurisdiccionalForm(request.POST)
        if form.is_valid():
            oj = form.save()
            oj_name = format_proper_name(oj.nombre)

            action = request.POST.get('action')

            if action == 'save_and_add_another':
                form = OrganoJurisdiccionalForm()
                context['form'] = form
                response = render(request, template, context)
                response['HX-Trigger'] = json.dumps({
                    'object_list_updated': None,
                    'show_toast': {
                        'type': 'success',
                        'message': f'Órgano Jurisdiccional "{oj_name}" creado con éxito.',
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
                                'message': f'Órgano Jurisdiccional "{oj_name}" creado con éxito.',
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
        context['form'] = OrganoJurisdiccionalForm()
        return render(request, template, context)
    

def organo_jurisdiccional_details(request, pk):
    '''
    Muestra los detalles de un Órgano Jurisdiccional sin posibilidad de modificación.
    '''
    oj = get_object_or_404(OrganoJurisdiccional, pk=pk)
    oj_name = format_proper_name(oj.nombre)


    datagrid_items = [
        ('Órgano Jurisdiccional', oj.nombre),
        ('Siglas'               , oj.siglas),
        ('Estado'               , oj.activo),
    ]

    template = 'organizacion/organo_jurisdiccional/details.html'

    context = {
        'url': reverse('organizacion:organo_jurisdiccional_details', kwargs={'pk': pk}),
        'modal_title': f'{oj_name}',
        'obj': oj,
        'datagrid_items': datagrid_items,
    }

    return render(request, template, context)


def organo_jurisdiccional_update(request, pk):
    '''
    Modifica o actualiza el registro de un Órgano Jurisdiccional.
    '''
    oj = get_object_or_404(OrganoJurisdiccional, pk=pk)
    oj_name = format_proper_name(oj.nombre)

    template = 'organizacion/organo_jurisdiccional/create.html'

    context = {
        'url': reverse('organizacion:organo_jurisdiccional_update', kwargs={'pk': pk}),
        'modal_title': f'Editar: {oj_name}',
        'update': True,
        'obj': oj,
    }

    if request.method == 'POST':
        form = OrganoJurisdiccionalForm(request.POST, instance=oj)
        if form.is_valid():
            form.save()

            return HttpResponse(
                status=204,
                headers={
                    'HX-Trigger': json.dumps({
                        'object_updated': None,
                        'show_toast': {
                            'type': 'success',
                            'message': f'El Órgano Jurisdiccional "{oj_name}" se actualizó con éxito.'
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
        context['form'] = OrganoJurisdiccionalForm(instance=oj)
        return render(request, template, context)


def organo_jurisdiccional_toggle(request, pk):
    '''
    Cambia el estado del registro de activo a inactivo y viceversa.
    '''
    oj = get_object_or_404(OrganoJurisdiccional, pk=pk)
    oj_name = format_proper_name(oj.nombre)

    template = 'organizacion/organo_jurisdiccional/toggle.html'

    context = {
        'url': reverse('organizacion:organo_jurisdiccional_toggle', kwargs={'pk': pk}),
        'modal_title': f'Cambiar el estado: {oj_name}',
        'toggle': True,
        'obj': oj,
    }

    if request.method == 'POST':
        oj.activo = not oj.activo
        oj.save()

        toggle = 'activó' if oj.activo else 'desactivó'

        return HttpResponse(
            status=204,
            headers={
                'HX-Trigger': json.dumps({
                    'object_updated': None,
                    'show_toast': {
                        'type': 'success',
                        'message': f'El Órgano Jurisdiccional {oj_name} se {toggle} con éxito.',
                    }
                })
            }
        )
    response = render(request, template, context)
    response['HX-Modal-Size'] = 'modal-sm'
    return response


def organos_jurisdiccionales_export(request):
    '''
    Exporta los datos filtrados y ordenados a un archivo xlsx.
    '''
    queryset = OrganoJurisdiccional.objects.all()

    # ── Filtros ───────────────────────────────
    form = OrganoJurisdiccionalFiltersForm(request.GET or None)
    form.setup_htmx(request.path)
    if form.is_valid():
        queryset = filter_organos_jurisdiccionales(
            queryset=queryset,
            filters=form.cleaned_data
        )

    # ── Ordenamiento ──────────────────────────
    order_by = request.GET.get('order_by', 'nombre_normalizado').strip()
    direction = request.GET.get('direction', 'asc')
    queryset = sort_organos_jurisdiccionales(
        queryset=queryset,
        order_by=order_by,
        direction=direction
    )

    # ── Columnas ───────────────────────────
    columns = [
        {'header': 'Órgano Jurisdiccional', 'field': 'nombre', 'width': 25, 'format': 'cell'},
        {'header': 'Siglas', 'field': 'siglas', 'width': 15, 'format': 'cell'},
        {'header': 'Estado', 'field': 'activo', 'width': 15, 'format': 'boolean'},
    ]

    return export_queryset_to_xlsx(
        queryset=queryset,
        columns_config=columns,
        filename='Órganos Jurisdiccionales',
        sheet_name='Órganos Jurisdiccionales'
    )