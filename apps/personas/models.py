from django.db.models.functions import Lower, Upper
from django.conf import settings
from django.db import models

from apps.common.utils import normalize_alphabetic

from .choices import TipoDocumento, Genero, EstadoCivil

from .validators import (
    validate_adult_age, validate_birth_date,
    validate_person_name, validate_id_number,

)

from .utils import (
    format_person_name, normalize_id_number,
    calculate_age
)


class Persona(models.Model):
    '''
    Registra a las personas sin importar su vínculo legal con la entidad.
    Una persona puede existir sin tener una cuenta de usuario en el sistema.
    '''

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='persona',
    )

    # ── Datos de identificación ──────
    tipo_documento = models.CharField(
        verbose_name='Tipo de documento',
        max_length=5,
        choices=TipoDocumento.choices,
        default=TipoDocumento.DNI,
    )
    
    numero_documento = models.CharField(
        verbose_name='Número de documento', 
        max_length=15, 
        db_index=True,
    )
    
    # ── Datos personales ─────────────
    nombres = models.CharField(
        verbose_name='Nombres', 
        max_length=50,
        db_index=True,
        validators=[validate_person_name],
    )

    apellido_paterno = models.CharField(
        verbose_name='Apellido paterno', 
        max_length=50,
        db_index=True,
        validators=[validate_person_name],
    )
    
    apellido_materno = models.CharField(
        verbose_name='Apellido materno', 
        max_length=50,
        db_index=True,
        validators=[validate_person_name],
    )
    
    nombres_normalizado = models.CharField(
        verbose_name='Nombre normalizado',
        max_length=256,
        blank=True,
        editable=False,
        db_index=True
    )

    apellido_paterno_normalizado = models.CharField(
        verbose_name='Apellido paterno normalizado',
        max_length=256,
        blank=True,
        editable=False,
        db_index=True
    )

    apellido_materno_normalizado = models.CharField(
        verbose_name='Apellido materno normalizado',
        max_length=256,
        blank=True,
        editable=False,
        db_index=True
    )

    nombre_completo_normalizado = models.CharField(
        verbose_name='Nombre completo normalizado',
        max_length=256,
        blank=True,
        editable=False,
        db_index=True
    )

    genero = models.CharField(
        verbose_name='Género',
        max_length=5,
        choices=Genero.choices,
        default=Genero.MAS,
    )
    
    fecha_nacimiento = models.DateField(
        verbose_name='Fecha de nacimiento',
        validators=[
            validate_birth_date,
            validate_adult_age
        ]
    )
    
    estado_civil = models.CharField(
        verbose_name='Estado civil',
        max_length=50,
        choices=EstadoCivil.choices,
        default=EstadoCivil.SOL,
    )

    email = models.EmailField(
        verbose_name='Correo electrónico',
        unique=True,
    )

    
    # ── Estado ───────────────────────
    activo = models.BooleanField('Activo', default=True)

    # ── Auditoría ────────────────────
    creado = models.DateTimeField('Creado', auto_now_add=True)
    modificado = models.DateTimeField('Modificado', auto_now=True)    

    class Meta:
        verbose_name = 'Persona'
        verbose_name_plural = 'Personas'
        ordering = [
            'apellido_paterno_normalizado'
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['tipo_documento', 'numero_documento'],
                name='unique_tipo_numero_documento',
            ),

            models.UniqueConstraint(
                Lower('email'),
                name='unique_persona_email_ci',
            ),

            # models.UniqueConstraint(
            #     Upper('numero_documento'),
            #     name='unique_persona_numero_documento_ci',
            # )
        ]

    # ── Propiedades ──────────────────
    @property
    def nombre_completo(self) -> str:
        '''Retorna el nombre completo de la persona.'''
        # return f'{self.nombres} {self.apellido_paterno} {self.apellido_materno}'.strip()
        return ' '.join(filter(None,[
            self.nombres,
            self.apellido_paterno,
            self.apellido_materno,
        ]))
    
    @property
    def nombre_corto(self) -> str:
        '''Retorna el primer nombre y primer apellido.'''
        primer_nombre = self.nombres.split()[0] if self.nombres else ''
        return f'{primer_nombre} {self.apellido_paterno}'.strip()
            
    @property
    def edad(self) -> int:
        '''Calcula la edad en años'''
        return calculate_age(self.fecha_nacimiento)

    @property
    def tiene_usuario(self) -> bool:
        return self.usuario_id is not None
    
    # ── Métodos privados ─────────────
    def _normalize_values(self):
        '''
        Normaliza los datos antes de validarlos o almacenarlos.
        '''
        if self.numero_documento and self.numero_documento.strip():
            self.numero_documento = normalize_id_number(self.numero_documento)

        person_fields = [
            'nombres',
            'apellido_paterno',
            'apellido_materno',
        ]

        for field_name in person_fields:
            value = getattr(self, field_name)
            
            if not value:
                continue

            formatted_value = format_person_name(value)

            setattr(self, field_name, formatted_value)
            
        if self.nombres and self.nombres.strip():
            self.nombres_normalizado = normalize_alphabetic(self.nombres)

        if self.apellido_paterno and self.apellido_paterno.strip():
            self.apellido_paterno_normalizado = normalize_alphabetic(self.apellido_paterno)

        if self.apellido_materno and self.apellido_materno.strip():
            self.apellido_materno_normalizado = normalize_alphabetic(self.apellido_materno)

        if self.email:
            self.email = self.email.lower()

        self.nombre_completo_normalizado = normalize_alphabetic(self.nombre_completo)

    def clean(self):
        super().clean()
        self._normalize_values()
        if self.tipo_documento and self.numero_documento:
            self.numero_documento = validate_id_number(
                self.tipo_documento, self.numero_documento
            )
        
        # self.numero_documento = validate_id_number(self.tipo_documento, self.numero_documento)

    def save(self, *args, **kwargs):
        self._normalize_values()
        # self.full_clean()
        super().save(*args, **kwargs)

    # ── Representación ─────────────── 
    def __str__(self):
        return f'{self.numero_documento} {self.apellido_paterno} {self.apellido_materno}, {self.nombres}'
    
    def __repr__(self):
        return (
            f'<Persona '
            f'{self.tipo_documento}={self.numero_documento} | '
            f'{self.apellido_paterno} {self.apellido_materno}, {self.nombres}>'
        )