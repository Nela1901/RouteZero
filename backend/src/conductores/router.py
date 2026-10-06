from fastapi import APIRouter, Depends, Path, Response
from sqlalchemy.orm import Session

from src.conductores.repository import RepositorioConductores
from src.conductores.schemas import ConductorActualizar, ConductorCrear, ConductorOut
from src.conductores.service import ServicioConductores
from src.core.security import UsuarioActual, get_db_con_rls, requiere_rol

router = APIRouter(prefix="/api/conductores", tags=["conductores"])

_UUID = r"^[0-9a-fA-F-]{36}$"


@router.post("", response_model=ConductorOut, status_code=201)
def registrar_conductor(
    body: ConductorCrear,
    usuario: UsuarioActual = Depends(requiere_rol("ADMINISTRADOR")),
    db: Session = Depends(get_db_con_rls),
) -> dict:
    return ServicioConductores(RepositorioConductores(db)).registrar(body, usuario.usuario_id)


@router.get("/{conductor_id}", response_model=ConductorOut)
def ver_conductor(
    conductor_id: str = Path(pattern=_UUID),
    _usuario: UsuarioActual = Depends(requiere_rol("ADMINISTRADOR")),
    db: Session = Depends(get_db_con_rls),
) -> dict:
    return ServicioConductores(RepositorioConductores(db)).obtener(conductor_id)


@router.delete("/{conductor_id}", status_code=204)
def eliminar_conductor(
    conductor_id: str = Path(pattern=_UUID),
    usuario: UsuarioActual = Depends(requiere_rol("ADMINISTRADOR")),
    db: Session = Depends(get_db_con_rls),
) -> Response:
    ServicioConductores(RepositorioConductores(db)).eliminar(conductor_id, usuario.usuario_id)
    return Response(status_code=204)


@router.put("/{conductor_id}", response_model=ConductorOut)
def editar_conductor(
    body: ConductorActualizar,
    conductor_id: str = Path(pattern=_UUID),
    usuario: UsuarioActual = Depends(requiere_rol("ADMINISTRADOR")),
    db: Session = Depends(get_db_con_rls),
) -> dict:
    return ServicioConductores(RepositorioConductores(db)).editar(conductor_id, body, usuario.usuario_id)


@router.get("", response_model=list[ConductorOut])
def listar_conductores(
    disponible: bool | None = None,
    _usuario: UsuarioActual = Depends(requiere_rol("ADMINISTRADOR")),
    db: Session = Depends(get_db_con_rls),
) -> list[dict]:
    return ServicioConductores(RepositorioConductores(db)).listar(disponible)
