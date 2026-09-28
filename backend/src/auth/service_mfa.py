import httpx
from fastapi import HTTPException, status

from src.auditoria.repository import RepositorioAuditoria
from src.auth import supabase_client
from src.auth.repository import RepositorioUsuarios


class ServicioMFA:
    def __init__(self, repo: RepositorioUsuarios):
        self.repo = repo
        self.auditoria = RepositorioAuditoria(repo.session)

    def iniciar_inscripcion(self, usuario_id: str, access_token: str) -> dict:
        estado = self.repo.obtener_estado_mfa(usuario_id)
        if estado["mfa_activo"]:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "El MFA ya está activo en esta cuenta; desactívalo antes de inscribir uno nuevo",
            )
        data = supabase_client.mfa_enroll(access_token)
        totp = data.get("totp", {})
        return {
            "factor_id": data["id"],
            "qr_code": totp.get("qr_code", ""),
            "secret": totp.get("secret", ""),
        }

    def _verificar_codigo_totp(self, usuario_id: str, access_token: str, factor_id: str, codigo: str) -> dict:
        """Verifica el código con Supabase y devuelve su respuesta (una sesión aal2 con tokens nuevos)."""
        if self.repo.esta_bloqueado_mfa(usuario_id):
            raise HTTPException(
                status.HTTP_429_TOO_MANY_REQUESTS,
                "Verificación de MFA bloqueada temporalmente por intentos fallidos",
            )
        try:
            challenge = supabase_client.mfa_challenge(access_token, factor_id)
            sesion = supabase_client.mfa_verify(access_token, factor_id, challenge["id"], codigo)
        except httpx.HTTPStatusError as exc:
            self.repo.registrar_intento_mfa_fallido(usuario_id)
            self.auditoria.registrar(usuario_id, "mfa_codigo_invalido", "auth")
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Código TOTP inválido") from exc
        self.repo.resetear_intentos_mfa(usuario_id)
        return sesion

    def verificar_login(self, usuario_id: str, access_token: str, factor_id: str, codigo: str) -> dict:
        return self._verificar_codigo_totp(usuario_id, access_token, factor_id, codigo)

    def confirmar_inscripcion(self, usuario_id: str, access_token: str, factor_id: str, codigo: str) -> None:
        self._verificar_codigo_totp(usuario_id, access_token, factor_id, codigo)
        self.repo.activar_mfa(usuario_id)
        self.auditoria.registrar(usuario_id, "mfa_activado", "auth")

    def desactivar(
        self,
        usuario_id: str,
        email: str,
        access_token: str,
        factor_id: str,
        password: str,
        codigo: str,
    ) -> None:
        try:
            supabase_client.login_password(email, password)
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Contraseña incorrecta") from exc

        self._verificar_codigo_totp(usuario_id, access_token, factor_id, codigo)

        try:
            supabase_client.mfa_unenroll(access_token, factor_id)
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "No se pudo desactivar el MFA") from exc

        self.repo.desactivar_mfa(usuario_id)
        self.auditoria.registrar(usuario_id, "mfa_desactivado", "auth")
