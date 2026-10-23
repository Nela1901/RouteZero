"""HU-015: dashboard de indicadores de sostenibilidad, contra la base real.

Reutiliza los datos de `test_rutas.py` (pedidos, vehículos y conductores propios de la prueba, en una fecha
lejana: hoy + 200 días), así que el periodo de cada prueba solo contiene sus propias rutas. Al final se borra todo."""

from datetime import date, timedelta

import pytest
from conftest import EMAIL_OPERADOR, PASSWORD_OPERADOR, admin_db, auth, login
from fastapi import HTTPException
from test_rutas import (  # noqa: F401  (datos es una fixture que pytest necesita ver en este módulo)
    FECHA,
    confirmar,
    datos,
    generar,
)

from src.core.config import settings
from src.sostenibilidad import service as modulo_servicio
from src.sostenibilidad.service import MAXIMO_DIAS, periodo_valido

SIN_DATOS = date(2031, 1, 1)  # un día sin jornadas en ninguna base de prueba


def dashboard(client, token: str, desde: date, hasta: date | None = None):
    return client.get("/api/sostenibilidad/dashboard", headers=auth(token), params={"desde": desde.isoformat(), "hasta": (hasta or desde).isoformat()})


@pytest.fixture(scope="module")
def token_admin(client):
    return login(client, "Dev-Sostenibilidad").json()["access_token"]


# ------------------------------------------------------------------------------ periodo
def test_sin_fechas_el_periodo_es_el_mes_en_curso():
    assert periodo_valido(None, None, date(2026, 10, 23)) == (date(2026, 10, 1), date(2026, 10, 23))
    assert periodo_valido(None, date(2026, 9, 15), date(2026, 10, 23)) == (date(2026, 9, 1), date(2026, 9, 15))


def test_un_periodo_invertido_o_de_mas_de_un_anio_se_rechaza():
    with pytest.raises(HTTPException) as e:
        periodo_valido(date(2026, 10, 5), date(2026, 10, 1), date(2026, 10, 23))
    assert e.value.status_code == 422
    with pytest.raises(HTTPException) as e:
        periodo_valido(date(2025, 1, 1), date(2025, 1, 1) + timedelta(days=MAXIMO_DIAS), date(2026, 10, 23))
    assert e.value.status_code == 422
    assert periodo_valido(date(2025, 1, 1), date(2025, 1, 1) + timedelta(days=MAXIMO_DIAS - 1), date(2026, 10, 23))


# ---------------------------------------------------------------------------- escenarios
def test_sin_jornadas_el_dashboard_muestra_ceros_y_un_mensaje(client, token_admin):
    r = dashboard(client, token_admin, SIN_DATOS)
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["hay_datos"] is False and "No hay jornadas" in cuerpo["mensaje"]
    assert cuerpo["totales"] == {
        "rutas": 0, "distancia_km": 0, "emision_co2_kg": 0, "combustible_l": 0, "combustible_ahorrado_l": 0,
        "ahorro_soles": 0, "cumplimiento_ventanas_pct": 0,
    }
    assert cuerpo["entregas"] == {"entregadas": 0, "pendientes": 0, "fallidas": 0} and cuerpo["por_dia"] == []


def test_un_borrador_no_cuenta_como_jornada(client, token_admin, datos):
    generar(datos)
    assert dashboard(client, token_admin, FECHA).json()["hay_datos"] is False


