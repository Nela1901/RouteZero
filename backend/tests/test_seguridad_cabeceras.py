"""OWASP A02 y A10: cabeceras de seguridad, CORS con los métodos que usa el frontend y respuestas 503 claras cuando
Supabase o la base de datos no responden."""

import asyncio

import httpx
import pytest
from sqlalchemy.exc import OperationalError

from src.auth import supabase_client
from src.core.config import settings
from src.main import base_de_datos_no_disponible, servicio_externo_no_responde

RUTA_ENTREGA = "/api/rutas/00000000-0000-0000-0000-000000000000/paradas/00000000-0000-0000-0000-000000000000/entrega"


def test_toda_respuesta_lleva_las_cabeceras_de_seguridad(client):
    for ruta in ("/api/health", "/api/no-existe"):
        r = client.get(ruta)
        assert r.headers["x-content-type-options"] == "nosniff"
        assert r.headers["x-frame-options"] == "DENY"
        assert r.headers["referrer-policy"] == "no-referrer"
        assert r.headers["cache-control"] == "no-store"


@pytest.mark.parametrize("metodo", ["GET", "POST", "PUT", "PATCH", "DELETE"])
def test_cors_permite_los_metodos_que_usa_el_frontend(client, metodo):
    """Sin PATCH el navegador rechazaba el permiso previo de registrar una entrega (HU-014) y la acción fallaba en producción."""
    r = client.options(
        RUTA_ENTREGA,
        headers={"Origin": settings.frontend_origin, "Access-Control-Request-Method": metodo, "Access-Control-Request-Headers": "authorization,content-type"},
    )
    assert r.status_code == 200
    assert metodo in r.headers["access-control-allow-methods"]
    assert r.headers["access-control-allow-origin"] == settings.frontend_origin


def test_cors_rechaza_otros_origenes_y_no_usa_comodin(client):
    r = client.options(RUTA_ENTREGA, headers={"Origin": "https://sitio-ajeno.test", "Access-Control-Request-Method": "GET"})
    assert r.status_code == 400
    assert r.headers.get("access-control-allow-origin") != "*"
    assert "access-control-allow-credentials" not in r.headers


def test_si_supabase_no_responde_el_login_contesta_503(client, monkeypatch):
    def sin_red(*args, **kwargs):
        raise httpx.ConnectError("sin conexión con Supabase")

    monkeypatch.setattr(supabase_client, "login_password", sin_red)
    r = client.post("/api/auth/login", json={"email": "prueba@routezero.dev", "password": "123456789"})
    assert r.status_code == 503
    assert "servicio externo" in r.json()["detail"]
    assert "Supabase" not in r.json()["detail"]


def test_si_la_base_de_datos_cae_responde_503_sin_detalles_de_conexion():
    error = OperationalError("SELECT 1", {}, Exception("password authentication failed for user app_backend host=db.interno"))
    respuesta = asyncio.run(base_de_datos_no_disponible(None, error))
    assert respuesta.status_code == 503
    cuerpo = respuesta.body.decode()
    assert "base de datos" in cuerpo
    assert "app_backend" not in cuerpo
    assert "db.interno" not in cuerpo


def test_un_error_de_red_con_el_servicio_externo_se_traduce_a_503():
    respuesta = asyncio.run(servicio_externo_no_responde(None, httpx.ReadTimeout("tiempo agotado")))
    assert respuesta.status_code == 503
