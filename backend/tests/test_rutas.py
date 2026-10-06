"""Módulo de rutas (specs `route-planning` y `route-optimization`) contra la base de datos real.

Para no alterar los datos de la usuaria, las pruebas crean sus propios clientes, pedidos, vehículos y
conductores y usan un repositorio que limita al motor a esos registros. Las rutas se generan para una
fecha lejana (hoy + 200 días), así que nunca pisan borradores reales. Al final se borra todo lo creado.
"""

import random
import threading
import uuid
from contextlib import contextmanager
from datetime import date, timedelta

import psycopg2
import pytest
from conftest import EMAIL_OPERADOR, PASSWORD_OPERADOR, UID, admin_db, auth, login
from fastapi import HTTPException
from sqlalchemy import text

from src.core.config import settings
from src.core.database import SessionLocal
from src.rutas import router as router_rutas
from src.rutas.repository import RepositorioRutas
from src.rutas.service import BLOQUEO_GENERACION, ServicioRutas, hoy_en_peru, red_vial_compartida

FECHA = hoy_en_peru() + timedelta(days=200)
PRESUPUESTO_S = 2.0


# ----------------------------------------------------------------------------------- datos de prueba
class RepositorioDePrueba(RepositorioRutas):
    """Igual que el real, pero el motor solo ve los registros creados por la prueba."""

    def __init__(self, session, datos: dict):
        super().__init__(session)
        self.datos = datos

    def pedidos_pendientes(self):
        return [p for p in super().pedidos_pendientes() if p["pedido_id"] in self.datos["pedidos"]]

    def vehiculos_disponibles(self, fecha):
        return [v for v in super().vehiculos_disponibles(fecha) if v["vehiculo_id"] in self.datos["vehiculos"]]

    def conductores_elegibles(self, fecha):
        return [c for c in super().conductores_elegibles(fecha) if c["conductor_id"] in self.datos["conductores"]]


def insertar_pedido(cliente_id: str, peso: float = 30.0, prioridad: str = "ESTANDAR") -> str:
    azar = random.Random()
    fila = admin_db(
        "INSERT INTO pedidos (cliente_id, descripcion, peso_kg, prioridad, latitud, longitud, ventana_inicio, ventana_fin) "
        "VALUES (%s, %s, %s, %s, %s, %s, '08:00', '18:00') RETURNING pedido_id",
        (cliente_id, "Pedido de prueba de rutas", peso, prioridad, azar.uniform(-12.075, -12.030), azar.uniform(-75.235, -75.190)),
        fetch=True,
    )
    return str(fila[0][0])


