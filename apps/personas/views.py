import json

from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib import messages
from django.apps import apps
from django.http import HttpResponse
from django.urls import reverse

from apps.common.querysets import (
    sort_queryset, filter_by_status, 
    search_queryset, export_queryset_to_xlsx)

from .models import Persona
from .forms import PersonaForm, PersonaFiltersForm


ORDER_FIELDS = {
    'numero_documento'  : 'numero_documento',
    'nombres'           : 'nombres_normalizado',
    'apellido_paterno'  : 'apellido_paterno_normalizado',
    'apellido_materno'  : 'apellido_materno_normalizado',
    'genero'            : 'genero',
    'fecha_nacimiento'  : 'fecha_nacimiento',
    'estado_civil'      : 'estado_civil',
    'activo'            : 'activo',
}

SEARCH_FIELDS = [
    'numero_documento',
    'nombres_normalizado',
    'apellido_paterno_normalizado',
    'apellido_materno_normalizado',
    'fecha_nacimiento',
]

NORMALIZED_FIELDS = [
    'nombres_normalizado',
    'apellido_paterno_normalizado',
    'apellido_materno_normalizado',
]


@permission_required(
    'personas.view_persona',
    raise_exception=True,
)
def personas_list(request):
    persons = Persona.objects.all()
    unfiltered_persons = persons.count()

    # ── Filtros y búsqueda ───────────
    form = PersonaFiltersForm(
        request.GET or None,
        request_path=request.path
    )

    per_page = 10

    if form.is_valid():
        # Búsqueda.
        search = form.cleaned_data.get('search', '').strip()
        persons = search_queryset(
            queryset=persons,
            search=search,
            search_fields=SEARCH_FIELDS,
            normalized_fields=NORMALIZED_FIELDS,
        )
    
        # Filtros.
        status = form.cleaned_data.get('status')
        persons = filter_by_status(
            queryset=persons,
            status=status,
            status_field='activo',
        )

        per_page = form.cleaned_data.get('per_page') or 10

    # ── Ordenamiento ──────────────────
    order_by = request.GET.get('order_by', 'apellido_paterno').strip()
    direction = request.GET.get('direction', 'asc')
    persons = sort_queryset(
        queryset=persons,
        order_by=order_by,
        direction=direction,
        order_fields=ORDER_FIELDS,
        default_field='apellido_paterno_normalizado'
    )

    # ── Paginación ───────────────────
    try:
        page_num = int(request.GET.get('page', 1))
    except (ValueError, TypeError):
        page_num = 1

    paginator = Paginator(persons, per_page)
    page_obj = paginator.get_page(page_num)
    page_range = paginator.get_elided_page_range(
        number=page_num,
        on_each_side=2,
        on_ends=1
    )

    # ── Evalua la petición ───────────
    if request.headers.get('HX-Request'):
        template = 'personas/partials/_datatable.html'
    else:
        template = 'personas/list.html'

    context = {
        'pre_title': apps.get_app_config('personas').verbose_name,
        'title': f'Administración de Personas',
        'list': True,

        'form': form,

        'paginator': paginator,
        'page_obj': page_obj,
        'page_range': page_range,

        'is_empty_database': unfiltered_persons == 0,
        'order_by': order_by,
        'direction': direction,
    }

    return render(request, template, context)


def persona_create(request):
    '''
    Registra a una persona independientemente de su vínculo
    con la institución.
    '''

    if request.method == 'POST':
        form = PersonaForm(request.POST)
        if form.is_valid():
            persona = form.save()
            messages.success(
                request,
                f'Persona {persona.nombre_completo} registrado con éxito.'
            )
            return redirect('personas:list')

        messages.error(
            request,
            'Por favor corrija los errores del formulario.'
        )
    else:
        form = PersonaForm()

    context = {
        'url': reverse('personas:create'),
        'pre_title': 'Personas',
        'title': 'Administración de Personas',
        'page_title': 'Nueva Persona',
        'url': reverse('personas:create'),
        'form': form,

        'base_template': (
            'layouts/htmx_page.html'
            if request.headers.get('HX-Request')
            else 'layouts/base_page.html'
        )
    }

    # template = 'personas/partials/_create.html'
    template = 'personas/create.html'

    return render(request, template, context)



