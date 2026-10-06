from typing import Literal

from fastapi import APIRouter, Depends, Path, Response
from sqlalchemy.orm import Session

from src.core.security import UsuarioActual, get_db_con_rls, requiere_rol
from src.flota.repository import RepositorioVehiculos
from src.flota.schemas import VehiculoActualizar, VehiculoCrear, VehiculoOut
from src.flota.service import ServicioVehiculos

router = APIRouter(prefix="/api/vehiculos", tags=["flota"])

_UUID = r"^[0-9a-fA-F-]{36}$"


@router.post("", response_model=VehiculoOut, status_code=201)
def registrar_vehiculo(
    body: VehiculoCrear,
    _usuario: UsuarioActual = Depends(requiere_rol("ADMINISTRADOR")),
    db: Session = Depends(get_db_con_rls),
) -> dict:
    return ServicioVehiculos(RepositorioVehiculos(db)).registrar(body)


@router.get("/{vehiculo_id}", response_model=VehiculoOut)
def ver_vehiculo(
    vehiculo_id: str = Path(pattern=_UUID),
    _usuario: UsuarioActual = Depends(requiere_rol("ADMINISTRADOR")),
    db: Session = Depends(get_db_con_rls),
) -> dict:
    return ServicioVehiculos(RepositorioVehiculos(db)).obtener(vehiculo_id)


@router.delete("/{vehiculo_id}", status_code=204)
def eliminar_vehiculo(
    vehiculo_id: str = Path(pattern=_UUID),
    _usuario: UsuarioActual = Depends(requiere_rol("ADMINISTRADOR")),
    db: Session = Depends(get_db_con_rls),
) -> Response:
    ServicioVehiculos(RepositorioVehiculos(db)).eliminar(vehiculo_id)
    return Response(status_code=204)


@router.put("/{vehiculo_id}", response_model=VehiculoOut)
def editar_vehiculo(
    body: VehiculoActualizar,
    vehiculo_id: str = Path(pattern=_UUID),
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
