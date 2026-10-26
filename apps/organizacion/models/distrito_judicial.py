from django.core.exceptions import ValidationError
from django.db import models, IntegrityError

from apps.common.utils.text import normalize_alphanumeric, format_proper_name


class DistritoJudicial(models.Model):
    # Distrito Judicial
    nombre = models.CharField('Nombre', max_length=256, unique=True)
    nombre_normalizado = models.CharField(
        verbose_name='Nombre Normalizado',
        max_length=256,
        blank=True,
        unique=True,
        editable=False,
        error_messages={
            'unique': 'El Distrito Judicial ya existe.',
        }        
    )

    # Corte Superior de Justicia.
    corte = models.CharField('Corte', max_length=256, unique=True, blank=False, null=True)
    siglas = models.CharField('Siglas', max_length=20, blank=True, null=True) 

    # Datos geográficos.
    latitud = models.CharField('Latitud', max_length=10, blank=True, null=True)
    longitud = models.CharField('Longitud', max_length=10, blank=True, null=True)

    activo = models.BooleanField('Activo', default=True)
    # TODO: Ampliar estos datos.
    # delimitacion_territorial
    # provincias
    # datos históricos

    # Auditoría.
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Distrito Judicial'
        verbose_name_plural = 'Distritos Judiciales'
        ordering = ['nombre_normalizado']

        constraints = [
            models.CheckConstraint(
                condition=~models.Q(nombre=''),
                name='dj_nombre_not_empty',
            ),
            models.UniqueConstraint(
                fields=['nombre_normalizado'],
                name='dj_unique_nombre_normalizado',
                condition=~models.Q(nombre_normalizado='')
            ),
            # Los campos siglas y ubigeo_inei aceptan nulos, en caso
            # contengan valores válidos deberán ser únicos.
            models.UniqueConstraint(
                fields=['siglas'],
                name='dj_unique_acronyms_when_has_value',
                condition=models.Q(siglas__isnull=False) & ~models.Q(siglas='')
            ),
        ]

    def _normalize_values(self):
        nombre = format_proper_name(self.nombre.strip())

        if self.nombre and self.nombre.strip():
            self.nombre = nombre
            self.nombre_normalizado = normalize_alphanumeric(self.nombre)
            
        if self.corte and self.corte.strip():
            self.corte = format_proper_name(self.corte)
        else:
            self.corte = f'Corte Superior de Justicia de {nombre}'

        if self.siglas and self.siglas.strip():
            self.siglas = self.siglas.upper()
        else:
            self.siglas = f'CSJ {nombre.upper()}'

    def _normalize_empty_optional_fields(self):
        '''
        Convierte las cadenas vacías a None en los campos opcionales
        para que los UniqueContraint condicionales funcionen correctamente
        a nivel de base de datos.
        '''
        optional_fields = ['siglas', 'latitud', 'longitud']
        for field in optional_fields:
            if getattr(self, field) == '':
                setattr(self, field, None)

    def _check_unique_fields(self):
        '''
        Valida la unicidad de los campos opcionales únicos y asocia
        los errores del campo visible correspondiente.
        '''
        errors = {}

        optional_fields_map = {
            'nombre_normalizado': 'El Distrito Judicial ya existe.',
            'siglas': 'Las siglas ya existen.',
            'latitud': 'La latitud ya existe.',
            'longitud': 'La longitud ya existe.',
        }

        for field, message in optional_fields_map.items():
            value = getattr(self, field)
            if value:
                queryset = DistritoJudicial.objects.filter(**{field: value})
                if self.pk:
                    queryset = queryset.exclude(pk=self.pk)
                if queryset.exists():
                    if field == 'nombre_normalizado':
                        errors['nombre'] = message
                    else:
                        errors[field] = message

        if errors:
            raise ValidationError(errors)

    def clean(self):
        super().clean()

        self._normalize_values()
        self._normalize_empty_optional_fields()
        self._check_unique_fields()

    def save(self, *args, **kwargs):
        self._normalize_values()
        self._normalize_empty_optional_fields()
        super().save(*args, **kwargs)

    def __str__(self):
        return {self.nombre}