from django.urls import path

from apps.usuarios.views import acceso

urlpatterns = [
    path('iniciar/', acceso.UsuarioLoginView.as_view(), name='iniciar_sesion'),
    path('cerrar/', acceso.UsuarioLogoutView.as_view(), name='cerrar_sesion'),
]