@pytest.fixture
def datos():
    """6 pedidos, 2 vehículos y 2 conductores propios de la prueba; se borran al terminar.

    Se preparan y se limpian con una sola conexión: abrir una por inserción hacía la suite muy lenta."""
    sufijo = uuid.uuid4().hex[:6]
    conn = psycopg2.connect(settings.database_admin_url, connect_timeout=15)
    azar = random.Random()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO clientes (nombre, tipo_negocio, latitud, longitud) VALUES (%s, 'BODEGA', -12.0653, -75.2049) RETURNING cliente_id",
            (f"Cliente rutas {sufijo}",),
        )
        cliente = str(cur.fetchone()[0])
        pedidos = []
        for i in range(6):
            cur.execute(
                "INSERT INTO pedidos (cliente_id, descripcion, peso_kg, prioridad, latitud, longitud, ventana_inicio, ventana_fin) "
                "VALUES (%s, 'Pedido de prueba de rutas', %s, 'ESTANDAR', %s, %s, '08:00', '18:00') RETURNING pedido_id",
                (cliente, 30.0 + i, azar.uniform(-12.075, -12.030), azar.uniform(-75.235, -75.190)),
            )
            pedidos.append(str(cur.fetchone()[0]))
        vehiculos, conductores = [], []
        for i in range(2):
            cur.execute(
                'INSERT INTO vehiculos (placa, tipo, capacidad_kg, consumo_km_l, factor_emision_co2, "año_fabricacion") '
                "VALUES (%s, 'CAMIONETA', 300, 10, %s, 2020) RETURNING vehiculo_id",
                (f"R{sufijo[:5]}{i}", 0.20 + 0.05 * i),
            )
            vehiculos.append(str(cur.fetchone()[0]))
            cur.execute(
                "INSERT INTO conductores (nombre, dni, categoria_licencia, telefono, licencia_vence, horario_inicio, horario_fin, "
                "consentimiento_datos, consentimiento_en) VALUES (%s, %s, 'A-IIb', '987654321', %s, '06:00', '14:00', TRUE, now()) "
                "RETURNING conductor_id",
                (f"Conductor rutas {sufijo} {i}", "9" + "".join(str(azar.randint(0, 9)) for _ in range(7)), FECHA + timedelta(days=400)),
            )
            conductores.append(str(cur.fetchone()[0]))
        conn.commit()
    finally:
        conn.close()
    d = {"cliente": cliente, "pedidos": pedidos, "vehiculos": vehiculos, "conductores": conductores}
    yield d

    conn = psycopg2.connect(settings.database_admin_url, connect_timeout=15)
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM rutas WHERE vehiculo_id = ANY(%s::uuid[]) OR conductor_id = ANY(%s::uuid[])", (d["vehiculos"], d["conductores"]))
        cur.execute("DELETE FROM ruta_pedidos WHERE pedido_id = ANY(%s::uuid[])", (d["pedidos"],))
        cur.execute("DELETE FROM pedidos WHERE pedido_id = ANY(%s::uuid[])", (d["pedidos"],))
        cur.execute("DELETE FROM clientes WHERE cliente_id = %s", (d["cliente"],))
        cur.execute("DELETE FROM vehiculos WHERE vehiculo_id = ANY(%s::uuid[])", (d["vehiculos"],))
        cur.execute("DELETE FROM conductores WHERE conductor_id = ANY(%s::uuid[])", (d["conductores"],))
        conn.commit()
    finally:
        conn.close()


@contextmanager
def servicio(datos: dict, **kwargs):
    """Servicio sobre una sesión real con la misma semántica de commit que `get_db_con_rls`."""
    session = SessionLocal()
    try:
        session.execute(text("SET LOCAL app.usuario_actual_id = :u"), {"u": UID})
        yield ServicioRutas(RepositorioDePrueba(session, datos), red_vial_compartida(), **kwargs)
        session.commit()
    except HTTPException:
        session.commit()
        raise
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def generar(datos: dict, fecha=FECHA, **kwargs) -> dict:
    with servicio(datos, **kwargs) as s:
        return s.generar(fecha, PRESUPUESTO_S, UID)


def estados_pedidos(ids) -> dict:
    filas = admin_db("SELECT pedido_id, estado FROM pedidos WHERE pedido_id = ANY(%s::uuid[])", (list(ids),), fetch=True)
    return {str(i): e for i, e in filas}


def estados_rutas(lote_id: str) -> list:
    return [f[0] for f in admin_db("SELECT estado FROM rutas WHERE lote_id = %s", (lote_id,), fetch=True)]


def ids_en_resultado(r: dict) -> list:
    return [p["pedido_id"] for x in r["rutas"] for p in x["paradas"]]


# ----------------------------------------------------------------------------------- generación
def test_generar_crea_un_borrador_y_no_cambia_los_pedidos(datos):
    r = generar(datos)
    assert r["lote_id"] and not r["imposible"]
    assert r["fuente_distancias"] == "calles"
    assert r["rutas"] and all(x["estado"] == "PLANIFICADA" for x in r["rutas"])
    assert estados_rutas(r["lote_id"]) == ["PLANIFICADA"] * len(r["rutas"])
    assert set(estados_pedidos(datos["pedidos"]).values()) == {"PENDIENTE"}
    # cada pedido aparece exactamente una vez: en una parada o sin cobertura
    cubiertos = ids_en_resultado(r) + [s["pedido_id"] for s in r["sin_cobertura"]]
    assert sorted(cubiertos) == sorted(datos["pedidos"])
    primera = r["rutas"][0]
    assert primera["metricas"]["emision_co2_kg"] > 0 and primera["paradas"][0]["orden"] == 1
    assert primera["paradas"][0]["hora_estimada"] is not None
    assert r["comparativa_base"]["costo"] <= r["comparativa_base"]["costo_base"] + 1e-9


