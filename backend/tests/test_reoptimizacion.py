"""HU-012: re-optimización de rutas en curso, registro de entregas e incidentes de tráfico, contra la base real.

Reutiliza los datos de `test_rutas.py` (pedidos, vehículos y conductores propios de la prueba, en una fecha lejana).
Requiere haber ejecutado `scripts/migracion_reoptimizacion.sql`. Al final se borra todo lo creado.
"""

import uuid
from datetime import time

import pytest
from conftest import EMAIL_OPERADOR, PASSWORD_OPERADOR, UID, admin_db, auth, login
from fastapi import HTTPException
from test_rutas import (  # noqa: F401  (datos es una fixture que pytest necesita ver en este módulo)
    FECHA,
    PRESUPUESTO_S,
    RepositorioDePrueba,
    datos,
    estados_pedidos,
    generar,
    ids_en_resultado,
    insertar_pedido,
    servicio,
)

from src.rutas import router as router_rutas
from src.rutas.service import ServicioRutas, red_vial_compartida

DIEZ = time(10, 0)
MARCA_INCIDENTE = "prueba-reoptimizacion"


@pytest.fixture(autouse=True)
def _sin_incidentes_de_prueba():
    """Los incidentes son globales (afectan a toda re-optimización): se borran los de las pruebas antes y después."""
    admin_db("DELETE FROM incidentes_trafico WHERE descripcion = %s", (MARCA_INCIDENTE,))
    yield
    admin_db("DELETE FROM incidentes_trafico WHERE descripcion = %s", (MARCA_INCIDENTE,))


def confirmar(datos: dict) -> dict:
    """Genera y confirma las rutas de la jornada; devuelve el resultado de la generación."""
    r = generar(datos)
    with servicio(datos) as s:
        s.confirmar(r["lote_id"], UID)
    return r


def reoptimizar(datos: dict, hora=DIEZ, **kwargs) -> dict:
    with servicio(datos) as s:
        return s.reoptimizar(FECHA, PRESUPUESTO_S, hora, UID, **kwargs)


def confirmar_lote(datos: dict, lote_id: str) -> dict:
    with servicio(datos) as s:
        return s.confirmar(lote_id, UID)


def marcar(datos: dict, ruta_id: str, pedido_id: str, estado: str = "ENTREGADO") -> dict:
    with servicio(datos) as s:
        return s.marcar_entrega(ruta_id, pedido_id, estado, UID)


def paradas_de(ruta_id: str) -> list:
    return admin_db(
        "SELECT pedido_id, orden_entrega, estado_entrega FROM ruta_pedidos WHERE ruta_id = %s ORDER BY orden_entrega", (ruta_id,), fetch=True
    )


def estado_de(ruta_id: str) -> str:
    return admin_db("SELECT estado FROM rutas WHERE ruta_id = %s", (ruta_id,), fetch=True)[0][0]


# ----------------------------------------------------------------------------------- escenario 2
def test_sin_rutas_activas_informa_y_sugiere_generar(datos):
    generar(datos)  # solo hay un borrador: no cuenta como ruta activa
    r = reoptimizar(datos)
    assert r["sin_rutas_activas"] is True and r["lote_id"] is None and r["rutas"] == []
    assert "Genere" in r["mensaje"]


# ----------------------------------------------------------------------------------- escenario 1
def test_un_pedido_urgente_nuevo_se_integra_dentro_del_limite_y_se_confirma(datos):
    original = confirmar(datos)
    urgente = insertar_pedido(datos["cliente"], peso=10.0, prioridad="EXPRESS")
    datos["pedidos"].append(urgente)

    r = reoptimizar(datos)
    assert r["lote_id"] and not r["sin_rutas_activas"]
    assert r["pedidos_nuevos"] == 1 and r["pedidos_retirados"] == 0
    assert r["dentro_del_limite"] and r["tiempo_ejecucion_s"] <= 30
    assert r["hora_considerada"] == DIEZ
    assert urgente in ids_en_resultado(r)
    assert all(x["estado"] == "PLANIFICADA" and x["reemplaza_ruta_id"] for x in r["rutas"])
    assert estados_pedidos([urgente])[urgente] == "PENDIENTE"  # un borrador no cambia los pedidos

    originales = {x["ruta_id"] for x in original["rutas"]}
    assert {x["reemplaza_ruta_id"] for x in r["rutas"]} == originales

    c = confirmar_lote(datos, r["lote_id"])
    assert c["rutas_confirmadas"] == len(originales) and c["pedidos_asignados"] == 1
    assert estados_pedidos([urgente])[urgente] == "ASIGNADO"
    en_rutas = [p[0] for ruta_id in originales for p in paradas_de(ruta_id)]
    assert sorted(str(i) for i in en_rutas) == sorted(datos["pedidos"])  # cada pedido, una sola vez, en las rutas de siempre
    assert all(estado_de(ruta_id) == "CONFIRMADA" for ruta_id in originales)
    assert admin_db("SELECT count(*) FROM rutas WHERE reemplaza_ruta_id IS NOT NULL AND lote_id = %s", (r["lote_id"],), fetch=True)[0][0] == 0


