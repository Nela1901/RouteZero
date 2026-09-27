from collections.abc import Generator
from dataclasses import dataclass

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.core.config import settings
from src.core.database import SessionLocal

bearer_scheme = HTTPBearer()

# Supabase firma los tokens con llaves asimétricas (ES256) publicadas en este endpoint
# JWKS público — no hace falta guardar ningún secreto para verificar la firma.
_jwks_client = jwt.PyJWKClient(f"{settings.supabase_url}/auth/v1/.well-known/jwks.json")


@dataclass
class UsuarioActual:
    usuario_id: str
    rol_id: str
    email: str
    aal: str
    mfa_activo: bool
    session_id: str
    estado_sesion: str | None  # None: la sesión no está registrada en sesiones_activas


def decodificar_token(token: str, verificar_exp: bool = True) -> dict:
    """Verifica firma y audiencia del JWT de Supabase.

    `verificar_exp=False` solo se usa al renovar sesión, para identificar de quién es
    un access token ya vencido (la firma sigue verificándose).
    """
    try:
        signing_key = _jwks_client.get_signing_key_from_jwt(token)
        return jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256"],
            audience="authenticated",
            options={"verify_exp": verificar_exp},
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        ) from exc


def get_current_user_parcial(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> UsuarioActual:
    """Identifica al usuario a partir del JWT, aceptando sesiones aal1.

    Solo debe usarse en el paso de verificación MFA del login. Cualquier otro
    endpoint debe usar `get_current_user`, que exige aal2 si el usuario tiene MFA.
    """
    payload = decodificar_token(credentials.credentials)
    usuario_id = payload.get("sub")
    if not usuario_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token sin usuario asociado")

    token_version = payload.get("ver", 1)

    with SessionLocal() as session:
        # La firma del JWT ya prueba que este usuario_id es legítimo, así que es
        # correcto fijar la variable de RLS a ese mismo id antes de leer su propia fila.
        session.execute(
            text("SET LOCAL app.usuario_actual_id = :uid"), {"uid": usuario_id}
        )
        row = session.execute(
            text("SELECT rol_id, token_version, mfa_activo FROM usuarios WHERE usuario_id = :uid"),
            {"uid": usuario_id},
        ).one_or_none()
        session_id = payload.get("session_id", "")
        fila_sesion = session.execute(
            text("SELECT estado FROM sesiones_activas WHERE supabase_session_id = :sid"),
            {"sid": session_id},
        ).one_or_none()
        estado_sesion = fila_sesion[0] if fila_sesion else None

    if row is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Usuario sin perfil registrado")

    rol_id, version_actual, mfa_activo = row
    if int(token_version) != int(version_actual):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token revocado, inicia sesión de nuevo",
        )

    return UsuarioActual(
        usuario_id=usuario_id,
        rol_id=str(rol_id),
        email=payload.get("email", ""),
        aal=payload.get("aal", "aal1"),
        mfa_activo=bool(mfa_activo),
        session_id=session_id,
        estado_sesion=estado_sesion,
    )


def get_current_user(
    usuario: UsuarioActual = Depends(get_current_user_parcial),
) -> UsuarioActual:
    """Usuario plenamente autenticado.

    Exige que la sesión del token esté registrada y ACTIVA en `sesiones_activas` (así una
    revocación surte efecto de inmediato y un token obtenido llamando a Supabase
    directamente, sin pasar por nuestro login, no sirve), y aal2 si el usuario tiene MFA.
    """
    if usuario.estado_sesion != "ACTIVA":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión no registrada o revocada, inicia sesión de nuevo",
        )
    if usuario.mfa_activo and usuario.aal != "aal2":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requiere completar la verificación MFA",
        )
    return usuario


def get_db_con_rls(
    usuario: UsuarioActual = Depends(get_current_user_parcial),
) -> Generator[Session, None, None]:
    """Sesión de base de datos con app.usuario_actual_id fijado para que RLS filtre por el usuario autenticado.

    No decide el nivel de autenticación exigido: el endpoint debe declarar además
    `get_current_user` (o `get_current_user_parcial` en el paso MFA del login).
    """
    session = SessionLocal()
    try:
        session.execute(
            text("SET LOCAL app.usuario_actual_id = :usuario_id"),
            {"usuario_id": usuario.usuario_id},
        )
        yield session
        session.commit()
    except HTTPException:
        # Un HTTPException es una respuesta de negocio esperada (código inválido, etc.),
        # no un fallo del sistema: se guardan los cambios ya hechos (p. ej. contador de
        # intentos fallidos) antes de propagar el error al cliente.
        session.commit()
        raise
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
