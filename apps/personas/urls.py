from django.urls import path

from .views import (
    personas_list, persona_create,
)


app_name = 'personas'

urlpatterns = [
    path('', personas_list, name='list'),

    path('create/', persona_create, name='create')
]