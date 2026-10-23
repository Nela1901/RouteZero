"""HU-014: vista del conductor (mi ruta, vínculo por correo, alertas y entregas propias), contra la base real.

Reutiliza los datos de `test_rutas.py` (pedidos, vehículos y conductores propios de la prueba, en una fecha lejana).
Al final se borra todo lo creado, incluido el vínculo de la cuenta con el conductor de prueba."""

from datetime import time, timedelta

import pytest
from conftest import EMAIL_OPERADOR, PASSWORD_OPERADOR, UID, admin_db, auth, login
from fastapi import HTTPException
from test_rutas import (  # noqa: F401  (datos es una fixture que pytest necesita ver en este módulo)
    FECHA,
    PRESUPUESTO_S,
    RepositorioDePrueba,
    datos,
    generar,
    insertar_pedido,
    servicio,
)

from src.red_vial.grafo import cargar_grafo
from src.rutas import router as router_rutas
from src.rutas.service import ServicioRutas, red_vial_compartida

CORREO = "conductor.prueba@routezero.dev"
MARCA_INCIDENTE = "prueba-conductor"
DIEZ, OCHO_Y_MEDIA = time(10, 0), time(8, 30)


@pytest.fixture(autouse=True)
def _sin_incidentes_de_prueba():
    admin_db("DELETE FROM incidentes_trafico WHERE descripcion = %s", (MARCA_INCIDENTE,))
    yield
    admin_db("DELETE FROM incidentes_trafico WHERE descripcion = %s", (MARCA_INCIDENTE,))


@pytest.fixture
def dos_rutas(datos):
    """Rutas confirmadas de al menos dos vehículos: se suman dos pedidos pesados para que no quepan en uno solo."""
    for _ in range(2):
        datos["pedidos"].append(insertar_pedido(datos["cliente"], peso=150.0))
    r = generar(datos)
    assert len(r["rutas"]) >= 2
    with servicio(datos) as s:
        s.confirmar(r["lote_id"], UID)
    return r


def conductor_de(ruta: dict) -> str:
    return ruta["conductor"]["conductor_id"]


def dar_correo(conductor_id: str, correo: str = CORREO) -> None:
    admin_db("UPDATE conductores SET correo = %s WHERE conductor_id = %s", (correo, conductor_id))


def mi_ruta(datos: dict, correo: str | None = CORREO, fecha=FECHA, hora=DIEZ, usuario=UID) -> dict:
    with servicio(datos) as s:
        return s.mi_ruta(usuario, correo, fecha, hora)


def marcar(datos: dict, ruta_id: str, pedido_id: str, estado="ENTREGADO", correo=CORREO) -> dict:
    with servicio(datos) as s:
        return s.marcar_entrega(ruta_id, pedido_id, estado, UID, "CONDUCTOR", correo)


# ----------------------------------------------------------------------------------- vínculo
def test_una_cuenta_sin_conductor_con_su_correo_recibe_un_mensaje_claro(datos):
    r = mi_ruta(datos, correo="nadie@routezero.dev")
    assert r["vinculado"] is False
    assert r["ruta"] is None
    assert r["conductor"] is None
    assert "vinculado" in r["mensaje"]
    assert "correo" in r["mensaje"]


def test_el_vinculo_se_hace_por_correo_sin_distinguir_mayusculas_y_queda_guardado(dos_rutas, datos):
    conductor = conductor_de(dos_rutas["rutas"][0])
    dar_correo(conductor, "Conductor.Prueba@RouteZero.dev")
    r = mi_ruta(datos, correo="conductor.prueba@routezero.dev")
    assert r["vinculado"]
    assert r["conductor"]["conductor_id"] == conductor
    assert str(admin_db("SELECT usuario_id FROM conductores WHERE conductor_id = %s", (conductor,), fetch=True)[0][0]) == UID
    # ya vinculado, no necesita el correo
    assert mi_ruta(datos, correo=None)["conductor"]["conductor_id"] == conductor


# ----------------------------------------------------------------------------------- mi ruta
def test_el_conductor_ve_su_ruta_con_sus_paradas_y_la_siguiente(dos_rutas, datos):
    propia = dos_rutas["rutas"][0]
    dar_correo(conductor_de(propia))
    r = mi_ruta(datos)
    assert r["ruta"]["ruta_id"] == propia["ruta_id"]
    assert r["ruta"]["estado"] == "CONFIRMADA"
    assert [p["pedido_id"] for p in r["ruta"]["paradas"]] == [p["pedido_id"] for p in propia["paradas"]]
    assert r["pendientes"] == len(propia["paradas"])
    assert r["entregadas"] == 0
    assert r["siguiente_orden"] == 1
    assert len(r["ruta"]["tramos"]) == len(propia["paradas"]) + 1
    assert all("nodos" not in t for t in r["ruta"]["tramos"])  # los nodos son internos, no se exponen
    assert r["deposito"]["latitud"] < 0
    assert r["mensaje"] is None