#     # ── Paginación ───────────────────    

# def sedes_list(request, dj_id):
#     '''
#     Muestra las sedes y subsedes permitiendo su ordenamiento, paginación,
#     filtros y la exportación de datos como archivo xlsx.
#     '''
#     queryset = SedeJudicial.objects.filter(distrito_judicial=dj_id)
#     unfiltered_count = queryset.count()

#     dj = get_object_or_404(DistritoJudicial, pk=dj_id)
#     corte = format_proper_name(dj.corte)


#     # ── Filtros y búsqueda ───────────
#     form = SedeJudicialFiltersForm(
#         request.GET or None,
#         request_path=request.path,
#     )

#     per_page = 10

#     if form.is_valid():
#         # Búsqueda.
#         search = form.cleaned_data.get('search', '').strip()
#         queryset = search_queryset(
#             queryset=queryset,
#             search=search,
#             search_fields=SEARCH_FIELDS,
#             normalized_fields=NORMALIZED_FIELDS,
#         )

#         # Filtros.
#         status = form.cleaned_data.get('status')
#         queryset = filter_by_status(
#             queryset=queryset,
#             status=status,
#             status_field='activo'
#         )

#         per_page = form.cleaned_data.get('per_page') or 10
    
#     # ── Ordenamiento ──────────────────
#     order_by = request.GET.get('order_by', 'nombre_normalizado').strip()
#     direction = request.GET.get('direction', 'asc')
#     queryset = sort_queryset(
#         queryset=queryset,
#         order_by=order_by,
#         direction=direction,
#         order_fields=ORDER_FIELDS,
#         default_field='nombre_normalizado'
#     )

#     # ── Paginación ───────────────────
#     try:
#         page_num = int(request.GET.get('page', 1))
#     except (ValueError, TypeError):
#         page_num = 1

#     paginator = Paginator(queryset, per_page)
#     page_obj = paginator.get_page(page_num)
#     page_range = paginator.get_elided_page_range(
#         number=page_obj.number,
#         on_each_side=2,
#         on_ends=1
#     )

#     # ── Breadcrumbs ──────────────────
#     breadcrumbs = build_breadcrumbs(
#         ('Inicio', '/'),
#         ('Distritos Judiciales', reverse('organizacion:distritos_judiciales_list')),
#         (dj.nombre, None)
#     )
    
#     # Si la petición viene de un elemento HTMX, renderiza un partial,
#     # en caso contrario, renderiza la plantilla completa.
#     if request.headers.get('HX-Request'):
#         template = 'organizacion/sede_judicial/partials/_datatable.html'
#     else:
#         template = 'organizacion/sede_judicial/list.html'

#     context = {
#         'pre_title': apps.get_app_config('organizacion').verbose_name,
#         'title': 'Sedes Judiciales',
#         'distrito_judicial': dj,

#         'form': form,
        
#         'paginator': paginator,
#         'page_obj': page_obj,
#         'page_range': page_range,

#         'is_empty_database': unfiltered_count == 0,
#         'order_by': order_by,
#         'direction': direction,

#         'breadcrumbs': breadcrumbs,
#     }
    
#     return render(request, template, context)


# def sede_create(request, dj_id):
#     '''
#     Crea el registro de una Sede o subsede judicial.
#     '''
#     dj = get_object_or_404(DistritoJudicial, pk=dj_id)
#     corte = format_proper_name(dj.corte)

#     template = 'organizacion/sede_judicial/create.html'

