"""HT-02 — cifrado en tránsito: confirma que la conexión a la base de datos va cifrada con
TLS, tanto de hecho (el servidor de Supabase ya lo exige) como por configuración propia
(`sslmode=require` en el engine, ver `src/core/database.py` y `src/auth/mantenimiento.py`):
si algún día se apunta a un host que no lo exija, la conexión debe fallar, no degradar en
silencio a texto plano. El cifrado en reposo (AES-256) es una garantía de la infraestructura
de Supabase, no verificable desde aquí — documentado en `design.md` de este cambio.
"""

import psycopg2

from src.core.config import settings


def test_la_conexion_a_la_base_de_datos_usa_tls():
    conn = psycopg2.connect(settings.database_url, connect_timeout=15)
    try:
        assert conn.info.ssl_in_use is True
        assert conn.info.ssl_attribute("protocol").startswith("TLSv1")
    finally:
        conn.close()


def test_el_engine_de_la_app_tambien_conecta_por_tls():
    """Usa el engine real de `src/core/database.py` (con su `connect_args={"sslmode":
    "require"}"), no una conexión armada a mano — así valida la configuración que el
    backend realmente usa en cada petición, no solo que el proveedor lo permita."""
    from src.core.database import engine

    conexion_cruda = engine.raw_connection()
    try:
        assert conexion_cruda.driver_connection.info.ssl_in_use is True
    finally:
        conexion_cruda.close()
