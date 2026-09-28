from datetime import datetime, time
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field

TipoNegocio = Literal["BODEGA", "RESTAURANTE", "MERCADO", "COMERCIO", "OTRO"]


class ClienteCrear(BaseModel):
    nombre: str = Field(min_length=1, max_length=150)
    tipo_negocio: TipoNegocio
    referencia: str | None = Field(default=None, max_length=2000)
    latitud: Decimal = Field(ge=-90, le=90, decimal_places=8)
    longitud: Decimal = Field(ge=-180, le=180, decimal_places=8)
    horario_inicio: time = time(6, 0)
    horario_fin: time = time(21, 0)


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
