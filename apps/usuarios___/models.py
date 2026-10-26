from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

from apps.personas.validators import validate_id_number, validar_numero_documento
from apps.personas.models import Persona

from .managers import UsuarioManager


class Usuario(AbstractUser):
    '''
    Modelo de usuario del sistema.
    El nombre de usuario (username) es el número de documento de identidad
    de la persona. Se conserva toda la funcionalidad del sistema de
    autenticación y autorización de Django (grupos y permisos).
    '''

    first_name = None
    last_name = None

    persona = models.OneToOneField(
        Persona,
        verbose_name='Persona',
        on_delete=models.PROTECT,
        related_name='usuario',
        help_text=(
            'Un usuario es una persona registrada en la institución.'
            'Si no existe, se crea automáticamente con los datos de identidad.'
        ),)

    email = models.EmailField('Correo electrónico', unique=True)

    REQUIRED_FIELDS = ['email']

    objects = UsuarioManager()

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['username']

    def clean(self):
        super().clean()
        if self.persona_id and self.persona.tipo_documento:
            if self.username != self.persona.numero_documento:
                raise ValidationError(
                    {
                        'username': (
                            'El nombre de usuario debe ser el número de documento de'
                            'identidad de la persona.'
                        )
                    }
                )
            validar_numero_documento(self.persona.tipo_documento, self.username)

    def get_full_name(self):
        return self.persona.nombre_completo

    @property
    def tipo_documento(self):
        return self.persona.tipo_documento

    @property
    def numero_documento(self):
        return self.persona.numero_documento