#     context = {
#         'url': reverse('organizacion:sede_create', kwargs={'dj_id': dj.pk}),
#         'modal_title': f'Nueva Sede Judicial - {corte}',
#         'create': True,
#     }

#     if request.method == 'POST':
#         form = SedeJudicialForm(request.POST)
#         if form.is_valid():
#             sede = form.save(commit=False)
#             sede.distrito_judicial = dj
#             sede.save()
#             sede_nombre = format_proper_name(sede.nombre)

#             action = request.POST.get('action')

#             if action == 'save_and_add_another':
#                 form = SedeJudicialForm()
#                 context['form'] = form
#                 response = render(request, template, context)
#                 response['HX-Trigger'] = json.dumps({
#                     'object_list_updated': None,
#                     'show_toast': {
#                         'type': 'success',
#                         'message': f'Sede Judicial "{sede_nombre}" creado con éxito.',
#                     }
#                 })
#                 return response
#             else:
#                 return HttpResponse(
#                     status=204,
#                     headers={
#                         'HX-Trigger': json.dumps({
#                             'object_created': None,
#                             'show_toast': {
#                                 'type': 'success',
#                                 'message': f'Sede Judicial "{sede_nombre}" creado con éxito.',
#                             }
#                         })
#                     }
#                 )
#         else:
#             context['form'] = form
#             response = render(request, template, context)
#             response['HX-Trigger'] = json.dumps({
#                 'show_toast': {
#                     'type': 'error',
#                     'message': 'El formulario contiene errores. Revise la información ingresada antes de continuar.',
#                 }
#             })
#             return response
#     else:
#         context['form'] = SedeJudicialForm()
#         return render(request, template, context)
    

# def sede_details(request, pk):
#     '''
#     Muestra los detalles de una Sede Judicial sin posibilidad de modificación.
#     '''
#     sede = get_object_or_404(SedeJudicial, pk=pk)
#     distrito_judicial = format_proper_name(sede.distrito_judicial.nombre)
#     corte = format_proper_name(sede.distrito_judicial.corte)
#     sede_nombre = format_proper_name(sede.nombre)

#     datagrid_items = [
#         ('Distrito Judicial' , distrito_judicial),
#         ('Corte'             , corte),
#         ('Nombre de la sede' , sede_nombre),
#         ('Sede superior'     , sede.sede_superior),

#         ('Siglas'            , sede.siglas),
#         ('Estado'            , sede.activo),
#     ]

#     template = 'organizacion/sede_judicial/details.html'

#     context = {
#         'url': reverse('organizacion:sede_details', kwargs={'pk': pk}),
#         'modal_title': f'{sede_nombre} - {corte}',
#         'obj': sede,
#         'datagrid_items': datagrid_items,
#     }

#     return render(request, template, context)


# def sede_update(request, pk):
#     '''
#     Modifica o actualiza el registro de una Sede Judicial.
#     '''
#     sede = get_object_or_404(SedeJudicial, pk=pk)
#     sede_nombre = format_proper_name(sede.nombre)
#     corte_nombre = format_proper_name(sede.distrito_judicial.corte)

#     template = 'organizacion/sede_judicial/create.html'

#     context = {
#         'url': reverse('organizacion:sede_update', kwargs={'pk': pk}),
#         'modal_title': f'Editar: {sede_nombre} - {corte_nombre}',
#         'update': True,
#         'obj': sede,
#     }

#     if request.method == 'POST':
#         form = SedeJudicialForm(request.POST, instance=sede)
#         if form.is_valid():
#             form.save()

#             return HttpResponse(
#                 status=204,
#                 headers={
#                     'HX-Trigger': json.dumps({
#                         'object_updated': None,
#                         'show_toast': {
#                             'type': 'success',
#                             'message': f'La Sede Judicial "{sede_nombre}" se actualizó con éxito.'
#                         }
#                     })
#                 }
#             )
#         else:
#             context['form'] = form
#             response = render(request, template, context)
#             response['HX-Trigger'] = json.dumps({
#                 'show_toast': {
#                     'type': 'error',
#                     'message': 'El formulario contiene errores. Revise la información ingresada antes de continuar.',
#                 }
#             })
#             return response
#     else:
#         context['form'] = SedeJudicialForm(instance=sede)
#         return render(request, template, context)


