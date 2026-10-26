from datetime import date

from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from .validators import validate_name


TIPO_DOCUMENTO = ([
    ('DNI', 'DOCUMENTO NACIONAL DE IDENTIDAD'),
    ('RUC', 'REGISTRO ÚNICO DE CONTRIBUYENTES'),
    ('PAS', 'PASAPORTE'),
    ('CFP', 'CARNÉ DE FUERZAS POLICIALES'),
    ('CFA', 'CARNÉ DE LAS FUERZAS ARMADAS'),
    ('CEX', 'CARNÉ DE EXTRANJERÍA'),
])

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


class Person(AbstractUser):   
    username = models.CharField(
        'DNI', 
        max_length=8, 
        unique=True,
        validators=[
            RegexValidator(
                r'^\d{8}$',
                'El DNI debe tener 8 dígitos.'
            )
        ]
    )
    
    # Campos de identificación.
    tipo_documento = models.CharField(
        'Tipo de documento',
        max_length=5,
        choices=TIPO_DOCUMENTO,
        default='DNI'
    )
    
    # Campos de datos personales.
    nombres = models.CharField(
        'Nombres', max_length=250,
        validators=[validate_name]
    )
    
    apellido_paterno = models.CharField(
        'Apellido paterno', 
        max_length=250,
        validators=[validate_name]  
    )
    
    apellido_materno = models.CharField(
        'Apellido materno', 
        max_length=250,
        validators=[validate_name]
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
        default=None,
    )
    estado_civil = models.CharField(
        'Estado civil',
        max_length=5,
        choices=ESTADO_CIVIL_CHOICES,
        default='SOL',
    )
    email = models.EmailField(
        'Correo electrónico',
        unique=True,
        blank=False,
        null=False
    )
    
    # Campos adicionales.
    biografia = models.TextField('Biografía', null=True, blank=True)
    observaciones = models.TextField('Observaciones', null=True, blank=True)
    # terminos = models.BooleanField('Términos y condiciones',  default=False)
    
    # Eliminamos los campos que Django crea por defecto ya que no los usaremos.
    first_name = None
    last_name = None
    
    # Configuramos los campos requeridos para la creación de usuarios.
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    @property
    def edad(self):
        # Calcula la edad del usuario
        if self.fecha_nacimiento:
            today = date.today()
            return today.year - self.fecha_nacimiento.year - (
                (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
            )
        return None
    
    # def get_short_name(self):
    #     """
    #     Devuelve el primer nombre y el apellido paterno del usuario.
    #     """
        
    #     return ' '.join(filter(
    #         None, [
    #             self.nombres.split()[0],
    #             self.apellido_paterno
    #         ]
    #     ))

    
    # def get_full_name(self):
    #     """
    #     Devuelve el nombre completo del usuario.
    #     """
            
    #     return ' '.join(filter(
    #         None, [
    #             self.nombres,
    #             self.apellido_paterno,
    #             self.apellido_materno
    #         ]
    #     ))
                    
    def save(self, *args, **kwargs):
        self.nombres = self.nombres.upper().strip()
        self.apellido_paterno = self.apellido_paterno.upper().strip()
        self.apellido_materno = self.apellido_materno.upper().strip()
        self.email = self.email.lower().strip()
        super().save(*args, **kwargs)
        
    def __str__(self):
        # Ignora campos vacíos o None para evitar errores o espacios demás.
        full_name = ' '.join(
            filter(
                None, [
                    self.nombres,
                    self.apellido_paterno, self.apellido_materno
                ]
            )
        )
        return f'({self.username}) {full_name}'
    
    class Meta:
        db_table = 'Persona'
        verbose_name = 'Persona'
        verbose_name_plural = 'Personas'
        ordering = [
            'apellido_paterno', 'apellido_materno',
            'nombres',
        ]