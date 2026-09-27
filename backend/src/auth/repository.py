from datetime import datetime, timedelta, timezone

from sqlalchemy import text
from sqlalchemy.orm import Session

MAX_INTENTOS = 3
BLOQUEO_MINUTOS = 15

# Contadores de bloqueo independientes (RN-001): uno para contraseña y otro para MFA.
# Los nombres de columna salen de esta tabla fija, nunca de datos del usuario.
_CONTADORES = {
    "login": ("intentos_fallidos", "bloqueado_hasta"),
    "mfa": ("mfa_intentos_fallidos", "mfa_bloqueado_hasta"),
}


class RepositorioUsuarios:
    """Acceso a `usuarios` (contadores de bloqueo, MFA, token_version), vía SQL parametrizado."""

    def __init__(self, session: Session):
        self.session = session

    def usuario_id_por_email(self, email: str) -> str | None:
        """Busca el id en auth.users mediante una función SECURITY DEFINER (el rol de la
        aplicación no tiene acceso directo al esquema `auth`)."""
        row = self.session.execute(
            text("SELECT public.usuario_id_por_email(:email)"), {"email": email}
        ).one()
        return str(row[0]) if row[0] is not None else None

    def existe_perfil(self, usuario_id: str) -> bool:
        row = self.session.execute(
            text("SELECT 1 FROM usuarios WHERE usuario_id = :uid"), {"uid": usuario_id}
        ).one_or_none()
        return row is not None

    def fijar_contexto_rls(self, usuario_id: str) -> None:
        """Fija app.usuario_actual_id en la transacción actual. Solo lo usa el login, donde el
        backend actúa de confianza sobre la cuenta que se está autenticando (aún sin token)."""
        self.session.execute(
            text("SET LOCAL app.usuario_actual_id = :uid"), {"uid": usuario_id}
        )

    def _segundos_bloqueo(self, contador: str, usuario_id: str) -> int:
        _, col_bloqueo = _CONTADORES[contador]
        row = self.session.execute(
            text(f"SELECT {col_bloqueo} FROM usuarios WHERE usuario_id = :uid"),
            {"uid": usuario_id},
        ).one()
        bloqueado_hasta = row[0]
        if bloqueado_hasta is None:
            return 0
        restante = (bloqueado_hasta - datetime.now(timezone.utc)).total_seconds()
        return max(0, int(restante) + (1 if restante % 1 else 0))

    def _esta_bloqueado(self, contador: str, usuario_id: str) -> bool:
        return self._segundos_bloqueo(contador, usuario_id) > 0

    def _registrar_fallo(self, contador: str, usuario_id: str) -> None:
        col_intentos, col_bloqueo = _CONTADORES[contador]
        row = self.session.execute(
            text(f"SELECT {col_intentos} FROM usuarios WHERE usuario_id = :uid"),
            {"uid": usuario_id},
        ).one()
        intentos = (row[0] or 0) + 1
        bloqueado_hasta = None
        if intentos >= MAX_INTENTOS:
            bloqueado_hasta = datetime.now(timezone.utc) + timedelta(minutes=BLOQUEO_MINUTOS)
            intentos = 0
        self.session.execute(
            text(
                f"UPDATE usuarios SET {col_intentos} = :intentos, {col_bloqueo} = :bloqueado "
                "WHERE usuario_id = :uid"
            ),
            {"intentos": intentos, "bloqueado": bloqueado_hasta, "uid": usuario_id},
        )

    def _resetear(self, contador: str, usuario_id: str) -> None:
        col_intentos, col_bloqueo = _CONTADORES[contador]
        self.session.execute(
            text(f"UPDATE usuarios SET {col_intentos} = 0, {col_bloqueo} = NULL WHERE usuario_id = :uid"),
            {"uid": usuario_id},
        )

    def esta_bloqueado_login(self, usuario_id: str) -> bool:
        return self._esta_bloqueado("login", usuario_id)

    def segundos_bloqueo_login(self, usuario_id: str) -> int:
        return self._segundos_bloqueo("login", usuario_id)

    def registrar_intento_login_fallido(self, usuario_id: str) -> None:
        self._registrar_fallo("login", usuario_id)

    def resetear_intentos_login(self, usuario_id: str) -> None:
        self._resetear("login", usuario_id)

    def esta_bloqueado_mfa(self, usuario_id: str) -> bool:
        return self._esta_bloqueado("mfa", usuario_id)

    def registrar_intento_mfa_fallido(self, usuario_id: str) -> None:
        self._registrar_fallo("mfa", usuario_id)

    def resetear_intentos_mfa(self, usuario_id: str) -> None:
        self._resetear("mfa", usuario_id)

    def obtener_estado_mfa(self, usuario_id: str) -> dict:
        row = self.session.execute(
            text(
                "SELECT mfa_activo, mfa_intentos_fallidos, mfa_bloqueado_hasta "
                "FROM usuarios WHERE usuario_id = :uid"
            ),
            {"uid": usuario_id},
        ).one()
        return {
            "mfa_activo": row[0],
            "mfa_intentos_fallidos": row[1],
            "mfa_bloqueado_hasta": row[2],
        }

    def activar_mfa(self, usuario_id: str) -> None:
        self.session.execute(
            text("UPDATE usuarios SET mfa_activo = TRUE WHERE usuario_id = :uid"),
            {"uid": usuario_id},
        )

    def desactivar_mfa(self, usuario_id: str) -> None:
        self.session.execute(
            text("UPDATE usuarios SET mfa_activo = FALSE WHERE usuario_id = :uid"),
            {"uid": usuario_id},
        )

    def incrementar_token_version(self, usuario_id: str) -> None:
        self.session.execute(
            text("UPDATE usuarios SET token_version = token_version + 1 WHERE usuario_id = :uid"),
            {"uid": usuario_id},
        )


