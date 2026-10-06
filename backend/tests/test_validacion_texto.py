"""Qué caracteres admite cada campo de texto: nombres de persona (solo letras), nombres de negocio
(letras y números), descripciones y referencias (puntuación básica). Se comprueba al registrar y al editar.
"""

import random
import uuid
from datetime import date, timedelta

import pytest

from conftest import EMAIL_OPERADOR, PASSWORD_OPERADOR, admin_db, auth, login
from src.core.texto import validar_nombre_negocio, validar_nombre_persona, validar_texto_libre

estado: dict = {"conductores": [], "clientes": [], "pedidos": []}


# ---------- Reglas, sin base de datos ----------


@pytest.mark.parametrize("valor", ["Sara Hernán Caso", "José Ñahui", "Ana María", "Muñoz Pérez", "Ürsula"])
def test_nombre_de_persona_acepta_letras_y_espacios(valor):
    assert validar_nombre_persona(valor) == valor


@pytest.mark.parametrize("valor", ["Juan 2", "Pedro3", "Ana_María", "Luis@", "Rosa <b>", "O'Brien", "Ana-María", "Juan.", "Eva;"])
def test_nombre_de_persona_rechaza_numeros_y_signos(valor):
    with pytest.raises(ValueError):
        validar_nombre_persona(valor)


@pytest.mark.parametrize(
    "valor", ["Bodega 24 Horas", "Mercado Modelo - Puesto 14", "Distribuidora S.A.C.", "A & B Comercial", "Café (Centro)", "Panadería San Carlos"]
)
def test_nombre_de_negocio_acepta_letras_numeros_y_signos_de_razon_social(valor):
    assert validar_nombre_negocio(valor) == valor


@pytest.mark.parametrize("valor", ["Bodega <script>", "Tienda $$", "Local {1}", "Puesto 5%", "Bodega_Sol", "Comercial *", "Tienda;", "A=B", "Casa|Sol", "Bodega\\Sol"])
def test_nombre_de_negocio_rechaza_signos_raros(valor):
    with pytest.raises(ValueError):
        validar_nombre_negocio(valor)


@pytest.mark.parametrize("valor", ["Frente al Mercado Modelo, Huancayo", "Av. Real #123 (esquina con Jr. Lima)", "10 cajas; frágil", "¿Atiende de 8 a 12?", "Piso 2 - Of. 5/6"])
def test_texto_libre_acepta_puntuacion_basica(valor):
    assert validar_texto_libre(valor) == valor


@pytest.mark.parametrize("valor", ["<b>negrita</b>", "precio $10", "100% listo", "a@b", "x=1", "{json}", "[lista]", "a|b", "a\\b", "~casa", "`x`", "a^2", "*x*", "x_y", "a+b"])
def test_texto_libre_rechaza_caracteres_especiales(valor):
    with pytest.raises(ValueError):
        validar_texto_libre(valor)


# ---------- Contra la API ----------


def test_logins(client):
    estado["tok_admin"] = login(client, "Dev-Texto-Admin").json()["access_token"]
    estado["tok_operador"] = login(client, "Dev-Texto-Op", email=EMAIL_OPERADOR, password=PASSWORD_OPERADOR).json()["access_token"]


def _conductor(**cambios) -> dict:
    cuerpo = {
        "nombre": "Sara Hernán Caso",
        "dni": "9" + "".join(random.choice("0123456789") for _ in range(7)),
        "categoria_licencia": "A-IIb",
        "telefono": "987654321",
        "licencia_vence": str(date.today() + timedelta(days=400)),
        "consentimiento_datos": True,
    }
    cuerpo.update(cambios)
    return cuerpo


def test_conductor_nombre_con_numeros_o_signos_da_422_y_con_tildes_se_acepta(client):
    for malo in ("Sara 123", "Sara@Caso", "Sara_Caso", "Sara <b>"):
        r = client.post("/api/conductores", headers=auth(estado["tok_admin"]), json=_conductor(nombre=malo))
        assert r.status_code == 422, malo
    r = client.post("/api/conductores", headers=auth(estado["tok_admin"]), json=_conductor(nombre="Sara Hernán Cañari"))
    assert r.status_code == 201
    estado["conductores"].append(r.json()["conductor_id"])