def test_el_dashboard_suma_las_metricas_de_las_rutas_confirmadas(client, token_admin, datos):
    lote = generar(datos)
    confirmar(datos, lote["lote_id"])
    cuerpo = dashboard(client, token_admin, FECHA).json()

    esperado = admin_db(
        "SELECT COUNT(*), SUM(m.emision_co2_kg), SUM(m.combustible_l), SUM(m.combustible_ahorrado_l), SUM(m.distancia_optimizada_km) "
        "FROM rutas r JOIN metricas_sostenibilidad m ON m.ruta_id = r.ruta_id WHERE r.lote_id = %s",
        (lote["lote_id"],), fetch=True,
    )[0]
    t = cuerpo["totales"]
    assert cuerpo["hay_datos"] is True and cuerpo["mensaje"] is None
    assert t["rutas"] == esperado[0] == len(lote["rutas"])
    assert t["emision_co2_kg"] == pytest.approx(float(esperado[1]), abs=0.01)
    assert t["combustible_l"] == pytest.approx(float(esperado[2]), abs=0.01)
    assert t["combustible_ahorrado_l"] == pytest.approx(float(esperado[3]), abs=0.01)
    assert t["distancia_km"] == pytest.approx(float(esperado[4]), abs=0.01)
    assert t["emision_co2_kg"] > 0 and 0 <= t["cumplimiento_ventanas_pct"] <= 100
    # RN-009: emisión = distancia × factor de emisión del vehículo (0.20 y 0.25 kg/km en los vehículos de prueba)
    assert 0.20 * t["distancia_km"] - 0.01 <= t["emision_co2_kg"] <= 0.25 * t["distancia_km"] + 0.01
    # El ahorro en soles es el combustible ahorrado por el precio del litro
    assert t["ahorro_soles"] == pytest.approx(t["combustible_ahorrado_l"] * settings.precio_combustible_soles_l)
    assert cuerpo["precio_combustible_soles_l"] == settings.precio_combustible_soles_l
    assert cuerpo["entregas"] == {"entregadas": 0, "pendientes": len(datos["pedidos"]) - len(lote["sin_cobertura"]), "fallidas": 0}
    assert [d["fecha"] for d in cuerpo["por_dia"]] == [FECHA.isoformat()]
    assert cuerpo["por_dia"][0]["emision_co2_kg"] == pytest.approx(t["emision_co2_kg"], abs=0.01)


def test_las_entregas_registradas_y_los_pedidos_cancelados_se_reflejan(client, token_admin, datos):
    lote = generar(datos)
    confirmar(datos, lote["lote_id"])
    paradas = admin_db(
        "SELECT rp.ruta_pedido_id, rp.pedido_id FROM ruta_pedidos rp JOIN rutas r ON r.ruta_id = rp.ruta_id WHERE r.lote_id = %s "
        "ORDER BY rp.ruta_pedido_id", (lote["lote_id"],), fetch=True,
    )
    entregado, fallido, cancelado = paradas[0], paradas[1], paradas[2]
    admin_db("UPDATE ruta_pedidos SET estado_entrega = 'ENTREGADO' WHERE ruta_pedido_id = %s", (entregado[0],))
    admin_db("UPDATE ruta_pedidos SET estado_entrega = 'FALLIDO' WHERE ruta_pedido_id = %s", (fallido[0],))
    admin_db("UPDATE pedidos SET estado = 'CANCELADO' WHERE pedido_id = %s", (cancelado[1],))
    e = dashboard(client, token_admin, FECHA).json()["entregas"]
    assert e == {"entregadas": 1, "fallidas": 1, "pendientes": len(paradas) - 3}


def test_solo_el_administrador_ve_el_dashboard(client, token_admin):
    token_operador = login(client, "Dev-Sostenibilidad-Op", email=EMAIL_OPERADOR, password=PASSWORD_OPERADOR).json()["access_token"]
    assert dashboard(client, token_operador, SIN_DATOS).status_code == 403
    assert client.get("/api/sostenibilidad/dashboard").status_code in (401, 403)
    assert dashboard(client, token_admin, SIN_DATOS, SIN_DATOS - timedelta(days=1)).status_code == 422


def test_sin_parametros_el_dashboard_responde_el_mes_en_curso(client, token_admin):
    cuerpo = client.get("/api/sostenibilidad/dashboard", headers=auth(token_admin)).json()
    hoy = modulo_servicio.hoy_en_peru()
    assert cuerpo["desde"] == hoy.replace(day=1).isoformat() and cuerpo["hasta"] == hoy.isoformat()


# ------------------------------------------------------------------------ compensación (HU-017)
class RepoFalso:
    """Devuelve siempre la misma emisión, sin tocar la base."""

    def __init__(self, emision: float):
        self.emision = emision

    def totales(self, desde, hasta):
        return {"emision_co2_kg": self.emision}


