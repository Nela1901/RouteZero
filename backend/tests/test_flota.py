"""Suite del módulo de flota (HT-04): registro, edición, listado filtrado y control de
acceso por rol (solo ADMINISTRADOR). Portada de `tests_manual/e2e_flota.py`.
"""

import uuid
from datetime import date, timedelta

from conftest import EMAIL_OPERADOR, PASSWORD_OPERADOR, admin_db, auth, login

estado: dict = {}


def _placa_de_prueba(prefijo: str = "T") -> str:
    return f"{prefijo}{uuid.uuid4().hex[:6].upper()}"


def test_login_administrador(client):
    r = login(client, "Dev-Flota")
    assert r.status_code == 200
    estado["tok_admin"] = r.json()["access_token"]


def test_registrar_vehiculo(client):
    placa = _placa_de_prueba()
    estado["placa"] = placa
    r = client.post(
        "/api/vehiculos",
        headers=auth(estado["tok_admin"]),
        json={
            "placa": placa,
            "tipo": "CAMIONETA",
            "capacidad_kg": "1500.00",
            "consumo_km_l": "10.50",
            "factor_emision_co2": "0.2500",
            "anio_fabricacion": 2020,
        },
    )
    assert r.status_code == 201
    cuerpo = r.json()
    assert cuerpo["estado"] == "DISPONIBLE"
    estado["vehiculo_id"] = cuerpo["vehiculo_id"]


def test_placa_duplicada_da_409(client):
    r = client.post(
        "/api/vehiculos",
        headers=auth(estado["tok_admin"]),
        json={
            "placa": estado["placa"],
            "tipo": "MOTO",
            "capacidad_kg": "50.00",
            "consumo_km_l": "30.00",
            "factor_emision_co2": "0.1000",
            "anio_fabricacion": 2021,
        },
    )
    assert r.status_code == 409


def test_editar_vehiculo_cambia_el_estado(client):
    r = client.put(
        f"/api/vehiculos/{estado['vehiculo_id']}",
        headers=auth(estado["tok_admin"]),
        json={"estado": "MANTENIMIENTO"},
    )
    assert r.status_code == 200
    assert r.json()["estado"] == "MANTENIMIENTO"


def test_editar_vehiculo_inexistente_da_404(client):
    r = client.put(
        f"/api/vehiculos/{uuid.uuid4()}",
        headers=auth(estado["tok_admin"]),
        json={"estado": "DISPONIBLE"},
    )
    assert r.status_code == 404


def test_listar_filtrado_por_estado_incluye_el_editado(client):
    r = client.get("/api/vehiculos", headers=auth(estado["tok_admin"]), params={"estado": "MANTENIMIENTO"})
    assert r.status_code == 200
    assert estado["vehiculo_id"] in [v["vehiculo_id"] for v in r.json()]


def test_listar_filtrado_por_otro_estado_no_lo_incluye(client):
    r = client.get("/api/vehiculos", headers=auth(estado["tok_admin"]), params={"estado": "DISPONIBLE"})
    assert r.status_code == 200
    assert estado["vehiculo_id"] not in [v["vehiculo_id"] for v in r.json()]


def test_registrar_vehiculo_sin_token_da_401(client):
    r = client.post(
        "/api/vehiculos",
        json={
            "placa": _placa_de_prueba("S"),
            "tipo": "MOTO",
            "capacidad_kg": "50.00",
            "consumo_km_l": "30.00",
            "factor_emision_co2": "0.1000",
            "anio_fabricacion": 2021,
        },
    )
    assert r.status_code == 401


def test_operador_no_puede_listar_flota(client):
    r = login(client, "Dev-Flota-Op", email=EMAIL_OPERADOR, password=PASSWORD_OPERADOR)
    assert r.status_code == 200
    tok_operador = r.json()["access_token"]
    estado["tok_operador"] = tok_operador

    r = client.get("/api/vehiculos", headers=auth(tok_operador))
    assert r.status_code == 403


def test_operador_no_puede_registrar_vehiculos(client):
    r = client.post(
        "/api/vehiculos",
        headers=auth(estado["tok_operador"]),
        json={
            "placa": _placa_de_prueba("O"),
            "tipo": "MOTO",
            "capacidad_kg": "50.00",
            "consumo_km_l": "30.00",
            "factor_emision_co2": "0.1000",
            "anio_fabricacion": 2021,
        },
    )
    assert r.status_code == 403


def test_registrar_vehiculo_con_fechas_de_documentos(client):
    placa = _placa_de_prueba("D")
    soat = (date.today() + timedelta(days=200)).isoformat()
    revision = (date.today() + timedelta(days=90)).isoformat()
    r = client.post(
        "/api/vehiculos",
        headers=auth(estado["tok_admin"]),
        json={
            "placa": placa,
            "tipo": "FURGON",
            "capacidad_kg": "900.00",
            "consumo_km_l": "9.00",
            "factor_emision_co2": "0.2800",
            "anio_fabricacion": 2022,
            "soat_vence": soat,
            "revision_tecnica_vence": revision,
        },
    )
    assert r.status_code == 201
    assert r.json()["soat_vence"] == soat
    assert r.json()["revision_tecnica_vence"] == revision
    admin_db("DELETE FROM vehiculos WHERE placa = %s", (placa,))


def test_registrar_vehiculo_sin_fechas_las_deja_vacias(client):
    r = client.get("/api/vehiculos", headers=auth(estado["tok_admin"]))
    propio = next(v for v in r.json() if v["vehiculo_id"] == estado["vehiculo_id"])
    assert propio["soat_vence"] is None
    assert propio["revision_tecnica_vence"] is None


def test_renovar_documentos_actualiza_las_fechas(client):
    nueva = (date.today() + timedelta(days=365)).isoformat()
    r = client.put(
        f"/api/vehiculos/{estado['vehiculo_id']}",
        headers=auth(estado["tok_admin"]),
        json={"soat_vence": nueva},
    )
    assert r.status_code == 200
    assert r.json()["soat_vence"] == nueva


def test_fecha_de_documento_invalida_da_422(client):
    r = client.put(
        f"/api/vehiculos/{estado['vehiculo_id']}",
        headers=auth(estado["tok_admin"]),
        json={"soat_vence": "no-es-una-fecha"},
    )
    assert r.status_code == 422


def test_limpieza(client):
    admin_db("DELETE FROM vehiculos WHERE placa = %s", (estado["placa"],))
