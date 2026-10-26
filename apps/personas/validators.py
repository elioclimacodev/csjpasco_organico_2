import re

from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError
from datetime import date

from .choices import TipoDocumento
from .utils import is_adult


# Patrón reutilizable para validar nombres y apellidos.
PERSON_NAME_PATTERN = re.compile(
    # r"^[a-zA-ZÁÉÍÓÚÑáéíóúñÜü]"
    # r"[a-zA-ZÁÉÍÓÚÑáéíóúñÜü\s\'-]*"
    # r"[a-zA-ZÁÉÍÓÚÑáéíóúñÜü]$"
    r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+"
    r"(?:[ '-][A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+)*$"    
)

def validate_person_name(value: str) -> None:
    '''
    Valida el formato de nombres y apellidos.
    '''
    
    if not value or not value.strip():
        raise ValidationError('Debe ingresar un nombre o apellido.')
    
    if not PERSON_NAME_PATTERN.fullmatch(value):
        raise ValidationError('Solo debe contener caracteres alfabéticos, apóstrofes o guiones.')
    

DOCUMENT_TYPE_RULES = {
        'DNI': {
            'regex': r'^\d{8}$',
            'error': 'El DNI debe tener 8 dígitos numéricos.',
        },
        # 'RUC': {
        #     'regex': r'^\d{11}$',
        #     'error': 'El RUC debe tener 11 dígitos numéricos.',   
        # },
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

# def validate_id_number(id_type: str, id_number: str) -> None:
#     '''
#     Valida el formato del número de documento de identidad según
#     el tipo de documento seleccionado.
#     '''
    
#     rule = DOCUMENT_TYPE_RULES.get(id_type)
    
#     if not rule:
#         raise ValidationError('Tipo de documento no soportado.')
    
#     if not id_number:
#         raise ValidationError('Debe ingresar el número de documento.')
    
#     if not re.fullmatch(rule['regex'], id_number,):
#         raise ValidationError(rule['error'])
#     # return id_number.upper()
    

def validate_birth_date(birth_date: date) -> None:
    '''
    Valida que la fecha de nacimiento no sea una fecha futura.
    '''

    if birth_date and birth_date > date.today():
        raise ValidationError('La fecha de nacimiento no puede ser futura.')

    
def validate_adult_age(birth_date: date) -> None:
    '''
    Valida si una persona es mayor de edad.
    '''

    if birth_date and not is_adult(birth_date):
        raise ValidationError('La persona debe ser mayor de edad.')


# from .choices import TipoDocumento

# PATRONES_DOCUMENTO = {
#     TipoDocumento.DNI: r"^\d{8}$",
#     TipoDocumento.PAS: r"^[A-Za-z0-9]{9}$",
#     TipoDocumento.CEX: r"^[A-Za-z0-9]{9}$",
#     TipoDocumento.CPP: r"^[A-Za-z0-9]{9}$",
# }


# def validar_numero_documento(tipo_documento, numero_documento):
#     """Valida que el número de documento coincida con el formato de su tipo."""
#     patron = PATRONES_DOCUMENTO.get(tipo_documento)
#     if patron is None:
#         raise ValidationError(
#             _("Tipo de documento no válido: %(tipo)s"), params={"tipo": tipo_documento}
#         )
#     if not numero_documento or not re.match(patron, str(numero_documento)):
#         raise ValidationError(
#             _(
#                 "El número de documento no es válido para el tipo %(tipo)s "
#                 "(%(formato)s)."
#             ),
#             params={
#                 "tipo": tipo_documento,
#                 "formato": _formato_legible(tipo_documento),
#             },
#         )
#     return numero_documento.upper()


# def _formato_legible(tipo_documento):
#     if tipo_documento == TipoDocumento.DNI:
#         return "8 dígitos"
#     return "9 caracteres alfanuméricos"




# Reglas específicas del código 2, pero con claves Enum
REGLAS_DOCUMENTO = {
    TipoDocumento.DNI: {
        'regex': r'^\d{8}$',
        'error': _('El DNI debe tener 8 dígitos numéricos.'),
    },
    TipoDocumento.PAS: {
        'regex': r'^[a-zA-Z0-9]{9,12}$',
        'error': _('El Pasaporte debe tener entre 9 y 12 caracteres alfanuméricos.'),
    },
    TipoDocumento.CFP: {
        'regex': r'^\d{8}$',
        'error': _('El Carné Policial debe tener 8 dígitos numéricos.'),
    },
    TipoDocumento.CFA: {
        'regex': r'^\d{8}$',
        'error': _('El Carné de las FF.AA. debe tener 8 dígitos numéricos.'),
    },
    TipoDocumento.CEX: {
        'regex': r'^[a-zA-Z]\d{8}$',
        'error': _('El Carné de Extranjería debe empezar con letra y seguir con 8 dígitos.'),
    },
    TipoDocumento.CPP: {
        'regex': r'^\d{9}$',
        'error': _('El Carné de Permiso Temporal debe tener 9 dígitos numéricos.'),
    },
}

def validate_id_number(tipo_documento, numero_documento):
    """
    Valida el número de documento usando reglas precisas.
    Retorna el número normalizado (mayúsculas) si es válido.
    """
    if not numero_documento:
        raise ValidationError(_('Debe ingresar el número de documento.'))

    regla = REGLAS_DOCUMENTO.get(tipo_documento)
    if not regla:
        raise ValidationError(
            _('Tipo de documento no soportado: %(tipo)s'),
            params={'tipo': tipo_documento}
        )

    if not re.fullmatch(regla['regex'], str(numero_documento)):
        raise ValidationError(regla['error'])

    # Normaliza a mayúsculas (útil para PAS, CEX, etc.)
    return numero_documento.upper()