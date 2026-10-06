from fastapi import APIRouter, Depends, Path, Response
from sqlalchemy.orm import Session

from src.clientes.repository import RepositorioClientes
from src.clientes.schemas import ClienteActualizar, ClienteCrear, ClienteOut
from src.clientes.service import ServicioClientes
from src.core.security import UsuarioActual, get_db_con_rls, requiere_rol

router = APIRouter(prefix="/api/clientes", tags=["clientes"])

_UUID = r"^[0-9a-fA-F-]{36}$"


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


@router.get("/{cliente_id}", response_model=ClienteOut)
def ver_cliente(
    cliente_id: str = Path(pattern=_UUID),
    _usuario: UsuarioActual = Depends(requiere_rol("OPERADOR", "ADMINISTRADOR")),
    db: Session = Depends(get_db_con_rls),
) -> dict:
    return ServicioClientes(RepositorioClientes(db)).obtener(cliente_id)


@router.put("/{cliente_id}", response_model=ClienteOut)
def editar_cliente(
    body: ClienteActualizar,
    cliente_id: str = Path(pattern=_UUID),
    _usuario: UsuarioActual = Depends(requiere_rol("OPERADOR", "ADMINISTRADOR")),
    db: Session = Depends(get_db_con_rls),
) -> dict:
    return ServicioClientes(RepositorioClientes(db)).editar(cliente_id, body)


@router.delete("/{cliente_id}", status_code=204)
def eliminar_cliente(
    cliente_id: str = Path(pattern=_UUID),
    _usuario: UsuarioActual = Depends(requiere_rol("OPERADOR", "ADMINISTRADOR")),
    db: Session = Depends(get_db_con_rls),
) -> Response:
    ServicioClientes(RepositorioClientes(db)).eliminar(cliente_id)
    return Response(status_code=204)
