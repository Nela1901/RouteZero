"""CRUD completo de flota, conductores, clientes y pedidos: detalle por id, edición completa y
eliminación con sus reglas (409 si el registro tiene datos relacionados, 404 si no existe,
403 según el rol).
"""

import random
import string
import uuid
from datetime import date, timedelta

from conftest import EMAIL_OPERADOR, PASSWORD_OPERADOR, admin_db, auth, login

estado: dict = {"vehiculos": [], "conductores": [], "clientes": [], "pedidos": [], "rutas": []}
INEXISTENTE = "00000000-0000-4000-8000-000000000000"


def _placa() -> str:
    return f"C{uuid.uuid4().hex[:6].upper()}"


def _dni() -> str:
    return "9" + "".join(random.choice("0123456789") for _ in range(7))


def _nombre(prefijo: str) -> str:
    return f"{prefijo} {uuid.uuid4().hex[:6]}"


def _crear_vehiculo(client) -> dict:
    r = client.post(
        "/api/vehiculos",
        headers=auth(estado["tok_admin"]),
        json={
            "placa": _placa(),
            "tipo": "CAMIONETA",
            "capacidad_kg": "900.00",
            "consumo_km_l": "9.50",
            "factor_emision_co2": "2.3100",
            "anio_fabricacion": 2021,
        },
    )
    assert r.status_code == 201
    estado["vehiculos"].append(r.json()["vehiculo_id"])
    return r.json()


def _crear_conductor(client) -> dict:
    r = client.post(
        "/api/conductores",
        headers=auth(estado["tok_admin"]),
        json={
            "nombre": "Conductor " + "".join(random.choices(string.ascii_lowercase, k=6)),
            "dni": _dni(),
            "categoria_licencia": "A-IIb",
            "telefono": "964000000",
            "licencia_vence": str(date.today() + timedelta(days=400)),
            "consentimiento_datos": True,
        },
    )
    assert r.status_code == 201
    estado["conductores"].append(r.json()["conductor_id"])
    return r.json()


def _crear_cliente(client) -> dict:
    r = client.post(
        "/api/clientes",
        headers=auth(estado["tok_operador"]),
        json={
            "nombre": _nombre("Cliente CRUD"),
            "tipo_negocio": "BODEGA",
            "latitud": "-12.0653",
            "longitud": "-75.2049",
            "horario_inicio": "07:00:00",
            "horario_fin": "18:00:00",
        },
    )
    assert r.status_code == 201
    estado["clientes"].append(r.json()["cliente_id"])
    return r.json()


def _crear_pedido(client, cliente_id: str) -> dict:
    r = client.post(
        "/api/pedidos",
        headers=auth(estado["tok_operador"]),
        json={
            "cliente_id": cliente_id,
            "descripcion": "Pedido de prueba CRUD",
            "peso_kg": "40.00",
            "prioridad": "ESTANDAR",
            "latitud": "-12.0653",
            "longitud": "-75.2049",
            "ventana_inicio": "08:00:00",
            "ventana_fin": "12:00:00",
        },
    )
    assert r.status_code == 201
    estado["pedidos"].append(r.json()["pedido_id"])
    return r.json()


def _ruta_para(vehiculo_id: str, conductor_id: str) -> str:
    fila = admin_db(
        "INSERT INTO rutas (lote_id, vehiculo_id, conductor_id, fecha_jornada) "
        "VALUES (gen_random_uuid(), %s, %s, CURRENT_DATE) RETURNING ruta_id",
        (vehiculo_id, conductor_id),
        fetch=True,
    )
    estado["rutas"].append(str(fila[0][0]))
    return str(fila[0][0])


def test_logins(client):
    r = login(client, "Dev-Crud-Admin")
    assert r.status_code == 200
    estado["tok_admin"] = r.json()["access_token"]
    r = login(client, "Dev-Crud-Op", email=EMAIL_OPERADOR, password=PASSWORD_OPERADOR)
    assert r.status_code == 200
    estado["tok_operador"] = r.json()["access_token"]


# ---------- Flota ----------


