from django.urls import path

from apps.usuarios.views import registro


urlpatterns = [
    path('registro/', registro.registro, name='registro'),
    path('activar-cuenta/<uidb64>/<token>/', registro.activar_cuenta, name='activar_cuenta'),
    path('registro-completo/', registro.registro_completo, name='registro_completo'),

]