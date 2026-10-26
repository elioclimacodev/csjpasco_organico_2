import re
import unicodedata


def normalize_alphabetic(text: str) -> str:
    """
    Normaliza texto alfabético para búsquedas y comparaciones.

    Transformaciones aplicadas:
      - Rechaza entradas que no sean strings no vacíos.
      - Convierte a minúsculas y elimina espacios extremos.
      - Conserva la ñ (no es un diacrítico eliminable).
      - Elimina acentos y signos diacríticos de las demás letras.
      - Descarta dígitos, puntuación y cualquier símbolo no alfabético.
      - Colapsa espacios múltiples internos en uno solo.

    Args:
        text: Cadena a normalizar.

    Returns:
        Cadena normalizada, o vacía si la entrada no es un str válido.

    Ejemplos:
        normalize_alphabetic('Ñoño Ávila')
        'ñoño avila'
        normalize_alphabetic('  Perú 2024!  ')
        'peru'
        normalize_alphabetic(None)
        ''
    """
    # Rechaza entradas no string o vacías sin lanzar excepción.
    # Retornar '' es seguro para campos normalizados en modelos.
    if not isinstance(text, str) or not text.strip():
        return ''

    text = text.lower().strip()

    result = []
    for char in text:
        if char == 'ñ':
            # La ñ es una letra propia del español, no un carácter
            # base + diacrítico. Se conserva directamente.
            result.append('ñ')

        elif char == ' ':
            # Los espacios se conservan; se colapsarán al final.
            result.append(' ')

        elif unicodedata.category(char) == 'Ll':
            # 'Ll' = letra minúscula Unicode.
            # Descompone el carácter en forma NFD para separar
            # la letra base de sus marcas diacríticas.
            decomposed = unicodedata.normalize('NFD', char)

            # Conserva solo los caracteres que NO sean marcas
            # diacríticas (categoría 'Mn' = Mark, Nonspacing).
            base_char = ''.join(
                c for c in decomposed
                if unicodedata.category(c) != 'Mn'
            )
            result.append(base_char)

        # Cualquier otro carácter (dígitos, puntuación, símbolos)
        # se descarta silenciosamente.

    normalized = ''.join(result)

    # Colapsa secuencias de espacios en uno solo y elimina
    # los espacios que hayan quedado en los extremos.
    normalized = re.sub(r' +', ' ', normalized).strip()

    return normalized


def normalize_alphanumeric(text: str) -> str:
    """
    Normaliza texto alfanumérico para búsquedas y comparaciones.
    Transformaciones aplicadas:
    - Remueve los acentos diacríticos, excepto la ñ.
    - Mantiene solo letras, dígitos, espacios y la ñ.
    - Convierte a minúsculas.
    
    Ejemplos:
        'Código: 123-ABC!'  -> 'codigo 123 abc'
        'Ñandú #42'         -> 'ñandu 42'
        'café2go@mail'      -> 'cafe2go mail'
    """

    if not isinstance(text, str) or not text.strip():
        return ''
    
    text = text.lower()

    result = []
    for char in text:
        if char == 'ñ':
            result.append('ñ')
        elif unicodedata.category(char) == 'Ll':  # letras
            decomposed = unicodedata.normalize('NFD', char)
            base_char = ''.join(
                c for c in decomposed
                if unicodedata.category(c) != 'Mn'  # eliminar diacríticos
            )
            result.append(base_char)
        elif char.isdigit():
            result.append(char)
        elif char == ' ':
            result.append(' ')
        else:
            # Reemplazar símbolos/signos de puntuación con un espacio (para evitar la fusión de palabras)
            result.append(' ')

    normalized = ''.join(result)

    # Colapsa múltiples espacios y espacios de inicio y fin
    normalized = re.sub(r' +', ' ', normalized).strip()

    return normalized
    

def format_proper_name(value:str) -> str:
    """
    Convierte nombres geográficos o nombres propios a formato correcto.

    Ejemplos:
        madre de dios -> Madre de Dios
        san martin -> San Martin
        la libertad -> La Libertad
        provincia constitucional del callao
            -> Provincia Constitucional del Callao
    """
    if not isinstance(value, str):
        return ""

    lowercase_words = {
        "de", "del", "la", "las", "los",
        "y", "e", "o", "u",
        "en", "a", "al", "por", "para",
        "da", "das", "do", "dos",           # portugués
        "van", "von",                       # apellidos europeos
    }

    words = value.strip().lower().split()

    result = []

    for i, word in enumerate(words):
        if i > 0 and word in lowercase_words:
            result.append(word)
        else:
            result.append(word.capitalize())

    return " ".join(result)
