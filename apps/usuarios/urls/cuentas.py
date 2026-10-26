from django.urls import path

from apps.usuarios.views import cuentas


urlpatterns = [
    path('', cuentas.usuarios_list, name='list'),
]