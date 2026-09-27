"""Cliente delgado para la API de Auth de Supabase (login, MFA).

Todas las funciones reenvían el token del propio usuario (patrón `anon key`),
salvo que se indique lo contrario. El backend nunca expone estas llamadas
directamente al frontend, siempre actúa como intermediario.
"""

import httpx

from src.core.config import settings


def _headers(access_token: str) -> dict:
    return {
        "apikey": settings.supabase_anon_key,
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }


def login_password(email: str, password: str) -> dict:
    resp = httpx.post(
        f"{settings.supabase_url}/auth/v1/token?grant_type=password",
        headers={"apikey": settings.supabase_anon_key, "Content-Type": "application/json"},
        json={"email": email, "password": password},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def refrescar_sesion(refresh_token: str) -> dict:
    resp = httpx.post(
        f"{settings.supabase_url}/auth/v1/token?grant_type=refresh_token",
        headers={"apikey": settings.supabase_anon_key, "Content-Type": "application/json"},
        json={"refresh_token": refresh_token},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def obtener_usuario(access_token: str) -> dict:
    resp = httpx.get(
        f"{settings.supabase_url}/auth/v1/user",
        headers=_headers(access_token),
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def cerrar_sesion(access_token: str, scope: str) -> None:
    """scope: 'local' (esta sesión), 'global' (todas) u 'others' (todas menos esta)."""
    resp = httpx.post(
        f"{settings.supabase_url}/auth/v1/logout?scope={scope}",
        headers=_headers(access_token),
        timeout=10,
    )
    resp.raise_for_status()


def mfa_enroll(access_token: str) -> dict:
    resp = httpx.post(
        f"{settings.supabase_url}/auth/v1/factors",
        headers=_headers(access_token),
        json={"factor_type": "totp"},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def mfa_challenge(access_token: str, factor_id: str) -> dict:
    resp = httpx.post(
        f"{settings.supabase_url}/auth/v1/factors/{factor_id}/challenge",
        headers=_headers(access_token),
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def mfa_verify(access_token: str, factor_id: str, challenge_id: str, codigo: str) -> dict:
    resp = httpx.post(
        f"{settings.supabase_url}/auth/v1/factors/{factor_id}/verify",
        headers=_headers(access_token),
        json={"challenge_id": challenge_id, "code": codigo},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def mfa_unenroll(access_token: str, factor_id: str) -> None:
    resp = httpx.request(
        "DELETE",
        f"{settings.supabase_url}/auth/v1/factors/{factor_id}",
        headers=_headers(access_token),
        timeout=10,
    )
    resp.raise_for_status()
