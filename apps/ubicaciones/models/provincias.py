# models.py
from django.core.exceptions import ValidationError
from django.db import models


from apps.common.utils import normalize_alphanumeric, format_proper_name
from apps.ubicaciones.models import Departamento


class Provincia(models.Model):
    departamento = models.ForeignKey(
        Departamento,
        on_delete=models.PROTECT,
        related_name='provincias',
        verbose_name='Departamento',
    )
    nombre = models.CharField('Nombre', max_length=256)
    nombre_normalizado = models.CharField('Nombre normalizado', max_length=256, blank=True, editable=False)
    ubigeo_inei = models.CharField('Ubigeo INEI', max_length=6, blank=True, null=True)
    ubigeo_reniec = models.CharField('Ubigeo RENIEC', max_length=6, blank=True, null=True)
    codigo_postal = models.CharField('Código Postal', max_length=5, blank=True, null=True)
    activo = models.BooleanField('Activo',  default=True )

    # Auditoría.
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Provincia'
        verbose_name_plural = 'Provincias'
        ordering = ['nombre_normalizado']
        constraints = [
            # Unicidad.
            models.UniqueConstraint(
                fields=['departamento', 'id'],
                name='unique_provincia_in_departamento'
            ),
            
            models.UniqueConstraint(
                fields=['ubigeo_inei'],
                name='unique_provincia_ubigeo_inei_when_has_value',
                condition=models.Q(ubigeo_inei__isnull=False) & ~models.Q(ubigeo_inei=''),
            ),
            models.UniqueConstraint(
                fields=['ubigeo_reniec'],
                name='unique_provincia_ubigeo_reniec_when_has_value',
                condition=models.Q(ubigeo_reniec__isnull=False) & ~models.Q(ubigeo_reniec=''),
            ),
            models.UniqueConstraint(
                fields=['codigo_postal'],
                name='unique_provincia_codigo_postal_when_has_value',
                condition=models.Q(codigo_postal__isnull=False) & ~models.Q(codigo_postal=''),
            ),
        ]
        
    @property
    def pais_nombre(self):
        return self.departamento.pais.nombre
    
    @property
    def departamento_nombre(self):
        return self.departamento.nombre
    
    @property
    def get_full_name(self):
        return f'{self.nombre}, {self.departamento.nombre}, {self.departamento.pais.nombre}'

    def _normalize_values(self):
        """
        Normaliza el nombre a mayúsculas y genera su versión
        normalizada (sin acentos, en minúsculas) para búsquedas.
        """
        if self.nombre and self.nombre.strip():
            self.nombre = format_proper_name(self.nombre)
            self.nombre_normalizado = normalize_alphanumeric(self.nombre)

    def _normalize_empty_strings(self):
        """
        Convierte cadenas vacías a None en campos opcionales,
        para que los UniqueConstraints condicionales funcionen
        correctamente a nivel de base de datos.
        """
        optional_fields = ('ubigeo_inei', 'ubigeo_reniec', 'codigo_postal')
        for field in optional_fields:
            if getattr(self, field) == '':
                setattr(self, field, None)

    def _check_unique_optional_fields(self):
        """
        Valida unicidad de campos opcionales a nivel Python,
        para producir mensajes de error por campo específico.

        Nota: los UniqueConstraints en Meta son la salvaguarda
        final a nivel de base de datos.
        """
        errors = {}

        field_map = {
            'ubigeo_inei':   'El Ubigeo del INEI ya existe.',
            'ubigeo_reniec': 'El Ubigeo del RENIEC ya existe.',
            'codigo_postal':   'El código postal ya existe.',
        }

        for field, message in field_map.items():
            value = getattr(self, field)
            if value:
                qs = Provincia.objects.filter(**{field: value})
                if self.pk:
                    qs = qs.exclude(pk=self.pk)
                if qs.exists():
                    errors[field] = message

        if errors:
            raise ValidationError(errors)

    def clean(self):
        '''
        Esta función es ejecutada por el admin y por full_clean().
        No se debe llamar desde save() para no interferir con el flujo
        interno del admin de Django.
        '''
        super().clean()

        self._normalize_empty_strings()
        self._normalize_values()
        self._check_unique_optional_fields()

    def save(self, *args, **kwargs):
        self._normalize_empty_strings()
        self._normalize_values()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre