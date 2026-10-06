from datetime import date

from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session

from src.core.security import UsuarioActual, get_db_con_rls, requiere_rol
from src.rutas.repository import RepositorioRutas
from src.rutas.schemas import (
    GenerarRutas,
    ResultadoConfirmacion,
    ResultadoDescarte,
    ResultadoGeneracion,
    RutaOut,
)
from src.rutas.service import ServicioRutas

router = APIRouter(prefix="/api/rutas", tags=["rutas"])

_UUID = r"^[0-9a-fA-F-]{36}$"


def _servicio(db: Session) -> ServicioRutas:
    return ServicioRutas(RepositorioRutas(db))


@router.post("/generar", response_model=ResultadoGeneracion, status_code=201)
def generar_rutas(
    body: GenerarRutas,
    usuario: UsuarioActual = Depends(requiere_rol("ADMINISTRADOR")),
    db: Session = Depends(get_db_con_rls),
) -> dict:
    """Genera rutas en borrador (PLANIFICADA) para todos los pedidos pendientes; no cambia el estado de los pedidos."""
    return _servicio(db).generar(body.fecha_jornada, body.tiempo_max_s, usuario.usuario_id)


@router.post("/lotes/{lote_id}/confirmar", response_model=ResultadoConfirmacion)
def confirmar_lote(
    lote_id: str = Path(pattern=_UUID),
    usuario: UsuarioActual = Depends(requiere_rol("ADMINISTRADOR")),
    db: Session = Depends(get_db_con_rls),
) -> dict:
    """Pasa las rutas del lote a CONFIRMADA y sus pedidos a ASIGNADO."""
    return _servicio(db).confirmar(lote_id, usuario.usuario_id)


@router.delete("/lotes/{lote_id}", response_model=ResultadoDescarte)
def descartar_lote(
    lote_id: str = Path(pattern=_UUID),
    usuario: UsuarioActual = Depends(requiere_rol("ADMINISTRADOR")),
    db: Session = Depends(get_db_con_rls),
) -> dict:
    """Elimina un lote de borradores; las rutas confirmadas no se pueden descartar."""
    return _servicio(db).descartar(lote_id, usuario.usuario_id)


@router.get("", response_model=list[RutaOut])
def listar_rutas(
    fecha: date,
    _usuario: UsuarioActual = Depends(requiere_rol("ADMINISTRADOR", "OPERADOR")),
    db: Session = Depends(get_db_con_rls),
) -> list[dict]:
    return _servicio(db).listar(fecha)


@router.get("/{ruta_id}", response_model=RutaOut)
def detalle_ruta(
    ruta_id: str = Path(pattern=_UUID),
    _usuario: UsuarioActual = Depends(requiere_rol("ADMINISTRADOR", "OPERADOR")),
    db: Session = Depends(get_db_con_rls),
) -> dict:
    return _servicio(db).detalle(ruta_id)
