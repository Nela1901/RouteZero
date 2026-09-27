from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from src.auth.repository import RepositorioUsuarios
from src.auth.schemas import ConfirmarMFARequest, DesactivarMFARequest, InscribirMFAResponse
from src.auth.service_mfa import ServicioMFA
from src.core.security import UsuarioActual, bearer_scheme, get_current_user, get_db_con_rls

router = APIRouter(prefix="/api/auth/mfa", tags=["mfa"])


@router.post("/inscribir", response_model=InscribirMFAResponse)
def inscribir(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    usuario: UsuarioActual = Depends(get_current_user),
    db: Session = Depends(get_db_con_rls),
) -> dict:
    servicio = ServicioMFA(RepositorioUsuarios(db))
    return servicio.iniciar_inscripcion(usuario.usuario_id, credentials.credentials)


@router.post("/confirmar", status_code=204)
def confirmar(
    body: ConfirmarMFARequest,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    usuario: UsuarioActual = Depends(get_current_user),
    db: Session = Depends(get_db_con_rls),
) -> None:
    servicio = ServicioMFA(RepositorioUsuarios(db))
    servicio.confirmar_inscripcion(usuario.usuario_id, credentials.credentials, body.factor_id, body.codigo)


@router.post("/desactivar", status_code=204)
def desactivar(
    body: DesactivarMFARequest,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    usuario: UsuarioActual = Depends(get_current_user),
    db: Session = Depends(get_db_con_rls),
) -> None:
    servicio = ServicioMFA(RepositorioUsuarios(db))
    servicio.desactivar(
        usuario.usuario_id,
        usuario.email,
        credentials.credentials,
        body.factor_id,
        body.password,
        body.codigo,
    )
