"""HU-016 y HT-12: reporte de sostenibilidad en PDF.

Las pruebas del generador y del cálculo no tocan la base (usan datos y un repositorio simulados); las del endpoint
usan la base real con los datos de `test_rutas.py` (fecha lejana, hoy + 200 días) y se limpian solas."""

import io
from datetime import date, datetime

import pytest
from conftest import EMAIL_OPERADOR, PASSWORD_OPERADOR, admin_db, auth, login
from fastapi import HTTPException
from pypdf import PdfReader
from test_rutas import (  # noqa: F401  (datos es una fixture que pytest necesita ver en este módulo)
    FECHA,
    confirmar,
    datos,
    generar,
)

from src.sostenibilidad import service as modulo_servicio
from src.sostenibilidad.reporte import generar_pdf
from src.sostenibilidad.service import MAXIMO_RUTAS_EN_REPORTE, ServicioSostenibilidad

SIN_DATOS = date(2031, 1, 1)


def texto_del_pdf(contenido: bytes) -> str:
    return "\n".join(pagina.extract_text() for pagina in PdfReader(io.BytesIO(contenido)).pages)


# ------------------------------------------------------------------- datos de ejemplo
def datos_de_reporte(parcial: bool = False, excede: bool = True, rutas: int = 2, omitidas: int = 0, sin_datos: int = 1) -> dict:
    flota = [
        {"placa": "ABC-101", "tipo": "CAMIONETA", "precio_compra_soles": 90000.0, "vida_util_anios": 10, "combustible_l": 5.0,
         "combustible_soles": 22.5, "depreciacion_soles": 542.47, "costo_total_soles": 564.97},
    ] + [
        {"placa": f"SIN-{i}", "tipo": "MOTO", "precio_compra_soles": None, "vida_util_anios": None, "combustible_l": 0.0,
         "combustible_soles": 0.0, "depreciacion_soles": None, "costo_total_soles": None}
        for i in range(sin_datos)
    ]
    return {
        "desde": date(2026, 10, 1), "hasta": date(2026, 10, 22), "dias": 22, "generado_en": datetime(2026, 10, 23, 9, 30), "parcial": parcial,
        "totales": {"rutas": rutas + omitidas, "distancia_km": 120.5, "emision_co2_kg": 28.4, "combustible_l": 14.2,
                    "combustible_ahorrado_l": 2.5, "ahorro_soles": 11.25, "cumplimiento_ventanas_pct": 96.7},
        "rutas": [{"fecha": date(2026, 10, 20), "placa": "ABC-101", "conductor": "Carlos Quispe Ñahui", "paradas": 5, "distancia_km": 40.1,
                   "emision_co2_kg": 9.5}] * rutas,
        "rutas_omitidas": omitidas,
        "flota": flota, "flota_sin_datos": sin_datos,
        "plan": {
            "mes_evaluado": {"desde": date(2026, 10, 1), "hasta": date(2026, 10, 22), "emision_co2_kg": 1000.0 if excede else 60.0,
                             "meta_kg": 800.0, "porcentaje_meta": 125.0 if excede else 7.5, "excede_meta": excede},
            "acciones": ["Regenerar y re-optimizar las rutas."] if excede else [],
            "arboles_necesarios": 46, "emision_co2_kg": 1000.0, "kg_co2_por_arbol_anio": 22.0,
        },
        "supuestos": {"precio_combustible_soles_l": 4.5, "kg_co2_por_arbol_anio": 22.0},
    }


# ----------------------------------------------------------------------- el generador
def test_el_pdf_es_valido_y_trae_las_secciones_y_las_cifras():
    contenido = generar_pdf(datos_de_reporte())
    assert contenido.startswith(b"%PDF") and contenido.rstrip().endswith(b"%%EOF")
    texto = texto_del_pdf(contenido)
    for esperado in (
        "Reporte de sostenibilidad", "Andina Reparto S.A.C.", "01/10/2026 al 22/10/2026", "1. Resumen del periodo", "120.5 km", "28.4 kg",
        "S/ 11.25", "96.7 %", "2. Emisiones de CO2 por ruta", "ABC-101", "Ñahui", "3. Costo del ciclo de vida de la flota", "S/ 90,000.00",
        "10 años", "S/ 564.97", "4. Metas de sostenibilidad y compensación", "La meta se supera.", "46 árboles", "5. Supuestos y notas",
        "S/ 4.50 por litro",
    ):
        assert esperado in texto, esperado
    assert "REPORTE PARCIAL" not in texto


