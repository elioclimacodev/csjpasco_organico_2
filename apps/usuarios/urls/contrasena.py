from django.urls import path

from apps.usuarios.views import contrasena


urlpatterns = [
    # Restablecer contraseña.
    path('restablecer/', contrasena.UsuarioPasswordResetView.as_view(), name='restablecer_contrasena'),
    path('restablecer/enviado/', contrasena.UsuarioPasswordResetDoneView.as_view(), name='restablecer_contrasena_enviado'),
    path('restablecer/<uidb64>/<token>/', contrasena.UsuarioPasswordResetConfirmView.as_view(), name='restablecer_contrasena_confirmar'),
    path('restablecer/completado/', contrasena.UsuarioPasswordResetComplete.as_view(), name='restablecer_contrasena_completado'),

    # Cambiar contraseña.
    path('cambiar/', contrasena.UsuarioPasswordChangeView.as_view(), name='cambiar_contrasena'),
    path('cambiar/completado/', contrasena.UsuarioPasswordChangeDoneView.as_view(), name='cambiar_contrasena_completado'),
]