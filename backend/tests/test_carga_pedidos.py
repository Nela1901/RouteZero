"""Prueba de carga (HT-08, spec `api-scalability`): con 1,000 pedidos en la base de datos, el percentil 95 de
las operaciones de consulta, registro y cancelación debe ser de 2 segundos o menos.

Se ejecuta aparte de la suite normal:  pytest tests/test_carga_pedidos.py -m carga -s --no-cov

Inserta 1,000 pedidos de un cliente propio de la prueba y los borra al terminar. Mide la API completa
(autenticación, sesión de base de datos y consulta) contra la base de datos real, así que el resultado
incluye la latencia de red hacia Supabase.
"""

import time
import uuid

import numpy as np
import psycopg2
import pytest
from conftest import admin_db, auth, login

from src.core.config import settings

TOTAL = 1000
LIMITE_S = 2.0
MUESTRAS = 30

pytestmark = pytest.mark.carga


@pytest.fixture(scope="module")
def mil_pedidos():
    cliente = str(admin_db(
        "INSERT INTO clientes (nombre, tipo_negocio, latitud, longitud) VALUES (%s, 'BODEGA', -12.0653, -75.2049) RETURNING cliente_id",
        (f"Cliente de carga {uuid.uuid4().hex[:6]}",), fetch=True,
    )[0][0])
    admin_db(
        "INSERT INTO pedidos (cliente_id, descripcion, peso_kg, prioridad, latitud, longitud, ventana_inicio, ventana_fin, estado, creado_en) "
        "SELECT %s, 'Pedido de carga', 10 + random() * 90, "
        "(ARRAY['EXPRESS','ESTANDAR','ECONOMICO'])[1 + floor(random() * 3)::int], "
        "-12.075 + random() * 0.045, -75.235 + random() * 0.045, '08:00', '18:00', "
        "(ARRAY['PENDIENTE','PENDIENTE','PENDIENTE','ASIGNADO','ENTREGADO'])[1 + floor(random() * 5)::int], "
        "now() - (random() * interval '30 days') FROM generate_series(1, %s)",
        (cliente, TOTAL),
    )
    yield cliente
    admin_db("DELETE FROM pedidos WHERE cliente_id = %s", (cliente,))
    admin_db("DELETE FROM clientes WHERE cliente_id = %s", (cliente,))


def percentil_95(tiempos: list) -> float:
    return float(np.percentile(tiempos, 95))


def test_el_listado_filtrado_usa_el_indice_compuesto(mil_pedidos):
    conn = psycopg2.connect(settings.database_url, connect_timeout=15)
    try:
        cur = conn.cursor()
        consulta = (
            "EXPLAIN (ANALYZE, BUFFERS OFF, TIMING OFF) SELECT pedido_id FROM pedidos WHERE estado = 'PENDIENTE' "
            "ORDER BY creado_en DESC, pedido_id LIMIT 50"
        )
        cur.execute(consulta)
        normal = "\n".join(f[0] for f in cur.fetchall())
        cur.execute("SET enable_seqscan = off")
        cur.execute(consulta)
        con_indice = "\n".join(f[0] for f in cur.fetchall())
    finally:
        conn.close()
    print("\n  Plan elegido por el planificador:\n   " + normal.replace("\n", "\n   "))
    print("\n  Plan con el recorrido secuencial desactivado:\n   " + con_indice.replace("\n", "\n   "))
    # Con solo 1,000 filas el planificador puede preferir leer la tabla completa (es igual de rápido);
    # lo que se comprueba es que el índice compuesto existe y puede servir para este listado.
    assert "idx_pedidos_estado_creado" in con_indice or "idx_pedidos_estado_creado" in normal


def test_percentil_95_de_consulta_registro_y_cancelacion_con_mil_pedidos(client, mil_pedidos):
    token = login(client, "Dev-Carga").json()["access_token"]
    total = client.get("/api/pedidos", headers=auth(token)).json()["total"]
    assert total >= TOTAL

    consultas, registros, cancelaciones, creados = [], [], [], []
    for _ in range(MUESTRAS):
        inicio = time.perf_counter()
        r = client.get("/api/pedidos", headers=auth(token), params={"estado": "PENDIENTE"})
        consultas.append(time.perf_counter() - inicio)
        assert r.status_code == 200 and len(r.json()["items"]) == 50

    for _ in range(15):
        inicio = time.perf_counter()
        r = client.post(
            "/api/pedidos",
            headers=auth(token),
            json={"cliente_id": mil_pedidos, "peso_kg": "25.00", "latitud": "-12.0600", "longitud": "-75.2100",
                  "ventana_inicio": "08:00:00", "ventana_fin": "12:00:00"},
        )
        registros.append(time.perf_counter() - inicio)
        assert r.status_code == 201
        creados.append(r.json()["pedido_id"])

    for pedido_id in creados:
        inicio = time.perf_counter()
        r = client.delete(f"/api/pedidos/{pedido_id}", headers=auth(token))
        cancelaciones.append(time.perf_counter() - inicio)
        assert r.status_code == 200

    resumen = {"consulta (página de 50)": consultas, "registro": registros, "cancelación": cancelaciones}
    print(f"\n  Con {total} pedidos en la base de datos (límite del percentil 95: {LIMITE_S:.0f} s):")
    for nombre, tiempos in resumen.items():
        print(f"   {nombre:24s} mediana {np.median(tiempos):.2f} s | p95 {percentil_95(tiempos):.2f} s | máximo {max(tiempos):.2f} s ({len(tiempos)} muestras)")
    for nombre, tiempos in resumen.items():
        assert percentil_95(tiempos) <= LIMITE_S, nombre