def test_vehiculo_detalle_y_edicion_completa(client):
    v = _crear_vehiculo(client)
    r = client.get(f"/api/vehiculos/{v['vehiculo_id']}", headers=auth(estado["tok_admin"]))
    assert r.status_code == 200
    assert r.json()["placa"] == v["placa"]

    nueva_placa = _placa()
    r = client.put(
        f"/api/vehiculos/{v['vehiculo_id']}",
        headers=auth(estado["tok_admin"]),
        json={"placa": nueva_placa, "capacidad_kg": "1200.00", "tipo": "FURGON"},
    )
    assert r.status_code == 200
    assert r.json()["placa"] == nueva_placa
    assert r.json()["tipo"] == "FURGON"
    estado["vehiculo"] = r.json()


def test_vehiculo_placa_repetida_da_409_pero_la_propia_se_acepta(client):
    otro = _crear_vehiculo(client)
    r = client.put(
        f"/api/vehiculos/{otro['vehiculo_id']}",
        headers=auth(estado["tok_admin"]),
        json={"placa": estado["vehiculo"]["placa"]},
    )
    assert r.status_code == 409
    r = client.put(
        f"/api/vehiculos/{otro['vehiculo_id']}", headers=auth(estado["tok_admin"]), json={"placa": otro["placa"]}
    )
    assert r.status_code == 200


def test_vehiculo_inexistente_da_404_y_id_invalido_422(client):
    assert client.get(f"/api/vehiculos/{INEXISTENTE}", headers=auth(estado["tok_admin"])).status_code == 404
    assert client.delete(f"/api/vehiculos/{INEXISTENTE}", headers=auth(estado["tok_admin"])).status_code == 404
    assert client.get("/api/vehiculos/no-es-uuid", headers=auth(estado["tok_admin"])).status_code == 422


def test_vehiculo_con_rutas_no_se_elimina(client):
    v = estado["vehiculo"]
    c = _crear_conductor(client)
    _ruta_para(v["vehiculo_id"], c["conductor_id"])
    r = client.delete(f"/api/vehiculos/{v['vehiculo_id']}", headers=auth(estado["tok_admin"]))
    assert r.status_code == 409
    assert "rutas" in r.json()["detail"]
    estado["conductor_con_ruta"] = c


def test_vehiculo_sin_rutas_se_elimina(client):
    libre = _crear_vehiculo(client)
    r = client.delete(f"/api/vehiculos/{libre['vehiculo_id']}", headers=auth(estado["tok_admin"]))
    assert r.status_code == 204
    assert client.get(f"/api/vehiculos/{libre['vehiculo_id']}", headers=auth(estado["tok_admin"])).status_code == 404


def test_operador_no_ve_ni_edita_ni_elimina_vehiculos(client):
    v = estado["vehiculo"]["vehiculo_id"]
    tok = estado["tok_operador"]
    assert client.get(f"/api/vehiculos/{v}", headers=auth(tok)).status_code == 403
    assert client.put(f"/api/vehiculos/{v}", headers=auth(tok), json={"capacidad_kg": "1.00"}).status_code == 403
    assert client.delete(f"/api/vehiculos/{v}", headers=auth(tok)).status_code == 403


# ---------- Conductores ----------


def test_conductor_detalle_y_edicion_de_nombre_y_dni(client):
    c = _crear_conductor(client)
    r = client.get(f"/api/conductores/{c['conductor_id']}", headers=auth(estado["tok_admin"]))
    assert r.status_code == 200
    assert r.json()["dni"] == c["dni"]

    nuevo_dni = _dni()
    r = client.put(
        f"/api/conductores/{c['conductor_id']}",
        headers=auth(estado["tok_admin"]),
        json={"nombre": "  Nombre Corregido  ", "dni": nuevo_dni},
    )
    assert r.status_code == 200
    assert r.json()["nombre"] == "Nombre Corregido"
    assert r.json()["dni"] == nuevo_dni
    estado["conductor"] = r.json()


def test_conductor_dni_repetido_da_409_y_campos_vacios_422(client):
    otro = _crear_conductor(client)
    r = client.put(
        f"/api/conductores/{otro['conductor_id']}",
        headers=auth(estado["tok_admin"]),
        json={"dni": estado["conductor"]["dni"]},
    )
    assert r.status_code == 409
    for cuerpo in ({"nombre": "   "}, {"dni": "123"}, {"nombre": None}, {"telefono": "12345"}, {"telefono": "9999999999"}):
        r = client.put(f"/api/conductores/{otro['conductor_id']}", headers=auth(estado["tok_admin"]), json=cuerpo)
        assert r.status_code == 422, cuerpo


