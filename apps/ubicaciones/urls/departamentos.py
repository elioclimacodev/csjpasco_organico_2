from django.urls import path

from apps.ubicaciones.views import departamentos


urlpatterns = [
    path(
        '', 
        departamentos.departamentos_list, 
        name='departamentos_list'
    ),
    path(
        'exportar/xlsx/', 
        departamentos.departamento_export, 
        name='departamentos_export'
    ),

    path(
        'nuevo/', 
        departamentos.departamento_create, 
        name='departamento_create'
    ),
    path(
        '<int:pk>/detalles/', 
        departamentos.departamento_details, 
        name='departamento_details'
    ),
    path(
        '<int:pk>/editar/',
        departamentos.departamento_update,
        name='departamento_update'
    ),
    path(
        '<int:pk>/estado/',
        departamentos.departamento_toggle,
        name='departamento_toggle'
    )
]