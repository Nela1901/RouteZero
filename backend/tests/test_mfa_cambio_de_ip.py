"""Verificación del código TOTP cuando Supabase responde `mfa_ip_address_mismatch` (el desafío y la verificación salieron
por IPs distintas). Pruebas sin base de datos ni red: el cliente de Supabase y el repositorio se reemplazan por dobles."""

import httpx
import pytest
from fastapi import HTTPException

from src.auth import service_mfa, supabase_client
from src.auth.service_mfa import INTENTOS_ANTE_CAMBIO_DE_IP, ServicioMFA


class SesionFalsa:
    def execute(self, *args, **kwargs):
        return None


class RepoFalso:
    session = SesionFalsa()

    def __init__(self):
        self.fallidos = 0
        self.reseteos = 0

    def esta_bloqueado_mfa(self, usuario_id):
        return False

    def registrar_intento_mfa_fallido(self, usuario_id):
        self.fallidos += 1

    def resetear_intentos_mfa(self, usuario_id):
        self.reseteos += 1


def error_http(codigo_http: int, error_code: str | None) -> httpx.HTTPStatusError:
    peticion = httpx.Request("POST", "https://supabase.test/auth/v1/factors/x/verify")
    cuerpo = {"error_code": error_code} if error_code else None
    respuesta = httpx.Response(codigo_http, json=cuerpo, request=peticion) if cuerpo else httpx.Response(codigo_http, content=b"no es json", request=peticion)
    return httpx.HTTPStatusError("error", request=peticion, response=respuesta)


@pytest.fixture
def servicio(monkeypatch):
    repo = RepoFalso()
    monkeypatch.setattr(service_mfa, "RepositorioAuditoria", lambda session: type("A", (), {"registrar": lambda self, *a, **k: None})())
    monkeypatch.setattr(supabase_client, "mfa_challenge", lambda token, factor: {"id": "desafio"})
    return ServicioMFA(repo), repo


def verificar(servicio_mfa: ServicioMFA) -> dict:
    return servicio_mfa._verificar_codigo_totp("usuario", "token", "factor", "123456")


def test_si_la_ip_cambia_se_repite_la_verificacion_y_no_cuenta_como_fallo(servicio, monkeypatch):
    mfa, repo = servicio
    respuestas = [error_http(422, "mfa_ip_address_mismatch"), error_http(422, "mfa_ip_address_mismatch"), {"access_token": "ok"}]

    def verify(*args):
        r = respuestas.pop(0)
        if isinstance(r, Exception):
            raise r
        return r

    monkeypatch.setattr(supabase_client, "mfa_verify", verify)
    assert verificar(mfa) == {"access_token": "ok"}
    assert repo.fallidos == 0
    assert repo.reseteos == 1
    assert respuestas == []


def test_si_la_ip_sigue_cambiando_responde_503_sin_contar_un_intento_fallido(servicio, monkeypatch):
    mfa, repo = servicio
    llamadas = []

    def verify(*args):
        llamadas.append(1)
        raise error_http(422, "mfa_ip_address_mismatch")

    monkeypatch.setattr(supabase_client, "mfa_verify", verify)
    with pytest.raises(HTTPException) as e:
        verificar(mfa)
    assert e.value.status_code == 503
    assert len(llamadas) == INTENTOS_ANTE_CAMBIO_DE_IP
    assert repo.fallidos == 0


def test_un_codigo_invalido_sigue_contando_como_intento_fallido_y_no_se_reintenta(servicio, monkeypatch):
    mfa, repo = servicio
    llamadas = []

    def verify(*args):
        llamadas.append(1)
        raise error_http(422, "mfa_verification_failed")

    monkeypatch.setattr(supabase_client, "mfa_verify", verify)
    with pytest.raises(HTTPException) as e:
        verificar(mfa)
    assert e.value.status_code == 400
    assert len(llamadas) == 1
    assert repo.fallidos == 1


def test_una_respuesta_que_no_es_json_se_trata_como_codigo_invalido(servicio, monkeypatch):
    mfa, repo = servicio

    def verify(*args):
        raise error_http(500, None)

    monkeypatch.setattr(supabase_client, "mfa_verify", verify)
    with pytest.raises(HTTPException) as e:
        verificar(mfa)
    assert e.value.status_code == 400
    assert repo.fallidos == 1
