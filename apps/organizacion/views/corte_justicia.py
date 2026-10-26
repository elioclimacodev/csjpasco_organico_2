
# import json

# from django.core.paginator import Paginator
# from django.shortcuts import render, get_object_or_404
# from django.http import HttpResponse
# from django.urls import reverse
# from django.apps import apps

# from apps.common.querysets import (
#     sort_queryset, filter_by_status, 
#     search_queryset, export_queryset_to_xlsx
# )
# from apps.common.utils import format_proper_name

# from apps.organizacion.models import DistritoJudicial, CorteJusticia
# from apps.organizacion.forms import CorteJusticiaForm, CorteJusticiaFiltersForm


# ORDER_FIELDS = {
#     'nombre'                        : 'nombre_normalizado',
#     'siglas'                        : 'siglas',
#     'fecha_funcionamiento'          : 'fecha_funcionamiento',
#     'nro_documento_funcionamiento'  : 'nro_documento_funcionamiento',
#     'archivo_funcionamiento'        : 'archivo_funcionamiento',
#     'activo'                        : 'activo',
# }

# SEARCH_FIELDS = ['siglas']

# NORMALIZED_FIELDS = ['nombre_normalizado']


# def cortes_list(request, dj_id):
#     '''
#     Muestra las Cortes Superiores de Justicia permitiendo su ordenamiento, paginación,
#     filtrado y exportación como archivo xlsx.
#     '''
#     dj = get_object_or_404(DistritoJudicial, pk=dj_id)
#     queryset = CorteJusticia.objects.filter(distrito_judicial=dj)
#     unfiltered_count = queryset.count()

#     #── Filtros y búsqueda ───────────
#     form = CorteJusticiaFiltersForm(
#         request.GET or None,
#         request_path=request.path
#     )

#     per_page = 10

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

#         per_page = form.cleaned_data.get('per_page') or 10
    
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

#     #── Paginación ───────────────────
#     try:
#         page_num = int(request.GET.get('page', 1))
#     except (TypeError, ValueError):
#         page_num = 1

#     paginator = Paginator(queryset, per_page)
#     page_obj = paginator.get_page(page_num)
#     page_range = paginator.get_elided_page_range(
#         number=page_obj.number,
#         on_each_side=2,
#         on_ends=1,
#     )

#     # Si la petición viene de un elemento HTMX, renderiza un partial;
#     # en caso contrario, rederiza la plantilla completa.
#     if request.headers.get('HX-Request'):
#         template = 'organizacion/corte_justicia/partials/_datatable.html'
#     else:
#         template = 'organizacion/corte_justicia/list.html'

#     context = {
#         'pre_title': apps.get_app_config('organizacion').verbose_name,
#         'title': f'{DistritoJudicial._meta.verbose_name} de {dj.nombre}',
#         'distrito_judicial': dj,

#         'form': form,

#         'paginator': paginator,
#         'page_obj': page_obj,
#         'page_range': page_range,

#         'is_empty_database': unfiltered_count == 0,
#         'order_by': order_by,
#         'direction':direction
#     }

#     return render(request, template, context)


# def corte_create(request, dj_id):
#     '''
#     Crea el registro de un Distrito Judicial.
#     '''
#     dj = get_object_or_404(DistritoJudicial, pk=dj_id)
    
#     template = 'organizacion/corte_justicia/create.html'

#     context = {
#         'url': reverse('organizacion:corte_create', kwargs={'dj_id': dj.id}),
#         'modal_title': f'Nueva Corte en el Distrito Judicial de {dj.nombre}',
#         # 'create': True,
#     }

#     if request.method == 'POST':
#         form = CorteJusticiaForm(request.POST, request.FILES)
#         if form.is_valid():
#             obj = form.save(commit=False)
#             obj.distrito_judicial = dj
#             obj.save()
#             obj_name = format_proper_name(obj.nombre)

#             return HttpResponse(
#                 status=204,
#                 headers={
#                     'HX-Trigger': json.dumps({
#                         'object_created': None,
#                         'show_toast': {
#                             'type': 'success',
#                             'message': f'Corte Superior de Justicia de "{obj_name}" creado con éxito.',
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
#         context['form'] = CorteJusticiaForm()
#         return render(request, template, context)
    

# def corte_details(request, pk):
#     '''
#     Muestra los detalles de un Distrito Judicial sin posibilidad de modificación.
#     '''
#     obj = get_object_or_404(CorteJusticia, pk=pk)
#     obj_name = format_proper_name(obj.nombre)

