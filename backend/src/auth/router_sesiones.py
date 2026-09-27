from fastapi import APIRouter, Depends, Path, Request
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from src.auth.repository import RepositorioSesiones, RepositorioUsuarios
from src.auth.schemas import (
    LoginMFARequest,
    LoginRequest,
    LoginResponse,
    RenovarRequest,
    SesionOut,
)
from src.auth.service_sesiones import ServicioSesiones
from src.core.database import sesion_como_usuario
from src.core.security import (
    UsuarioActual,
    bearer_scheme,
    get_current_user,
    get_current_user_parcial,
    get_db_con_rls,
)

router = APIRouter(prefix="/api/auth", tags=["sesiones"])

_UUID = r"^[0-9a-fA-F-]{36}$"


def _info_cliente(request: Request) -> tuple[str | None, str | None]:
    """User-Agent e IP del cliente. Solo informativos (se muestran al usuario en su listado
    de sesiones), nunca se usan para autorizar; por eso basta con el primer valor de
    X-Forwarded-For cuando el backend corre detrás de un proxy (Render)."""
    dispositivo = request.headers.get("user-agent")
    reenviada = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
    ip = reenviada or (request.client.host if request.client else None)
    return dispositivo, (ip[:45] if ip else None)


def _servicio(db: Session) -> ServicioSesiones:
    return ServicioSesiones(RepositorioUsuarios(db), RepositorioSesiones(db))


@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest, request: Request) -> dict:
    dispositivo, ip = _info_cliente(request)
    with sesion_como_usuario() as db:
        return _servicio(db).login(body.email, body.password, dispositivo, ip)


@router.post("/login/mfa", response_model=LoginResponse)
def login_mfa(
    body: LoginMFARequest,
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    usuario: UsuarioActual = Depends(get_current_user_parcial),
    db: Session = Depends(get_db_con_rls),
) -> dict:
    dispositivo, ip = _info_cliente(request)
    return _servicio(db).completar_login_mfa(
        usuario, credentials.credentials, body.factor_id, body.codigo, dispositivo, ip
    )


@router.post("/sesiones/renovar", response_model=LoginResponse)
def renovar(body: RenovarRequest) -> dict:
    with sesion_como_usuario() as db:
        return _servicio(db).renovar(body.access_token, body.refresh_token)


@router.get("/sesiones", response_model=list[SesionOut])
def listar_sesiones(
    usuario: UsuarioActual = Depends(get_current_user),
    db: Session = Depends(get_db_con_rls),
) -> list[dict]:
    return _servicio(db).listar_propias(usuario)


@router.delete("/sesiones/{sesion_id}", status_code=204)
def revocar_sesion(
    sesion_id: str = Path(pattern=_UUID),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    usuario: UsuarioActual = Depends(get_current_user),
    db: Session = Depends(get_db_con_rls),
) -> None:
    _servicio(db).revocar(usuario, credentials.credentials, sesion_id)


@router.delete("/sesiones", status_code=204)
def revocar_todas(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    usuario: UsuarioActual = Depends(get_current_user),
    db: Session = Depends(get_db_con_rls),
) -> None:
    _servicio(db).revocar_todas(usuario, credentials.credentials)