def test_cada_conductor_ve_solo_su_ruta(dos_rutas, datos):
    a, b = dos_rutas["rutas"][0], dos_rutas["rutas"][1]
    dar_correo(conductor_de(a))
    r = mi_ruta(datos)
    ajenos = {p["pedido_id"] for p in b["paradas"]}
    assert r["ruta"]["ruta_id"] == a["ruta_id"]
    assert not ajenos & {p["pedido_id"] for p in r["ruta"]["paradas"]}
    assert r["ruta"]["conductor"]["conductor_id"] == conductor_de(a)


def test_un_borrador_no_se_muestra_al_conductor(datos):
    r = generar(datos)  # sin confirmar
    dar_correo(conductor_de(r["rutas"][0]))
    m = mi_ruta(datos)
    assert m["vinculado"]
    assert m["ruta"] is None
    assert m["mensaje"] == "No tienes rutas asignadas por el momento."


def test_sin_ruta_ese_dia_el_conductor_recibe_el_aviso(dos_rutas, datos):
    dar_correo(conductor_de(dos_rutas["rutas"][0]))
    m = mi_ruta(datos, fecha=FECHA + timedelta(days=1))
    assert m["vinculado"]
    assert m["ruta"] is None
    assert m["mensaje"] == "No tienes rutas asignadas por el momento."
    assert m["siguiente_orden"] is None
    assert m["pendientes"] == 0


# ----------------------------------------------------------------------------------- entregas propias
def test_el_conductor_avanza_por_sus_paradas_hasta_completar_la_ruta(dos_rutas, datos):
    propia = dos_rutas["rutas"][0]
    dar_correo(conductor_de(propia))
    paradas = propia["paradas"]
    for i, p in enumerate(paradas[:-1], start=1):
        assert marcar(datos, propia["ruta_id"], p["pedido_id"])["estado_ruta"] == "EN_EJECUCION"
        m = mi_ruta(datos)
        assert m["entregadas"] == i
        assert m["siguiente_orden"] == i + 1
        assert m["ruta"]["estado"] == "EN_EJECUCION"
    ultimo = marcar(datos, propia["ruta_id"], paradas[-1]["pedido_id"], "FALLIDO")
    assert ultimo["estado_ruta"] == "COMPLETADA"
    m = mi_ruta(datos)
    assert m["siguiente_orden"] is None
    assert m["pendientes"] == 0
    assert m["ruta"]["estado"] == "COMPLETADA"


def test_un_conductor_no_puede_registrar_entregas_de_otra_ruta(dos_rutas, datos):
    propia, ajena = dos_rutas["rutas"][0], dos_rutas["rutas"][1]
    dar_correo(conductor_de(propia))
    with pytest.raises(HTTPException) as e:
        marcar(datos, ajena["ruta_id"], ajena["paradas"][0]["pedido_id"])
    assert e.value.status_code == 403
    assert admin_db("SELECT estado_entrega FROM ruta_pedidos WHERE ruta_id = %s ORDER BY orden_entrega", (ajena["ruta_id"],), fetch=True)[0][0] == "PENDIENTE"


def test_una_cuenta_sin_vinculo_tampoco_puede_registrar_entregas(dos_rutas, datos):
    ruta = dos_rutas["rutas"][0]
    with pytest.raises(HTTPException) as e:
        marcar(datos, ruta["ruta_id"], ruta["paradas"][0]["pedido_id"], correo="nadie@routezero.dev")
    assert e.value.status_code == 403


def test_un_pedido_cancelado_no_cuenta_como_pendiente_ni_como_siguiente(dos_rutas, datos):
    propia = dos_rutas["rutas"][0]
    dar_correo(conductor_de(propia))
    primero = propia["paradas"][0]["pedido_id"]
    admin_db("UPDATE pedidos SET estado = 'CANCELADO' WHERE pedido_id = %s", (primero,))
    m = mi_ruta(datos)
    assert m["pendientes"] == len(propia["paradas"]) - 1
    assert m["siguiente_orden"] == 2
    assert next(p for p in m["ruta"]["paradas"] if p["pedido_id"] == primero)["pedido_estado"] == "CANCELADO"


