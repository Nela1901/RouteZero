"""Auditoría de las consultas críticas de la API (HT-11, RNF-011): tiempo en la base y tipo de recorrido de tablas.

Con las tablas casi vacías de un entorno de desarrollo, PostgreSQL siempre elige recorrer la tabla completa y
cualquier consulta parece rápida. Por eso el script carga, DENTRO DE UNA TRANSACCIÓN QUE AL FINAL SE DESHACE,
un volumen parecido al de seis meses de operación (2 700 rutas, 16 200 pedidos entregados, 150 pendientes),
actualiza las estadísticas y mide cada consulta con `EXPLAIN (ANALYZE)`. Nada queda guardado.

Uso, desde `backend/`:  python scripts/auditar_consultas.py   (usa DATABASE_ADMIN_URL del .env)

Para cada consulta informa el tiempo de ejecución en el servidor (mejor de 3 corridas, sin la latencia de red),
si recorre completa una tabla grande («seq scan») y, con los recorridos completos desactivados, si existe un
índice que la resuelva. Sale con código 1 si alguna consulta supera el umbral de 500 ms o recorre completa una
tabla de más de 1 000 filas sin que exista un índice utilizable.
"""

import json
import sys
from datetime import date
from pathlib import Path

import psycopg2

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.core.config import settings  # noqa: E402

UMBRAL_MS = 500.0
FILAS_TABLA_GRANDE = 1000
CORRIDAS = 3
DIAS, RUTAS_POR_DIA, PARADAS_POR_RUTA, PEDIDOS_PENDIENTES = 180, 15, 6, 150


def cargar_volumen(cur) -> dict:
    """Inserta el volumen sintético (se deshace al final) y devuelve identificadores útiles para las consultas."""
    cur.execute("SELECT vehiculo_id FROM vehiculos ORDER BY placa LIMIT 1")
    vehiculo = cur.fetchone()[0]
    cur.execute("SELECT conductor_id, usuario_id FROM conductores ORDER BY dni LIMIT 1")
    conductor, usuario_conductor = cur.fetchone()
    cur.execute(
        "INSERT INTO clientes (nombre, tipo_negocio, latitud, longitud) VALUES ('auditoria-consultas', 'BODEGA', -12.0653, -75.2049) RETURNING cliente_id"
    )
    cliente = cur.fetchone()[0]
    total_historico = DIAS * RUTAS_POR_DIA * PARADAS_POR_RUTA
    cur.execute(
        "INSERT INTO pedidos (cliente_id, descripcion, peso_kg, prioridad, latitud, longitud, ventana_inicio, ventana_fin, estado, creado_en) "
        "SELECT %s, 'auditoria', 20 + (g %% 40), (ARRAY['EXPRESS','ESTANDAR','ECONOMICO'])[1 + g %% 3], -12.07 + (g %% 400) / 10000.0, "
        "-75.23 + (g %% 300) / 10000.0, '08:00', '18:00', 'ENTREGADO', now() - (g || ' minutes')::interval FROM generate_series(1, %s) g",
        (cliente, total_historico),
    )
    cur.execute(
        "INSERT INTO pedidos (cliente_id, descripcion, peso_kg, prioridad, latitud, longitud, ventana_inicio, ventana_fin, estado) "
        "SELECT %s, 'auditoria', 20 + (g %% 40), (ARRAY['EXPRESS','ESTANDAR','ECONOMICO'])[1 + g %% 3], -12.07 + (g %% 400) / 10000.0, "
        "-75.23 + (g %% 300) / 10000.0, '08:00', '18:00', 'PENDIENTE' FROM generate_series(1, %s) g",
        (cliente, PEDIDOS_PENDIENTES),
    )
    cur.execute(
        "INSERT INTO rutas (lote_id, vehiculo_id, conductor_id, fecha_jornada, hora_salida, hora_regreso, distancia_km, tiempo_min, estado) "
        "SELECT gen_random_uuid(), %s, %s, current_date - (d || ' days')::interval, '08:00', '14:00', 40, 360, 'COMPLETADA' "
        "FROM generate_series(1, %s) d, generate_series(1, %s) r",
        (vehiculo, conductor, DIAS, RUTAS_POR_DIA),
    )
    cur.execute(
        "INSERT INTO metricas_sostenibilidad (ruta_id, emision_co2_kg, combustible_l, combustible_ahorrado_l, distancia_optimizada_km, cumplimiento_ventanas_pct) "
        "SELECT ruta_id, 10, 4, 0.5, 40, 95 FROM rutas WHERE vehiculo_id = %s AND distancia_km = 40 AND estado = 'COMPLETADA' "
        "AND ruta_id NOT IN (SELECT ruta_id FROM metricas_sostenibilidad)",
        (vehiculo,),
    )
    cur.execute(
        "INSERT INTO ruta_pedidos (ruta_id, pedido_id, orden_entrega, estado_entrega) "
        "SELECT r.ruta_id, p.pedido_id, ((p.n - 1) %% %s) + 1, 'ENTREGADO' FROM "
        "(SELECT ruta_id, row_number() OVER (ORDER BY ruta_id) AS n FROM rutas WHERE vehiculo_id = %s AND distancia_km = 40 AND estado = 'COMPLETADA') r "
        "JOIN (SELECT pedido_id, row_number() OVER (ORDER BY creado_en) AS n FROM pedidos WHERE descripcion = 'auditoria' AND estado = 'ENTREGADO') p "
        "ON p.n BETWEEN (r.n - 1) * %s + 1 AND r.n * %s",
        (PARADAS_POR_RUTA, vehiculo, PARADAS_POR_RUTA, PARADAS_POR_RUTA),
    )
    for tabla in ("pedidos", "rutas", "ruta_pedidos", "metricas_sostenibilidad", "logs_auditoria", "sesiones_activas"):
        cur.execute(f"ANALYZE {tabla}")  # nosec B608: nombres fijos de este script
    cur.execute("SELECT ruta_id FROM rutas WHERE vehiculo_id = %s AND distancia_km = 40 ORDER BY ruta_id LIMIT 15", (vehiculo,))
    rutas_dia = [str(r[0]) for r in cur.fetchall()]
    cur.execute("SELECT usuario_id FROM sesiones_activas LIMIT 1")
    fila = cur.fetchone()
    cur.execute("SELECT supabase_session_id FROM sesiones_activas LIMIT 1")
    sesion = cur.fetchone()
    return {
        "hoy": date.today(), "hace_un_mes": date.fromordinal(date.today().toordinal() - 30), "hace_un_anio": date.fromordinal(date.today().toordinal() - 365),
        "rutas_dia": rutas_dia, "lote": None, "usuario": str(fila[0]) if fila else None, "sesion": sesion[0] if sesion else None,
        "usuario_conductor": str(usuario_conductor) if usuario_conductor else None, "conductor": str(conductor),
    }


