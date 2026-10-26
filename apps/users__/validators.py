import re

from django.core.exceptions import ValidationError


        
def validate_name(value):
    """
    Valida que el texto contenga solo letras, espacios, tildes y diéresis.
    """
    
    if len(value) < 2:
        raise ValidationError('El nombre o apellido debe tener más de dos letras.')
    if not re.match(r'^[A-Za-zÁÉÍÓÚáéíóúÑñÜü -]+$', (value or '').strip()):
        raise ValidationError('Solo se permiten letras y espacios.')