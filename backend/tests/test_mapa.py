"""HU-013: mapa de rutas con trazado por calles y congestión por hora punta, contra la base real.

Reutiliza los datos de `test_rutas.py` (pedidos, vehículos y conductores propios de la prueba, en una fecha lejana).
Requiere haber ejecutado `scripts/migracion_reoptimizacion.sql`. Al final se borra todo lo creado."""

from datetime import time

import pytest
from conftest import EMAIL_OPERADOR, PASSWORD_OPERADOR, admin_db, auth, login
from test_rutas import (  # noqa: F401  (datos es una fixture que pytest necesita ver en este módulo)
    FECHA,
    PRESUPUESTO_S,
    RepositorioDePrueba,
    datos,
    generar,
    servicio,
)

from src.rutas import router as router_rutas
from src.rutas.service import ServicioRutas, red_vial_compartida

MARCA_INCIDENTE = "prueba-mapa"
DIEZ, OCHO_Y_MEDIA = time(10, 0), time(8, 30)


@pytest.fixture(autouse=True)
def _sin_incidentes_de_prueba():
    admin_db("DELETE FROM incidentes_trafico WHERE descripcion = %s", (MARCA_INCIDENTE,))
    yield
    admin_db("DELETE FROM incidentes_trafico WHERE descripcion = %s", (MARCA_INCIDENTE,))


def mapa(datos: dict) -> dict:
    with servicio(datos) as s:
        return s.mapa(FECHA)


def congestion(datos: dict, hora) -> dict:
    with servicio(datos) as s:
        return s.congestion(hora)


def por_calle(respuesta: dict) -> dict:
    return {v["calle"]: v for v in respuesta["vias"]}


# ----------------------------------------------------------------------------------- mapa
def test_sin_rutas_el_mapa_viene_vacio_con_el_deposito(datos):
    m = mapa(datos)
    assert m["rutas"] == []
    assert m["deposito"]["latitud"] < 0 and m["deposito"]["longitud"] < 0


def test_cada_ruta_trae_un_tramo_por_parada_mas_el_regreso_y_empalma_con_ellas(datos):
    generar(datos)
    m = mapa(datos)
    assert m["rutas"]
    deposito = [round(m["deposito"]["latitud"], 5), round(m["deposito"]["longitud"], 5)]
    for ruta in m["rutas"]:
        paradas, tramos = ruta["paradas"], ruta["tramos"]
        assert len(tramos) == len(paradas) + 1
        assert (tramos[0]["desde"], tramos[-1]["hasta"]) == (0, 0)
        assert tramos[0]["puntos"][0] == deposito and tramos[-1]["puntos"][-1] == deposito
        for i, p in enumerate(paradas):
            punto = [round(float(p["latitud"]), 5), round(float(p["longitud"]), 5)]
            assert tramos[i]["puntos"][-1] == punto and tramos[i + 1]["puntos"][0] == punto
            assert tramos[i]["hasta"] == tramos[i + 1]["desde"] == p["orden"]
        assert all(len(t["puntos"]) >= 2 and t["distancia_km"] >= 0 and t["duracion_min"] >= 0 for t in tramos)
        assert all(p["estado_entrega"] == "PENDIENTE" for p in paradas)
    # en calles reales los tramos tienen más de dos puntos
    assert any(len(t["puntos"]) > 2 for r in m["rutas"] for t in r["tramos"])


def test_el_trazado_se_reutiliza_mientras_nada_cambie_y_se_recalcula_con_un_incidente(datos):
    generar(datos)
    primero = mapa(datos)
    assert mapa(datos) == primero  # misma respuesta desde la caché
    with servicio(datos) as s:
        s.registrar_incidente("Av. Ferrocarril", 5.0, MARCA_INCIDENTE, "444a2660-2006-4deb-9cee-61552721128e")
    con_incidente = mapa(datos)
    # congestionar una avenida nunca acorta un tramo: el camino más rápido solo puede empeorar o quedar igual
    tiempos = lambda r: [t["duracion_min"] for x in r["rutas"] for t in x["tramos"]]  # noqa: E731
    assert len(tiempos(con_incidente)) == len(tiempos(primero))
    assert all(t >= a for t, a in zip(tiempos(con_incidente), tiempos(primero)))


