from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field

TipoVehiculo = Literal["CAMIONETA", "FURGON", "MOTO"]
EstadoVehiculo = Literal["DISPONIBLE", "EN_RUTA", "MANTENIMIENTO", "INACTIVO"]


class VehiculoCrear(BaseModel):
    placa: str = Field(min_length=1, max_length=10, pattern=r"^[A-Za-z0-9-]+$")
    tipo: TipoVehiculo
    capacidad_kg: Decimal = Field(gt=0, le=99999.99, decimal_places=2)
    consumo_km_l: Decimal = Field(gt=0, le=9999.99, decimal_places=2)
    factor_emision_co2: Decimal = Field(gt=0, le=99.9999, decimal_places=4)
    anio_fabricacion: int = Field(ge=1990, le=2100)
    # Documentos obligatorios para circular en el Perú; solo se guarda su fecha de vencimiento.
    soat_vence: date | None = None
    revision_tecnica_vence: date | None = None


class VehiculoActualizar(BaseModel):
    tipo: TipoVehiculo | None = None
    capacidad_kg: Decimal | None = Field(default=None, gt=0, le=99999.99, decimal_places=2)
    consumo_km_l: Decimal | None = Field(default=None, gt=0, le=9999.99, decimal_places=2)
    factor_emision_co2: Decimal | None = Field(default=None, gt=0, le=99.9999, decimal_places=4)
    anio_fabricacion: int | None = Field(default=None, ge=1990, le=2100)
    estado: EstadoVehiculo | None = None
    soat_vence: date | None = None
    revision_tecnica_vence: date | None = None


class VehiculoOut(BaseModel):
    vehiculo_id: str
    placa: str
    tipo: str
    capacidad_kg: Decimal
    consumo_km_l: Decimal
    factor_emision_co2: Decimal
    anio_fabricacion: int
    estado: str
    creado_en: datetime
    soat_vence: date | None
    revision_tecnica_vence: date | None
