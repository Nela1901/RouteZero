"""Suite del módulo de clientes (HU-010 / HT-06): registro con preferencias de entrega,
nombre duplicado, campos vacíos o inválidos y listado.
"""

import uuid

from conftest import EMAIL_OPERADOR, PASSWORD_OPERADOR, admin_db, auth, login

estado: dict = {"ids": []}


def _cuerpo(**cambios) -> dict:
    cuerpo = {
        "nombre": estado.get("nombre", f"Mercado de Prueba {uuid.uuid4().hex[:6]}"),
        "tipo_negocio": "MERCADO",
        "referencia": "Junto al paradero principal",
        "latitud": "-12.0653",
        "longitud": "-75.2049",
        "horario_inicio": "07:00:00",
        "horario_fin": "12:00:00",
    }
    cuerpo.update(cambios)
    return cuerpo


def test_login_operador(client):
    r = login(client, "Dev-Clientes", email=EMAIL_OPERADOR, password=PASSWORD_OPERADOR)
    assert r.status_code == 200
    estado["tok"] = r.json()["access_token"]
    estado["nombre"] = f"Mercado de Prueba {uuid.uuid4().hex[:6]}"


def test_registrar_cliente_con_preferencias_de_entrega(client):
    r = client.post("/api/clientes", headers=auth(estado["tok"]), json=_cuerpo())
    assert r.status_code == 201
    cuerpo = r.json()
    assert cuerpo["tipo_negocio"] == "MERCADO"
    assert cuerpo["horario_inicio"].startswith("07:00")
    assert cuerpo["horario_fin"].startswith("12:00")
    estado["ids"].append(cuerpo["cliente_id"])


def test_nombre_duplicado_da_409(client):
    r = client.post("/api/clientes", headers=auth(estado["tok"]), json=_cuerpo())
    assert r.status_code == 409


def test_nombre_duplicado_sin_distinguir_mayusculas_da_409(client):
    r = client.post("/api/clientes", headers=auth(estado["tok"]), json=_cuerpo(nombre=estado["nombre"].upper()))
    assert r.status_code == 409


def test_nombre_duplicado_con_espacios_sobrantes_da_409(client):
    r = client.post("/api/clientes", headers=auth(estado["tok"]), json=_cuerpo(nombre=f"  {estado['nombre']}  "))
    assert r.status_code == 409


def test_campos_vacios_o_invalidos_dan_422(client):
    sin_tipo = _cuerpo(nombre=f"Sin tipo {uuid.uuid4().hex[:6]}")
    del sin_tipo["tipo_negocio"]
    casos = [
        _cuerpo(nombre="   "),
        _cuerpo(nombre=""),
        sin_tipo,
        _cuerpo(nombre=f"Tipo malo {uuid.uuid4().hex[:6]}", tipo_negocio="GIMNASIO"),
    ]
    for cuerpo in casos:
        r = client.post("/api/clientes", headers=auth(estado["tok"]), json=cuerpo)
        assert r.status_code == 422, cuerpo


def test_horario_invertido_da_422(client):
    r = client.post(
        "/api/clientes",
        headers=auth(estado["tok"]),
        json=_cuerpo(nombre=f"Horario malo {uuid.uuid4().hex[:6]}", horario_inicio="12:00:00", horario_fin="07:00:00"),
    )
    assert r.status_code == 422


def test_referencia_en_blanco_se_guarda_vacia(client):
    r = client.post(
        "/api/clientes",
        headers=auth(estado["tok"]),
        json=_cuerpo(nombre=f"Sin referencia {uuid.uuid4().hex[:6]}", referencia="   "),
    )
    assert r.status_code == 201
    assert r.json()["referencia"] is None
    estado["ids"].append(r.json()["cliente_id"])


def test_listar_incluye_al_cliente_registrado(client):
    r = client.get("/api/clientes", headers=auth(estado["tok"]))
    assert r.status_code == 200
    assert estado["ids"][0] in [c["cliente_id"] for c in r.json()]


def test_registrar_sin_token_da_401(client):
    r = client.post("/api/clientes", json=_cuerpo(nombre=f"Sin token {uuid.uuid4().hex[:6]}"))
    assert r.status_code == 401


def test_limpieza(client):
    for cliente_id in estado["ids"]:
        admin_db("DELETE FROM clientes WHERE cliente_id = %s", (cliente_id,))