# ----------------------------------------------------------------------------------- congestión
def test_a_las_diez_las_tres_vias_estan_en_verde_y_en_hora_punta_en_amarillo(datos):
    fluido = congestion(datos, DIEZ)
    assert fluido["en_punta"] is False
    assert {v["nivel"] for v in fluido["vias"]} == {"VERDE"}
    punta = congestion(datos, OCHO_Y_MEDIA)
    assert punta["en_punta"] is True
    vias = por_calle(punta)
    assert {v["nivel"] for v in vias.values()} == {"AMARILLO"}
    assert vias["Av. Ferrocarril"]["factor"] == 1.8 and vias["Av. Ferrocarril"]["motivos"] == ["hora punta"]
    assert all(len(v["segmentos"]) > 0 and len(v["segmentos"][0]) == 2 for v in vias.values())


def test_un_incidente_pone_la_via_en_rojo_y_se_suma_a_la_hora_punta(datos):
    with servicio(datos) as s:
        s.registrar_incidente("Av. Ferrocarril", 3.0, MARCA_INCIDENTE, "444a2660-2006-4deb-9cee-61552721128e")
        s.registrar_incidente("Calle Real", 1.5, MARCA_INCIDENTE, "444a2660-2006-4deb-9cee-61552721128e")
    fuera = por_calle(congestion(datos, DIEZ))
    assert fuera["Av. Ferrocarril"]["nivel"] == "ROJO" and fuera["Av. Ferrocarril"]["motivos"] == ["incidente"]
    assert fuera["Calle Real"]["nivel"] == "AMARILLO"
    assert fuera["Av. Giráldez"]["nivel"] == "VERDE"
    punta = por_calle(congestion(datos, OCHO_Y_MEDIA))
    assert punta["Av. Ferrocarril"]["factor"] == pytest.approx(5.4)
    assert punta["Av. Ferrocarril"]["motivos"] == ["hora punta", "incidente"]
    assert punta["Calle Real"]["nivel"] == "AMARILLO"  # 1.3 x 1.5 = 1.95 < 2


# ----------------------------------------------------------------------------------- API y roles
def test_la_api_del_mapa_y_la_congestion_y_su_control_de_acceso(client, datos, monkeypatch):
    monkeypatch.setattr(router_rutas, "_servicio", lambda db: ServicioRutas(RepositorioDePrueba(db, datos), red_vial_compartida()))
    tok_admin = login(client, "Dev-Mapa").json()["access_token"]
    tok_op = login(client, "Dev-Mapa-Op", email=EMAIL_OPERADOR, password=PASSWORD_OPERADOR).json()["access_token"]

    sin = client.get("/api/rutas/mapa", headers=auth(tok_op), params={"fecha": FECHA.isoformat()})
    assert sin.status_code == 200 and sin.json()["rutas"] == []
    assert client.get("/api/rutas/mapa", headers=auth(tok_op), params={"fecha": "no-es-fecha"}).status_code == 422
    assert client.get("/api/rutas/mapa", params={"fecha": FECHA.isoformat()}).status_code in (401, 403)

    generado = client.post("/api/rutas/generar", headers=auth(tok_admin), json={"fecha_jornada": FECHA.isoformat(), "tiempo_max_s": PRESUPUESTO_S})
    assert generado.status_code == 201
    con = client.get("/api/rutas/mapa", headers=auth(tok_op), params={"fecha": FECHA.isoformat()})
    assert con.status_code == 200 and len(con.json()["rutas"]) == len(generado.json()["rutas"])

    c = client.get("/api/rutas/congestion", headers=auth(tok_op), params={"hora": "08:30"})
    assert c.status_code == 200 and c.json()["en_punta"] is True and len(c.json()["vias"]) == 3
    assert client.get("/api/rutas/congestion", headers=auth(tok_op)).status_code == 200  # sin hora: la actual
    assert client.get("/api/rutas/congestion", headers=auth(tok_op), params={"hora": "25:99"}).status_code == 422
