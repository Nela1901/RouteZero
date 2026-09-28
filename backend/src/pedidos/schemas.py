from datetime import datetime, time
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, model_validator

Prioridad = Literal["EXPRESS", "ESTANDAR", "ECONOMICO"]
EstadoPedido = Literal["PENDIENTE", "ASIGNADO", "EN_CAMINO", "ENTREGADO", "CANCELADO"]


class PedidoCrear(BaseModel):
    cliente_id: str = Field(pattern=r"^[0-9a-fA-F-]{36}$")
    descripcion: str | None = Field(default=None, max_length=2000)
    peso_kg: Decimal = Field(gt=0, le=99999.99, decimal_places=2)
    volumen_m3: Decimal | None = Field(default=None, gt=0, le=999.999, decimal_places=3)
    prioridad: Prioridad = "ESTANDAR"
    latitud: Decimal = Field(ge=-90, le=90, decimal_places=8)
    longitud: Decimal = Field(ge=-180, le=180, decimal_places=8)
    ventana_inicio: time
    ventana_fin: time

    @model_validator(mode="after")
    def _ventana_valida(self):
        if self.ventana_fin <= self.ventana_inicio:
            raise ValueError("La ventana de tiempo fin debe ser posterior al inicio")
        return self


class PedidoOut(BaseModel):
    pedido_id: str
    cliente_id: str
    descripcion: str | None
    peso_kg: Decimal
    volumen_m3: Decimal | None
    prioridad: str
    latitud: Decimal
    longitud: Decimal
    ventana_inicio: time
    ventana_fin: time
    estado: str
    creado_en: datetime