def test_conductor_nombre_al_editar_tambien_se_valida(client):
    cid = estado["conductores"][0]
    r = client.put(f"/api/conductores/{cid}", headers=auth(estado["tok_admin"]), json={"nombre": "Sara 2"})
    assert r.status_code == 422
    r = client.put(f"/api/conductores/{cid}", headers=auth(estado["tok_admin"]), json={"nombre": "Sara Hernán Nuñez"})
    assert r.status_code == 200


def _cliente(**cambios) -> dict:
    cuerpo = {
        "nombre": f"Bodega 24 Horas {uuid.uuid4().hex[:6]}",
        "tipo_negocio": "BODEGA",
        "referencia": "Av. Real #123 (frente al parque)",
        "latitud": "-12.0653",
        "longitud": "-75.2049",
    }
    cuerpo.update(cambios)
    return cuerpo


def test_cliente_nombre_acepta_numeros_pero_no_signos_raros(client):
    tok = estado["tok_operador"]
    for malo in ("Bodega <script>", "Tienda $10", "Puesto 5%"):
        r = client.post("/api/clientes", headers=auth(tok), json=_cliente(nombre=malo))
        assert r.status_code == 422, malo
    r = client.post("/api/clientes", headers=auth(tok), json=_cliente())
    assert r.status_code == 201
    estado["clientes"].append(r.json())


def test_cliente_referencia_rechaza_caracteres_especiales_al_registrar_y_al_editar(client):
    tok = estado["tok_operador"]
    for mala in ("Cerca de {parque}", "Frente a <b>", "precio=10"):
        r = client.post("/api/clientes", headers=auth(tok), json=_cliente(referencia=mala))
        assert r.status_code == 422, mala
    cid = estado["clientes"][0]["cliente_id"]
    assert client.put(f"/api/clientes/{cid}", headers=auth(tok), json={"referencia": "Frente a <b>"}).status_code == 422
    assert client.put(f"/api/clientes/{cid}", headers=auth(tok), json={"nombre": "Bodega <x>"}).status_code == 422
    assert client.put(f"/api/clientes/{cid}", headers=auth(tok), json={"referencia": "Jr. Lima N° 45, Piso 2"}).status_code == 200


def test_pedido_descripcion_con_caracteres_especiales_da_422_y_con_puntuacion_se_acepta(client):
    tok = estado["tok_operador"]
    cid = estado["clientes"][0]["cliente_id"]
    base = {
        "cliente_id": cid,
        "peso_kg": "5.00",
        "latitud": "-12.0653",
        "longitud": "-75.2049",
        "ventana_inicio": "08:00:00",
        "ventana_fin": "12:00:00",
    }
    for mala in ("10 cajas <b>", "precio $10", "x=1", "a|b"):
        r = client.post("/api/pedidos", headers=auth(tok), json={**base, "descripcion": mala})
        assert r.status_code == 422, mala
    r = client.post("/api/pedidos", headers=auth(tok), json={**base, "descripcion": "10 cajas de gaseosa; frágil (Piso 2)"})
    assert r.status_code == 201
    pid = r.json()["pedido_id"]
    estado["pedidos"].append(pid)

    assert client.put(f"/api/pedidos/{pid}", headers=auth(tok), json={"descripcion": "<script>"}).status_code == 422
    assert client.put(f"/api/pedidos/{pid}", headers=auth(tok), json={"descripcion": "Entregar en puerta"}).status_code == 200


def test_pedido_descripcion_vacia_se_guarda_sin_descripcion(client):
    tok = estado["tok_operador"]
    cid = estado["clientes"][0]["cliente_id"]
    r = client.post(
        "/api/pedidos",
        headers=auth(tok),
        json={"cliente_id": cid, "descripcion": "   ", "peso_kg": "5.00", "latitud": "-12.0653", "longitud": "-75.2049", "ventana_inicio": "08:00:00", "ventana_fin": "12:00:00"},
    )
    assert r.status_code == 201
    assert r.json()["descripcion"] is None
    estado["pedidos"].append(r.json()["pedido_id"])


def test_limpieza(client):
    for pid in estado["pedidos"]:
        admin_db("DELETE FROM pedidos WHERE pedido_id = %s", (pid,))
    for c in estado["clientes"]:
        admin_db("DELETE FROM clientes WHERE cliente_id = %s", (c["cliente_id"],))
    for cid in estado["conductores"]:
        admin_db("DELETE FROM conductores WHERE conductor_id = %s", (cid,))
