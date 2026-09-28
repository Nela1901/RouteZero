from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.clientes.repository import RepositorioClientes
from src.clientes.schemas import ClienteCrear, ClienteOut
from src.clientes.service import ServicioClientes
from src.core.security import UsuarioActual, get_db_con_rls, requiere_rol

router = APIRouter(prefix="/api/clientes", tags=["clientes"])


@router.post("", response_model=ClienteOut, status_code=201)
def registrar_cliente(
    body: ClienteCrear,
    _usuario: UsuarioActual = Depends(requiere_rol("OPERADOR", "ADMINISTRADOR")),
    db: Session = Depends(get_db_con_rls),
) -> dict:
    return ServicioClientes(RepositorioClientes(db)).registrar(body)


@router.get("", response_model=list[ClienteOut])
def listar_clientes(
    _usuario: UsuarioActual = Depends(requiere_rol("OPERADOR", "ADMINISTRADOR")),
    db: Session = Depends(get_db_con_rls),
) -> list[dict]:
    return ServicioClientes(RepositorioClientes(db)).listar()