def test_conductor_con_rutas_no_se_elimina_y_sin_rutas_si(client):
    r = client.delete(
        f"/api/conductores/{estado['conductor_con_ruta']['conductor_id']}", headers=auth(estado["tok_admin"])
    )
    assert r.status_code == 409

    libre = _crear_conductor(client)
    r = client.delete(f"/api/conductores/{libre['conductor_id']}", headers=auth(estado["tok_admin"]))
    assert r.status_code == 204
    assert client.get(f"/api/conductores/{libre['conductor_id']}", headers=auth(estado["tok_admin"])).status_code == 404

    filas = admin_db(
        "SELECT detalle FROM logs_auditoria WHERE accion = 'conductor_eliminado' AND detalle = %s",
        (libre["conductor_id"],),
        fetch=True,
    )
    assert len(filas) == 1
    assert libre["dni"] not in filas[0][0]


def test_conductor_inexistente_da_404(client):
    assert client.get(f"/api/conductores/{INEXISTENTE}", headers=auth(estado["tok_admin"])).status_code == 404
    assert client.delete(f"/api/conductores/{INEXISTENTE}", headers=auth(estado["tok_admin"])).status_code == 404


def test_operador_no_accede_al_detalle_de_conductores(client):
    c = estado["conductor"]["conductor_id"]
    tok = estado["tok_operador"]
    assert client.get(f"/api/conductores/{c}", headers=auth(tok)).status_code == 403
    assert client.delete(f"/api/conductores/{c}", headers=auth(tok)).status_code == 403


# ---------- Clientes ----------


def test_cliente_detalle_y_edicion(client):
    c = _crear_cliente(client)
    r = client.get(f"/api/clientes/{c['cliente_id']}", headers=auth(estado["tok_operador"]))
    assert r.status_code == 200

    nuevo = _nombre("Cliente Editado")
    r = client.put(
        f"/api/clientes/{c['cliente_id']}",
        headers=auth(estado["tok_operador"]),
        json={"nombre": nuevo, "tipo_negocio": "RESTAURANTE", "horario_inicio": "08:00:00", "referencia": "  Frente al parque  "},
    )
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["nombre"] == nuevo
    assert cuerpo["tipo_negocio"] == "RESTAURANTE"
    assert cuerpo["horario_inicio"].startswith("08:00")
    assert cuerpo["referencia"] == "Frente al parque"
    estado["cliente"] = cuerpo


def test_cliente_validaciones_al_editar(client):
    tok = estado["tok_operador"]
    cid = estado["cliente"]["cliente_id"]
    otro = _crear_cliente(client)

    r = client.put(f"/api/clientes/{otro['cliente_id']}", headers=auth(tok), json={"nombre": estado["cliente"]["nombre"].upper()})
    assert r.status_code == 409
    r = client.put(f"/api/clientes/{otro['cliente_id']}", headers=auth(tok), json={"nombre": otro["nombre"]})
    assert r.status_code == 200

    r = client.put(f"/api/clientes/{cid}", headers=auth(tok), json={"horario_fin": "06:00:00"})
    assert r.status_code == 422
    r = client.put(f"/api/clientes/{cid}", headers=auth(tok), json={"latitud": "-33.00000000", "longitud": "-70.00000000"})
    assert r.status_code == 422
    for cuerpo in ({"nombre": "   "}, {"tipo_negocio": "GIMNASIO"}, {"nombre": None}):
        assert client.put(f"/api/clientes/{cid}", headers=auth(tok), json=cuerpo).status_code == 422, cuerpo
    assert client.put(f"/api/clientes/{cid}", headers=auth(tok), json={}).status_code == 400


def test_cliente_con_pedidos_no_se_elimina_y_sin_pedidos_si(client):
    tok = estado["tok_operador"]
    con_pedido = estado["cliente"]
    pedido = _crear_pedido(client, con_pedido["cliente_id"])
    estado["pedido"] = pedido
    r = client.delete(f"/api/clientes/{con_pedido['cliente_id']}", headers=auth(tok))
    assert r.status_code == 409
    assert "pedidos" in r.json()["detail"]

    libre = _crear_cliente(client)
    assert client.delete(f"/api/clientes/{libre['cliente_id']}", headers=auth(tok)).status_code == 204
    assert client.get(f"/api/clientes/{libre['cliente_id']}", headers=auth(tok)).status_code == 404


