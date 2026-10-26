from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.urls import reverse_lazy

from .forms import CustomPasswordResetForm, CustomSetPasswordForm


class CustomPasswordResetView(SuccessMessageMixin, PasswordResetView):
    """
    Muestra un formulario para que el usuario ingrese su dirección de correo 
    electrónico.
    La vista verifica si el correo proporcionado se encuentra registrado en la 
    base de datos y, de ser así, genera un enlace único para el restablecimiento 
    de la contraseña.
    Dicho enlace tendrá un solo uso.
    """
    
    form_class = CustomPasswordResetForm
    template_name = 'password/reset.html'
    email_template_name = 'password/reset_email.html'
    subject_template_name = 'password/reset_subject.txt'
    success_message = '''
        Le hemos enviado por correo electrónico las instrucciones para establecer su 
        contraseña, en caso de que exista una cuenta asociada al correo que ingresó. 
        Debería recibirlas en breve. Si no recibe el mensaje, por favor verifique 
        que haya ingresado la dirección con la que se registró y revise su carpeta 
        de correo no deseado.
    '''

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request
        print(f'--------- {request}')
        context['protocol'] = 'https' if request.is_secure() else 'http'
        context['domain'] = request.get_host()
        return context

    
 
   
    # def form_invalid(self, form):
    #     """
    #     Si el formulario tiene errores y viene de HTMX, 
    #     se devuelve solo el fragmento con el formulario y sus errores.
    #     """
        
    #     if self.request.headers.get('HX-Request'):
    #         html = render_to_string(
    #             'password/reset_form.html',
    #             {'form': form, 'title': 'Restablecer contraseña'},
    #             request=self.request
    #         )
    #         return HttpResponse(html)
    #     return super().form_invalid(form)

    # def form_valid(self, form):
    #     """
    #     Si la solicitud proviene de HTMX, devuelve un fragmento de éxito.
    #     """

    #     form.save(request=self.request)
    #     if self.request.headers.get('HX-Request'):
            
    #         html = render_to_string(
    #             'password/reset_success.html',
    #             {'title': 'Correo de recuperación'},
    #             request=self.request
    #         )
    #         return HttpResponse(html)
    #     return super().form_valid(form)
    
    
    
class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """
    Vista que permite definir una nueva contraseña
    después de validar el token del enlace enviado al correo.
    """

    form_class = CustomSetPasswordForm
    template_name = 'password/reset_confirm.html'
    success_url = reverse_lazy('login_user')
    extra_context = {'title': 'Correo enviado'}

    def form_invalid(self, form):
        """Si hay errores en el formulario, se renderiza el parcial de error."""
        if self.request.headers.get('HX-Request'):
            html = render_to_string(
                'password/reset_confirm.html',
                {'form': form},
                request=self.request
            )
            return HttpResponse(html)
        return super().form_invalid(form)

    def form_valid(self, form):
        """Si la solicitud es HTMX, renderiza una confirmación parcial."""
        response = super().form_valid(form)
        if self.request.headers.get('HX-Request'):
            html = render_to_string(
                'password/reset_confirm_success.html',
                {},
                request=self.request
            )
            return HttpResponse(html)
        return response