def test_la_fecha_pasada_se_rechaza_y_no_se_crea_nada(datos):
    ayer = hoy_en_peru() - timedelta(days=1)
    with pytest.raises(HTTPException) as e:
        generar(datos, fecha=ayer)
    assert e.value.status_code == 422
    assert admin_db("SELECT count(*) FROM rutas WHERE vehiculo_id = ANY(%s::uuid[])", (datos["vehiculos"],), fetch=True)[0][0] == 0


def test_regenerar_reemplaza_el_borrador_anterior(datos):
    primero = generar(datos)
    segundo = generar(datos)
    assert segundo["lote_id"] != primero["lote_id"]
    assert estados_rutas(primero["lote_id"]) == []  # el borrador anterior ya no existe
    assert estados_rutas(segundo["lote_id"])


def test_un_pedido_mas_pesado_que_la_flota_queda_sin_cobertura(datos):
    pesado = insertar_pedido(datos["cliente"], peso=5000.0)
    datos["pedidos"].append(pesado)
    r = generar(datos)
    sin = {s["pedido_id"]: s for s in r["sin_cobertura"]}
    assert sin[pesado]["motivo"] == "PESO_EXCEDE_CAPACIDAD"
    assert "Divida" in sin[pesado]["sugerencia"]
    assert pesado not in ids_en_resultado(r)


def test_sin_vehiculos_no_hay_rutas_y_se_conservan_los_borradores_previos(datos):
    previo = generar(datos)
    datos_sin_flota = datos | {"vehiculos": []}
    r = generar(datos_sin_flota)
    assert r["imposible"] and r["lote_id"] is None and r["rutas"] == []
    assert len(r["sin_cobertura"]) == 6 and {s["motivo"] for s in r["sin_cobertura"]} == {"SIN_RECURSOS"}
    assert "no es posible" in r["mensaje"].lower()
    assert estados_rutas(previo["lote_id"])  # el borrador anterior sigue ahí


def test_un_conductor_con_la_licencia_vencida_para_esa_fecha_no_se_asigna(datos):
    admin_db("UPDATE conductores SET licencia_vence = %s WHERE conductor_id = ANY(%s::uuid[])", (FECHA, datos["conductores"]))
    r = generar(datos)
    assert r["imposible"]  # la licencia vence ese mismo día: no es válida para la jornada


def test_una_segunda_generacion_simultanea_recibe_un_conflicto(datos):
    candado = threading.Lock()
    candado.acquire()
    with pytest.raises(HTTPException) as e:
        generar(datos, bloqueo=candado)
    assert e.value.status_code == 409 and "en curso" in e.value.detail


# ----------------------------------------------------------------------------------- recursos comprometidos
def vehiculos_y_conductores_de(lote: dict) -> tuple:
    return (
        {x["vehiculo"]["vehiculo_id"] for x in lote["rutas"]},
        {x["conductor"]["conductor_id"] for x in lote["rutas"]},
    )


def confirmar(datos: dict, lote_id: str) -> None:
    with servicio(datos) as s:
        s.confirmar(lote_id, UID)


