from django.core.exceptions import ValidationError
from django.db import models, IntegrityError

from apps.common.utils.text import format_proper_name, normalize_alphanumeric


class MateriaJurisdiccional(models.Model):
    nombre = models.CharField('Nombre', max_length=256,)
    nombre_normalizado = models.CharField(
        verbose_name='Nombre Normalizado',
        max_length=256,
        blank=True,
        unique=True,
        editable=False,
        error_messages={
            'unique': 'Ya existe una materia con este nombre.',
        }        
    )
    siglas = models.CharField('Siglas', max_length=15, blank=True, null=True)
    activo = models.BooleanField('Activo', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Materia'
        verbose_name_plural = 'Materias'
        ordering = ['nombre']
        constraints = [
            models.UniqueConstraint(
                fields=['siglas'],
                name='materia_unique_siglas_when_has_value',
                condition=models.Q(siglas__isnull=False) & ~models.Q(siglas='')
            )
        ]

    # ── Normalización ───────────────────────────────
    def _normalize_values(self):
        if self.nombre and self.nombre.strip():
            self.nombre = format_proper_name(self.nombre)
            self.nombre_normalizado = normalize_alphanumeric(self.nombre)
            
        if self.siglas and self.siglas.strip():
            self.siglas = self.siglas.upper()

    def _normalize_empty_optional_fields(self):
        for field in ('siglas',):
            if getattr(self, field) == '':
                setattr(self, field, None)

    # ── Validación ──────────────────────────────────
    def _check_unique_fields(self):
        '''
        Valida la unicidad de los campos opcionales únicos y asocia
        los errores del campo visible correspondiente.
        '''
        errors = {}
        unique_fields_map = {
            'nombre_normalizado': 'La materia ya existe.',
            'siglas': 'Las siglas ya existen.',
        }

        for field, message in unique_fields_map.items():
            value = getattr(self, field)
            if value:
                qs = MateriaJurisdiccional.objects.filter(**{field: value})
                if self.pk:
                    qs = qs.exclude(pk=self.pk)
                if qs.exists():
                    if field == 'nombre_normalizado':
                        errors['nombre'] = message
                    else:
                        errors[field] = message
        if errors:
            raise ValidationError(errors)
  
    def clean(self):
        super().clean()

        self._normalize_empty_optional_fields()
        self._normalize_values()
        self._check_unique_fields()

    def save(self, *args, **kwargs):
        self._normalize_empty_optional_fields()
        self._normalize_values()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre        