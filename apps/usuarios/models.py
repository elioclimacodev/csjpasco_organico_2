from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.personas.choices import TipoDocumento

from .managers import CustomUserManager


class Usuario(AbstractUser):
    '''
    Registra los usuarios que pueden acceder al sistema, bajo la premisa que
    un usuario es una persona, pero una persona no necesariamente es un 
    usuario.
    '''

    # Deshabilitamos el campo 'username' por defecto, ya que usaremos el
    # número de documento como nombre de usuario.
    username = None

    # Campos personalizados para la autenticación.
    tipo_documento = models.CharField(
        verbose_name='Tipo de documento',
        max_length=5,
        choices=TipoDocumento.choices,
        default=TipoDocumento.DNI,
    )

    numero_documento = models.CharField(
        verbose_name='Número de documento',
        max_length=15,
        unique=True,
    )

    # Campos obligatorios.
    email = models.EmailField(
        verbose_name='Correo electrónico',
        unique=True,
    )

    # Define con qué campo se autenticará el usuario.
    USERNAME_FIELD = 'numero_documento'

    # Campos obligatorios al crear el 'superusuario' además del
    # USERNAME_FIELD.
    REQUIRED_FIELDS = ['tipo_documento', 'email']

    # Asignamos el manager personalizado.
    objects = CustomUserManager()


    def __str__(self):
        return f'{self.get_tipo_documento_display()} - {self.numero_documento}'