def test_un_vehiculo_y_un_conductor_confirmados_no_se_reasignan_el_mismo_dia(datos):
    todos = list(datos["pedidos"])
    datos["pedidos"] = todos[:2]  # dos pedidos livianos caben en un solo vehículo
    primero = generar(datos)
    vehiculos_1, conductores_1 = vehiculos_y_conductores_de(primero)
    assert len(vehiculos_1) == 1
    confirmar(datos, primero["lote_id"])

    datos["pedidos"] = todos  # llegan los demás pedidos y se regenera para la misma fecha
    segundo = generar(datos)
    vehiculos_2, conductores_2 = vehiculos_y_conductores_de(segundo)
    assert segundo["rutas"] and not segundo["imposible"]
    assert vehiculos_2.isdisjoint(vehiculos_1) and conductores_2.isdisjoint(conductores_1)
    assert set(estados_rutas(primero["lote_id"])) == {"CONFIRMADA"}


def test_si_todos_los_recursos_estan_comprometidos_no_se_puede_generar_y_lo_confirmado_se_conserva(datos):
    admin_db("UPDATE pedidos SET peso_kg = 100 WHERE pedido_id = ANY(%s::uuid[])", (datos["pedidos"],))  # 6 × 100 kg = 2 × 300 kg
    primero = generar(datos)
    vehiculos_1, _ = vehiculos_y_conductores_de(primero)
    assert len(vehiculos_1) == 2 and not primero["sin_cobertura"]
    confirmar(datos, primero["lote_id"])

    nuevos = [insertar_pedido(datos["cliente"]) for _ in range(2)]
    datos["pedidos"].extend(nuevos)
    segundo = generar(datos)
    assert segundo["imposible"] and segundo["lote_id"] is None and segundo["rutas"] == []
    assert {s["pedido_id"] for s in segundo["sin_cobertura"]} == set(nuevos)
    assert {s["motivo"] for s in segundo["sin_cobertura"]} == {"SIN_RECURSOS"}
    assert set(estados_rutas(primero["lote_id"])) == {"CONFIRMADA"}


def test_los_recursos_comprometidos_un_dia_siguen_libres_para_otra_fecha(datos):
    primero = generar(datos)
    confirmar(datos, primero["lote_id"])
    nuevo = insertar_pedido(datos["cliente"])
    datos["pedidos"].append(nuevo)  # para que la limpieza lo borre
    otro_dia = generar(datos | {"pedidos": [nuevo]}, fecha=FECHA + timedelta(days=1))
    assert otro_dia["rutas"] and not otro_dia["imposible"]


def test_un_borrador_no_compromete_recursos(datos):
    primero = generar(datos)
    segundo = generar(datos)  # regenerar: el borrador anterior se reemplaza y sus recursos vuelven a estar libres
    assert not segundo["imposible"]
    assert vehiculos_y_conductores_de(segundo)[0] == vehiculos_y_conductores_de(primero)[0]


# ----------------------------------------------------------------------------------- confirmar y descartar
def test_confirmar_pasa_las_rutas_a_confirmada_y_los_pedidos_a_asignado(datos):
    r = generar(datos)
    with servicio(datos) as s:
        c = s.confirmar(r["lote_id"], UID)
    assert c["rutas_confirmadas"] == len(r["rutas"]) and c["pedidos_asignados"] == len(ids_en_resultado(r))
    assert set(estados_rutas(r["lote_id"])) == {"CONFIRMADA"}
    estados = estados_pedidos(datos["pedidos"])
    for pid in datos["pedidos"]:
        assert estados[pid] == ("ASIGNADO" if pid in ids_en_resultado(r) else "PENDIENTE")
    auditoria = admin_db("SELECT count(*) FROM logs_auditoria WHERE accion = 'ruta_confirmada' AND detalle = %s", (r["lote_id"],), fetch=True)
    assert auditoria[0][0] == 1


def test_la_auditoria_de_la_generacion_guarda_solo_el_lote(datos):
    r = generar(datos)
    filas = admin_db("SELECT detalle FROM logs_auditoria WHERE accion = 'ruta_generada' AND detalle = %s", (r["lote_id"],), fetch=True)
    assert len(filas) == 1  # el detalle es el identificador del lote, sin nombres ni DNI de conductores


