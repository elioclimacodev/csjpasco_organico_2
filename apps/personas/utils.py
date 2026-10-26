import re
from datetime import date


def format_person_name(value: str) -> str:
    '''
    Normaliza nombres y apellidos de una persona.

    Reglas:
    - Verifica si es una cadena.
    - Elimina espacios al inicio y final.
    - Unifica espacios múltiples en uno solo.
    - Unifica apóstrofes múltiples en uno solo.
    - Unifica guiones múltiples en uno solo.
    - Convierte cada palabra a formato de nombre propio.
    - Conserva correctamente los apellidos con guiones.
    - Conserva correctamente los apellidos con apóstrofes.
    
    Ejemplos:
        DE LA CRUZ      -> De la Cruz
        jean-pierre     -> Jean-Pierre
        d'onofrio       -> D'Onofrio
    '''

    if not isinstance(value, str) or not value.strip():
        return ''
    
    value = value.strip()

    # Elimina espacios duplicados.
    value = re.sub(r'\s+', ' ', value)
    
    # Elimina guiones duplicados.
    value = re.sub(r'-+', '-', value)

    # Elimina apóstrofes duplicados.
    value = re.sub(r"'+", "'", value)

    # Elimina separadores sobrantes en extremos.
    value = value.strip(" -'")

    lowercase_words = {
        "de", "del", "la", "las", "los",
        "y", "e", "o", "u",
        "en", "a", "al", "por", "para",
        "da", "das", "do", "dos",           # portugués
        "van", "von",                       # apellidos europeos
    }

    normalized_words = []

    for index, word in enumerate(value.lower().split()):
        
        # Manejo de nombres con apóstrofes.
        apostrophe_parts = [
            part.capitalize()
            for part in word.split("'")
        ]
        word = "'".join(apostrophe_parts)

        # Manejo de apellidos compuestos con guiones.
        hyphen_parts = [
            part.capitalize()
            for part in word.split('-')
        ]
        word = '-'.join(hyphen_parts)

        # Partículas que normalmente permanecen en minúsculas.
        if index > 0 and word.lower() in lowercase_words:
            normalized_words.append(word.lower())
        else:
            normalized_words.append(word)

    return ' '.join(normalized_words)


def normalize_id_number(id_number: str) -> str:
    '''
    Normaliza el número de documento para eliminar espacios en blancos
    y convierte a mayúsculas en caso contenga caracteres alfabéticos.
    '''

    if not isinstance(id_number, str):
        return ''
    
    return id_number.strip().upper()
    

def calculate_age(birth_date: date) -> int:
    '''
    Calcula la edad de una persona en años.
    '''

    if not birth_date:
        raise ValueError('Debe ingresar la fecha de nacimiento.')

    today = date.today()
    age = today.year - birth_date.year

    # Si aún no ha cumplido años.
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1

    return age
    

def is_adult(birth_date: date, min_age: int = 18) -> bool:
    '''
    Determina si una persona es mayor de edad.
    '''
    if birth_date is None:
        return False

    return calculate_age(birth_date) >= min_age