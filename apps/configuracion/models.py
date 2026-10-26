from django.db import models

from django.core.cache import cache
from django.core.exceptions import ValidationError

from apps.organizacion.models.distrito_judicial import DistritoJudicial
from apps.organizacion.models.corte_justicia import CorteSuperior


class ConfiguracionInstitucional(models.Model):
    '''
    Configuración general de la instalación del sistema.
    Solo debe existir un registro.
    '''
    distrito_judicial = models.OneToOneField(
        DistritoJudicial,
        verbose_name='Distrito Judicial',
        on_delete=models.PROTECT,
    )

    corte_superior = models.OneToOneField(
        CorteSuperior,
        verbose_name='Corte Superior de Justicia',
        on_delete=models.PROTECT,
    )

    activo = models.BooleanField(
        verbose_name='Activo',
        default=True,
    )

    # TODO: Incorporar estos campos.
    # logo = models.ImageField()
    # favicon
    # correo_institucional
    # telefono,
    # direccion
    # anexo

    class Meta:
        verbose_name = 'Configuración Institucional'
        verbose_name_plural = 'Configuración Institucional'

    def clean(self):
        if (
            not self.pk and
            ConfiguracionInstitucional.objects.exists()
        ):
            raise ValidationError(
                'Ya existe una configuración institucional activa.'
            )

    def __str__(self):
        return str(self.corte_superior)