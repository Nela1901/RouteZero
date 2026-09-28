from typing import Literal

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.security import UsuarioActual, get_db_con_rls, requiere_rol
from src.flota.repository import RepositorioVehiculos
from src.flota.schemas import VehiculoActualizar, VehiculoCrear, VehiculoOut
from src.flota.service import ServicioVehiculos

router = APIRouter(prefix="/api/vehiculos", tags=["flota"])


@router.post("", response_model=VehiculoOut, status_code=201)
def registrar_vehiculo(
    body: VehiculoCrear,
    _usuario: UsuarioActual = Depends(requiere_rol("ADMINISTRADOR")),
    db: Session = Depends(get_db_con_rls),
) -> dict:
    return ServicioVehiculos(RepositorioVehiculos(db)).registrar(body)


@router.put("/{vehiculo_id}", response_model=VehiculoOut)
def editar_vehiculo(
    vehiculo_id: str,
    body: VehiculoActualizar,
    _usuario: UsuarioActual = Depends(requiere_rol("ADMINISTRADOR")),
    db: Session = Depends(get_db_con_rls),
) -> dict:
    return ServicioVehiculos(RepositorioVehiculos(db)).editar(vehiculo_id, body)


@router.get("", response_model=list[VehiculoOut])
def listar_vehiculos(
    estado: Literal["DISPONIBLE", "EN_RUTA", "MANTENIMIENTO", "INACTIVO"] | None = None,
    _usuario: UsuarioActual = Depends(requiere_rol("ADMINISTRADOR")),
    db: Session = Depends(get_db_con_rls),
) -> list[dict]:
    return ServicioVehiculos(RepositorioVehiculos(db)).listar(estado)
