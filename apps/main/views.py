from django.shortcuts import render


def cuenta_sin_permisos(user):
    """
    Indica si el usuario no tiene ningún permiso, ni directo ni por grupos
    (spec FR-003a). Los superusuarios nunca reciben el aviso.

    `get_all_permissions` reutiliza la caché de permisos que ya llenó el
    menú lateral en la misma solicitud (research R7).
    """
    return not user.is_superuser and not user.get_all_permissions()


# La sesión la exige `apps.usuarios.middleware.LoginRequiredMiddleware`.
def index(request):
    template = 'main/index.html'
    context = {
        'pre_title': 'Título secundario',
        'title': 'Título de prueba',
        'card_title': 'Título de la tarjeta',
        'cuenta_sin_permisos': cuenta_sin_permisos(request.user),
    }
    return render(request, template, context)
