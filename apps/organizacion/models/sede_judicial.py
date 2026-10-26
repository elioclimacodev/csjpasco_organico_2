# models.py
from django.db import models
from django.core.exceptions import ValidationError

from apps.common.utils.text import format_proper_name, normalize_alphanumeric

from apps.organizacion.models import DistritoJudicial


class SedeJudicial(models.Model):
    """
    Representa una sede judicial (sede principal o subsede) dentro de
    la organización jerárquica de una Corte de Justicia.
    """

    distrito_judicial = models.ForeignKey(
        DistritoJudicial,
        on_delete=models.PROTECT,
        related_name='sedes',
        verbose_name='Distrito Judicial',
        null=False,
        blank=False,
    )

    sede_superior = models.ForeignKey(
        'self',
        on_delete=models.PROTECT,
        related_name='subsedes',
        verbose_name='Sede Superior',
        null=True,
        blank=True,
    )

    nombre = models.CharField('Nombre', max_length=256, blank=False)
    nombre_normalizado = models.CharField(
        'Nombre Normalizado',
        max_length=256,
        blank=True,
        editable=False,
    )

    siglas = models.CharField('Siglas', max_length=15, blank=True, null=True)
    activo = models.BooleanField('Activo', default=True)

    #── Auditoría ────────────────────
    created_at = models.DateTimeField('Creado el', auto_now_add=True)
    modified_at = models.DateTimeField('Actualizado el', auto_now=True)

    class Meta:
        verbose_name = 'Sede'
        verbose_name_plural = 'Sedes'
        ordering = ['nombre']
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(nombre=''),
                name='sede_nombre_not_empty',
            ),
            # models.UniqueConstraint(
            #     fields=['nombre_normalizado'],
            #     name='sede_unique_nombre_normalizado',
            #     condition=~models.Q(nombre_normalizado=''),
            # ),
            # models.UniqueConstraint(
            #     fields=['siglas'],
            #     name='sede_unique_siglas_when_has_value',
            #     condition=models.Q(siglas__isnull=False) & ~models.Q(siglas=''),
            # ),
        ]

    @property
    def distrito_judicial_nombre(self):
        return self.distrito_judicial.nombre if self.distrito_judicial.nombre else ''
    
    @property
    def corte_nombre(self):
        return self.distrito_judicial.corte if self.distrito_judicial.corte else ''
    
    @property
    def sede_superior_nombre(self):
        return self.sede_superior.nombre if self.sede_superior else '···'

    # ── Normalización ───────────────────────────────
    # Estos métodos se llaman tanto desde clean() como desde save():
    # - Desde clean(): para que las validaciones de unicidad/jerarquía
    #   comparen contra valores ya normalizados.
    # - Desde save(): para que CUALQUIER guardado (con o sin formulario,
    #   desde el shell, un comando, etc.) persista datos normalizados,
    #   incluso si nadie llamó a full_clean().
    # Son idempotentes, así que ejecutarlos dos veces no tiene costo
    # funcional, solo el de formatear strings ya formateados.
    def _normalize_values(self):
        """Aplica formato consistente a los campos antes de guardarlos."""
        if self.nombre and self.nombre.strip():
            self.nombre = format_proper_name(self.nombre)
            self.nombre_normalizado = normalize_alphanumeric(self.nombre)

        if self.siglas and self.siglas.strip():
            self.siglas = self.siglas.upper()

    def _normalize_empty_optional_fields(self):
        """
        Convierte campos vacíos en None para que la BD aplique
        NULL correctamente.
        """
        for field in ('siglas',):
            if getattr(self, field) == '':
                setattr(self, field, None)

    # ── Validación ──────────────────────────────────
    # IMPORTANTE: estos checks solo se ejecutan cuando algo llama a
    # full_clean() (un ModelForm, el admin, o una llamada manual).
    # Un .save() directo (shell, script, comando) YA NO los ejecuta.
    # La protección de último nivel sigue siendo la base de datos
    # (UniqueConstraint, PROTECT), que lanzará IntegrityError en vez
    # de ValidationError si alguien se salta la validación.
    def _check_unique_fields(self):
        """
        Valida manualmente la unicidad de los campos cuya restricción es
        condicional (UniqueConstraint con `condition`), ya que Django NO
        las valida automáticamente en full_clean(). El error se asocia
        siempre al campo visible para el usuario en el formulario.
        """
        errors = {}

        unique_fields_map = {
            'nombre_normalizado': ('nombre', 'Ya existe una sede con este nombre.'),
            'siglas': ('siglas', 'Estas siglas ya están en uso por otra sede.'),
        }

        for db_field, (visible_field, message) in unique_fields_map.items():
            value = getattr(self, db_field)
            if value:
                queryset = SedeJudicial.objects.filter(**{db_field: value})
                if self.pk:
                    queryset = queryset.exclude(pk=self.pk)
                if queryset.exists():
                    errors[visible_field] = message

        return errors

    def _check_hierarchy(self):
        """
        Evita que una sede sea su propia sede superior, o que la
        jerarquía de sedes superiores forme un ciclo (ej. A → B → A).
        """
        errors = {}

        if self.sede_superior_id is None:
            return errors

        if self.sede_superior_id == self.pk:
            errors['sede_superior'] = 'Una sede no puede ser su propia sede superior.'
            return errors

        visited_ids = {self.pk}
        current = self.sede_superior
        max_depth = 100

        for _ in range(max_depth):
            if current is None:
                break
            if current.pk in visited_ids:
                errors['sede_superior'] = 'La jerarquía de sedes no puede formar un ciclo.'
                break
            visited_ids.add(current.pk)
            current = current.sede_superior

        return errors

    def clean(self):
        super().clean()
        # Se normaliza aquí también: la validación de unicidad/jerarquía
        # debe comparar contra los valores ya formateados, no contra los
        # valores "crudos" que llegaron del formulario.
        self._normalize_values()
        self._normalize_empty_optional_fields()

        errors = {}
        # errors.update(self._check_unique_fields())
        errors.update(self._check_hierarchy())

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        # Se normaliza aquí para garantizar que TODO guardado persista
        # datos formateados, sin depender de que se haya llamado a
        # full_clean() (por ejemplo, desde el shell o un script).
        # NOTA: ya no se llama a full_clean() aquí. La validación de
        # negocio (unicidad amigable, jerarquía) solo se aplica cuando
        # se pasa por un ModelForm/admin o se invoca full_clean()
        # manualmente. Un .save() directo sin pasar por ahí confía
        # únicamente en las constraints de la base de datos.
        self._normalize_values()
        self._normalize_empty_optional_fields()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre