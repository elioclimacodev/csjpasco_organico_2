from django.urls import path

from apps.ubicaciones.views import paises


urlpatterns = [
    path('', paises.countries_list, name='countries_list'),    
    path('exportar/xlsx/', paises.countries_export, name='countries_export'),
    path('nuevo/', paises.country_create, name='country_create'),

    path('<int:pk>/detalles/', paises.country_details, name='country_details'),
    path('<int:pk>/editar/', paises.country_update, name='country_update'),
    path('<int:pk>/estado/', paises.country_toggle, name='country_toggle'),
]