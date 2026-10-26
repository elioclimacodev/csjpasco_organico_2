from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.html import strip_tags
from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from django.conf import settings

from apps.users.models import Person

from .tokens import account_activation_token
from .forms import CustomUserCreationForm


def terms_of_service(request):
    """
    Muestra los términos y las condiciones del servicio, previo al registro
    del nuevo usuario.
    """
    
    template = 'registration/terms_of_service.html'
    context = {
        'title': 'Términos del servicio',
    }
    return render(request, template, context)


def registration_user(request):
    """
    Registra un nuevo usuario. Si el fomulario tiene errores, los muestra usando
    HTMX; si el registro es exitoso, crea el usuario con estado is_active=False y
    redirige a la vista de confirmación de envío del correo electrónico con 
    el enlace de activación.
    """
    
    title = 'Registro de usuario'
    
    # Si el usuario ya está autenticado se le redirige a la
    # página principal del sistema.
    if request.user.is_authenticated:
        return redirect(settings.LOGIN_REDIRECT_URL)
    
    # Registro de usuario.
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # El usuario estará inactivo hasta la activación por
            # email.
            user.is_active = False
            # Guarda el hash de la contraseña.
            user.set_password(form.cleaned_data['password2'])
            user.save()
            
            # Invocamos a la función que envía el correo de activación.
            send_activation_email(request, user)
            return redirect('registration_confirm')

        if request.headers.get('HX-Request'):
            context = {
                'title': title,
                'form': form,
            }
            return render(request, 'registration/partials/form.html', context)
    else:
        form = CustomUserCreationForm(initial={'terminos': True})
    
    template = 'registration/register.html'
    context = {
        'title': title,
        'form': form,
    }
    return render(request, template, context)


def registration_confirm(request):
    """
    Muestra un mensaje de conformación del envío del correo electrónico
    con el enlace de activación.
    """
    
    template = 'registration/register_confirm_content.html'
    context = {'title': 'Correo de activación enviado'}
    return render(request, template, context)


def send_activation_email(request, user):
    """
    Envía el correo electrónico con el enlace de activación.
    """
    
    # Establece el tipo de protocolo según el tipo de conexión.
    protocol = 'https' if request.is_secure() else 'http'
    
    # Obtiene el dominio del sitio.
    # domain = get_current_site(request).domain # Para producción
    domain = request.get_host() # Solo para desarrollo.
    
    # Prepara el contenido del correo usando una plantilla.
    message = render_to_string(
        'registration/register_activation_email.html', {
            'protocol': protocol,
            'user': user,
            'domain': domain,
            # Codifica el UID para en una cadena Base64 segura para el uso
            # en URLs.
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            # Token de un solo uso.
            'token': account_activation_token.make_token(user),
        }
    )
    
    # Devuelve el mensaje HTML eliminado todas las etiquetas (<p>, <div>, <b>, etc)
    text_content = strip_tags(message)
    
    # Instancia el objeto email con los parámetros del mensaje.
    email = EmailMultiAlternatives(
        subject='CSJ Pasco: Activación de cuenta de usuario',
        body=text_content,
        from_email=settings.EMAIL_HOST_USER,
        to=[user.email],
    )
    
    # Adjunta al objeto email una versión alternativa en formato texto 
    # en caso el mensaje no se pueda mostrar de manera correcta.
    email.attach_alternative(message, 'text/html')
    
    # Envía el correo electrónico al usuario.
    email.send()


def activate(request, uidb64, token):
    """
    Decodifica el UID base64 del enlace, obtiene el usuario que ha solicitado
    la creación del usuario y valida el token de activación.
    Si todo es válido, activa la cuenta con is_active = True y muestra el 
    página de activación exitosa; en caso contrario muestra la página 
    indicando que el enlace no es válido o ha expirado.
    """
    
    try:
        # Decodifica el UID.
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Person.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Person.DoesNotExist):
        user = None
        
    if user is not None and account_activation_token.check_token(user, token):
        # Si el usuario ya está activo lo redirige al login.
        if user.is_active:
            pass
            # return redirect('login')
        
        # En caso contrario cambia el estado del usuario a activo y 
        # guarda el estado.
        user.is_active = True
        user.save()
        
        # TODO: Inicia sesión automáticamente.
        # TODO: login(request, user)
        
        # Muestra la página de éxito.
        return render(request, 'registration/register_activation.html', {'user': user, 'success': True})

    # Muestra la página de error.
    return render(request, 'registration/register_activation.html', {'success': False})
    