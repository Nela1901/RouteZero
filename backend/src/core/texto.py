"""Validación de texto de los formularios: qué caracteres admite cada tipo de campo.

La interfaz filtra lo que se escribe con las mismas reglas (frontend/src/components/utilesCrud.ts);
aquí se vuelven a exigir porque la API no puede fiarse de que la petición venga de la pantalla.
Los patrones usan Unicode: aceptan tildes, la ñ y la ü, pero no el guion bajo ni signos raros.
"""

import re

_LETRA = r"[^\W\d_]"  # cualquier letra (con tildes, ñ, ü) y nada más
_LETRA_O_NUMERO = r"[^\W_]"

# Nombre de una persona: solo letras y espacios.
_NOMBRE_PERSONA = re.compile(rf"^(?:{_LETRA}| )+$")
# Nombre de un negocio: letras, números y los signos habituales de una razón social (S.A.C., Bodega "A & B", Puesto 14 - Norte).
_NOMBRE_NEGOCIO = re.compile(rf"^(?:{_LETRA_O_NUMERO}|[ .,\-&'()])+$")
# Descripciones y puntos de referencia: letras, números y la puntuación de una dirección o una frase.
_TEXTO_LIBRE = re.compile(rf"^(?:{_LETRA_O_NUMERO}|[ .,;:\-()#/°¿?¡!&'])+$")


def validar_nombre_persona(valor: str) -> str:
    if not _NOMBRE_PERSONA.match(valor):
        raise ValueError("El nombre solo puede contener letras y espacios")
    return valor


def validar_nombre_negocio(valor: str) -> str:
    if not _NOMBRE_NEGOCIO.match(valor):
        raise ValueError("El nombre del negocio solo puede contener letras, números, espacios y los signos . , - & ' ( )")
    return valor


def validar_texto_libre(valor: str) -> str:
    if not _TEXTO_LIBRE.match(valor):
        raise ValueError("El texto solo puede contener letras, números, espacios y los signos . , ; : - ( ) # / ° ¿ ? ¡ ! & '")
    return valor