# def sede_toggle(request, pk):
#     '''
#     Cambia el estado del registro de activo a inactivo y viceversa.
#     '''
#     sede = get_object_or_404(SedeJudicial, pk=pk)
#     sede_nombre = format_proper_name(sede.nombre)
#     corte_nombre = format_proper_name(sede.distrito_judicial.corte)

#     template = 'organizacion/sede_judicial/toggle.html'

#     context = {
#         'url': reverse('organizacion:sede_toggle', kwargs={'pk': pk}),
#         'modal_title': f'Cambiar el estado: {sede_nombre} - {corte_nombre}',
#         'toggle': True,
#         'obj': sede,
#     }

#     if request.method == 'POST':
#         sede.activo = not sede.activo
#         sede.save()

#         toggle = 'activó' if sede.activo else 'desactivó'

#         return HttpResponse(
#             status=204,
#             headers={
#                 'HX-Trigger': json.dumps({
#                     'object_updated': None,
#                     'show_toast': {
#                         'type': 'success',
#                         'message': f'La {sede_nombre}, {corte_nombre} se {toggle} con éxito.',
#                     }
#                 })
#             }
#         )
#     response = render(request, template, context)
#     response['HX-Modal-Size'] = 'modal-sm'
#     return response


# def sedes_export(request, dj_id):
#     '''
#     Exporta los datos filtrados y ordenados a un archivo xlsx.
#     '''
#     queryset = SedeJudicial.objects.filter(
#         Q(distrito_judicial=dj_id)
#     )

#     # ── Filtros y búsqueda ───────────────────────────────
#     form = SedeJudicialFiltersForm(
#         request.GET or None,
#         request_path=request.path
#     )

#     if form.is_valid():
#         # Búsqueda.
#         search = form.cleaned_data.get('search','').strip()
#         queryset = search_queryset(
#             queryset=queryset,
#             search=search,
#             search_fields=SEARCH_FIELDS,
#             normalized_fields=NORMALIZED_FIELDS,
#         )

#         # Filtros.
#         status = form.cleaned_data.get('status')
#         queryset = filter_by_status(
#             queryset=queryset,
#             status=status,
#             status_field='activo',
#         )

#     #── Ordenamiento ─────────────────
#     order_by = request.GET.get('order_by', 'nombre_normalizado').strip()
#     direction = request.GET.get('direction', 'asc')

#     queryset = sort_queryset(
#         queryset=queryset,
#         order_by=order_by,
#         direction=direction,
#         order_fields=ORDER_FIELDS,
#         default_field='nombre_normalizado',
#     )

#     # ── Columnas ───────────────────────────
#     columns = [
#         {'header': 'Distrito Judicial', 'field': 'distrito_judicial_nombre', 'width': 25, 'format': 'cell'},
#         {'header': 'Corte', 'field': 'corte_nombre', 'width': 40, 'format': 'cell'},
#         {'header': 'Sede', 'field': 'nombre', 'width': 30, 'format': 'cell'},
#         {'header': 'Inmediato Superior', 'field': 'sede_superior_nombre', 'width': 30, 'format': 'cell'},
#         {'header': 'Siglas', 'field': 'siglas', 'width': 15, 'format': 'cell'},
#         {'header': 'Estado', 'field': 'activo', 'width': 15, 'format': 'boolean'},
#     ]

#     return export_queryset_to_xlsx(
#         queryset=queryset,
#         columns_config=columns,
#         filename='Sedes Judiciales',
#         sheet_name='Sedes Judiciales',
#     )