#     template = 'organizacion/corte_justicia/details.html'

#     datagrid_items = [
#         ('Distrito Judicial', obj.distrito_judicial.nombre),
#         ('Nombre'           , obj_name),
#         ('Siglas'           , obj.siglas),
#         ('Nivel'            , obj.nivel),
#         ('Estado'           , obj.activo),
#     ]   

#     context = {
#         'url': reverse('organizacion:corte_details', kwargs={'pk': pk}),
#         'title': f'{obj_name}',
#         'modal_title': f'{obj_name}',
#         'obj': obj,
#         'datagrid_items': datagrid_items,
#     }

#     return render(request, template, context)


# def corte_update(request, pk):
#     '''
#     Modifica o actualiza el registro de un Distrito Judicial.
#     '''
#     obj = get_object_or_404(CorteJusticia, pk=pk)
#     obj_name = format_proper_name(obj.nombre)

#     template = 'organizacion/corte_justicia/create.html'

#     context = {
#         'url': reverse('organizacion:corte_update', kwargs={'pk': pk}),
#         'modal_title': f'Editar: {obj_name}',
#         'obj': obj,
#     }

#     if request.method == 'POST':
#         form = CorteJusticiaForm(request.POST, instance=obj)
#         if form.is_valid():
#             form.save()

#             return HttpResponse(
#                 status=204,
#                 headers= {
#                     'HX-Trigger': json.dumps({
#                         'object_updated': None,
#                         'show_toast': {
#                             'type': 'success',
#                             'message': f'"{obj_name}" se actualizó con éxito.'
#                         }
#                     })
#                 }
#             )
#         else:
#             context['form'] = form
#             response = render(request, template, context)
#             response['HX-Trigger']=json.dumps({
#                 'show_toast': {
#                     'type': 'error',
#                     'message': 'El formulario contiene errores. Revise la información ingresada antes de continuar.',
#                 }
#             })
#             return response
#     else:
#         context['form'] = CorteJusticiaForm(instance=obj)
#         return render(request, template, context)
            

# def corte_toggle(request, pk):
#     '''
#     Cambia el estado del registro de activo a inactivo y viceversa.
#     '''
#     obj = get_object_or_404(CorteJusticia, pk=pk)
#     obj_name = format_proper_name(obj.nombre)
    
#     template = 'organizacion/corte_justicia/toggle.html'

#     context = {
#         'url': reverse('organizacion:corte_toggle', kwargs={'pk': pk}),
#         'modal_title': f'Cambiar el estado: {obj_name}',
#         'modal_type': 'danger' if obj.activo else 'success',
#         'model_name': obj._meta.verbose_name,
#         'toggle': True,
#         'obj': obj,
#     }

#     if request.method == 'POST':
#         obj.activo = not obj.activo
#         obj.save()
#         toggle = 'activó' if obj.activo else 'desactivó'

#         return HttpResponse(
#             status=204,
#             headers={
#                 'HX-Trigger': json.dumps({
#                     'object_updated': None,
#                     'show_toast': {
#                         'type': 'success',
#                         'message': f'{obj_name} se {toggle} con éxito.',
#                     }
#                 })
#             }
#         )

#     response = render(request, template, context)
#     response['HX-Modal-Size'] = 'modal-sm'
#     return response


# def cortes_export(request, dj_id):
#     '''
#     Exporta los datos filtrados y ordenados a un archivo xlsx.
#     '''
#     queryset = CorteJusticia.objects.filter(distrito_judicial=dj_id)

#     #── Filtros y búsqueda ───────────
#     form = CorteJusticiaFiltersForm(
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

#     # Encabezados.
#     columns = [
#         {'header': 'Distrito Judicial', 'field': 'distrito_judicial_nombre',   'width': 20, 'format': 'cell'},
#         {'header': 'Corte', 'field': 'nombre', 'width': 35, 'format': 'cell'},        
#         {'header': 'Siglas', 'field': 'siglas', 'width': 15, 'format': 'cell_center'},
#         {'header': 'Estado', 'field': 'activo', 'width': 15, 'format': 'boolean'},
#     ]

#     return export_queryset_to_xlsx(
#         queryset=queryset,
#         columns_config=columns,
#         filename="Corte Superior de Justicia",
#         sheet_name="Corte Superior de Justicia",
#     )