def test_lo_ya_entregado_no_se_altera_y_la_ruta_pasa_a_en_ejecucion(datos):
    original = confirmar(datos)
    ruta = original["rutas"][0]
    primera = ruta["paradas"][0]["pedido_id"]
    m = marcar(datos, ruta["ruta_id"], primera)
    assert m["estado_entrega"] == "ENTREGADO" and m["estado_ruta"] == "EN_EJECUCION"
    assert estados_pedidos([primera])[primera] == "ENTREGADO"

    r = reoptimizar(datos)
    assert primera not in ids_en_resultado(r)  # lo entregado no se vuelve a planificar
    confirmar_lote(datos, r["lote_id"])
    paradas = paradas_de(ruta["ruta_id"])
    assert str(paradas[0][0]) == primera and paradas[0][2] == "ENTREGADO" and paradas[0][1] == 1
    assert [p[1] for p in paradas] == list(range(1, len(paradas) + 1))  # orden continuo tras lo ya hecho
    assert estado_de(ruta["ruta_id"]) == "EN_EJECUCION"


def test_un_pedido_cancelado_estando_asignado_se_retira_de_su_ruta(datos):
    original = confirmar(datos)
    ruta = original["rutas"][0]
    cancelado = ruta["paradas"][-1]["pedido_id"]
    admin_db("UPDATE pedidos SET estado = 'CANCELADO' WHERE pedido_id = %s", (cancelado,))

    r = reoptimizar(datos)
    assert r["pedidos_retirados"] == 1
    assert cancelado not in ids_en_resultado(r)
    confirmar_lote(datos, r["lote_id"])
    assert cancelado not in [str(p[0]) for p in paradas_de(ruta["ruta_id"])]
    assert estados_pedidos([cancelado])[cancelado] == "CANCELADO"


def test_un_incidente_se_aplica_a_la_re_optimizacion_hasta_que_se_resuelve(datos):
    confirmar(datos)
    with servicio(datos) as s:
        incidente = s.registrar_incidente("Av. Ferrocarril", 3.0, MARCA_INCIDENTE, UID)
    assert incidente["activo"] and incidente["factor"] == 3.0

    con = reoptimizar(datos)
    assert con["incidentes_aplicados"] == ["Av. Ferrocarril"]
    assert all(x["paradas"] for x in con["rutas"] if x["cantidad_paradas"])

    with servicio(datos) as s:
        assert s.resolver_incidente(incidente["incidente_id"], UID)["activo"] is False
        with pytest.raises(HTTPException) as e:
            s.resolver_incidente(incidente["incidente_id"], UID)
    assert e.value.status_code == 404
    sin = reoptimizar(datos)
    assert sin["incidentes_aplicados"] == []


def test_si_se_cancela_un_pedido_despues_de_re_optimizar_no_se_puede_confirmar(datos):
    confirmar(datos)
    urgente = insertar_pedido(datos["cliente"], peso=10.0, prioridad="EXPRESS")
    datos["pedidos"].append(urgente)
    r = reoptimizar(datos)
    admin_db("UPDATE pedidos SET estado = 'CANCELADO' WHERE pedido_id = %s", (urgente,))
    with pytest.raises(HTTPException) as e:
        confirmar_lote(datos, r["lote_id"])
    assert e.value.status_code == 409


def test_descartar_la_re_optimizacion_deja_las_rutas_en_curso_intactas(datos):
    original = confirmar(datos)
    antes = {x["ruta_id"]: paradas_de(x["ruta_id"]) for x in original["rutas"]}
    r = reoptimizar(datos)
    with servicio(datos) as s:
        assert s.descartar(r["lote_id"], UID)["rutas_eliminadas"] == len(r["rutas"])
    assert {x["ruta_id"]: paradas_de(x["ruta_id"]) for x in original["rutas"]} == antes


def test_una_ruta_sin_paradas_pendientes_termina_al_confirmar(datos):
    original = confirmar(datos)
    ruta = original["rutas"][0]
    for p in ruta["paradas"][:-1]:
        marcar(datos, ruta["ruta_id"], p["pedido_id"])
    ultimo = ruta["paradas"][-1]["pedido_id"]
    admin_db("UPDATE pedidos SET estado = 'CANCELADO' WHERE pedido_id = %s", (ultimo,))
    r = reoptimizar(datos)
    confirmar_lote(datos, r["lote_id"])
    assert estado_de(ruta["ruta_id"]) == "COMPLETADA"