def test_confirmar_se_rechaza_si_un_pedido_fue_cancelado_durante_la_revision(datos):
    r = generar(datos)
    cancelado = ids_en_resultado(r)[0]
    admin_db("UPDATE pedidos SET estado = 'CANCELADO' WHERE pedido_id = %s", (cancelado,))
    with pytest.raises(HTTPException) as e:
        with servicio(datos) as s:
            s.confirmar(r["lote_id"], UID)
    assert e.value.status_code == 409 and cancelado in e.value.detail and "Regenere" in e.value.detail
    assert set(estados_rutas(r["lote_id"])) == {"PLANIFICADA"}  # nada cambió
    assert "ASIGNADO" not in estados_pedidos(datos["pedidos"]).values()


def test_confirmar_dos_veces_o_un_lote_inexistente_se_rechaza(datos):
    r = generar(datos)
    with servicio(datos) as s:
        s.confirmar(r["lote_id"], UID)
    with pytest.raises(HTTPException) as e:
        with servicio(datos) as s:
            s.confirmar(r["lote_id"], UID)
    assert e.value.status_code == 409
    with pytest.raises(HTTPException) as e:
        with servicio(datos) as s:
            s.confirmar(str(uuid.uuid4()), UID)
    assert e.value.status_code == 404


def test_regenerar_no_toca_las_rutas_confirmadas_y_solo_considera_pedidos_pendientes(datos):
    primero = generar(datos)
    with servicio(datos) as s:
        s.confirmar(primero["lote_id"], UID)
    confirmados = set(ids_en_resultado(primero))
    nuevos = [insertar_pedido(datos["cliente"]) for _ in range(2)]
    datos["pedidos"].extend(nuevos)
    segundo = generar(datos)
    assert set(estados_rutas(primero["lote_id"])) == {"CONFIRMADA"}  # intactas
    en_borrador = set(ids_en_resultado(segundo)) | {s["pedido_id"] for s in segundo["sin_cobertura"]}
    assert en_borrador.isdisjoint(confirmados)
    assert set(nuevos) <= en_borrador


def test_descartar_elimina_el_borrador_y_deja_los_pedidos_pendientes(datos):
    r = generar(datos)
    with servicio(datos) as s:
        d = s.descartar(r["lote_id"], UID)
    assert d["rutas_eliminadas"] == len(r["rutas"])
    assert estados_rutas(r["lote_id"]) == []
    assert set(estados_pedidos(datos["pedidos"]).values()) == {"PENDIENTE"}


def test_las_rutas_confirmadas_no_se_pueden_descartar(datos):
    r = generar(datos)
    with servicio(datos) as s:
        s.confirmar(r["lote_id"], UID)
    with pytest.raises(HTTPException) as e:
        with servicio(datos) as s:
            s.descartar(r["lote_id"], UID)
    assert e.value.status_code == 409 and "confirmadas" in e.value.detail