class RepositorioSesiones:
    """Acceso a `sesiones_activas`, el espejo propio (visible al usuario) de las sesiones de Supabase."""

    def __init__(self, session: Session):
        self.session = session

    def registrar(
        self,
        usuario_id: str,
        supabase_session_id: str,
        dispositivo_info: str | None,
        ip_origen: str | None,
        refresh_token_hash: str,
    ) -> None:
        self.session.execute(
            text(
                "INSERT INTO sesiones_activas "
                "(usuario_id, supabase_session_id, dispositivo_info, ip_origen, "
                " refresh_token_hash, rotada_en) "
                "VALUES (:uid, :sid, :dispositivo, :ip, :hash, CURRENT_TIMESTAMP) "
                "ON CONFLICT (supabase_session_id) DO UPDATE "
                "SET ultimo_uso_en = CURRENT_TIMESTAMP, estado = 'ACTIVA', "
                "    refresh_token_hash = EXCLUDED.refresh_token_hash, "
                "    refresh_token_anterior_hash = NULL, rotada_en = CURRENT_TIMESTAMP"
            ),
            {
                "uid": usuario_id,
                "sid": supabase_session_id,
                "dispositivo": dispositivo_info,
                "ip": ip_origen,
                "hash": refresh_token_hash,
            },
        )

    def bloquear_para_rotacion(self, supabase_session_id: str) -> dict | None:
        """Lee la sesión con FOR UPDATE: dos renovaciones simultáneas de la misma sesión se
        serializan, así la segunda ya ve el token rotado por la primera (sin carreras)."""
        row = self.session.execute(
            text(
                "SELECT estado, refresh_token_hash, refresh_token_anterior_hash, "
                "       EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - rotada_en)), "
                "       EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - ultimo_uso_en)) "
                "FROM sesiones_activas WHERE supabase_session_id = :sid FOR UPDATE"
            ),
            {"sid": supabase_session_id},
        ).one_or_none()
        if row is None:
            return None
        return {
            "estado": row[0],
            "hash_actual": row[1],
            "hash_anterior": row[2],
            "segundos_desde_rotacion": float(row[3]) if row[3] is not None else None,
            "segundos_inactiva": float(row[4]) if row[4] is not None else 0.0,
        }

    def marcar_expirada(self, supabase_session_id: str) -> None:
        self.session.execute(
            text("UPDATE sesiones_activas SET estado = 'EXPIRADA' WHERE supabase_session_id = :sid"),
            {"sid": supabase_session_id},
        )

    def guardar_rotacion(self, supabase_session_id: str, hash_nuevo: str) -> None:
        """El token vigente pasa a ser `hash_nuevo` y el que había queda como anterior."""
        self.session.execute(
            text(
                "UPDATE sesiones_activas SET refresh_token_anterior_hash = refresh_token_hash, "
                "refresh_token_hash = :nuevo, rotada_en = CURRENT_TIMESTAMP, "
                "ultimo_uso_en = CURRENT_TIMESTAMP "
                "WHERE supabase_session_id = :sid"
            ),
            {"nuevo": hash_nuevo, "sid": supabase_session_id},
        )

    def tocar(self, supabase_session_id: str) -> None:
        self.session.execute(
            text(
                "UPDATE sesiones_activas SET ultimo_uso_en = CURRENT_TIMESTAMP "
                "WHERE supabase_session_id = :sid AND estado = 'ACTIVA'"
            ),
            {"sid": supabase_session_id},
        )

    def marcar_revocada(self, supabase_session_id: str) -> None:
        self.session.execute(
            text("UPDATE sesiones_activas SET estado = 'REVOCADA' WHERE supabase_session_id = :sid"),
            {"sid": supabase_session_id},
        )

    def marcar_todas_revocadas(self, usuario_id: str) -> None:
        self.session.execute(
            text(
                "UPDATE sesiones_activas SET estado = 'REVOCADA' "
                "WHERE usuario_id = :uid AND estado = 'ACTIVA'"
            ),
            {"uid": usuario_id},
        )

    def listar_activas(self, usuario_id: str) -> list[dict]:
        rows = self.session.execute(
            text(
                "SELECT sesion_id, dispositivo_info, ip_origen, creado_en, ultimo_uso_en, supabase_session_id "
                "FROM sesiones_activas WHERE usuario_id = :uid AND estado = 'ACTIVA' "
                "ORDER BY ultimo_uso_en DESC"
            ),
            {"uid": usuario_id},
        ).all()
        return [
            {
                "sesion_id": str(r[0]),
                "dispositivo_info": r[1],
                "ip_origen": r[2],
                "creado_en": r[3],
                "ultimo_uso_en": r[4],
                "supabase_session_id": r[5],
            }
            for r in rows
        ]

    def obtener(self, sesion_id: str) -> dict | None:
        row = self.session.execute(
            text(
                "SELECT sesion_id, usuario_id, supabase_session_id, estado "
                "FROM sesiones_activas WHERE sesion_id = :sid"
            ),
            {"sid": sesion_id},
        ).one_or_none()
        if row is None:
            return None
        return {
            "sesion_id": str(row[0]),
            "usuario_id": str(row[1]),
            "supabase_session_id": row[2],
            "estado": row[3],
        }
