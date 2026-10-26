import re

from django.core.exceptions import ValidationError

"""
Patrones de validación de nombres y apellidos que debe permitir
lo siguiente:
- Letras (a-z, A-Z).
- Tildes y la ñ (ÁÉÍÓÚÑáéíóúñ).
- Diérisis (Üü).
- Apóstrofes (') para nombres o apellidos como O'Higgins, D'onofrio.
- Guiones (-) para apellidos compuestos como Gonzáles-Olaechea.

Regex:
[a-zA-ZÁÉÍÓÚÑáéíóúñÜü]        -> Debe empezar con una letra.
[a-zA-ZÁÉÍÓÚÑáéíóúñÜü\\s\'-]* -> Puede seguir con una o más letras, incluido un espacio,
                                 apóstrofe o guión.
[a-zA-ZÁÉÍÓÚÑáéíóúñÜü]$       -> Debe terminar con una letra.
"""

# Compilando el patrón una sola vez.
patron = re.compile(r"^[a-zA-ZÁÉÍÓÚÑáéíóúñÜü][a-zA-ZÁÉÍÓÚÑáéíóúñÜü\s\'-]*[a-zA-ZÁÉÍÓÚÑáéíóúñÜü]$")


def validar_nombres_apellidos(valor):
    if not valor:
        raise ValidationError('Debe ingresar un nombre o apellido.')
    
    valor = valor.strip()               # Quita los espacios al inicio y final.
    valor = re.sub(r'\s+', ' ', valor)  # Convierte múltiples espacios en uno solo.
    valor = re.sub(r'-+', '-', valor)   # Convierte los guiones duplicados en uno solo.
    valor = re.sub(r"'+", "'", valor)   # Convierte los apóstrofes duplicados en uno solo.
    
    if not re.match(patron, valor):
        raise ValidationError(
            'Formato inválido. Solo debe contener caracteres alfabéticos, apóstrofes o guiones.'
        )
    
    return valor.upper()


def validar_numero_documento(tipo_documento, numero):
    '''
    Valida los distintos tipos de documentos de identificación del estado peruano.
    '''
    
    tipos = {
        'DNI': {
            'regex': r'^\d{8}$',
            'error': 'El DNI debe tener 8 dígitos numéricos.',
        },
        'RUC': {
            'regex': r'^\d{11}$',
            'error': 'El RUC debe tener 11 dígitos numéricos.',   
        },
        'PAS': {
            'regex': r'^[a-zA-Z0-9]{9,12}$',
            'error': 'El número de Pasaporte debe tener entre 9 a 12 caracteres alfanuméricos.',
        },  
        'CFP': {
            'regex': r'^\d{8}$',
            'error': 'El Carné de las Fuerzas Policiales debe tener 8 dígitos numéricos.',
        },
        'CFA': {
            'regex': r'^\d{8}$',
            'error': 'El Carné de las Fuerzas Armadas debe tener 8 dígitos numéricos.',
        },
        'CEX': {
            'regex': r'^[a-zA-Z]\d{8}$',
            'error': 'El Carné de Extranjería debe empezar con una letra seguida de 8 dígitos numéricos.',
        },
        'CPP': {
            'regex': r'^\d{9}$',
            'error': 'El Carné de Permiso Temporal de Permanencia debe tener 9 dígitos numéricos.',
        },
    }
    
    tipo = tipos.get(tipo_documento)
    
    # Si el tipo de documento está en la lista de formatos se validad con su
    # correspondiente regex.
    if tipo:
        if not re.fullmatch(tipo['regex'], numero):
            raise ValidationError(tipo['error'])
        
    return numero