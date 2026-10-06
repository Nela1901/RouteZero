"""Suite del módulo de pedidos (HT-05): clientes, zona de cobertura (RN-007), registro,
listado filtrado y cancelación (HU-008). Portada de `tests_manual/e2e_pedidos.py`.
"""

import uuid

from conftest import EMAIL_OPERADOR, PASSWORD_OPERADOR, admin_db, auth, login

estado: dict = {}


def test_login_administrador_y_operador(client):
    r = login(client, "Dev-Pedidos")
    assert r.status_code == 200
    estado["tok_admin"] = r.json()["access_token"]

    r = login(client, "Dev-Pedidos-Op", email=EMAIL_OPERADOR, password=PASSWORD_OPERADOR)
    assert r.status_code == 200
    estado["tok_operador"] = r.json()["access_token"]


def test_registrar_cliente_dentro_de_la_zona(client):
    r = client.post(
        "/api/clientes",
        headers=auth(estado["tok_operador"]),
        json={
            "nombre": f"Bodega Los Andes {uuid.uuid4().hex[:6]}",
            "tipo_negocio": "BODEGA",
            "referencia": "Frente al Mercado Modelo, Huancayo",
            "latitud": "-12.0653",
            "longitud": "-75.2049",
        },
    )
    assert r.status_code == 201
    cuerpo = r.json()
    estado["cliente_id"] = cuerpo["cliente_id"]
    # HU-007: el punto de referencia queda cubierto por diseño, como texto libre.
    assert cuerpo["referencia"] == "Frente al Mercado Modelo, Huancayo"


def test_registrar_cliente_fuera_de_la_zona_da_422(client):
    r = client.post(
        "/api/clientes",
        headers=auth(estado["tok_operador"]),
        json={
            "nombre": "Cliente en Lima",
            "tipo_negocio": "COMERCIO",
            "latitud": "-12.0464",
            "longitud": "-77.0428",  # Lima, fuera de Huancayo
        },
    )
    assert r.status_code == 422


def test_registrar_pedido_dentro_de_la_zona(client):
    r = client.post(
        "/api/pedidos",
        headers=auth(estado["tok_operador"]),
        json={
            "cliente_id": estado["cliente_id"],
            "peso_kg": "25.50",
            "prioridad": "EXPRESS",
            "latitud": "-12.0600",
            "longitud": "-75.2100",
            "ventana_inicio": "08:00:00",
            "ventana_fin": "12:00:00",
        },
    )
    assert r.status_code == 201
    cuerpo = r.json()
    estado["pedido_id"] = cuerpo["pedido_id"]
    assert cuerpo["estado"] == "PENDIENTE"


def test_registrar_pedido_fuera_de_la_zona_da_422(client):
    r = client.post(
        "/api/pedidos",
        headers=auth(estado["tok_operador"]),
        json={
            "cliente_id": estado["cliente_id"],
            "peso_kg": "10.00",
            "latitud": "-12.0464",
            "longitud": "-77.0428",
            "ventana_inicio": "08:00:00",
            "ventana_fin": "12:00:00",
        },
    )
    assert r.status_code == 422


def test_registrar_pedido_con_cliente_inexistente_da_404(client):
    r = client.post(
        "/api/pedidos",
        headers=auth(estado["tok_operador"]),
        json={
            "cliente_id": str(uuid.uuid4()),
            "peso_kg": "10.00",
            "latitud": "-12.0600",
            "longitud": "-75.2100",
            "ventana_inicio": "08:00:00",
            "ventana_fin": "12:00:00",
        },
    )
    assert r.status_code == 404


def test_registrar_pedido_con_ventana_invertida_da_422(client):
    r = client.post(
        "/api/pedidos",
        headers=auth(estado["tok_operador"]),
        json={
            "cliente_id": estado["cliente_id"],
            "peso_kg": "10.00",
            "latitud": "-12.0600",
            "longitud": "-75.2100",
            "ventana_inicio": "12:00:00",
            "ventana_fin": "08:00:00",
        },
    )
    assert r.status_code == 422


def test_listar_filtrado_por_prioridad_express_incluye_el_pedido(client):
    r = client.get("/api/pedidos", headers=auth(estado["tok_operador"]), params={"prioridad": "EXPRESS"})
    assert r.status_code == 200
    assert estado["pedido_id"] in [p["pedido_id"] for p in r.json()]


def test_listar_filtrado_por_otra_prioridad_no_lo_incluye(client):
    r = client.get("/api/pedidos", headers=auth(estado["tok_operador"]), params={"prioridad": "ECONOMICO"})
    assert r.status_code == 200
    assert estado["pedido_id"] not in [p["pedido_id"] for p in r.json()]


def test_cancelar_pedido_pendiente(client):
    r = client.delete(f"/api/pedidos/{estado['pedido_id']}", headers=auth(estado["tok_operador"]))
    assert r.status_code == 200
    assert r.json()["estado"] == "CANCELADO"


def test_cancelar_pedido_ya_cancelado_da_409(client):
    r = client.delete(f"/api/pedidos/{estado['pedido_id']}", headers=auth(estado["tok_operador"]))
    assert r.status_code == 409


def test_cancelar_pedido_inexistente_da_404(client):
    r = client.delete(f"/api/pedidos/{uuid.uuid4()}", headers=auth(estado["tok_operador"]))
    assert r.status_code == 404


def test_administrador_tambien_puede_listar_pedidos(client):
    r = client.get("/api/pedidos", headers=auth(estado["tok_admin"]))
    assert r.status_code == 200


def test_registrar_pedido_sin_token_da_401(client):
    r = client.post(
        "/api/pedidos",
        json={
            "cliente_id": estado["cliente_id"],
            "peso_kg": "10.00",
            "latitud": "-12.0600",
            "longitud": "-75.2100",
            "ventana_inicio": "08:00:00",
            "ventana_fin": "12:00:00",
        },
    )
    assert r.status_code == 401


def test_limpieza(client):
    admin_db("DELETE FROM pedidos WHERE cliente_id = %s", (estado["cliente_id"],))
    admin_db("DELETE FROM clientes WHERE cliente_id = %s", (estado["cliente_id"],))
