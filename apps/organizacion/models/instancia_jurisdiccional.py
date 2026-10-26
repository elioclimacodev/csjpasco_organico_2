from django.db import models

from apps.common.utils import format_proper_name, normalize_alphanumeric

from apps.organizacion.models import OrganoJurisdiccional, MateriaJurisdiccional, SedeJudicial


class InstanciaJurisdiccional(models.Model):
    organo = models.ForeignKey(
        OrganoJurisdiccional,
        on_delete=models.PROTECT,
        related_name='instancias_por_organo',
    )

    materia = models.ForeignKey(
        MateriaJurisdiccional,
        on_delete=models.PROTECT,
        related_name='instancias_por_materia',
    )

    sede = models.ForeignKey(
        SedeJudicial,
        on_delete=models.PROTECT,
        related_name='instancias_por_sede',
    )

    nombre = models.CharField(
        verbose_name='Instancia Jurisdiccional',
        max_length=256,
        blank=False,
        null=False,
    )

    nombre_normalizado = models.CharField(
        verbose_name='Nombre normalizado',
        max_length=256,
        editable=False,
    )

    siglas = models.CharField(
        verbose_name='Siglas', 
        max_length=15, 
        blank=True, 
        null=True
    )

    activo = models.BooleanField('Activo', default=True)
    
    #── Auditoría ────────────────────
    created_at = models.DateTimeField('Creado el', auto_now_add=True)
    modified_at = models.DateTimeField('Actualizado el', auto_now=True)
    
    class Meta:
        verbose_name = 'Instancia Jurisdiccional'
        verbose_name_plural = 'Instancias Jurisdiccionales'
        ordering = ['nombre_normalizado']

    # ── Campos calculados ────────────
    @property
    def organo_nombre(self):
        return format_proper_name(self.organo.nombre)
    
    @property
    def materia_nombre(self):
        return format_proper_name(self.materia.nombre)
    
    @property
    def sede_nombre(self):
        return format_proper_name(self.sede.nombre)

    # ── Normalización ────────────────
    def _normalize_values(self):
        if self.nombre and self.nombre.strip():
            self.nombre = format_proper_name(self.nombre)
            self.nombre_normalizado = normalize_alphanumeric(self.nombre)

        if self.siglas and self.siglas.strip():
            self.siglas = self.siglas.upper()

    def clean(self):
        super().clean()
        self._normalize_values()

    def save(self, *args, **kwargs):
        self._normalize_values()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre