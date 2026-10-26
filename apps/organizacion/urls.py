from django.urls import path

from apps.organizacion.views import (
    distrito_judicial       as dj,
    sede_judicial           as sj,
    organo_jurisdiccional   as oj,
    materia_jurisdiccional  as mj,
)


app_name = 'organizacion'
urlpatterns = []

# Distritos Judiciales.
urlpatterns += [
    path('distrito-judicial/nuevo/', dj.distrito_judicial_create, name='distrito_judicial_create'),
    path('distrito-judicial/<int:pk>/editar/', dj.distrito_judicial_update, name='distrito_judicial_update'),
    path('distrito-judicial/<int:pk>/detalles/', dj.distrito_judicial_details, name='distrito_judicial_details'),
    path('distrito-judicial/<int:pk>/estado/', dj.distrito_judicial_toggle, name='distrito_judicial_toggle'),
    
    path('distritos-judiciales/', dj.distritos_judiciales_list, name='distritos_judiciales_list'),
    path('distritos-judiciales/exportar/xlsx/', dj.distritos_judiciales_export, name='distritos_judiciales_export'),
]


# Sedes Judiciales.
urlpatterns += [
    path('sede/<int:pk>/editar/', sj.sede_update, name='sede_update'),
    path('sede/<int:pk>/detalles/', sj.sede_details, name='sede_details'),
    path('sede/<int:pk>/estado/', sj.sede_toggle, name='sede_toggle'),

    path('corte/<int:dj_id>/sedes/', sj.sedes_list, name='sedes_list'),
    path('corte/<int:dj_id>/sede/nuevo/', sj.sede_create, name='sede_create'),
    path('corte/<int:dj_id>/exportar/xlsx/', sj.sedes_export, name='sedes_export'),
]


# Órganos Jurisdiccionales.
urlpatterns += [
    path('organo-jurisdiccional/nuevo/', oj.organo_jurisdiccional_create, name='organo_jurisdiccional_create'),
    path('organo-jurisdiccional/<int:pk>/editar/', oj.organo_jurisdiccional_update, name='organo_jurisdiccional_update'),
    path('organo-jurisdiccional/<int:pk>/detalles/', oj.organo_jurisdiccional_details, name='organo_jurisdiccional_details'),
    path('organo-jurisdiccional/<int:pk>/estado/', oj.organo_jurisdiccional_toggle, name='organo_jurisdiccional_toggle'),
    
    path('organos-jurisdiccionales/', oj.organos_jurisdiccionales_list, name='organo_jurisdiccional_toggle'),
    path('organos-jurisdiccionales/exportar/xlsx/', oj.organos_jurisdiccionales_export, name='organos_jurisdiccionales_export'),    
]


# Materias Jurisdiccionales.
urlpatterns += [
    path('materia-jurisdiccional/nuevo/', mj.materia_jurisdiccional_create, name='materia_jurisdiccional_create'),
    path('materia-jurisdiccional/<int:pk>/editar/', mj.materia_jurisdiccional_update, name='materia_jurisdiccional_update'),
    path('materia-jurisdiccional/<int:pk>/detalles/', mj.materia_jurisdiccional_details, name='materia_jurisdiccional_details'),
    path('materia-jurisdiccional/<int:pk>/estado/', mj.materia_jurisdiccional_toggle, name='materia_jurisdiccional_toggle'),
    
    path('materias-jurisdiccionales/', mj.materias_jurisdiccionales_list, name='materias_jurisdiccionales_list'),
    path('materias-jurisdiccionales/exportar/xlsx/', mj.materias_jurisdiccionales_export, name='materias_jurisdiccionales_export'),       
]