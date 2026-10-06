from typing import Literal

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from src.core.security import UsuarioActual, get_db_con_rls, requiere_rol
from src.pedidos.repository import RepositorioPedidos
from src.pedidos.schemas import PaginaPedidos, PedidoActualizar, PedidoCrear, PedidoOut
from src.pedidos.service import ServicioPedidos

router = APIRouter(prefix="/api/pedidos", tags=["pedidos"])

_UUID = r"^[0-9a-fA-F-]{36}$"


def _servicio(db: Session) -> ServicioPedidos:
    return ServicioPedidos(RepositorioPedidos(db))


@router.post("", response_model=PedidoOut, status_code=201)
def registrar_pedido(
    body: PedidoCrear,
    _usuario: UsuarioActual = Depends(requiere_rol("OPERADOR", "ADMINISTRADOR")),
    db: Session = Depends(get_db_con_rls),
) -> dict:
    return _servicio(db).registrar(body)


@router.get("/{pedido_id}", response_model=PedidoOut)
def ver_pedido(
    pedido_id: str = Path(pattern=_UUID),
    _usuario: UsuarioActual = Depends(requiere_rol("OPERADOR", "ADMINISTRADOR")),
    db: Session = Depends(get_db_con_rls),
) -> dict:
    return _servicio(db).obtener(pedido_id)


@router.put("/{pedido_id}", response_model=PedidoOut)
def editar_pedido(
    body: PedidoActualizar,
    pedido_id: str = Path(pattern=_UUID),
    _usuario: UsuarioActual = Depends(requiere_rol("OPERADOR", "ADMINISTRADOR")),
    db: Session = Depends(get_db_con_rls),
) -> dict:
    return _servicio(db).editar(pedido_id, body)


@router.delete("/{pedido_id}", response_model=PedidoOut)
def cancelar_pedido(
    pedido_id: str = Path(pattern=_UUID),
    _usuario: UsuarioActual = Depends(requiere_rol("OPERADOR", "ADMINISTRADOR")),
    db: Session = Depends(get_db_con_rls),
) -> dict:
    return _servicio(db).cancelar(pedido_id)


@router.get("", response_model=PaginaPedidos)
def listar_pedidos(
    estado: Literal["PENDIENTE", "ASIGNADO", "EN_CAMINO", "ENTREGADO", "CANCELADO"] | None = None,
    prioridad: Literal["EXPRESS", "ESTANDAR", "ECONOMICO"] | None = None,
    limite: int = Query(50, ge=1, le=200, description="Pedidos por página (máximo 200)"),
    desplazamiento: int = Query(0, ge=0, description="Pedidos que se omiten al inicio"),
    _usuario: UsuarioActual = Depends(requiere_rol("OPERADOR", "ADMINISTRADOR")),
    db: Session = Depends(get_db_con_rls),
) -> dict:
    return _servicio(db).listar(estado, prioridad, limite, desplazamiento)
