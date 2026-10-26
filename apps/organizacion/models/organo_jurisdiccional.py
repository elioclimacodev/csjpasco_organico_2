from django.core.exceptions import ValidationError
from django.db import models, IntegrityError

from apps.common.utils.text import format_proper_name, normalize_alphanumeric


class OrganoJurisdiccional(models.Model):
    nombre = models.CharField('Nombre', max_length=256, unique=True)
    nombre_normalizado = models.CharField('Nombre Normalizado', max_length=256, blank=True)
    siglas = models.CharField('Siglas', max_length=15, blank=True, null=True)
    activo = models.BooleanField('Activo', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Órgano Jurisdiccional'
        verbose_name_plural = 'Órganos Jurisdiccionales'
        ordering = ['nombre']
        constraints = [
            models.UniqueConstraint(
                fields=['siglas'],
                name='oj_unique_siglas_when_has_value',
                condition=models.Q(siglas__isnull=False) & ~models.Q(siglas='')
            )
        ]

    # ── Normalización ───────────────────────────────
    def _normalize_values(self):
        if self.nombre and self.nombre.strip():
            self.nombre = format_proper_name(self.nombre)
            self.nombre_normalizado = normalize_alphanumeric(self.nombre)

    def _normalize_empty_optional_fields(self):
        for field in ('siglas',):
            if getattr(self, field) == '':
                setattr(self, field, None)

    # ── Validación ──────────────────────────────────
    def _check_unique_acronyms(self):
        if not self.siglas:
            return
        qs = OrganoJurisdiccional.objects.filter(siglas=self.siglas)
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        if qs.exists():
            raise ValidationError({'siglas': 'Las siglas ya existen.'})
        
    def clean(self):
        super().clean()
        self._normalize_empty_optional_fields()
        self._normalize_values()
        self._check_unique_acronyms()

    # ── Persistencia ────────────────────────────────
    def save(self, *args, **kwargs):
        self._normalize_empty_optional_fields()
        self._normalize_values()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre        