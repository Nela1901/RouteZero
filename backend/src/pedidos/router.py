from typing import Literal

from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session

from src.clientes.repository import RepositorioClientes
from src.core.security import UsuarioActual, get_db_con_rls, requiere_rol
from src.pedidos.repository import RepositorioPedidos
from src.pedidos.schemas import PedidoCrear, PedidoOut
from src.pedidos.service import ServicioPedidos

router = APIRouter(prefix="/api/pedidos", tags=["pedidos"])

_UUID = r"^[0-9a-fA-F-]{36}$"


def _servicio(db: Session) -> ServicioPedidos:
    return ServicioPedidos(RepositorioPedidos(db), RepositorioClientes(db))


@router.post("", response_model=PedidoOut, status_code=201)
def registrar_pedido(
    body: PedidoCrear,
    _usuario: UsuarioActual = Depends(requiere_rol("OPERADOR", "ADMINISTRADOR")),
    db: Session = Depends(get_db_con_rls),
) -> dict:
    return _servicio(db).registrar(body)


@router.delete("/{pedido_id}", response_model=PedidoOut)
def cancelar_pedido(
    pedido_id: str = Path(pattern=_UUID),
    _usuario: UsuarioActual = Depends(requiere_rol("OPERADOR", "ADMINISTRADOR")),
    db: Session = Depends(get_db_con_rls),
) -> dict:
    return _servicio(db).cancelar(pedido_id)


@router.get("", response_model=list[PedidoOut])
def listar_pedidos(
    estado: Literal["PENDIENTE", "ASIGNADO", "EN_CAMINO", "ENTREGADO", "CANCELADO"] | None = None,
    prioridad: Literal["EXPRESS", "ESTANDAR", "ECONOMICO"] | None = None,
    _usuario: UsuarioActual = Depends(requiere_rol("OPERADOR", "ADMINISTRADOR")),
    db: Session = Depends(get_db_con_rls),
) -> list[dict]:
    return _servicio(db).listar(estado, prioridad)
