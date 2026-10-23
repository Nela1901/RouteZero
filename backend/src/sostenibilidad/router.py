from datetime import date

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from src.auditoria.repository import RepositorioAuditoria
from src.core.security import UsuarioActual, get_db_con_rls, requiere_rol
from src.sostenibilidad.reporte import generar_pdf
from src.sostenibilidad.repository import RepositorioSostenibilidad
from src.sostenibilidad.schemas import CompensacionOut, DashboardOut
from src.sostenibilidad.service import ServicioSostenibilidad

router = APIRouter(prefix="/api/sostenibilidad", tags=["sostenibilidad"])


@router.get("/dashboard", response_model=DashboardOut)
def dashboard(
    desde: date | None = None,
    hasta: date | None = None,
    _usuario: UsuarioActual = Depends(requiere_rol("ADMINISTRADOR")),
    db: Session = Depends(get_db_con_rls),
) -> dict:
    return ServicioSostenibilidad(RepositorioSostenibilidad(db)).dashboard(desde, hasta)


@router.get("/compensacion", response_model=CompensacionOut)
def plan_de_compensacion(
    desde: date | None = None,
    hasta: date | None = None,
    _usuario: UsuarioActual = Depends(requiere_rol("ADMINISTRADOR")),
    db: Session = Depends(get_db_con_rls),
) -> dict:
    return ServicioSostenibilidad(RepositorioSostenibilidad(db)).compensacion(desde, hasta)


@router.get("/reporte", response_class=Response, responses={200: {"content": {"application/pdf": {}}}, 404: {"description": "Sin datos en el periodo"}})
def reporte_pdf(
    desde: date | None = None,
    hasta: date | None = None,
    usuario: UsuarioActual = Depends(requiere_rol("ADMINISTRADOR")),
    db: Session = Depends(get_db_con_rls),
) -> Response:
    datos = ServicioSostenibilidad(RepositorioSostenibilidad(db)).datos_del_reporte(desde, hasta)
    contenido = generar_pdf(datos)
    RepositorioAuditoria(db).registrar(usuario.usuario_id, "reporte_generado", "sostenibilidad", f"{datos['desde']} a {datos['hasta']}")
    nombre = f"reporte-sostenibilidad-{datos['desde']}-{datos['hasta']}.pdf"
    return Response(contenido, media_type="application/pdf", headers={"Content-Disposition": f'attachment; filename="{nombre}"'})
