from django.urls import path

from apps.ubicaciones.views import distritos


urlpatterns = [
    path('',
         distritos.distritos_list,
         name='distritos_list'),
    path('exportar/xlsx/',
         distritos.distritos_export,
         name='distritos_export'),
    path('nuevo/',
         distritos.distrito_create,
         name='distrito_create'),
    path('<int:pk>/detalles/',
         distritos.distrito_details,
         name='distrito_details'),
    path('<int:pk>/editar/',
         distritos.distrito_update,
         name='distrito_update'),
    path('<int:pk>/estado/',
         distritos.distrito_toggle,
         name='distrito_toggle')
]