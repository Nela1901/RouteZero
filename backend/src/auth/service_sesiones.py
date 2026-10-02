import hashlib

import httpx
from fastapi import HTTPException, status

from src.auditoria.repository import RepositorioAuditoria
from src.auth import supabase_client
from src.auth.politicas import DIAS_VIGENCIA_REFRESH, VENTANA_GRACIA_SEGUNDOS
from src.auth.repository import RepositorioSesiones, RepositorioUsuarios
from src.auth.service_mfa import ServicioMFA
from src.core.security import UsuarioActual, decodificar_token

MAX_DISPOSITIVO_INFO = 300


def _hash_token(token: str) -> str:
    """Solo se guarda el hash del refresh token, nunca el token: una fuga de la base de
    datos no entrega tokens utilizables."""
    return hashlib.sha256(token.encode()).hexdigest()


def _tokens(sesion: dict) -> dict:
    return {
        "estado": "ok",
        "access_token": sesion["access_token"],
        "refresh_token": sesion["refresh_token"],
        "expires_in": sesion.get("expires_in"),
    }


def _codigo_error_supabase(exc: httpx.HTTPStatusError) -> str:
    try:
        cuerpo = exc.response.json()
    except ValueError:
        return ""
    return cuerpo.get("error_code") or cuerpo.get("code") or ""