def test_cliente_inexistente_da_404(client):
    tok = estado["tok_operador"]
    assert client.get(f"/api/clientes/{INEXISTENTE}", headers=auth(tok)).status_code == 404
    assert client.put(f"/api/clientes/{INEXISTENTE}", headers=auth(tok), json={"nombre": "X"}).status_code == 404
    assert client.delete(f"/api/clientes/{INEXISTENTE}", headers=auth(tok)).status_code == 404


# ---------- Pedidos ----------


def test_pedido_detalle_y_edicion_mientras_esta_pendiente(client):
    tok = estado["tok_operador"]
    pid = estado["pedido"]["pedido_id"]
    r = client.get(f"/api/pedidos/{pid}", headers=auth(tok))
    assert r.status_code == 200

    r = client.put(
        f"/api/pedidos/{pid}",
        headers=auth(tok),
        json={"peso_kg": "55.50", "prioridad": "EXPRESS", "descripcion": "Descripción corregida", "ventana_fin": "13:00:00"},
    )
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["peso_kg"] == "55.50"
    assert cuerpo["prioridad"] == "EXPRESS"
    assert cuerpo["ventana_fin"].startswith("13:00")


def test_pedido_validaciones_al_editar(client):
    tok = estado["tok_operador"]
    pid = estado["pedido"]["pedido_id"]
    assert client.put(f"/api/pedidos/{pid}", headers=auth(tok), json={"ventana_fin": "07:00:00"}).status_code == 422
    assert (
        client.put(f"/api/pedidos/{pid}", headers=auth(tok), json={"latitud": "-33.0", "longitud": "-70.0"}).status_code
        == 422
    )
    assert client.put(f"/api/pedidos/{pid}", headers=auth(tok), json={"cliente_id": INEXISTENTE}).status_code == 404
    assert client.put(f"/api/pedidos/{pid}", headers=auth(tok), json={"peso_kg": "0"}).status_code == 422
    assert client.put(f"/api/pedidos/{pid}", headers=auth(tok), json={"peso_kg": None}).status_code == 422
    assert client.put(f"/api/pedidos/{pid}", headers=auth(tok), json={}).status_code == 400


def test_pedido_asignado_no_se_edita(client):
    tok = estado["tok_operador"]
    pid = estado["pedido"]["pedido_id"]
    admin_db("UPDATE pedidos SET estado = 'ASIGNADO' WHERE pedido_id = %s", (pid,))
    r = client.put(f"/api/pedidos/{pid}", headers=auth(tok), json={"peso_kg": "10.00"})
    assert r.status_code == 409


def test_pedido_inexistente_da_404(client):
    tok = estado["tok_operador"]
    assert client.get(f"/api/pedidos/{INEXISTENTE}", headers=auth(tok)).status_code == 404
    assert client.put(f"/api/pedidos/{INEXISTENTE}", headers=auth(tok), json={"peso_kg": "1.00"}).status_code == 404


def test_sin_token_da_401(client):
    for metodo, ruta in (
        ("get", f"/api/vehiculos/{INEXISTENTE}"),
        ("delete", f"/api/conductores/{INEXISTENTE}"),
        ("put", f"/api/clientes/{INEXISTENTE}"),
        ("get", f"/api/pedidos/{INEXISTENTE}"),
    ):
        r = client.request(metodo.upper(), ruta, json={"nombre": "x"} if metodo == "put" else None)
        assert r.status_code == 401, ruta


def test_limpieza(client):
    for ruta_id in estado["rutas"]:
        admin_db("DELETE FROM rutas WHERE ruta_id = %s", (ruta_id,))
    for pedido_id in estado["pedidos"]:
        admin_db("DELETE FROM ruta_pedidos WHERE pedido_id = %s", (pedido_id,))
        admin_db("DELETE FROM pedidos WHERE pedido_id = %s", (pedido_id,))
    for cliente_id in estado["clientes"]:
        admin_db("DELETE FROM clientes WHERE cliente_id = %s", (cliente_id,))
    for vehiculo_id in estado["vehiculos"]:
        admin_db("DELETE FROM vehiculos WHERE vehiculo_id = %s", (vehiculo_id,))
    for conductor_id in estado["conductores"]:
        admin_db("DELETE FROM conductores WHERE conductor_id = %s", (conductor_id,))
