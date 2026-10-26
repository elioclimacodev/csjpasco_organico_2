from django.urls import path

from apps.ubicaciones.views import provincias


urlpatterns = [
    path(
        '',
        provincias.provincias_list,
        name='provincias_list',
    ),
    path(
        'exportar/xlsx/',
        provincias.provincias_export,
        name='provincias_export',
    ),

    path(
        'nuevo/',
        provincias.provincia_create,
        name='provincia_create',
    ),
    path(
        '<int:pk>/detalles/',
        provincias.provincia_details,
        name='provincia_details',
    ),
    path(
        '<int:pk>/editar/',
        provincias.provincia_update,
        name='provincia_update',
    ),
    path(
        '<int:pk>/estado/',
        provincias.provincia_toggle,
        name='provincia_toggle',
    ),
]