def test_un_reporte_parcial_lo_indica_y_uno_completo_no():
    assert "REPORTE PARCIAL" in texto_del_pdf(generar_pdf(datos_de_reporte(parcial=True)))
    assert "REPORTE PARCIAL" not in texto_del_pdf(generar_pdf(datos_de_reporte(parcial=False)))


def test_los_vehiculos_sin_datos_de_compra_se_marcan_y_no_suman():
    texto = texto_del_pdf(generar_pdf(datos_de_reporte(sin_datos=2)))
    assert "sin dato" in texto and "2 vehículo(s) no tienen precio de compra" in texto
    assert "de los 1 vehículos con datos de compra" in texto and "S/ 564.97" in texto
    assert "no tienen precio de compra" not in texto_del_pdf(generar_pdf(datos_de_reporte(sin_datos=0)))


def test_la_meta_cumplida_no_sugiere_acciones():
    texto = texto_del_pdf(generar_pdf(datos_de_reporte(excede=False)))
    assert "La meta se cumple." in texto and "Regenerar y re-optimizar" not in texto


def test_muchas_rutas_ocupan_varias_paginas_y_las_omitidas_se_avisan():
    contenido = generar_pdf(datos_de_reporte(rutas=120, omitidas=15))
    paginas = PdfReader(io.BytesIO(contenido)).pages
    assert len(paginas) >= 3
    texto = texto_del_pdf(contenido)
    assert "faltan 15 rutas más antiguas" in texto and f"Página {len(paginas)} de {len(paginas)}" in texto


def test_un_texto_fuera_de_latin1_no_rompe_el_pdf():
    d = datos_de_reporte()
    d["rutas"][0] = {**d["rutas"][0], "conductor": "Conductor 王 café"}
    assert generar_pdf(d).startswith(b"%PDF")


# ----------------------------------------------------------------------- los datos
class RepoSimulado:
    def __init__(self, rutas: int = 2, flota: list[dict] | None = None, sin_completar: int = 0):
        self.rutas, self.sin_completar = rutas, sin_completar
        self.flota = flota or []

    def totales(self, desde, hasta):
        return {"rutas": self.rutas, "distancia_km": 100, "emision_co2_kg": 25, "combustible_l": 10, "combustible_ahorrado_l": 2,
                "ventanas_ponderadas": 950, "paradas": 10}

    def rutas_del_periodo(self, desde, hasta, limite):
        return [{"fecha_jornada": desde, "placa": "ABC-101", "conductor": "Ana", "paradas": 5, "distancia_km": 50, "emision_co2_kg": 12.5,
                 "combustible_l": 5, "combustible_ahorrado_l": 1}] * min(self.rutas, limite)

    def flota_del_periodo(self, desde, hasta):
        return self.flota

    def rutas_sin_completar(self, desde, hasta):
        return self.sin_completar


class Config:
    meta_mensual_co2_kg = 100.0
    kg_co2_por_arbol_anio = 22.0
    precio_combustible_soles_l = 4.5


def reporte(repo: RepoSimulado, desde=date(2026, 10, 1), hasta=date(2026, 10, 10)) -> dict:
    return ServicioSostenibilidad(repo, Config()).datos_del_reporte(desde, hasta)


def test_sin_rutas_en_el_periodo_no_se_genera_reporte_y_se_sugiere_otro_periodo():
    with pytest.raises(HTTPException) as e:
        reporte(RepoSimulado(rutas=0))
    assert e.value.status_code == 404
    assert "No hay datos suficientes para generar el reporte" in e.value.detail and "Seleccione otro periodo" in e.value.detail


def test_el_costo_del_ciclo_de_vida_prorratea_el_precio_y_suma_el_combustible():
    flota = [
        {"placa": "ABC-101", "tipo": "CAMIONETA", "precio_compra_soles": 73000, "vida_util_anios": 10, "combustible_l": 10},
        {"placa": "MOTO-1", "tipo": "MOTO", "precio_compra_soles": None, "vida_util_anios": None, "combustible_l": 4},
    ]
    r = reporte(RepoSimulado(flota=flota))  # 10 días del 1 al 10 de octubre
    camioneta, moto = r["flota"]
    assert r["dias"] == 10
    assert camioneta["depreciacion_soles"] == pytest.approx(73000 / (10 * 365) * 10)  # 200 soles
    assert camioneta["combustible_soles"] == pytest.approx(45.0)
    assert camioneta["costo_total_soles"] == pytest.approx(245.0)
    assert moto["costo_total_soles"] is None and moto["depreciacion_soles"] is None and moto["combustible_soles"] == pytest.approx(18.0)
    assert r["flota_sin_datos"] == 1


