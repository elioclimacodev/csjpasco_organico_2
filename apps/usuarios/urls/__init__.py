from django.urls import include, path


app_name = 'usuarios'
urlpatterns = [
    path('registro/', include('apps.usuarios.urls.registro')),
    path('sesion/', include('apps.usuarios.urls.acceso')),
    path('contrasena/', include('apps.usuarios.urls.contrasena')),
    path('cuentas/', include('apps.usuarios.urls.cuentas')),
]