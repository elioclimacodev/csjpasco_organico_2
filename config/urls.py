"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from django.conf.urls.static import static
from django.conf import settings

# Django.
urlpatterns = [
    path('admin/', admin.site.urls),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Respuesta única ante una denegación de acceso: página, ventana o
# notificación según la petición (feature 002, contracts/respuestas-acceso.md §2).
handler403 = 'apps.usuarios.views.denegacion.permiso_denegado'

# URLs de las aplicaciones del proyecto.
urlpatterns += [
    path('usuarios/', include('apps.usuarios.urls')),
    path('', include('apps.main.urls')),
    path('personas/', include('apps.personas.urls')),
    path('ubicaciones/', include('apps.ubicaciones.urls')),
    path('organizacion/', include('apps.organizacion.urls')),
]

# URLs para el flujo de 
# from django.contrib.auth import views as auth_views

# from apps.users.authentication.views import login_user
# from apps.users.registration.views import registration_user, terms_of_service, activate, registration_confirm
# from apps.users.password.views import CustomPasswordResetView

# urlpatterns += [
#     # Registro de usuarios.
#     path('usuarios/registro/nuevo/', registration_user, name='register'),
#     path('usuarios/registro/terminos-del-servicio/', terms_of_service, name='terms_of_service'),
#     path('usuarios/registro/activar/<str:uidb64>/<str:token>/', activate, name='activate'),
#     path('usuarios/registro/activar/confirmacion/', registration_confirm, name='registration_confirm'),
    
#     # Autenticación.
#     path('usuarios/ingresar/', login_user, name='login'),
#     path('usuarios/salir/', auth_views.LogoutView.as_view(next_page='/'), name='logout' ),
    
#     # Restablecer contraseña de usuario.
#     path(
#         'restablecer/',
#         # auth_views.PasswordResetView.as_view(
#         #     template_name='password/reset.html',
#         #     email_template_name='password/reset_email.html',
#         #     subject_template_name='password/reset_subject.txt',
#         #     extra_context={'field_name': 'email'}
#         # ),
#         CustomPasswordResetView.as_view(),
#         name='password_reset'
#     ),
    
#     path(
#         'restablecer/correo/enviado/',
#         auth_views.PasswordResetDoneView.as_view(
#             template_name='password/reset_done.html'
#         ),
#         name='password_reset_done'
#     ),
    
#     path(
#         'restablecer/<uidb64>/<token>/',
#         auth_views.PasswordResetConfirmView.as_view(
#             template_name='password/reset_confirm.html'
#         ),
#         name='password_reset_confirm'
#     ),
    
#     path(
#         'restablecer/completado/',
#         auth_views.PasswordResetCompleteView.as_view(
#             template_name='password/partials/reset_complete.html'
#         ),
#         name='password_reset_complete'
#     ),
# ]