# ----------------------------------------------------------------------------------- alertas de tráfico
def test_sin_congestion_no_hay_alertas_y_en_hora_punta_aparecen_las_vias(dos_rutas, datos):
    dar_correo(conductor_de(dos_rutas["rutas"][0]))
    assert mi_ruta(datos, hora=DIEZ)["alertas"] == []
    punta = mi_ruta(datos, hora=OCHO_Y_MEDIA)["alertas"]
    assert {a["calle"] for a in punta} == {"Av. Ferrocarril", "Av. Giráldez", "Calle Real"}
    assert all(a["nivel"] == "AMARILLO" and a["motivos"] == ["hora punta"] for a in punta)
    assert all(bool(a["segmentos"]) == a["en_tu_ruta"] for a in punta)  # solo se traza la vía que está en su ruta


@pytest.mark.skipif(cargar_grafo() is None, reason="no está el grafo real de Huancayo")
def test_la_alerta_marca_la_via_que_cruza_la_ruta_del_conductor(datos):
    lat, lon = (float(x) for x in cargar_grafo().tramos_de_calle("ferrocarril")[100][0])
    admin_db("UPDATE pedidos SET latitud = %s, longitud = %s WHERE pedido_id = %s", (lat, lon, datos["pedidos"][0]))
    r = generar(datos)
    with servicio(datos) as s:
        s.confirmar(r["lote_id"], UID)
        s.registrar_incidente("Av. Ferrocarril", 3.0, MARCA_INCIDENTE, UID)
    ruta = next(x for x in r["rutas"] if datos["pedidos"][0] in [p["pedido_id"] for p in x["paradas"]])
    dar_correo(conductor_de(ruta))
    alertas = mi_ruta(datos, hora=DIEZ)["alertas"]
    assert [a["calle"] for a in alertas] == ["Av. Ferrocarril"]
    assert alertas[0]["nivel"] == "ROJO"
    assert alertas[0]["motivos"] == ["incidente"]
    assert alertas[0]["en_tu_ruta"] is True
    assert len(alertas[0]["segmentos"]) > 0


# ----------------------------------------------------------------------------------- API y roles
def test_la_api_del_conductor_y_su_control_de_acceso(client, dos_rutas, datos, monkeypatch):
    monkeypatch.setattr(router_rutas, "_servicio", lambda db: ServicioRutas(RepositorioDePrueba(db, datos), red_vial_compartida()))
    propia, ajena = dos_rutas["rutas"][0], dos_rutas["rutas"][1]
    dar_correo(conductor_de(propia))
    tok_cond = login(client, "Dev-Conductor", email=CORREO).json()["access_token"]
    tok_admin = login(client, "Dev-Cond-Admin").json()["access_token"]
    tok_op = login(client, "Dev-Cond-Op", email=EMAIL_OPERADOR, password=PASSWORD_OPERADOR).json()["access_token"]
    params = {"fecha": FECHA.isoformat(), "hora": "10:00"}

    # solo el conductor tiene "mi ruta"
    assert client.get("/api/rutas/mi-ruta", headers=auth(tok_admin), params=params).status_code == 403
    assert client.get("/api/rutas/mi-ruta", headers=auth(tok_op), params=params).status_code == 403
    assert client.get("/api/rutas/mi-ruta", params=params).status_code in (401, 403)
    ok = client.get("/api/rutas/mi-ruta", headers=auth(tok_cond), params=params)
    assert ok.status_code == 200
    assert ok.json()["ruta"]["ruta_id"] == propia["ruta_id"]
    assert client.get("/api/rutas/mi-ruta", headers=auth(tok_cond), params={"hora": "25:99"}).status_code == 422

    # y solo registra las entregas de su ruta
    url = lambda r, p: f"/api/rutas/{r['ruta_id']}/paradas/{p['paradas'][0]['pedido_id']}/entrega"  # noqa: E731
    assert client.patch(url(ajena, ajena), headers=auth(tok_cond), json={"estado": "ENTREGADO"}).status_code == 403
    propia_ok = client.patch(url(propia, propia), headers=auth(tok_cond), json={"estado": "ENTREGADO"})
    assert propia_ok.status_code == 200
    assert propia_ok.json()["estado_ruta"] == "EN_EJECUCION"
    # el conductor sigue sin acceso a lo que no es suyo
    assert client.post("/api/rutas/reoptimizar", headers=auth(tok_cond), json={"fecha_jornada": FECHA.isoformat()}).status_code == 403
    assert client.get("/api/rutas/mapa", headers=auth(tok_cond), params={"fecha": FECHA.isoformat()}).status_code == 403