class Config:
    meta_mensual_co2_kg = 100.0
    kg_co2_por_arbol_anio = 22.0
    precio_combustible_soles_l = 4.5


def plan(emision: float) -> dict:
    desde, hasta = date(2026, 10, 1), date(2026, 10, 20)
    return modulo_servicio.ServicioSostenibilidad(RepoFalso(emision), Config()).compensacion(desde, hasta)


def test_los_arboles_necesarios_salen_de_las_emisiones_y_se_redondean_hacia_arriba():
    p = plan(1000.0)  # una tonelada
    assert p["hay_datos"] is True and p["toneladas_co2"] == 1.0
    assert p["arboles_necesarios"] == 46  # ceil(1000 / 22)
    assert len(p["alianzas"]) >= 1 and p["mensaje"] is None
    assert plan(22.0)["arboles_necesarios"] == 1 and plan(22.1)["arboles_necesarios"] == 2


def test_sin_emisiones_el_plan_pide_ejecutar_una_jornada():
    p = plan(0.0)
    assert p["hay_datos"] is False and p["arboles_necesarios"] == 0 and p["alianzas"] == [] and p["acciones"] == []
    assert "al menos una jornada operativa" in p["mensaje"]


def test_si_el_mes_supera_la_meta_se_alerta_y_se_sugieren_acciones():
    p = plan(150.0)
    mes = p["mes_evaluado"]
    assert mes["excede_meta"] is True and mes["porcentaje_meta"] == 150.0 and mes["meta_kg"] == 100.0
    assert len(p["acciones"]) == 3
    ok = plan(60.0)
    assert ok["mes_evaluado"]["excede_meta"] is False and ok["acciones"] == [] and ok["mes_evaluado"]["porcentaje_meta"] == 60.0


def test_la_meta_se_compara_con_el_mes_de_la_fecha_final_aunque_el_periodo_sea_mas_largo():
    class PorPeriodo:
        def totales(self, desde, hasta):
            return {"emision_co2_kg": 500.0 if desde == date(2026, 9, 1) else 40.0}

    p = modulo_servicio.ServicioSostenibilidad(PorPeriodo(), Config()).compensacion(date(2026, 9, 1), date(2026, 10, 20))
    assert p["emision_co2_kg"] == 500.0 and p["arboles_necesarios"] == 23
    assert p["mes_evaluado"]["desde"] == date(2026, 10, 1) and p["mes_evaluado"]["emision_co2_kg"] == 40.0
    assert p["mes_evaluado"]["excede_meta"] is False


def test_la_compensacion_por_la_api_usa_las_emisiones_de_las_rutas_confirmadas(client, token_admin, datos):
    sin = client.get("/api/sostenibilidad/compensacion", headers=auth(token_admin), params={"desde": SIN_DATOS.isoformat(), "hasta": SIN_DATOS.isoformat()})
    assert sin.status_code == 200 and sin.json()["hay_datos"] is False and sin.json()["arboles_necesarios"] == 0

    lote = generar(datos)
    confirmar(datos, lote["lote_id"])
    p = client.get("/api/sostenibilidad/compensacion", headers=auth(token_admin), params={"desde": FECHA.isoformat(), "hasta": FECHA.isoformat()}).json()
    esperado = dashboard(client, token_admin, FECHA).json()["totales"]["emision_co2_kg"]
    assert p["hay_datos"] is True and p["emision_co2_kg"] == pytest.approx(esperado)
    assert p["arboles_necesarios"] == -(-p["emision_co2_kg"] // settings.kg_co2_por_arbol_anio)


def test_solo_el_administrador_ve_la_compensacion(client, token_admin):
    token_operador = login(client, "Dev-Sostenibilidad-Op", email=EMAIL_OPERADOR, password=PASSWORD_OPERADOR).json()["access_token"]
    assert client.get("/api/sostenibilidad/compensacion", headers=auth(token_operador)).status_code == 403
    assert client.get("/api/sostenibilidad/compensacion", headers=auth(token_admin), params={"desde": "2026-10-05", "hasta": "2026-10-01"}).status_code == 422