class ServicioSesiones:
    def __init__(self, usuarios: RepositorioUsuarios, sesiones: RepositorioSesiones):
        self.usuarios = usuarios
        self.sesiones = sesiones
        self.auditoria = RepositorioAuditoria(usuarios.session)

    def _registrar_sesion(self, usuario_id: str, sesion: dict, dispositivo: str | None, ip: str | None) -> None:
        session_id = decodificar_token(sesion["access_token"]).get("session_id")
        if session_id:
            self.sesiones.registrar(
                usuario_id,
                session_id,
                (dispositivo or "")[:MAX_DISPOSITIVO_INFO] or None,
                ip,
                _hash_token(sesion["refresh_token"]),
            )

    def login(self, email: str, password: str, dispositivo: str | None, ip: str | None) -> dict:
        usuario_id = self.usuarios.usuario_id_por_email(email)
        tiene_perfil = False
        if usuario_id:
            self.usuarios.fijar_contexto_rls(usuario_id)
            tiene_perfil = self.usuarios.existe_perfil(usuario_id)

        if tiene_perfil:
            segundos = self.usuarios.segundos_bloqueo_login(usuario_id)
            if segundos > 0:
                raise HTTPException(
                    status.HTTP_429_TOO_MANY_REQUESTS,
                    f"Cuenta bloqueada por intentos fallidos. Intenta de nuevo en {segundos} segundos",
                )

        try:
            sesion = supabase_client.login_password(email, password)
        except httpx.HTTPStatusError as exc:
            if tiene_perfil:
                self.usuarios.registrar_intento_login_fallido(usuario_id)
                self.auditoria.registrar(usuario_id, "login_fallido", "auth", ip_origen=ip)
            # Mismo mensaje exista o no el correo, para no revelar qué cuentas existen.
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Credenciales inválidas") from exc

        if not tiene_perfil:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Usuario sin perfil registrado en RouteZero")

        self.usuarios.resetear_intentos_login(usuario_id)

        if self.usuarios.obtener_estado_mfa(usuario_id)["mfa_activo"]:
            # Supabase entrega una sesión aal1 tras la contraseña; el middleware no la acepta
            # como sesión completa mientras el usuario tenga MFA. Sirve solo para el paso TOTP.
            datos = supabase_client.obtener_usuario(sesion["access_token"])
            factor = next(
                (f for f in datos.get("factors", []) if f.get("status") == "verified"),
                None,
            )
            if factor is None:
                raise HTTPException(status.HTTP_409_CONFLICT, "MFA activo sin un factor verificado")
            self.auditoria.registrar(usuario_id, "login_password_ok_pendiente_mfa", "auth", ip_origen=ip)
            return {
                "estado": "mfa_required",
                "mfa_token": sesion["access_token"],
                "factor_id": factor["id"],
            }

        self._registrar_sesion(usuario_id, sesion, dispositivo, ip)
        self.auditoria.registrar(usuario_id, "login_exitoso", "auth", ip_origen=ip)
        return _tokens(sesion)

    def completar_login_mfa(
        self,
        usuario: UsuarioActual,
        mfa_token: str,
        factor_id: str,
        codigo: str,
        dispositivo: str | None,
        ip: str | None,
    ) -> dict:
        if not usuario.mfa_activo:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Esta cuenta no tiene MFA activo")
        sesion = ServicioMFA(self.usuarios).verificar_login(usuario.usuario_id, mfa_token, factor_id, codigo)
        self._registrar_sesion(usuario.usuario_id, sesion, dispositivo, ip)
        self.auditoria.registrar(usuario.usuario_id, "login_exitoso", "auth", detalle="via MFA", ip_origen=ip)
        return _tokens(sesion)

    def renovar(self, access_token_vencido: str, refresh_token: str) -> dict:
        # La firma se verifica, pero se tolera que el access token ya haya vencido: solo sirve
        # para saber a qué cuenta y sesión corresponde este intento de renovación.
        payload = decodificar_token(access_token_vencido, verificar_exp=False)
        usuario_id = payload.get("sub")
        if not usuario_id:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token sin usuario asociado")
        session_id = payload.get("session_id", "")
        self.usuarios.fijar_contexto_rls(usuario_id)

        # La sesión queda bloqueada (FOR UPDATE) hasta el final de la petición, así dos
        # renovaciones simultáneas con el mismo token se serializan sin carreras.
        fila = self.sesiones.bloquear_para_rotacion(session_id)
        if fila is None or fila["estado"] != "ACTIVA":
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, "Sesión no registrada o revocada, inicia sesión de nuevo"
            )

        if fila["segundos_inactiva"] > DIAS_VIGENCIA_REFRESH * 86400:
            self.sesiones.marcar_expirada(session_id)
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, "Sesión expirada por inactividad, inicia sesión de nuevo"
            )

        # La detección de reuso la hacemos nosotros: Supabase acepta refresh tokens ya rotados
        # (comprobado en este proyecto, aun con "detect and revoke compromised tokens" activo).
        hash_presentado = _hash_token(refresh_token)
        if fila["hash_actual"] is not None and hash_presentado != fila["hash_actual"]:
            segundos = fila["segundos_desde_rotacion"]
            es_anterior = hash_presentado == fila["hash_anterior"]
            if es_anterior and segundos is not None and segundos <= VENTANA_GRACIA_SEGUNDOS:
                pass  # reintento legítimo dentro de la ventana de gracia: no se penaliza
            elif es_anterior:
                # El token anterior se usa pasada la ventana: alguien conserva un token que el
                # dueño ya rotó. Se revoca la sesión y se invalidan los access tokens vigentes.
                self.sesiones.marcar_revocada(session_id)
                self.usuarios.incrementar_token_version(usuario_id)
                self.auditoria.registrar(usuario_id, "robo_sesion_detectado", "auth", detalle=f"sesion {session_id}")
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED,
                    "Token de refresco reutilizado: sesión revocada por seguridad",
                )
            else:
                # Token desconocido (o demasiado antiguo): se rechaza sin tocar la sesión, para
                # que enviar basura no permita cerrar la sesión de otra persona.
                raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token de refresco inválido o revocado")

        try:
            sesion = supabase_client.refrescar_sesion(refresh_token)
        except httpx.HTTPStatusError as exc:
            if _codigo_error_supabase(exc) in ("refresh_token_not_found", "session_not_found"):
                self.sesiones.marcar_revocada(session_id)
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, "Token de refresco inválido o revocado"
            ) from exc

        nuevo = decodificar_token(sesion["access_token"])
        self.usuarios.fijar_contexto_rls(nuevo["sub"])
        hash_nuevo = _hash_token(sesion["refresh_token"])
        if hash_nuevo != fila["hash_actual"]:
            self.sesiones.guardar_rotacion(session_id, hash_nuevo)
        else:
            self.sesiones.tocar(session_id)  # reintento en gracia: Supabase devolvió el vigente
        return _tokens(sesion)

    def listar_propias(self, usuario: UsuarioActual) -> list[dict]:
        sesiones = self.sesiones.listar_activas(usuario.usuario_id)
        for s in sesiones:
            # El identificador interno de Supabase no se expone al cliente.
            s["actual"] = s.pop("supabase_session_id") == usuario.session_id
        return sesiones

    def revocar(self, usuario: UsuarioActual, access_token: str, sesion_id: str) -> None:
        sesion = self.sesiones.obtener(sesion_id)
        # RLS solo deja ver las sesiones propias: una ajena se ve igual que una inexistente.
        if sesion is None or sesion["usuario_id"] != usuario.usuario_id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Sesión no encontrada")

        if sesion["supabase_session_id"] == usuario.session_id:
            try:
                supabase_client.cerrar_sesion(access_token, "local")
            except httpx.HTTPStatusError as exc:
                raise HTTPException(status.HTTP_502_BAD_GATEWAY, "No se pudo cerrar la sesión") from exc
        # Para las sesiones de otros dispositivos no hay forma de invalidarlas una a una en
        # Supabase con un cliente normal; basta con marcarlas REVOCADA aquí: el middleware exige
        # una sesión ACTIVA y `renovar` la rechaza, así que sus tokens no sirven contra la API.
        self.sesiones.marcar_revocada(sesion["supabase_session_id"])
        self.auditoria.registrar(usuario.usuario_id, "sesion_revocada", "auth", detalle=f"sesion {sesion_id}")

    def revocar_todas(self, usuario: UsuarioActual, access_token: str) -> None:
        try:
            supabase_client.cerrar_sesion(access_token, "global")
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status.HTTP_502_BAD_GATEWAY, "No se pudieron cerrar las sesiones") from exc
        self.sesiones.marcar_todas_revocadas(usuario.usuario_id)
        # Invalida de inmediato los access tokens ya emitidos, sin esperar a que venzan.
        self.usuarios.incrementar_token_version(usuario.usuario_id)
        self.auditoria.registrar(usuario.usuario_id, "todas_sesiones_revocadas", "auth")
