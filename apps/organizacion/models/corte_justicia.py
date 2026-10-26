from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import models


from apps.common.validators import pdf_file_validator
from apps.common.uploads import LocalUploadPath
from apps.common.utils import normalize_alphanumeric, format_proper_name

from apps.organizacion.models import DistritoJudicial


class CorteJusticia(models.Model):
    class NivelCorte(models.TextChoices):
        SUPERIOR = 'SUPERIOR', 'Corte Superior'
        SUPREMA = 'SUPREMA', 'Corte Suprema'
        CONSTITUCIONAL = 'CONSTITUCIONAL', 'Tribunal Constitucional'

    distrito_judicial = models.OneToOneField(
        DistritoJudicial,
        verbose_name='Distrito Judicial',
        on_delete=models.PROTECT,
        related_name='corte_superior',
    )

    nivel = models.CharField(
        verbose_name='Nivel Jerárquico',
        max_length=28,
        choices=NivelCorte.choices,
        default=NivelCorte.SUPERIOR,
    )

    nombre = models.CharField(
        verbose_name='Nombre',
        max_length=256,
        unique=True,
    )

    nombre_normalizado = models.CharField(
        verbose_name='Nombre normalizado',
        max_length=256,
        unique=True,
        editable=False,
        error_messages={
            'unique': 'La Corte Superior de Justicia ya existe.'
        }
    )

    siglas = models.CharField(
        verbose_name='Siglas',
        max_length=20,
        blank=True,
        null=True
    )

    # TODO: Incorporar estos campos cuando sea necesario.
    # fecha_instalacion = models.DateField(
    #     verbose_name='Fecha de instalación',
    #     blank=True,
    #     null=True,
    # )

    # norma_instalacion = models.CharField(
    #     verbose_name='Documento de instalación',
    #     max_length=256,
    #     blank=True,
    #     null=True,
    #     help_text='Ejem: Resolución Administrativa N.° 000159-2005-CE-PJ',
    # )

    # archivo_instalacion = models.FileField(
    #     verbose_name='Archivo de instalación',
    #     blank=True,
    #     null=True,
    #     validators=[pdf_file_validator],
    #     upload_to=LocalUploadPath(
    #         app_name='organizacion',
    #         model_name='corte_justicia',
    #         document_type='instalacion',
    #     ),        
    # )

    # fecha_funcionamiento = models.DateField(
    #     verbose_name='Fecha de funcionamiento',
    #     blank=True,
    #     null=True,
    # )

    # norma_funcionamiento = models.CharField(
    #     verbose_name='Documento de funcionamiento',
    #     max_length=256,
    #     blank=True,
    #     null=True,
    #     help_text='Ejem: Resolución Administrativa N.° 000159-2005-CE-PJ',
    # )

    # archivo_funcionamiento = models.FileField(
    #     verbose_name='Archivo de funcionamiento',
    #     blank=True,
    #     null=True,
    #     validators=[pdf_file_validator],
    #     upload_to=LocalUploadPath(
    #         app_name='organizacion',
    #         model_name='corte_justicia',
    #         document_type='funcionamiento',
    #     ),        
    # )

    activo = models.BooleanField(
        verbose_name='Activo',
        default=True,
    )

    class Meta:
        verbose_name = 'Corte Superior de Justicia'
        verbose_name_plural = 'Cortes Superiores de Justicia'
        ordering = ['nombre']

        constraints = [
            models.CheckConstraint(
                condition=~models.Q(nombre=''),
                name='csj_nombre_not_empty',
            ),
            # models.CheckConstraint(
            #     condition=(
            #         models.Q(fecha_instalacion__isnull=True)
            #         | models.Q(fecha_funcionamiento__isnull=True)
            #         | models.Q(fecha_funcionamiento__gte=models.F('fecha_instalacion'))
            #     ),
            #     name='csj_operation_date_gte_installation_date',
            # ),
        ]

    @property
    def distrito_judicial_nombre(self):
        return self.distrito_judicial.nombre if self.distrito_judicial else ''

    def _normalize_values(self):
        if self.nombre and self.nombre.strip():
            self.nombre = format_proper_name(self.nombre)
            self.nombre_normalizado = normalize_alphanumeric(self.nombre)

        # if self.norma_instalacion and self.norma_instalacion.strip():
        #     self.norma_instalacion = self.norma_instalacion.upper()

        # if self.norma_funcionamiento and self.norma_funcionamiento.strip():
        #     self.norma_funcionamiento = self.norma_funcionamiento.upper()            

    # def _validate_dates(self):
    #     '''
    #     Valida la coherencia de las fechas institucionales.
    #     '''
    #     errors = {}
    #     today = timezone.localdate()

    #     # La fecha de instalacion y funcionamiento no pueden ser futuras.
    #     if (
    #         self.fecha_instalacion and 
    #         self.fecha_instalacion > today
    #     ):
    #         errors['fecha_instalacion'] = (
    #             'La fecha de instalación no puede ser futura.'
    #         )

        
    #     if (
    #         self.fecha_funcionamiento and
    #         self.fecha_funcionamiento > timezone.localdate()
    #     ):
    #         errors['fecha_funcionamiento'] = 'La fecha de funcionamiento no puede ser futura.'

    #     # El funcionamiento no puede ser anterior a la instalación.
    #     if (
    #         self.fecha_instalacion and 
    #         self.fecha_funcionamiento and
    #         self.fecha_funcionamiento < self.fecha_instalacion
    #     ):
    #         errors['fecha_funcionamiento'] = 'La fecha de funcionamiento no puede ser anterior a la fecha de instalación.'

    #     return errors

    def clean(self):
        super().clean()
        self._normalize_values()

        # errors = {}
        # errors.update(self._validate_dates())

        # if errors:
        #     raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self._normalize_values()
        super().save(*args, **kwargs)


    def __str__(self):
        return self.nombre