def test_el_reporte_es_parcial_si_quedan_rutas_sin_completar():
    assert reporte(RepoSimulado(sin_completar=1))["parcial"] is True
    assert reporte(RepoSimulado(sin_completar=0))["parcial"] is False


def test_las_rutas_que_exceden_el_limite_se_resumen_como_omitidas():
    r = reporte(RepoSimulado(rutas=MAXIMO_RUTAS_EN_REPORTE + 25))
    assert len(r["rutas"]) == MAXIMO_RUTAS_EN_REPORTE and r["rutas_omitidas"] == 25
    assert r["totales"]["rutas"] == MAXIMO_RUTAS_EN_REPORTE + 25


def test_el_reporte_valida_el_periodo():
    with pytest.raises(HTTPException) as e:
        reporte(RepoSimulado(), desde=date(2026, 10, 10), hasta=date(2026, 10, 1))
    assert e.value.status_code == 422


# ----------------------------------------------------------------------- el endpoint
@pytest.fixture(scope="module")
def token_admin(client):
    return login(client, "Dev-Reporte").json()["access_token"]


def pedir(client, token: str, desde: date, hasta: date | None = None):
    return client.get("/api/sostenibilidad/reporte", headers=auth(token), params={"desde": desde.isoformat(), "hasta": (hasta or desde).isoformat()})


def test_sin_jornadas_el_endpoint_responde_404_con_el_mensaje_y_sin_pdf(client, token_admin):
    r = pedir(client, token_admin, SIN_DATOS)
    assert r.status_code == 404
    assert r.headers["content-type"].startswith("application/json")
    assert "No hay datos suficientes para generar el reporte" in r.json()["detail"]


def test_con_rutas_confirmadas_el_endpoint_descarga_un_pdf_y_lo_audita(client, token_admin, datos):
    lote = generar(datos)
    confirmar(datos, lote["lote_id"])
    r = pedir(client, token_admin, FECHA)

    assert r.status_code == 200 and r.headers["content-type"] == "application/pdf"
    assert f'filename="reporte-sostenibilidad-{FECHA}-{FECHA}.pdf"' in r.headers["content-disposition"]
    assert r.content.startswith(b"%PDF")
    texto = texto_del_pdf(r.content)
    assert f"{FECHA:%d/%m/%Y}" in texto and "Emisiones de CO2 por ruta" in texto and "REPORTE PARCIAL" in texto  # confirmadas, sin completar
    assert any(placa in texto for placa in (v for v in _placas(datos)))
    registro = admin_db(
        "SELECT COUNT(*) FROM logs_auditoria WHERE accion = 'reporte_generado' AND modulo = 'sostenibilidad' AND detalle = %s",
        (f"{FECHA} a {FECHA}",), fetch=True,
    )[0][0]
    assert registro >= 1  # la auditoría es de solo agregar: el registro de prueba no se borra


def _placas(datos: dict) -> list[str]:
    filas = admin_db("SELECT placa FROM vehiculos WHERE vehiculo_id = ANY(%s::uuid[])", (datos["vehiculos"],), fetch=True)
    return [f[0] for f in filas]


def test_solo_el_administrador_descarga_el_reporte_y_el_periodo_se_valida(client, token_admin):
    token_operador = login(client, "Dev-Reporte-Op", email=EMAIL_OPERADOR, password=PASSWORD_OPERADOR).json()["access_token"]
    assert pedir(client, token_operador, SIN_DATOS).status_code == 403
    assert client.get("/api/sostenibilidad/reporte").status_code in (401, 403)
    assert pedir(client, token_admin, date(2031, 1, 10), date(2031, 1, 1)).status_code == 422


def test_el_modulo_expone_el_calculo_de_hoy_en_peru():
    assert isinstance(modulo_servicio.hoy_en_peru(), date)
