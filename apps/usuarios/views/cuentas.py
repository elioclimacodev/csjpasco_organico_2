import json

from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib import messages
from django.apps import apps
from django.http import HttpResponse
from django.urls import reverse

from apps.common.querysets import (
    export_queryset_to_xlsx,
    filter_by_status,
    search_queryset,
    sort_queryset,
)

from apps.usuarios.forms.cuentas import UsuarioFiltersForm
from apps.personas.models import Persona
# from apps.usuarios.models import Usuario

Usuario = get_user_model()


ORDER_FIELDS = {
    'numero_documento'  : 'persona__numero_documento',
    'nombres'           : 'persona__nombres',
    'apellido_paterno'  : 'persona__apellido_paterno',
    'apellido_materno'  : 'persona__apellido_materno',
    'email'             : 'email',
    'last_login'        : 'last_login',
    'is_superuser'      : 'is_superuser',
    'is_staff'          : 'is_staff',
    'is_active'         : 'is_active',
}

SEARCH_FIELDS = [
    'persona__numero_documento',
    'persona__nombres_normalizado',
    'persona__apellido_paterno_normalizado',
    'persona__apellido_materno_normalizado',
    #correo

]

NORMALIZED_FIELDS = [
    'persona__nombres_normalizado',
    'persona__apellido_paterno_normalizado',
    'persona__apellido_materno_normalizado',
]


@permission_required(
    'usuarios.view_usuario',
    raise_exception=True,
)
def usuarios_list(request):
    users = (
        Usuario.objects.
        select_related('persona')
    )
    unfiltered_users = users.count()

    # ── Filtros y búsqueda ───────────
    form = UsuarioFiltersForm(
        request.GET or None,
        request_path=request.path,
    )

    per_page = 10

    if form.is_valid():
        # Búsqueda
        search = form.cleaned_data.get('search', '').strip()
        users = search_queryset(
            queryset=users,
            search=search,
            search_fields=SEARCH_FIELDS,
            normalized_fields=NORMALIZED_FIELDS,
        )

        # Filtros.
        status = form.cleaned_data.get('status')
        users = filter_by_status(
            queryset=users,
            status=status,
            status_field='activo',
        )

        per_page = form.cleaned_data.get('per_page') or 10

        # ── Ordenamiento ──────────────────
        order_by = request.GET.get('order_by', 'persona__apellido_paterno').strip()
        direction = request.GET.get('direction', 'asc')
        users = sort_queryset(
            queryset=users,
            order_by=order_by,
            direction=direction,
            order_fields=ORDER_FIELDS,
            default_field='persona__apellido_paterno_normalizado'
        )

    # ── Paginación ───────────────────
    try:
        page_num = int(request.GET.get('page', 1))
    except (ValueError, TypeError):
        page_num = 1

    paginator = Paginator(users, per_page)
    page_obj = paginator.get_page(page_num)
    page_range = paginator.get_elided_page_range(
        number=page_num,
        on_each_side=2,
        on_ends=1
    )

    # ── Evalua la petición ───────────
    if request.headers.get('HX-Request'):
        template = 'usuarios/cuentas/partials/_datatable.html'
    else:
        template = 'usuarios/cuentas/list.html'

    context = {
        'pre_title': apps.get_app_config('usuarios').verbose_name,
        'title': 'Administración de usuarios',
        'list': True,
        
        'form': form,

        'paginator': paginator,
        'page_obj': page_obj,
        'page_range': page_range,

        'is_empty_database': unfiltered_users == 0,
        'order_by': order_by,
        'direction': direction,
    }

    return render(request, template, context)

    