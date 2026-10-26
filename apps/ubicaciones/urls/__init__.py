from django.urls import path, include


app_name = 'ubicaciones'

urlpatterns = [
    path(
        'paises/', 
        include('apps.ubicaciones.urls.paises')
    ),
    path(
        'paises/<int:pais_id>/departamentos/', 
        include('apps.ubicaciones.urls.departamentos')
    ),
    path(
        'departamentos/<int:dpto_id>/provincias/',
        include('apps.ubicaciones.urls.provincias')
    ),
    path(
        'provincia/<int:prov_id>/distrito/',
        include('apps.ubicaciones.urls.distritos')
    )
]
