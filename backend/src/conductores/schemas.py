from datetime import date, datetime, time
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from src.core.texto import validar_nombre_persona

# Categorías de licencia de conducir del MTC (DS 007-2016-MTC) aplicables al reparto urbano.
CategoriaLicencia = Literal["A-I", "A-IIa", "A-IIb", "A-IIIa", "A-IIIb", "A-IIIc", "B-IIa", "B-IIb"]


_PATRON_CORREO = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class ConductorCrear(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    dni: str = Field(pattern=r"^[0-9]{8}$")
    categoria_licencia: CategoriaLicencia
    telefono: str = Field(pattern=r"^[0-9]{9}$")
    correo: str | None = Field(default=None, max_length=254, pattern=_PATRON_CORREO)
    licencia_vence: date
    horario_inicio: time = time(6, 0)
    horario_fin: time = time(14, 0)
    # RN-013: sin consentimiento explícito no se almacenan datos personales del conductor.
    consentimiento_datos: Literal[True]

    @field_validator("nombre")
    @classmethod
    def _limpiar_nombre(cls, valor: str) -> str:
        valor = valor.strip()
        if not valor:
            raise ValueError("El nombre no puede estar vacío")
        return validar_nombre_persona(valor)


class ConductorActualizar(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    dni: str | None = Field(default=None, pattern=r"^[0-9]{8}$")
    categoria_licencia: CategoriaLicencia | None = None
    telefono: str | None = Field(default=None, pattern=r"^[0-9]{9}$")
    correo: str | None = Field(default=None, max_length=254, pattern=_PATRON_CORREO)
    licencia_vence: date | None = None
    horario_inicio: time | None = None
    horario_fin: time | None = None
    disponible: bool | None = None

    @field_validator("nombre")
    @classmethod
    def _limpiar_nombre(cls, valor: str | None) -> str | None:
        if valor is None:
            return valor
        valor = valor.strip()
        if not valor:
            raise ValueError("El nombre no puede estar vacío")
        return validar_nombre_persona(valor)


class ConductorOut(BaseModel):
    conductor_id: str
    nombre: str
    dni: str
    categoria_licencia: str
    telefono: str
    correo: str | None
    licencia_vence: date
    horario_inicio: time
    horario_fin: time
    disponible: bool
    horas_conducidas_hoy: Decimal
    consentimiento_en: datetime
    creado_en: datetime
