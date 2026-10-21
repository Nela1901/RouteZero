from datetime import date

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from src.core.security import UsuarioActual, get_db_con_rls, requiere_rol
from src.rutas.repository import RepositorioRutas
from src.rutas.schemas import (
    GenerarRutas,
    IncidenteIn,
    IncidenteOut,
    MarcarEntrega,
    Reoptimizar,
    ResultadoConfirmacion,
    ResultadoDescarte,
    ResultadoEntrega,
    ResultadoGeneracion,
    ResultadoReoptimizacion,
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


@router.post("/reoptimizar", response_model=ResultadoReoptimizacion, status_code=201)
def reoptimizar_rutas(
    body: Reoptimizar,
    usuario: UsuarioActual = Depends(requiere_rol("ADMINISTRADOR")),
    db: Session = Depends(get_db_con_rls),
) -> dict:
    """Recalcula lo que falta de las rutas en curso (RN-012, ≤ 30 s) y lo deja como borrador por ruta; se
    confirma o se descarta con los mismos endpoints de lotes. Sin rutas activas responde con `sin_rutas_activas`."""
    return _servicio(db).reoptimizar(body.fecha_jornada, body.tiempo_max_s, body.hora_actual, usuario.usuario_id)


@router.patch("/{ruta_id}/paradas/{pedido_id}/entrega", response_model=ResultadoEntrega)
def marcar_entrega(
    body: MarcarEntrega,
    ruta_id: str = Path(pattern=_UUID),
    pedido_id: str = Path(pattern=_UUID),
    usuario: UsuarioActual = Depends(requiere_rol("ADMINISTRADOR", "OPERADOR")),
    db: Session = Depends(get_db_con_rls),
) -> dict:
    """Registra una parada como ENTREGADO o FALLIDO. La ruta pasa a EN_EJECUCION y, al atender la última, a COMPLETADA."""
    return _servicio(db).marcar_entrega(ruta_id, pedido_id, body.estado, usuario.usuario_id)


@router.post("/incidentes", response_model=IncidenteOut, status_code=201)
def registrar_incidente(
    body: IncidenteIn,
    usuario: UsuarioActual = Depends(requiere_rol("ADMINISTRADOR")),
    db: Session = Depends(get_db_con_rls),
) -> dict:
    """Registra una alerta de congestión en una de las vías de la RN-012. La siguiente re-optimización la aplica."""
    return _servicio(db).registrar_incidente(body.calle, body.factor, body.descripcion, usuario.usuario_id)


@router.get("/incidentes", response_model=list[IncidenteOut])
def listar_incidentes(
    solo_activos: bool = Query(default=True),
    _usuario: UsuarioActual = Depends(requiere_rol("ADMINISTRADOR", "OPERADOR", "CONDUCTOR")),
    db: Session = Depends(get_db_con_rls),
) -> list[dict]:
    return _servicio(db).listar_incidentes(solo_activos)


@router.delete("/incidentes/{incidente_id}", response_model=IncidenteOut)
def resolver_incidente(
    incidente_id: str = Path(pattern=_UUID),
    usuario: UsuarioActual = Depends(requiere_rol("ADMINISTRADOR")),
    db: Session = Depends(get_db_con_rls),
) -> dict:
    """Marca el incidente como resuelto: deja de aplicarse en las próximas re-optimizaciones."""
    return _servicio(db).resolver_incidente(incidente_id, usuario.usuario_id)


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
