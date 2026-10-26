from datetime import date

from django.core.exceptions import ValidationError
from django.db import models

from .validators import validar_numero_documento, validar_nombres_apellidos


class Persona(models.Model):
    '''
    Registra a las personas sin importar su vínculo con la entidad.
    '''
    
    # Choices.
    TIPO_DOCUMENTO = [
        ('DNI', 'DOCUMENTO NACIONAL DE IDENTIDAD'),
        ('RUC', 'REGISTRO ÚNICO DE CONTRIBUYENTES'),
        ('PAS', 'PASAPORTE'),                                   # 9 a 12 caracteres alfanuméricos
        ('CFP', 'CARNÉ DE FUERZAS POLICIALES'),
        ('CFA', 'CARNÉ DE LAS FUERZAS ARMADAS'),
        ('CEX', 'CARNÉ DE EXTRANJERÍA'),                        # 9 caracteres alfanuméricos (Letra + Números), Ejemplo: E12345678.
        ('CPP', 'CARNÉ DE PERMISO TEMPORAL DE PERMANENCIA'),   # 9 dígitos, 
    ]

    GENERO_CHOICES = [
        ('MAS', 'MASCULINO'),
        ('FEM', 'FEMENINO'),
    ]

    ESTADO_CIVIL_CHOICES = [
        ('SOL', 'SOLTERO'),
        ('CAS', 'CASADO'),
        ('DIV', 'DIVORCIADO'),
        ('VDO', 'VIUDO'),
        ('UDH', 'UNIÓN DE HECHO'),
    ]

    # Datos de identificación.
    tipo_documento = models.CharField(
        'Tipo de documento',
        max_length=5,
        choices=TIPO_DOCUMENTO,
        default='DNI'
    )
    
    numero_documento = models.CharField(
        'Número de documento', 
        max_length=15, 
        unique=True,
    )
    
    # Datos personales.
    nombres = models.CharField(
        'Nombres', 
        max_length=250,
    )
    
    apellido_paterno = models.CharField(
        'Apellido paterno', 
        max_length=250,
    )
    
    apellido_materno = models.CharField(
        'Apellido materno', 
        max_length=250,
    )
    
    foto = models.ImageField(
        'Fotografía',
        upload_to='users',
        null=True,
        blank=True
    )
    
    genero = models.CharField(
        'Género',
        max_length=5,
        choices=GENERO_CHOICES,
        default='MAS'
    )
    
    fecha_nacimiento = models.DateField(
        'Fecha de nacimiento',
        null=True,
        blank=True,
    )
    
    estado_civil = models.CharField(
        'Estado civil',
        max_length=5,
        choices=ESTADO_CIVIL_CHOICES,
        default='SOL',
    )
    
    # Estado.
    activo = models.BooleanField('Activo', default=True)

    # Auditoría.
    creado = models.DateTimeField('Creado', auto_now_add=True)
    modificado = models.DateTimeField('Modificado', auto_now=True)
    
    # Metadatos.
    class Meta:
        verbose_name = 'Persona'
        verbose_name_plural = 'Personas'
        ordering = ['apellido_paterno', 'apellido_materno', 'nombres']

    # Representación.
    def __str__(self):
        return f'{self.numero_documento} {self.apellido_paterno} {self.apellido_materno}, {self.nombres}'
    
    def __repr__(self):
        return f'<Persona dni={self.numero_documento} {self.apellido_paterno} {self.apellido_materno}, {self.nombres}>'
    
    # Propiedades.
    @property
    def nombre_completo(self):
        '''Retorna el nombre completo de la persona.'''
        return f'{self.nombres} {self.apellido_paterno} {self.apellido_materno}'
    
    @property
    def nombre_corto(self):
        '''Retorna el primer nombre y primer apellido.'''
        primer_nombre = self.nombres.split()[0]  # ✅ CORREGIDO
        return f'{primer_nombre} {self.apellido_paterno}'
            
    @property
    def edad(self):
        '''Calcula la edad en años'''
        if self.fecha_nacimiento:
            today = date.today()
            return today.year - self.fecha_nacimiento.year - (
                (today.month, today.day) < 
                (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
            )
        return None
    
    # Métodos del negocio.
    def deactivate(self):
        '''Soft delete: desactiva el registro sin eliminarlo'''
        self.activo = False
        self.save(update_fields=['activo', 'modificado'])
    
    def activate(self):
        '''Reactiva el registro'''
        self.activo = True
        self.save(update_fields=['activo', 'modificado'])
        
    def clean(self):
        super().clean()
        
        # Normaiza y valida los nombres y/o apellidos.
        if self.nombres:
            self.nombres = validar_nombres_apellidos(self.nombres)
        if self.apellido_paterno:
            self.apellido_paterno = validar_nombres_apellidos(self.apellido_paterno)
        if self.apellido_materno:
            self.apellido_materno = validar_nombres_apellidos(self.apellido_materno)
        
        # Valida el número de documento.
        try:
            validar_numero_documento(
                self.tipo_documento, 
                self.numero_documento,
            )
        except ValidationError as e:
            raise ValidationError({'numero_documento': e.message})
        
    def save(self, *args, **kwargs):
        # Por defecto van a haber cambios que se deben validar.
        hubo_cambios = True
        
        # Si la persona ya existe se verifica si se han realizado
        # cambios en su registro.
        if self.pk:
            persona = Persona.objects.get(pk=self.pk)
            hubo_cambios = (
                persona.numero_documento != self.numero_documento or
                persona.nombres != self.nombres or
                persona.apellido_paterno != self.apellido_paterno or
                persona.apellido_materno != self.apellido_materno
            )
        
        # Si se han registrado cambios se llama internamente a 
        # clean() y realiza otras validaciones propias del modelo
        if hubo_cambios:
            self.full_clean()
        
        # Guarda en la base de datos.
        super().save(*args, **kwargs)
        
    
class TipoContacto(models.Model):
    nombre = models.CharField('Tipo de contacto personal', max_length=50)

    # Estado.
    activo = models.BooleanField('Activo', default=True)

    # Auditoría.
    creado = models.DateTimeField('Creado', auto_now_add=True)
    modificado = models.DateTimeField('Modificado', auto_now=True)
    
    class Meta:
        verbose_name = 'Tipo de contacto'
        verbose_name_plural = 'Tipos de contacto'
    
    def __str__(self):
        return self.nombre
    
    
class PersonaContacto(models.Model):
    persona = models.ForeignKey(
        Persona, 
        on_delete=models.PROTECT,
        related_name='contactos',
    )
    tipo = models.ForeignKey(
        TipoContacto,
        on_delete=models.PROTECT,
        related_name='persona_contactos',
    )
    
    # El email, número de teléfono u otro contacto.
    valor = models.CharField(
        'Dato del contacto',
        max_length=150,
    )
    principal = models.BooleanField(
        'Contacto principal',
        default=False,
    )
    
    # Estado.
    activo = models.BooleanField('Activo', default=True)

    # Auditoría.
    creado = models.DateTimeField('Creado', auto_now_add=True)
    modificado = models.DateTimeField('Modificado', auto_now=True)