# ----------------------------------------------------------------------------------- API HTTP
def test_el_flujo_completo_por_la_api_y_el_control_de_acceso_por_rol(client, datos, monkeypatch):
    monkeypatch.setattr(router_rutas, "_servicio", lambda db: ServicioRutas(RepositorioDePrueba(db, datos), red_vial_compartida()))
    tok_admin = login(client, "Dev-Rutas").json()["access_token"]
    tok_op = login(client, "Dev-Rutas-Op", email=EMAIL_OPERADOR, password=PASSWORD_OPERADOR).json()["access_token"]

    # El Operador no puede generar, confirmar ni descartar
    assert client.post("/api/rutas/generar", headers=auth(tok_op), json={"fecha_jornada": FECHA.isoformat()}).status_code == 403
    assert client.post(f"/api/rutas/lotes/{uuid.uuid4()}/confirmar", headers=auth(tok_op)).status_code == 403
    assert client.delete(f"/api/rutas/lotes/{uuid.uuid4()}", headers=auth(tok_op)).status_code == 403

    # El Administrador genera un borrador
    r = client.post("/api/rutas/generar", headers=auth(tok_admin), json={"fecha_jornada": FECHA.isoformat(), "tiempo_max_s": PRESUPUESTO_S})
    assert r.status_code == 201
    cuerpo = r.json()
    lote = cuerpo["lote_id"]
    assert cuerpo["rutas"] and cuerpo["fuente_distancias"] == "calles" and cuerpo["tiempo_ejecucion_s"] > 0

    # El Operador consulta el listado y el detalle
    lista = client.get("/api/rutas", headers=auth(tok_op), params={"fecha": FECHA.isoformat()})
    assert lista.status_code == 200
    propias = [x for x in lista.json() if x["lote_id"] == lote]
    assert len(propias) == len(cuerpo["rutas"]) and propias[0]["estado"] == "PLANIFICADA" and propias[0]["paradas"] == []
    detalle = client.get(f"/api/rutas/{propias[0]['ruta_id']}", headers=auth(tok_op))
    assert detalle.status_code == 200 and detalle.json()["paradas"] and detalle.json()["conductor"]["nombre"].startswith("Conductor rutas")

    # El Administrador confirma; después ya no se puede descartar
    assert client.post(f"/api/rutas/lotes/{lote}/confirmar", headers=auth(tok_admin)).status_code == 200
    assert client.get(f"/api/rutas/{propias[0]['ruta_id']}", headers=auth(tok_op)).json()["estado"] == "CONFIRMADA"
    assert client.delete(f"/api/rutas/lotes/{lote}", headers=auth(tok_admin)).status_code == 409


def test_la_api_valida_la_fecha_el_identificador_y_la_autenticacion(client):
    tok_admin = login(client, "Dev-Rutas-2").json()["access_token"]
    ayer = (hoy_en_peru() - timedelta(days=1)).isoformat()
    assert client.post("/api/rutas/generar", headers=auth(tok_admin), json={"fecha_jornada": ayer}).status_code == 422
    assert client.post("/api/rutas/generar", headers=auth(tok_admin), json={"fecha_jornada": "no-es-fecha"}).status_code == 422
    assert client.post("/api/rutas/lotes/no-es-un-uuid/confirmar", headers=auth(tok_admin)).status_code == 422
    assert client.get(f"/api/rutas/{uuid.uuid4()}", headers=auth(tok_admin)).status_code == 404
    assert client.post(f"/api/rutas/lotes/{uuid.uuid4()}/confirmar", headers=auth(tok_admin)).status_code == 404
    assert client.get("/api/rutas", params={"fecha": FECHA.isoformat()}).status_code == 401


def test_la_api_responde_conflicto_si_hay_una_generacion_en_curso(client):
    tok_admin = login(client, "Dev-Rutas-3").json()["access_token"]
    BLOQUEO_GENERACION.acquire()
    try:
        r = client.post("/api/rutas/generar", headers=auth(tok_admin), json={"fecha_jornada": FECHA.isoformat()})
    finally:
        BLOQUEO_GENERACION.release()
    assert r.status_code == 409 and "en curso" in r.json()["detail"]


def test_la_generacion_con_los_datos_reales_responde_con_la_estructura_esperada(client):
    """Sin conductores reales la respuesta es 'imposible'; si los hubiera, se limpia el borrador creado."""
    tok_admin = login(client, "Dev-Rutas-4").json()["access_token"]
    r = client.post("/api/rutas/generar", headers=auth(tok_admin), json={"fecha_jornada": FECHA.isoformat(), "tiempo_max_s": PRESUPUESTO_S})
    assert r.status_code == 201
    cuerpo = r.json()
    assert {"lote_id", "imposible", "mensaje", "rutas", "sin_cobertura", "fuente_distancias", "comparativa_base"} <= cuerpo.keys()
    if cuerpo["lote_id"]:
        assert client.delete(f"/api/rutas/lotes/{cuerpo['lote_id']}", headers=auth(tok_admin)).status_code == 200