def consultas(c: dict) -> list[tuple[str, str, dict]]:
    """Las consultas más usadas, copiadas de los repositorios (mismos filtros y ordenamientos)."""
    p = {"hoy": c["hoy"], "mes": c["hace_un_mes"], "anio": c["hace_un_anio"], "ids": c["rutas_dia"], "conductor": c["conductor"]}
    return [
        ("Generación: pedidos pendientes", "SELECT pedido_id, peso_kg, prioridad, latitud, longitud, ventana_inicio, ventana_fin FROM pedidos WHERE estado = 'PENDIENTE' ORDER BY creado_en, pedido_id", p),
        ("Generación: vehículos disponibles", "SELECT vehiculo_id, placa, tipo, capacidad_kg, consumo_km_l, factor_emision_co2, estado FROM vehiculos WHERE estado = 'DISPONIBLE' AND vehiculo_id NOT IN (SELECT vehiculo_id FROM rutas WHERE fecha_jornada = %(hoy)s AND estado IN ('CONFIRMADA', 'EN_EJECUCION')) ORDER BY placa", p),
        ("Generación: conductores elegibles", "SELECT conductor_id, categoria_licencia, licencia_vence, horario_inicio, horario_fin, disponible FROM conductores WHERE disponible AND licencia_vence > %(hoy)s AND conductor_id NOT IN (SELECT conductor_id FROM rutas WHERE fecha_jornada = %(hoy)s AND estado IN ('CONFIRMADA', 'EN_EJECUCION')) ORDER BY dni", p),
        ("Rutas activas de la fecha (re-optimizar)", "SELECT r.ruta_id, r.estado, v.placa, c.nombre FROM rutas r JOIN vehiculos v ON v.vehiculo_id = r.vehiculo_id JOIN conductores c ON c.conductor_id = r.conductor_id WHERE r.fecha_jornada = %(mes)s AND r.estado IN ('CONFIRMADA', 'EN_EJECUCION') ORDER BY v.placa", p),
        ("Listado de rutas de una fecha", "SELECT r.ruta_id, r.estado, v.placa, c.nombre, m.emision_co2_kg, (SELECT count(*) FROM ruta_pedidos rp WHERE rp.ruta_id = r.ruta_id) FROM rutas r JOIN vehiculos v ON v.vehiculo_id = r.vehiculo_id JOIN conductores c ON c.conductor_id = r.conductor_id LEFT JOIN metricas_sostenibilidad m ON m.ruta_id = r.ruta_id WHERE r.fecha_jornada = %(mes)s ORDER BY r.creado_en", p),
        ("Paradas de las rutas de un día", "SELECT rp.ruta_id, rp.orden_entrega, rp.pedido_id, p.latitud, p.longitud, cl.nombre FROM ruta_pedidos rp JOIN pedidos p ON p.pedido_id = rp.pedido_id JOIN clientes cl ON cl.cliente_id = p.cliente_id WHERE rp.ruta_id = ANY(%(ids)s::uuid[]) ORDER BY rp.ruta_id, rp.orden_entrega", p),
        ("Ruta del conductor (mi-ruta)", "SELECT r.ruta_id, r.estado FROM rutas r WHERE r.conductor_id = %(conductor)s AND r.fecha_jornada = %(mes)s", p),
        ("Listado de pedidos paginado", "SELECT pedido_id, estado, prioridad FROM pedidos ORDER BY creado_en DESC, pedido_id LIMIT 50 OFFSET 0", p),
        ("Listado de pedidos por estado", "SELECT pedido_id, estado, prioridad FROM pedidos WHERE estado = 'PENDIENTE' ORDER BY creado_en DESC, pedido_id LIMIT 50 OFFSET 0", p),
        ("Dashboard: totales de 30 días", "SELECT COUNT(*), SUM(m.distancia_optimizada_km), SUM(m.emision_co2_kg), SUM(m.cumplimiento_ventanas_pct * p.paradas), SUM(p.paradas) FROM rutas r JOIN metricas_sostenibilidad m ON m.ruta_id = r.ruta_id JOIN LATERAL (SELECT COUNT(*) AS paradas FROM ruta_pedidos rp WHERE rp.ruta_id = r.ruta_id) p ON TRUE WHERE r.estado = ANY(ARRAY['CONFIRMADA','EN_EJECUCION','COMPLETADA']) AND r.fecha_jornada BETWEEN %(mes)s AND %(hoy)s", p),
        ("Dashboard: emisiones por día (30 días)", "SELECT r.fecha_jornada, SUM(m.emision_co2_kg) FROM rutas r JOIN metricas_sostenibilidad m ON m.ruta_id = r.ruta_id WHERE r.estado = ANY(ARRAY['CONFIRMADA','EN_EJECUCION','COMPLETADA']) AND r.fecha_jornada BETWEEN %(mes)s AND %(hoy)s GROUP BY r.fecha_jornada ORDER BY r.fecha_jornada", p),
        ("Dashboard: entregas (30 días)", "SELECT rp.estado_entrega, COUNT(*) FROM ruta_pedidos rp JOIN rutas r ON r.ruta_id = rp.ruta_id JOIN pedidos pe ON pe.pedido_id = rp.pedido_id WHERE r.estado = ANY(ARRAY['CONFIRMADA','EN_EJECUCION','COMPLETADA']) AND r.fecha_jornada BETWEEN %(mes)s AND %(hoy)s AND pe.estado <> 'CANCELADO' GROUP BY rp.estado_entrega", p),
        ("Reporte: rutas del periodo (30 días)", "SELECT r.fecha_jornada, v.placa, c.nombre, p.paradas, m.distancia_optimizada_km, m.emision_co2_kg FROM rutas r JOIN metricas_sostenibilidad m ON m.ruta_id = r.ruta_id JOIN vehiculos v ON v.vehiculo_id = r.vehiculo_id JOIN conductores c ON c.conductor_id = r.conductor_id JOIN LATERAL (SELECT COUNT(*) AS paradas FROM ruta_pedidos rp WHERE rp.ruta_id = r.ruta_id) p ON TRUE WHERE r.estado = ANY(ARRAY['CONFIRMADA','EN_EJECUCION','COMPLETADA']) AND r.fecha_jornada BETWEEN %(mes)s AND %(hoy)s ORDER BY r.fecha_jornada DESC, v.placa LIMIT 300", p),
        ("Reporte: costo de la flota (30 días)", "SELECT v.placa, v.precio_compra_soles, COALESCE(SUM(m.combustible_l), 0) FROM vehiculos v LEFT JOIN rutas r ON r.vehiculo_id = v.vehiculo_id AND r.estado = ANY(ARRAY['CONFIRMADA','EN_EJECUCION','COMPLETADA']) AND r.fecha_jornada BETWEEN %(mes)s AND %(hoy)s LEFT JOIN metricas_sostenibilidad m ON m.ruta_id = r.ruta_id GROUP BY v.vehiculo_id HAVING v.estado <> 'INACTIVO' OR COALESCE(SUM(m.combustible_l), 0) > 0 ORDER BY v.placa", p),
        ("Auditoría: últimos registros de un módulo", "SELECT log_id, accion, detalle, creado_en FROM logs_auditoria WHERE modulo = 'auth' ORDER BY creado_en DESC LIMIT 100", p),
        ("Auditoría: módulo poco frecuente", "SELECT log_id, accion, detalle, creado_en FROM logs_auditoria WHERE modulo = 'sostenibilidad' ORDER BY creado_en DESC LIMIT 100", p),
        ("Sesiones activas de un usuario", "SELECT sesion_id, dispositivo_info, creado_en FROM sesiones_activas WHERE usuario_id = %(usuario)s AND estado = 'ACTIVA' ORDER BY ultimo_uso_en DESC", {**p, "usuario": c["usuario"]}),
        ("Renovación de sesión (por sesión de Supabase)", "SELECT sesion_id, refresh_token_hash FROM sesiones_activas WHERE supabase_session_id = %(sesion)s FOR UPDATE", {**p, "sesion": c["sesion"]}),
    ]


