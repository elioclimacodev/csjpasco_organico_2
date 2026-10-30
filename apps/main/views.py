from django.shortcuts import render


# La sesión la exige `apps.usuarios.middleware.LoginRequiredMiddleware`.
def index(request):
    template = 'main/index.html'
    context = {
        'pre_title': 'Título secundario',
        'title': 'Título de prueba',
        'card_title': 'Título de la tarjeta',
    }
    return render(request, template, context)
