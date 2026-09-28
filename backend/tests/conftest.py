"""Fixtures y utilidades compartidas por la suite de pytest.

Son pruebas de integración reales: usan `TestClient` (mismo proceso, así `pytest-cov` sí
mide la cobertura del código) pero golpean la base de datos y Supabase Auth reales — el
mismo enfoque que ya se venía usando con los scripts de `tests_manual/`, solo que ahora en
un proceso que pytest puede instrumentar. Requieren el `.env` de la raíz del repo con
credenciales válidas y una cuenta de prueba creada a mano en Supabase (Authentication →
Users, "Auto Confirm User") con su fila correspondiente en `usuarios` (rol ADMINISTRADOR).
"""

import base64
import hashlib
import hmac
import struct
import time

import psycopg2
import pytest
from fastapi.testclient import TestClient

from src.core.config import settings
from src.main import app

EMAIL = "prueba@routezero.dev"
PASSWORD = "123456789"
UID = "444a2660-2006-4deb-9cee-61552721128e"


@pytest.fixture(scope="session")
def client() -> TestClient:
    return TestClient(app)


def totp(secret_b32: str, digits: int = 6, period: int = 30) -> str:
    """Genera un código TOTP válido a partir de un secreto, sin depender de una app externa."""
    secret_b32 = secret_b32.upper().replace(" ", "")
    padded = secret_b32 + "=" * ((8 - len(secret_b32) % 8) % 8)
    key = base64.b32decode(padded)
    counter = int(time.time() // period)
    msg = struct.pack(">Q", counter)
    h = hmac.new(key, msg, hashlib.sha1).digest()
    offset = h[-1] & 0x0F
    code = (struct.unpack(">I", h[offset : offset + 4])[0] & 0x7FFFFFFF) % (10**digits)
    return str(code).zfill(digits)


def esperar_siguiente_ventana_totp() -> None:
    """Espera al inicio de la siguiente ventana de 30 s, para no reutilizar un código ya usado."""
    time.sleep(30 - (time.time() % 30) + 1.5)


def db(sql: str, params: tuple | None = None, fetch: bool = False):
    """Ejecuta SQL directo contra la base (rol `app_backend`, respetando RLS vía la misma
    variable de sesión que fija el backend) para preparar o verificar estado de la prueba."""
    conn = psycopg2.connect(settings.database_url, connect_timeout=15)
    try:
        cur = conn.cursor()
        cur.execute("SELECT set_config('app.usuario_actual_id', %s, true)", (UID,))
        cur.execute(sql, params)
        fila = cur.fetchone() if fetch else None
        conn.commit()
        return fila
    finally:
        conn.close()


def reset_usuario_prueba() -> None:
    """Deja a la cuenta de prueba en un estado conocido: sin sesiones, sin bloqueos, sin MFA."""
    db("DELETE FROM sesiones_activas WHERE usuario_id=%s", (UID,))
    db(
        "UPDATE usuarios SET intentos_fallidos=0, bloqueado_hasta=NULL, mfa_intentos_fallidos=0, "
        "mfa_bloqueado_hasta=NULL, token_version=1, mfa_activo=FALSE WHERE usuario_id=%s",
        (UID,),
    )


def login(client: TestClient, ua: str = "Dev-A", password: str = PASSWORD, email: str = EMAIL):
    return client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
        headers={"User-Agent": ua},
    )


def auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def get(client: TestClient, ruta: str, token: str):
    return client.get(ruta, headers=auth(token))


@pytest.fixture(autouse=True, scope="session")
def _verificar_credenciales_de_prueba():
    if not settings.database_url:
        pytest.skip("Falta DATABASE_URL en el .env")
