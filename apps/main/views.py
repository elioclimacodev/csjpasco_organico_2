from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def index(request):
    template = 'main/index.html'
    context = {
        'pre_title': 'Título secundario',
        'title': 'Título de prueba',
        'card_title': 'Título de la tarjeta',
    }
    return render(request, template, context)


def signup(request):
    template = 'main/signup.html'
    context = {
        
    }
    return render(request, template, context)