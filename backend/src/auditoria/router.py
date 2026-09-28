from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.auditoria.repository import RepositorioAuditoria
from src.auditoria.schemas import LogAuditoriaOut
from src.core.security import UsuarioActual, get_db_con_rls, requiere_rol

router = APIRouter(prefix="/api/auditoria", tags=["auditoria"])


@router.get("", response_model=list[LogAuditoriaOut])
def listar_auditoria(
    modulo: str | None = None,
    limite: int = 100,
    _usuario: UsuarioActual = Depends(requiere_rol("ADMINISTRADOR")),
    db: Session = Depends(get_db_con_rls),
) -> list[dict]:
    limite = min(max(limite, 1), 500)
    return RepositorioAuditoria(db).listar(modulo, limite)
