from datetime import datetime, time
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from src.core.texto import validar_nombre_negocio, validar_texto_libre

TipoNegocio = Literal["BODEGA", "RESTAURANTE", "MERCADO", "COMERCIO", "OTRO"]


class ClienteCrear(BaseModel):
    nombre: str = Field(min_length=1, max_length=150)
    tipo_negocio: TipoNegocio
    referencia: str | None = Field(default=None, max_length=2000)
    latitud: Decimal = Field(ge=-90, le=90, decimal_places=8)
    longitud: Decimal = Field(ge=-180, le=180, decimal_places=8)
    horario_inicio: time = time(6, 0)
    horario_fin: time = time(21, 0)

    @field_validator("nombre")
    @classmethod
    def _limpiar_nombre(cls, valor: str) -> str:
        valor = valor.strip()
        if not valor:
            raise ValueError("El nombre no puede estar vacío")
        return validar_nombre_negocio(valor)

    @field_validator("referencia")
    @classmethod
    def _limpiar_referencia(cls, valor: str | None) -> str | None:
        valor = (valor or "").strip()
        return validar_texto_libre(valor) if valor else None

    @model_validator(mode="after")
    def _horario_valido(self):
        if self.horario_fin <= self.horario_inicio:
            raise ValueError("El horario de fin debe ser posterior al de inicio")
        return self


class ClienteActualizar(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=150)
    tipo_negocio: TipoNegocio | None = None
    referencia: str | None = Field(default=None, max_length=2000)
    latitud: Decimal | None = Field(default=None, ge=-90, le=90, decimal_places=8)
    longitud: Decimal | None = Field(default=None, ge=-180, le=180, decimal_places=8)
    horario_inicio: time | None = None
    horario_fin: time | None = None

    @field_validator("nombre")
    @classmethod
    def _limpiar_nombre(cls, valor: str | None) -> str | None:
        if valor is None:
            return valor
        valor = valor.strip()
        if not valor:
            raise ValueError("El nombre no puede estar vacío")
        return validar_nombre_negocio(valor)

    @field_validator("referencia")
    @classmethod
    def _limpiar_referencia(cls, valor: str | None) -> str | None:
        valor = (valor or "").strip()
        return validar_texto_libre(valor) if valor else None


class ClienteOut(BaseModel):
    cliente_id: str
    nombre: str
    tipo_negocio: str
    referencia: str | None
    latitud: Decimal
    longitud: Decimal
    horario_inicio: time
    horario_fin: time
    creado_en: datetime
