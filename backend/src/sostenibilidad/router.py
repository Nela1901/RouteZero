from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.security import UsuarioActual, get_db_con_rls, requiere_rol
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