def recorrer(plan: dict, nodos: list | None = None) -> list[dict]:
    nodos = [] if nodos is None else nodos
    nodos.append(plan)
    for hijo in plan.get("Plans", []):
        recorrer(hijo, nodos)
    return nodos


def explicar(cur, sql: str, params: dict) -> tuple[float, list[dict]]:
    cur.execute("EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) " + sql, params)
    raiz = cur.fetchone()[0]
    raiz = raiz if isinstance(raiz, list) else json.loads(raiz)
    return raiz[0]["Execution Time"], recorrer(raiz[0]["Plan"])


def main() -> int:
    conn = psycopg2.connect(settings.database_admin_url, connect_timeout=20)
    conn.autocommit = False
    cur = conn.cursor()
    problemas = 0
    try:
        cur.execute("SET LOCAL statement_timeout = '120s'")
        contexto = cargar_volumen(cur)
        for tabla in ("pedidos", "rutas", "ruta_pedidos", "metricas_sostenibilidad", "logs_auditoria", "sesiones_activas"):
            cur.execute(f"SELECT count(*) FROM {tabla}")  # nosec B608: nombres fijos de este script
            print(f"  {tabla:<26}{cur.fetchone()[0]:>8} filas")
        print()
        print(f"{'Consulta':<48}{'ms':>8}  {'Recorrido completo':<40}Índice disponible")
        print("-" * 118)
        for nombre, sql, params in consultas(contexto):
            tiempos = []
            for _ in range(CORRIDAS):
                ms, nodos = explicar(cur, sql, params)
                tiempos.append(ms)
            grandes = sorted({n["Relation Name"] for n in nodos if n["Node Type"] == "Seq Scan" and n.get("Actual Rows", 0) * max(n.get("Actual Loops", 1), 1) >= 0
                              and _filas_de(cur, n["Relation Name"]) > FILAS_TABLA_GRANDE})
            cur.execute("SET LOCAL enable_seqscan = off")
            _, con_indice = explicar(cur, sql, params)
            cur.execute("SET LOCAL enable_seqscan = on")
            indices = sorted({n["Index Name"] for n in con_indice if "Index Name" in n})
            marca = ""
            if min(tiempos) > UMBRAL_MS:
                marca, problemas = " <- supera 500 ms", problemas + 1
            if grandes and not indices:
                marca, problemas = marca + " <- sin índice", problemas + 1
            print(f"{nombre:<48}{min(tiempos):>8.1f}  {', '.join(grandes) or '-':<40}{', '.join(indices) or '-'}{marca}")
    finally:
        conn.rollback()  # el volumen de prueba nunca se guarda
        conn.close()
    print(f"\n{'Sin problemas' if not problemas else str(problemas) + ' problema(s) a revisar'}: umbral {UMBRAL_MS:.0f} ms. La transacción se deshizo.")
    return 1 if problemas else 0


_cache_filas: dict[str, int] = {}


def _filas_de(cur, tabla: str) -> int:
    if tabla not in _cache_filas:
        cur.execute("SELECT reltuples::bigint FROM pg_class WHERE relname = %s", (tabla,))
        _cache_filas[tabla] = max(cur.fetchone()[0], 0)
    return _cache_filas[tabla]


if __name__ == "__main__":
    sys.exit(main())
