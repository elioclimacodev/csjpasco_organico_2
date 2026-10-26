from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.contrib import messages

from .forms import CustomAuthenticationForm


def login_user(request):
    """
    Permite el inicio de sesión de los usuarios.
    """
    
    # Si el usuario está autenticado se le redirecciona a la
    # página principal.
    if request.user.is_authenticated:
        return redirect('main:index')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Si la opción "Recordarme en este equipo" no se encuentra 
            # activada, la sección expira al cierre del navegador.
            if not form.cleaned_data.get('remember_me'):
                request.session.set_expiry(0)
            else:
                # La sesión se mantendrá abierta por 7 días.
                request.session.set_expiry(60 * 60 * 24 * 7) 
                
            return redirect('main:index')
        
        if request.headers.get('HX-Request'):
            return render(request, 'authentication/login_form.html', {'form': form})
    else:
        form = CustomAuthenticationForm()
        
    context = {
        'form': form,
        'title': 'Bienvenido'
    }
    return render(request, 'authentication/login.html', context)


def logout_user(request):
    """
    Permite el cierre de la sesión de usuario.
    """
    
    logout(request)
    messages.info(
        request,
        'Has cerrado tu sesión correctamente'
    )
    return redirect('main:index')