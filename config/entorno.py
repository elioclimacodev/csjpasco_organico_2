"""
Lectura de la configuración desde el entorno, con falla explícita
(constitución §Configuración de entorno y dependencias).

Reglas (data-model §3):
- E1. Una cadena vacía equivale a "no definida".
- E2. Un booleano acepta true, false, 1, 0, sí, si y no, sin distinguir
  mayúsculas; cualquier otro valor es un error.
- E3. Una lista se separa por comas, se recortan los espacios y se ignoran
  los elementos vacíos.
- E4. Una variable obligatoria ausente es un error que indica su nombre.
"""
import os

from django.core.exceptions import ImproperlyConfigured


REVISE = 'Revise el archivo .env (ver .env.example).'

VERDADEROS = {'true', '1', 'sí', 'si'}
FALSOS = {'false', '0', 'no'}


def _valor(nombre):
    """Valor de la variable sin espacios, o `None` si no está definida o está vacía (E1)."""
    valor = os.getenv(nombre, '').strip()
    return valor or None


def env_requerida(nombre):
    '''
    Devuelve una variable de entorno obligatoria o falla explícitamente si no
    está definida (constitución, §Configuración de entorno y dependencias).
    '''
    valor = _valor(nombre)
    if valor is None:
        raise ImproperlyConfigured(
            f'La variable de entorno {nombre} es obligatoria y no está definida. {REVISE}'
        )
    return valor


def env_bool(nombre, por_defecto):
    """Devuelve una variable booleana (E2) o `por_defecto` si no está definida."""
    valor = _valor(nombre)
    if valor is None:
        return por_defecto
    if valor.lower() in VERDADEROS:
        return True
    if valor.lower() in FALSOS:
        return False
    raise ImproperlyConfigured(
        f'La variable de entorno {nombre} tiene el valor no reconocido "{valor}". '
        f'Use true o false (también se aceptan 1, 0, sí, si y no). {REVISE}'
    )


def env_lista(nombre, por_defecto=()):
    """Devuelve una lista separada por comas (E3) o `por_defecto` si no está definida."""
    valor = _valor(nombre)
    if valor is None:
        return list(por_defecto)
    return [elemento.strip() for elemento in valor.split(',') if elemento.strip()]


def env_entero(nombre, por_defecto, minimo=0):
    """Devuelve una variable entera mayor o igual que `minimo`, o `por_defecto` si no está definida."""
    valor = _valor(nombre)
    if valor is None:
        return por_defecto
    try:
        entero = int(valor)
    except ValueError:
        entero = None
    if entero is None or entero < minimo:
        raise ImproperlyConfigured(
            f'La variable de entorno {nombre} debe ser un número entero mayor o igual que {minimo}; '
            f'tiene el valor "{valor}". {REVISE}'
        )
    return entero
