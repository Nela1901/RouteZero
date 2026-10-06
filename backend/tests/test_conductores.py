"""Suite del módulo de conductores (HU-009 / HT-06): registro con consentimiento (RN-013),
DNI duplicado, validación de jornada, edición, listado filtrado y control de acceso por rol
(solo ADMINISTRADOR).
"""

import random
import uuid
from datetime import date, timedelta

from conftest import EMAIL_OPERADOR, PASSWORD_OPERADOR, admin_db, auth, login

estado: dict = {}


def _dni_de_prueba() -> str:
    return "9" + "".join(str(random.randint(0, 9)) for _ in range(7))


def _cuerpo(**cambios) -> dict:
    cuerpo = {
        "nombre": "Conductor de Prueba",
        "dni": estado.get("dni", _dni_de_prueba()),
        "categoria_licencia": "A-IIb",
        "telefono": "987654321",
        "correo": "conductor.prueba@example.com",
        "licencia_vence": (date.today() + timedelta(days=365)).isoformat(),
        "horario_inicio": "06:00:00",
        "horario_fin": "14:00:00",
        "consentimiento_datos": True,
    }
    cuerpo.update(cambios)
    return cuerpo


def test_login_administrador(client):
    r = login(client, "Dev-Conductores")
    assert r.status_code == 200
    estado["tok_admin"] = r.json()["access_token"]
    estado["dni"] = _dni_de_prueba()


def test_registrar_conductor(client):
    r = client.post("/api/conductores", headers=auth(estado["tok_admin"]), json=_cuerpo())
    assert r.status_code == 201
    cuerpo = r.json()
    assert cuerpo["disponible"] is True
    assert cuerpo["dni"] == estado["dni"]
    assert cuerpo["consentimiento_en"]
    estado["conductor_id"] = cuerpo["conductor_id"]


def test_dni_duplicado_da_409(client):
    r = client.post("/api/conductores", headers=auth(estado["tok_admin"]), json=_cuerpo())
    assert r.status_code == 409


def test_sin_consentimiento_da_422(client):
    r = client.post(
        "/api/conductores",
        headers=auth(estado["tok_admin"]),
        json=_cuerpo(dni=_dni_de_prueba(), consentimiento_datos=False),
    )
    assert r.status_code == 422


def test_sin_campo_de_consentimiento_da_422(client):
    cuerpo = _cuerpo(dni=_dni_de_prueba())
    del cuerpo["consentimiento_datos"]
    r = client.post("/api/conductores", headers=auth(estado["tok_admin"]), json=cuerpo)
    assert r.status_code == 422


def test_campos_vacios_o_invalidos_dan_422(client):
    for cambios in (
        {"nombre": "   "},
        {"dni": "1234"},
        {"dni": "12345abc"},
        {"telefono": "abc"},
        {"categoria_licencia": "Z-9"},
        {"correo": "no-es-un-correo"},
    ):
        r = client.post(
            "/api/conductores",
            headers=auth(estado["tok_admin"]),
            json=_cuerpo(dni=cambios.pop("dni", _dni_de_prueba()), **cambios),
        )
        assert r.status_code == 422, cambios


def test_licencia_vencida_da_422(client):
    r = client.post(
        "/api/conductores",
        headers=auth(estado["tok_admin"]),
        json=_cuerpo(dni=_dni_de_prueba(), licencia_vence=(date.today() - timedelta(days=1)).isoformat()),
    )
    assert r.status_code == 422


def test_correo_es_opcional(client):
    dni = _dni_de_prueba()
    cuerpo = _cuerpo(dni=dni)
    del cuerpo["correo"]
    r = client.post("/api/conductores", headers=auth(estado["tok_admin"]), json=cuerpo)
    assert r.status_code == 201
    assert r.json()["correo"] is None
    admin_db("DELETE FROM conductores WHERE dni = %s", (dni,))


def test_jornada_mayor_a_8_horas_da_422(client):
    r = client.post(
        "/api/conductores",
        headers=auth(estado["tok_admin"]),
        json=_cuerpo(dni=_dni_de_prueba(), horario_inicio="06:00:00", horario_fin="15:00:00"),
    )
    assert r.status_code == 422


def test_horario_invertido_da_422(client):
    r = client.post(
        "/api/conductores",
        headers=auth(estado["tok_admin"]),
        json=_cuerpo(dni=_dni_de_prueba(), horario_inicio="14:00:00", horario_fin="06:00:00"),
    )
    assert r.status_code == 422


def test_editar_conductor(client):
    r = client.put(
        f"/api/conductores/{estado['conductor_id']}",
        headers=auth(estado["tok_admin"]),
        json={"disponible": False, "telefono": "912345678"},
    )
    assert r.status_code == 200
    assert r.json()["disponible"] is False
    assert r.json()["telefono"] == "912345678"


def test_editar_licencia_a_una_fecha_vencida_da_422(client):
    r = client.put(
        f"/api/conductores/{estado['conductor_id']}",
        headers=auth(estado["tok_admin"]),
        json={"licencia_vence": (date.today() - timedelta(days=5)).isoformat()},
    )
    assert r.status_code == 422


def test_editar_horario_que_supera_8_horas_da_422(client):
    r = client.put(
        f"/api/conductores/{estado['conductor_id']}",
        headers=auth(estado["tok_admin"]),
        json={"horario_fin": "20:00:00"},
    )
    assert r.status_code == 422


def test_editar_sin_campos_da_400(client):
    r = client.put(f"/api/conductores/{estado['conductor_id']}", headers=auth(estado["tok_admin"]), json={})
    assert r.status_code == 400


def test_editar_conductor_inexistente_da_404(client):
    r = client.put(
        f"/api/conductores/{uuid.uuid4()}",
        headers=auth(estado["tok_admin"]),
        json={"disponible": True},
    )
    assert r.status_code == 404


def test_listar_filtrado_por_disponibilidad(client):
    r = client.get("/api/conductores", headers=auth(estado["tok_admin"]), params={"disponible": "false"})
    assert r.status_code == 200
    assert estado["conductor_id"] in [c["conductor_id"] for c in r.json()]

    r = client.get("/api/conductores", headers=auth(estado["tok_admin"]), params={"disponible": "true"})
    assert estado["conductor_id"] not in [c["conductor_id"] for c in r.json()]

    r = client.get("/api/conductores", headers=auth(estado["tok_admin"]))
    assert estado["conductor_id"] in [c["conductor_id"] for c in r.json()]


def test_el_registro_de_auditoria_no_guarda_el_dni(client):
    filas = admin_db(
        "SELECT detalle FROM logs_auditoria WHERE modulo = 'conductores' AND accion = 'conductor_registrado' "
        "AND detalle = %s",
        (estado["conductor_id"],),
        fetch=True,
    )
    assert len(filas) == 1
    assert estado["dni"] not in filas[0][0]


def test_registrar_sin_token_da_401(client):
    r = client.post("/api/conductores", json=_cuerpo(dni=_dni_de_prueba()))
    assert r.status_code == 401


def test_operador_no_puede_acceder_a_conductores(client):
    r = login(client, "Dev-Conductores-Op", email=EMAIL_OPERADOR, password=PASSWORD_OPERADOR)
    assert r.status_code == 200
    tok_operador = r.json()["access_token"]

    assert client.get("/api/conductores", headers=auth(tok_operador)).status_code == 403
    r = client.post("/api/conductores", headers=auth(tok_operador), json=_cuerpo(dni=_dni_de_prueba()))
    assert r.status_code == 403


def test_limpieza(client):
    admin_db("DELETE FROM conductores WHERE conductor_id = %s", (estado["conductor_id"],))