# ----------------------------------------------------------------------------------- entregas
def test_marcar_entregas_completa_la_ruta_al_atender_la_ultima(datos):
    original = confirmar(datos)
    ruta = original["rutas"][0]
    for p in ruta["paradas"][:-1]:
        assert marcar(datos, ruta["ruta_id"], p["pedido_id"])["estado_ruta"] == "EN_EJECUCION"
    ultimo = marcar(datos, ruta["ruta_id"], ruta["paradas"][-1]["pedido_id"], "FALLIDO")
    assert ultimo["estado_ruta"] == "COMPLETADA" and ultimo["estado_entrega"] == "FALLIDO"
    # una entrega fallida no marca el pedido como entregado
    assert estados_pedidos([ruta["paradas"][-1]["pedido_id"]]).popitem()[1] == "ASIGNADO"


def test_las_entregas_se_validan(datos):
    borrador = generar(datos)
    ruta = borrador["rutas"][0]
    pedido = ruta["paradas"][0]["pedido_id"]
    with pytest.raises(HTTPException) as e:
        marcar(datos, ruta["ruta_id"], pedido)  # la ruta es un borrador
    assert e.value.status_code == 409
    with servicio(datos) as s:
        s.confirmar(borrador["lote_id"], UID)
    marcar(datos, ruta["ruta_id"], pedido)
    with pytest.raises(HTTPException) as e:
        marcar(datos, ruta["ruta_id"], pedido)  # ya registrada
    assert e.value.status_code == 409
    with pytest.raises(HTTPException) as e:
        marcar(datos, ruta["ruta_id"], str(uuid.uuid4()))
    assert e.value.status_code == 404


# ----------------------------------------------------------------------------------- API y roles
def test_la_api_de_re_optimizacion_entregas_e_incidentes_y_su_control_de_acceso(client, datos, monkeypatch):
    monkeypatch.setattr(router_rutas, "_servicio", lambda db: ServicioRutas(RepositorioDePrueba(db, datos), red_vial_compartida()))
    tok_admin = login(client, "Dev-Reopt").json()["access_token"]
    tok_op = login(client, "Dev-Reopt-Op", email=EMAIL_OPERADOR, password=PASSWORD_OPERADOR).json()["access_token"]
    cuerpo = {"fecha_jornada": FECHA.isoformat(), "tiempo_max_s": PRESUPUESTO_S, "hora_actual": "10:00"}

    assert client.post("/api/rutas/reoptimizar", headers=auth(tok_op), json=cuerpo).status_code == 403
    assert client.post("/api/rutas/incidentes", headers=auth(tok_op), json={"calle": "Calle Real"}).status_code == 403
    assert client.post("/api/rutas/incidentes", headers=auth(tok_admin), json={"calle": "Jr. Cualquiera"}).status_code == 422
    assert client.post("/api/rutas/incidentes", headers=auth(tok_admin), json={"calle": "Calle Real", "factor": 1.0}).status_code == 422

    sin = client.post("/api/rutas/reoptimizar", headers=auth(tok_admin), json=cuerpo)
    assert sin.status_code == 201 and sin.json()["sin_rutas_activas"] is True

    r = client.post("/api/rutas/generar", headers=auth(tok_admin), json={"fecha_jornada": FECHA.isoformat(), "tiempo_max_s": PRESUPUESTO_S}).json()
    assert client.post(f"/api/rutas/lotes/{r['lote_id']}/confirmar", headers=auth(tok_admin)).status_code == 200
    ruta = r["rutas"][0]
    url = f"/api/rutas/{ruta['ruta_id']}/paradas/{ruta['paradas'][0]['pedido_id']}/entrega"
    assert client.patch(url, headers=auth(tok_op), json={"estado": "ENTREGADO"}).status_code == 200
    assert client.patch(url, headers=auth(tok_op), json={"estado": "ENTREGADO"}).status_code == 409
    assert client.patch(url, headers=auth(tok_op), json={"estado": "OTRO"}).status_code == 422

    inc = client.post("/api/rutas/incidentes", headers=auth(tok_admin), json={"calle": "Calle Real", "factor": 2.5, "descripcion": MARCA_INCIDENTE})
    assert inc.status_code == 201
    activos = client.get("/api/rutas/incidentes", headers=auth(tok_op)).json()
    assert inc.json()["incidente_id"] in [i["incidente_id"] for i in activos]

    re = client.post("/api/rutas/reoptimizar", headers=auth(tok_admin), json=cuerpo)
    assert re.status_code == 201 and re.json()["incidentes_aplicados"] == ["Calle Real"]
    assert client.post(f"/api/rutas/lotes/{re.json()['lote_id']}/confirmar", headers=auth(tok_admin)).status_code == 200
    assert client.delete(f"/api/rutas/incidentes/{inc.json()['incidente_id']}", headers=auth(tok_admin)).status_code == 200
    assert client.delete(f"/api/rutas/incidentes/{inc.json()['incidente_id']}", headers=auth(tok_admin)).status_code == 404
