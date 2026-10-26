from django.core.exceptions import ValidationError
from django.db import models

from apps.common.utils import normalize_alphanumeric, format_proper_name

class Pais(models.Model):
    '''
    Modelo que representa un país. Solo puede existir un registro por país (nombre único).
    Los campos ISO son opcionales pero únicos en caso se ingresen.
    '''

    nombre = models.CharField('Nombre', max_length=256, unique=True)
    nombre_normalizado = models.CharField('Nombre normalizado', max_length=256, blank=True, editable=False)
    codigo_alpha2 = models.CharField('ISO Alpha-2', max_length=2, blank=True, null=True) # ISO 3166-1 Alpha-2. Ejem: PE, AR, EC.
    codigo_alpha3 = models.CharField('ISO Alpha-3', max_length=3, blank=True, null=True) # ISO 3166-1, Alpha-3. Ejem: PER, ARG, ECU.    
    codigo_numerico = models.CharField('Código Numérico', max_length=3, blank=True, null=True)  # ISO 3166-1 Código Numérico. Ejem: 604, 032, 218    
    codigo_internacional = models.CharField('Código internacional', max_length=7, blank=True, null=True)  # Código internacional de llamada. Ejem. +51    
    activo = models.BooleanField('Activo',  default=True )                   
    
    # ── Auditoría ────────────────────
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'País'
        verbose_name_plural = 'Países'
        ordering = ['nombre_normalizado']
        constraints = [
            # Unicidad condicional: sólo cuando el campo tiene valor real.
            models.UniqueConstraint(
                fields=['codigo_alpha2'],
                name='unique_codigo_alpha2_when_value',
                condition=models.Q(codigo_alpha2__isnull=False) & ~models.Q(codigo_alpha2=''),
            ),
            models.UniqueConstraint(
                fields=['codigo_alpha3'],
                name='unique_codigo_alpha3_when_value',
                condition=models.Q(codigo_alpha3__isnull=False) & ~models.Q(codigo_alpha3='')
            ),
            models.UniqueConstraint(
                fields=['codigo_numerico'],
                name='unique_codigo_numerico_when_has_value',
                condition=models.Q(codigo_numerico__isnull=False) & ~models.Q(codigo_numerico='')
            ),
        ]
           
    def _normalize_values(self):
        '''
        Normaliza los valores:
        nombre = convierte a mayúsculas.
        nombre_normalizado = remueve las tildes y convierte a minúsculas para búsquedas.
        '''
        if self.nombre and self.nombre.strip():
            self.nombre = format_proper_name(self.nombre)
            self.nombre_normalizado = normalize_alphanumeric(self.nombre)

        if self.codigo_alpha2 and self.codigo_alpha2.strip():
            self.codigo_alpha2 = self.codigo_alpha2.upper()

        if self.codigo_alpha3 and self.codigo_alpha3.strip():
            self.codigo_alpha3 = self.codigo_alpha3.upper()

        if self.codigo_numerico:
            self.codigo_numerico = self.codigo_numerico.strip()

        if self.codigo_internacional:
            self.codigo_internacional = self.codigo_internacional.strip()
            
    def _normalize_empty_strings(self):
        '''
        Convierte las cadenas vacías a None en los campos opcionales,
        para que los UniqueConstraints condicionales funcionen
        correctamente a nivel de base de datos.
        '''
        optional_fields = (
            'codigo_alpha2', 'codigo_alpha3', 'codigo_numerico',
            'codigo_internacional',
        )
        for field in optional_fields:
            if getattr(self, field) == '':
                setattr(self, field, None)
    
    def _check_unique_optional_fields(self):
        '''
        Valida la unicidad de los campos opcionales a nivel de Python,
        para lanzar mensajes de error por campo específico.
        
        Nota: los UniqueConstraints en Meta son la salvaguarda final
        a nivel de base de datos.
        '''
        errors = {}
        
        field_map = {
            'codigo_alpha2': 'El código Alpha-2 ya existe.',
            'codigo_alpha3': 'El código Alpha-3 ya existe.',
            'codigo_numerico': 'El código numérico ya existe.',
        }
        
        for field, message in field_map.items():
            value = getattr(self, field)
            if value:
                qs = Pais.objects.filter(**{field: value})
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