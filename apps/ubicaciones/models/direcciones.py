from django.db import models

from apps.ubicaciones.models import Distrito


class Direccion(models.Model):

    # ── Choices ──────────────────────
    class Tipo(models.TextChoices):
        DOMICILIO = ('domicilio', 'Domicilio')
        LABORAL = ('laboral', 'Laboral')
    
    class Via(models.TextChoices):
        AVENIDA = ('avenida', 'Avenida')
        JIRON = ('jiron', 'Jirón')
        CALLE = ('calle', 'Calle')
        PASAJE = ('pasaje', 'Pasaje')
        ALAMEDA = ('alameda', 'Alameda')
        MALECON = ('malecon', 'Malecón')
        OVALO = ('ovalo', 'Óvalo')
        PARQUE = ('parque', 'Parque')
        PLAZA = ('plaza', 'Plaza')
        CARRETERA = ('carretera', 'Carretera')
        BLOCK = ('block', 'Block')
        OTROS = ('otros', 'Otros')

    class Exterior(models.TextChoices):
        NUMERO = ('numero', 'Número')
        KILOMETRO = ('kilometro', 'Kilómetro')
        MANZANA = ('manzana', 'Manzana')
        OTROS = ('otros', 'Otros')

    class Interior(models.TextChoices):
        NUMERO = ('numero', 'Número')
        INTERIOR = ('interior', 'Interior')
        DEPARTAMENTO = ('departamento', 'Departamento')
        OTROS = ('otros', 'Otros')

    class Zona(models.TextChoices):
        URBANIZACION = ('urbanizacion', 'Urbanización')
        PUEBLO_JOVEN = ('pueblo_joven', 'Pueblo Joven')
        UNIDAD_VECINAL = ('unidad_vecinal', 'Unidad Vecinal')
        CONJUNTO_HABITACIONAL = ('conjunto_habitacional', 'Conjunto Habitacional')
        ASENTAMIENTO_HUMANO = ('asentamiento_humano', 'Asentamiento Humano')
        COOPERATIVA = ('cooperativa', 'Cooperativa')
        RESIDENCIAL = ('residencial', 'Residencial')
        ZONA_INDUSTRIAL = ('zona_industrial', 'Zona Industrial')
        GRUPO = ('grupo', 'Grupo')
        CASERIO = ('caserio', 'Caserío')
        FUNDO = ('fundo', 'Fundo')
        OTROS = ('otros', 'Otros')

    tipo = models.CharField(
        verbose_name='Tipo',
        max_length=50,
        choices=Tipo.choices,
        default=Tipo.DOMICILIO,
    )

    via = models.CharField(
        verbose_name='Vía',
        max_length=50,
        choices=Via.choices,
        default=Via.JIRON,
    )

    via_nombre = models.CharField(
        verbose_name='Nombre de la vía',
        max_length=256,
        blank=False,
    )

    exterior = models.CharField(
        verbose_name='Exterior',
        max_length=50,
        choices=Exterior.choices,
    )

    exterior_nombre = models.CharField(
        verbose_name='Nombre de la vía exterior',
        max_length=256,
        blank=False,
    )

    interior = models.CharField(
        verbose_name='Interior',
        max_length=50,
        choices=Interior.choices,
        default=Interior.NUMERO
    )

    interior_nombre = models.CharField(
        verbose_name='Nombre del interior',
        max_length=256,
        blank=False,
    )
    
    zona = models.CharField(
        verbose_name='Zona',
        max_length=50,
        choices=Zona.choices,
    )

    zona_nombre = models.CharField(
        verbose_name='Nombre de la zona',
        max_length=256,
        blank=False,
    )

    referencia = models.CharField(
        verbose_name='Referencia',
        max_length=256,
        blank=False,
    )

    es_principal = models.BooleanField('Principal',  default=True)
    activo = models.BooleanField('Activo',  default=True)
    
    # ── Auditoría ────────────────────
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Dirección'
        verbose_name_plural = 'Direcciones'
        ordering = ['via']