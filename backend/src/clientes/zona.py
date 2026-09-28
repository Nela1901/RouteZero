"""Validación de zona de cobertura (RN-007): solo se aceptan coordenadas dentro del
área operativa del distrito de Huancayo (y El Tambo, donde opera Andina Reparto S.A.C.).

Es una caja delimitadora aproximada, suficiente para el alcance del MVP académico —
no reemplaza un polígono geográfico real.
"""

from decimal import Decimal

HUANCAYO_LAT_MIN = Decimal("-12.15")
HUANCAYO_LAT_MAX = Decimal("-11.95")
HUANCAYO_LON_MIN = Decimal("-75.30")
HUANCAYO_LON_MAX = Decimal("-75.10")


def dentro_de_zona_cobertura(latitud: Decimal, longitud: Decimal) -> bool:
    return (
        HUANCAYO_LAT_MIN <= latitud <= HUANCAYO_LAT_MAX
        and HUANCAYO_LON_MIN <= longitud <= HUANCAYO_LON_MAX
    )
