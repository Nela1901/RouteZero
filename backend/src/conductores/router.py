from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.conductores.repository import RepositorioConductores
from src.conductores.schemas import ConductorActualizar, ConductorCrear, ConductorOut
from src.conductores.service import ServicioConductores
from src.core.security import UsuarioActual, get_db_con_rls, requiere_rol

router = APIRouter(prefix="/api/conductores", tags=["conductores"])


@router.post("", response_model=ConductorOut, status_code=201)
def registrar_conductor(
    body: ConductorCrear,
    usuario: UsuarioActual = Depends(requiere_rol("ADMINISTRADOR")),
    db: Session = Depends(get_db_con_rls),
) -> dict:
    return ServicioConductores(RepositorioConductores(db)).registrar(body, usuario.usuario_id)


@router.put("/{conductor_id}", response_model=ConductorOut)
def editar_conductor(
    conductor_id: str,
    body: ConductorActualizar,
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
