import threading
import time as reloj
import uuid
from datetime import date, datetime, time, timedelta, timezone
from functools import lru_cache

from fastapi import HTTPException, status

from src.algoritmo.modelo import Arranque, Conductor, Par, Parametros, Pedido, Problema, Vehiculo
from src.algoritmo.motor import resolver
from src.auditoria.repository import RepositorioAuditoria
from src.core.config import Settings, settings
from src.core.security import reaplicar_contexto_rls
from src.red_vial.matrices import RedVial
from src.rutas import congestion
from src.rutas.repository import RepositorioRutas
from src.rutas.trazado import trazar

PERU = timezone(timedelta(hours=-5))  # Perú no usa horario de verano
PRESUPUESTO_MINIMO_S = 1.0
# Tiempo que se deja dentro del presupuesto total para guardar las rutas y responder (RN-015: 45 s en total)
RESERVA_PERSISTENCIA_S = 5.0

# RN-012: la re-optimización debe responder en 30 s como máximo. Se apunta a 25 s para dejar holgura frente a la
# lentitud de Render y de la red (medido: el motor usa todo su presupuesto).
LIMITE_REOPTIMIZACION_S = 30.0
PRESUPUESTO_REOPTIMIZACION_S = 25.0
# El mapa vuelve a pedir el trazado cada 30 s: se guarda lo ya calculado por ruta (paradas en orden + incidentes)
_CACHE_TRAZADOS: dict = {}
_MAX_TRAZADOS_EN_CACHE = 512

# Una sola generación a la vez por proceso: el cálculo ocupa la CPU (0.1 en Render gratuito) y dos
# generaciones simultáneas se estorbarían entre sí.
BLOQUEO_GENERACION = threading.Lock()


def memoria_pico_mb() -> float | None:
    """Pico de memoria residente del proceso (solo disponible en Linux, como en Render)."""
    try:
        import resource

        return round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 1)
    except ImportError:
        return None


def hoy_en_peru() -> date:
    return datetime.now(PERU).date()


@lru_cache(maxsize=1)
def red_vial_compartida() -> RedVial:
    return RedVial.cargar(settings.factor_velocidad_urbana)


def _segundos(valor: time) -> int:
    return valor.hour * 3600 + valor.minute * 60 + valor.second


def _hora(segundos: float) -> time:
    s = min(int(round(segundos)), 86399)
    return time(s // 3600, (s % 3600) // 60, s % 60)


class ServicioRutas:
    def __init__(
        self,
        repo: RepositorioRutas,
        red_vial: RedVial | None = None,
        config: Settings = settings,
        hoy=hoy_en_peru,
        bloqueo: threading.Lock = BLOQUEO_GENERACION,
    ):
        self.repo = repo
        self.red_vial = red_vial or red_vial_compartida()
        self.config = config
        self.hoy = hoy
        self.bloqueo = bloqueo
        self.auditoria = RepositorioAuditoria(repo.session)

    # ------------------------------------------------------------------ generar
    def generar(self, fecha: date, tiempo_max_s: float | None, usuario_id: str) -> dict:
        if fecha < self.hoy():
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "La fecha de la jornada no puede ser pasada")
        if not self.bloqueo.acquire(blocking=False):
            raise HTTPException(status.HTTP_409_CONFLICT, "Ya hay una generación de rutas en curso; espere a que termine")
        try:
            return self._generar(fecha, tiempo_max_s, usuario_id)
        finally:
            self.bloqueo.release()

    def _generar(self, fecha: date, tiempo_max_s: float | None, usuario_id: str) -> dict:
        inicio = reloj.perf_counter()
        cfg = self.config
        pedidos = self.repo.pedidos_pendientes()
        vehiculos = self.repo.vehiculos_disponibles(fecha)
        conductores = self.repo.conductores_elegibles(fecha)
        incidentes = self.repo.incidentes(True)
        # Se libera la conexión antes del cálculo, que puede durar hasta 40 s (ver design.md, D3)
        self.repo.session.commit()

        puntos = [(cfg.deposito_latitud, cfg.deposito_longitud)] + [(float(p["latitud"]), float(p["longitud"])) for p in pedidos]
        t_matrices = reloj.perf_counter()
        normal, punta = congestion.factores_de_matrices(incidentes)
        matrices = self.red_vial.matrices(puntos, congestion=normal, congestion_punta=punta)
        matrices_s = reloj.perf_counter() - t_matrices

        solicitado = tiempo_max_s if tiempo_max_s is not None else cfg.optimizacion_tiempo_s
        presupuesto_total = min(solicitado, cfg.optimizacion_tiempo_max_s)
        t_lectura = t_matrices - inicio
        presupuesto_motor = max(PRESUPUESTO_MINIMO_S, presupuesto_total - (reloj.perf_counter() - inicio) - RESERVA_PERSISTENCIA_S)
        problema = Problema(
            pedidos=[
                Pedido(p["pedido_id"], float(p["peso_kg"]), p["prioridad"], _segundos(p["ventana_inicio"]), _segundos(p["ventana_fin"]))
                for p in pedidos
            ],
            vehiculos=[
                Vehiculo(v["vehiculo_id"], v["placa"], v["tipo"], float(v["capacidad_kg"]), float(v["consumo_km_l"]),
                         float(v["factor_emision_co2"]), v["estado"])
                for v in vehiculos
            ],
            conductores=[
                Conductor(c["conductor_id"], c["categoria_licencia"], c["licencia_vence"], _segundos(c["horario_inicio"]),
                          _segundos(c["horario_fin"]), c["disponible"])
                for c in conductores
            ],
            distancia_m=matrices.distancia_m,
            tiempo_s=matrices.tiempo_s,
            parametros=Parametros(
                fecha=fecha,
                hora_inicio_jornada_s=_segundos(cfg.hora_inicio_jornada),
                atencion_s=cfg.tiempo_atencion_min * 60,
                tiempo_max_s=presupuesto_motor,
                franjas_punta=congestion.FRANJAS_PUNTA,
            ),
            tiempo_punta_s=matrices.tiempo_punta_s,
        )
        t_motor = reloj.perf_counter()
        resultado = resolver(problema)
        motor_s = reloj.perf_counter() - t_motor
        sin_cobertura = [{"pedido_id": s.pedido_id, "motivo": s.motivo, "sugerencia": s.sugerencia} for s in resultado.sin_cobertura]
        base = {
            "fecha_jornada": fecha,
            "fuente_distancias": matrices.fuente,
            "puntos_aproximados": len(matrices.puntos_aproximados),
            "iteraciones": resultado.iteraciones,
            "memoria_pico_mb": memoria_pico_mb(),
        }
        tiempos = {"lectura_s": t_lectura, "matrices_s": matrices_s, "motor_s": motor_s}

        if resultado.imposible or not resultado.rutas:
            # No se toca nada: los borradores anteriores se conservan
            return base | {
                "lote_id": None, "imposible": resultado.imposible, "mensaje": resultado.mensaje, "rutas": [],
                "sin_cobertura": sin_cobertura, "comparativa_base": None,
                "tiempo_ejecucion_s": reloj.perf_counter() - inicio, "tiempos": tiempos | {"persistencia_s": 0.0},
            }

        reaplicar_contexto_rls(self.repo.session, usuario_id)
        lote_id = str(uuid.uuid4())
        self.repo.bloquear_fecha(fecha)
        self.repo.borrar_borradores(fecha)
        t_persistencia = reloj.perf_counter()
        ahorro_total_l = max(0.0, resultado.litros_base - resultado.litros)
        filas_rutas, filas_paradas, filas_metricas = [], [], []
        for ruta in resultado.rutas:
            it = ruta.itinerario
            ruta_id = str(uuid.uuid4())
            filas_rutas.append({
                "ruta_id": ruta_id, "lote_id": lote_id, "vehiculo_id": ruta.par.vehiculo.id, "conductor_id": ruta.par.conductor.id,
                "fecha_jornada": fecha, "hora_salida": _hora(it.salida_s), "hora_regreso": _hora(it.regreso_s),
                "distancia_km": it.distancia_m / 1000.0, "tiempo_min": int(round(it.duracion_s / 60)),
            })
            for parada in it.paradas:
                filas_paradas.append({
                    "ruta_id": ruta_id, "pedido_id": parada.pedido_id, "orden_entrega": parada.orden,
                    "hora_estimada": _hora(parada.llegada_s), "minutos_retraso": int(round(parada.retraso_s / 60)),
                })
            a_tiempo = sum(1 for p in it.paradas if p.retraso_s <= 0)
            proporcion = it.litros / resultado.litros if resultado.litros else 0.0
            filas_metricas.append({
                "ruta_id": ruta_id, "emision_co2_kg": it.co2_kg, "combustible_l": it.litros,
                "combustible_ahorrado_l": ahorro_total_l * proporcion, "distancia_optimizada_km": it.distancia_m / 1000.0,
                "cumplimiento_ventanas_pct": 100.0 * a_tiempo / len(it.paradas),
            })
        # Tres INSERT en bloque en lugar de uno por fila: cada consulta es un viaje a la base remota
        self.repo.crear_rutas(filas_rutas)
        self.repo.crear_paradas(filas_paradas)
        self.repo.crear_metricas(filas_metricas)
        self.auditoria.registrar(usuario_id, "ruta_generada", "rutas", lote_id)

        rutas = self._rutas_con_paradas(self.repo.rutas_del_lote(lote_id))
        comparativa = {
            "costo_base": resultado.costo_base,
            "costo": resultado.costo,
            "distancia_base_km": resultado.distancia_base_m / 1000.0,
            "distancia_km": resultado.distancia_m / 1000.0,
            "mejora_distancia_pct": resultado.mejora_distancia_pct,
            "co2_base_kg": resultado.co2_base_kg,
            "co2_kg": resultado.co2_kg,
            "mejora_co2_pct": resultado.mejora_co2_pct,
        }
        return base | {
            "lote_id": lote_id, "imposible": False, "mensaje": resultado.mensaje, "rutas": rutas,
            "sin_cobertura": sin_cobertura, "comparativa_base": comparativa,
            "tiempo_ejecucion_s": reloj.perf_counter() - inicio,
            "tiempos": tiempos | {"persistencia_s": reloj.perf_counter() - t_persistencia},
        }

    # ------------------------------------------------------------------ confirmar y descartar
    def confirmar(self, lote_id: str, usuario_id: str) -> dict:
        estados = self.repo.estados_del_lote(lote_id)
        if not estados:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Lote de rutas no encontrado")
        if any(e != "PLANIFICADA" for e in estados):
            raise HTTPException(status.HTTP_409_CONFLICT, "Las rutas de este lote ya fueron confirmadas")
        reemplazos = self.repo.reemplazos_del_lote(lote_id)
        if reemplazos:
            return self._confirmar_reemplazo(lote_id, reemplazos, usuario_id)
        no_pendientes = [p["pedido_id"] for p in self.repo.bloquear_pedidos_del_lote(lote_id) if p["estado"] != "PENDIENTE"]
        if no_pendientes:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                f"No se puede confirmar: {len(no_pendientes)} pedido(s) ya no están pendientes "
                f"({', '.join(no_pendientes[:5])}{'…' if len(no_pendientes) > 5 else ''}). Regenere las rutas.",
            )
        rutas, pedidos = self.repo.confirmar_lote(lote_id)
        self.auditoria.registrar(usuario_id, "ruta_confirmada", "rutas", lote_id)
        return {"lote_id": lote_id, "rutas_confirmadas": rutas, "pedidos_asignados": pedidos}

    def _confirmar_reemplazo(self, lote_id: str, reemplazos: list[dict], usuario_id: str) -> dict:
        """Confirma una re-optimización: las paradas pendientes de cada ruta en curso pasan a las del borrador."""
        ids = [r["reemplaza_ruta_id"] for r in reemplazos]
        originales = self.repo.bloquear_rutas_originales(ids)
        if len(originales) != len(set(ids)) or any(o["estado"] not in ("CONFIRMADA", "EN_EJECUCION") for o in originales):
            raise HTTPException(
                status.HTTP_409_CONFLICT, "Las rutas en curso cambiaron después de re-optimizar. Vuelva a re-optimizar."
            )
        invalidos = self.repo.pedidos_invalidos_del_reemplazo(lote_id)
        if invalidos:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                f"No se puede confirmar: {len(invalidos)} pedido(s) cambiaron de estado después de re-optimizar "
                "(cancelados o ya entregados). Vuelva a re-optimizar.",
            )
        rutas, nuevos = self.repo.confirmar_reemplazo(lote_id, reemplazos)
        self.auditoria.registrar(usuario_id, "reoptimizacion_confirmada", "rutas", lote_id)
        return {"lote_id": lote_id, "rutas_confirmadas": rutas, "pedidos_asignados": nuevos}

    def descartar(self, lote_id: str, usuario_id: str) -> dict:
        estados = self.repo.estados_del_lote(lote_id)
        if not estados:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Lote de rutas no encontrado")
        if any(e != "PLANIFICADA" for e in estados):
            raise HTTPException(status.HTTP_409_CONFLICT, "Las rutas confirmadas no pueden descartarse")
        eliminadas = self.repo.borrar_lote(lote_id)
        self.auditoria.registrar(usuario_id, "ruta_descartada", "rutas", lote_id)
        return {"lote_id": lote_id, "rutas_eliminadas": eliminadas}

    # ------------------------------------------------------------------ consulta
    def listar(self, fecha: date) -> list[dict]:
        return [self._a_ruta_out(r, []) for r in self.repo.rutas_de_la_fecha(fecha)]

    def detalle(self, ruta_id: str) -> dict:
        ruta = self.repo.obtener_ruta(ruta_id)
        if ruta is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Ruta no encontrada")
        return self._rutas_con_paradas([ruta])[0]

    def _rutas_con_paradas(self, rutas: list[dict]) -> list[dict]:
        paradas = self.repo.paradas_de([r["ruta_id"] for r in rutas])
        return [self._a_ruta_out(r, paradas.get(r["ruta_id"], [])) for r in rutas]

    @staticmethod
    def _a_ruta_out(r: dict, paradas: list[dict]) -> dict:
        tiene_metricas = r["emision_co2_kg"] is not None
        return {
            "ruta_id": r["ruta_id"], "lote_id": r["lote_id"], "fecha_jornada": r["fecha_jornada"], "estado": r["estado"],
            "vehiculo": {"vehiculo_id": r["vehiculo_id"], "placa": r["placa"], "tipo": r["tipo"]},
            "conductor": {"conductor_id": r["conductor_id"], "nombre": r["conductor_nombre"]},
            "hora_salida": r["hora_salida"], "hora_regreso": r["hora_regreso"], "distancia_km": r["distancia_km"],
            "tiempo_min": r["tiempo_min"], "cantidad_paradas": r["cantidad_paradas"], "reemplaza_ruta_id": r["reemplaza_ruta_id"],
            "metricas": {
                "emision_co2_kg": r["emision_co2_kg"], "combustible_l": r["combustible_l"],
                "combustible_ahorrado_l": r["combustible_ahorrado_l"], "distancia_km": r["distancia_optimizada_km"],
                "cumplimiento_ventanas_pct": r["cumplimiento_ventanas_pct"],
            } if tiene_metricas else None,
            "paradas": [
                {"orden": p["orden_entrega"], "pedido_id": p["pedido_id"], "cliente": p["cliente"], "descripcion": p["descripcion"],
                 "peso_kg": p["peso_kg"], "prioridad": p["prioridad"], "latitud": p["latitud"], "longitud": p["longitud"],
                 "hora_estimada": p["hora_estimada"], "minutos_retraso": p["minutos_retraso"], "estado_entrega": p["estado_entrega"],
                 "pedido_estado": p["pedido_estado"]}
                for p in paradas
            ],
        }

    # ------------------------------------------------------------------ re-optimizar (HU-012)
    def reoptimizar(self, fecha: date, tiempo_max_s: float | None, hora_actual: time | None, usuario_id: str) -> dict:
        if fecha < self.hoy():
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "La fecha de la jornada no puede ser pasada")
        if not self.bloqueo.acquire(blocking=False):
            raise HTTPException(status.HTTP_409_CONFLICT, "Ya hay un cálculo de rutas en curso; espere a que termine")
        try:
            return self._reoptimizar(fecha, tiempo_max_s, hora_actual, usuario_id)
        finally:
            self.bloqueo.release()

    def _reoptimizar(self, fecha: date, tiempo_max_s: float | None, hora_actual: time | None, usuario_id: str) -> dict:
        """Recalcula lo que falta de las rutas en curso: congela lo ya atendido, retira los pedidos cancelados,
        integra los pendientes nuevos y aplica los incidentes de tráfico activos. El resultado queda como
        borrador por ruta; el administrador lo confirma o lo descarta."""
        inicio = reloj.perf_counter()
        cfg = self.config
        rutas = self.repo.rutas_activas(fecha)
        base = {
            "fecha_jornada": fecha, "hora_considerada": None, "pedidos_nuevos": 0, "pedidos_retirados": 0,
            "incidentes_aplicados": [], "comparativa": None, "fuente_distancias": "calles", "iteraciones": 0,
        }
        if not rutas:
            return base | {
                "lote_id": None, "sin_rutas_activas": True, "rutas": [], "sin_cobertura": [],
                "mensaje": "No hay rutas activas para re-optimizar en esa fecha. Genere nuevas rutas desde el módulo de rutas.",
                "tiempo_ejecucion_s": reloj.perf_counter() - inicio, "dentro_del_limite": True, "tiempos": {},
            }
        paradas = self.repo.paradas_para_reoptimizar([r["ruta_id"] for r in rutas])
        nuevos = self.repo.pedidos_pendientes()
        incidentes = self.repo.incidentes(True)
        # Se libera la conexión antes del cálculo, igual que al generar
        self.repo.session.commit()

        if hora_actual is not None:
            ahora_s = _segundos(hora_actual)
        elif fecha == self.hoy():
            ahora_s = _segundos(datetime.now(PERU).time())
        else:
            ahora_s = 0  # jornada futura: todavía no empezó nada
        ahora_s = max(ahora_s, _segundos(cfg.hora_inicio_jornada))

        puntos = [(cfg.deposito_latitud, cfg.deposito_longitud)]
        pedidos: list[Pedido] = []
        vistos: set[str] = set()

        def agregar(p: dict) -> None:
            if p["pedido_id"] in vistos:
                return
            vistos.add(p["pedido_id"])
            pedidos.append(Pedido(p["pedido_id"], float(p["peso_kg"]), p["prioridad"], _segundos(p["ventana_inicio"]), _segundos(p["ventana_fin"])))
            puntos.append((float(p["latitud"]), float(p["longitud"])))

        plan: dict[str, list[str]] = {}
        retirados = 0
        for r in rutas:
            pendientes = [p for p in paradas.get(r["ruta_id"], []) if p["estado_entrega"] == "PENDIENTE"]
            vigentes = [p for p in pendientes if p["pedido_estado"] != "CANCELADO"]
            retirados += len(pendientes) - len(vigentes)
            plan[r["vehiculo_id"]] = [p["pedido_id"] for p in vigentes]
            for p in vigentes:
                agregar(p)
        antes = len(pedidos)
        for p in nuevos:
            agregar(p)
        pedidos_nuevos = len(pedidos) - antes

        # Cada vehículo parte de su última parada atendida (o del depósito si todavía no entregó nada)
        parametros = Parametros(
            fecha=fecha, hora_inicio_jornada_s=_segundos(cfg.hora_inicio_jornada), atencion_s=cfg.tiempo_atencion_min * 60,
        )
        arranques: dict[str, Arranque] = {}
        for r in rutas:
            hechas = [p for p in paradas.get(r["ruta_id"], []) if p["estado_entrega"] != "PENDIENTE"]
            if hechas:
                ultima = max(hechas, key=lambda p: p["orden_entrega"])
                nodo = len(puntos)
                puntos.append((float(ultima["latitud"]), float(ultima["longitud"])))
                salida_original = _segundos(r["hora_salida"]) if r["hora_salida"] else parametros.hora_inicio_jornada_s
                trabajo = min(max(ahora_s - salida_original, 0), parametros.descanso_cada_s)
            else:
                nodo, trabajo = 0, 0.0
            arranques[r["vehiculo_id"]] = Arranque(nodo, float(ahora_s), float(trabajo))

        t_matrices = reloj.perf_counter()
        normal, punta = congestion.factores_de_matrices(incidentes)
        matrices = self.red_vial.matrices(puntos, congestion=normal, congestion_punta=punta)
        matrices_s = reloj.perf_counter() - t_matrices

        solicitado = tiempo_max_s if tiempo_max_s is not None else PRESUPUESTO_REOPTIMIZACION_S
        presupuesto_total = min(solicitado, LIMITE_REOPTIMIZACION_S)
        presupuesto_motor = max(PRESUPUESTO_MINIMO_S, presupuesto_total - (reloj.perf_counter() - inicio) - RESERVA_PERSISTENCIA_S)
        parametros.tiempo_max_s = presupuesto_motor
        parametros.franjas_punta = congestion.FRANJAS_PUNTA
        pares = [
            Par(
                Vehiculo(r["vehiculo_id"], r["placa"], r["tipo"], float(r["capacidad_kg"]), float(r["consumo_km_l"]),
                         float(r["factor_emision_co2"]), r["vehiculo_estado"]),
                Conductor(r["conductor_id"], r["categoria_licencia"], r["licencia_vence"], _segundos(r["horario_inicio"]),
                          _segundos(r["horario_fin"]), r["disponible"]),
            )
            for r in rutas
        ]
        problema = Problema(
            pedidos=pedidos, vehiculos=[p.vehiculo for p in pares], conductores=[p.conductor for p in pares],
            distancia_m=matrices.distancia_m, tiempo_s=matrices.tiempo_s, parametros=parametros,
            pares_fijos=pares, arranques=arranques, plan_vigente=plan, tiempo_punta_s=matrices.tiempo_punta_s,
        )
        t_motor = reloj.perf_counter()
        resultado = resolver(problema)
        motor_s = reloj.perf_counter() - t_motor

        reaplicar_contexto_rls(self.repo.session, usuario_id)
        lote_id = str(uuid.uuid4())
        self.repo.bloquear_fecha(fecha)
        self.repo.borrar_borradores_de_reemplazo([r["ruta_id"] for r in rutas])
        t_persistencia = reloj.perf_counter()
        por_vehiculo = {x.par.vehiculo.id: x for x in resultado.rutas}
        ahorro_total_l = max(0.0, resultado.litros_base - resultado.litros)
        filas_rutas, filas_paradas, filas_metricas = [], [], []
        for r in rutas:
            ruta_id = str(uuid.uuid4())
            calculada = por_vehiculo.get(r["vehiculo_id"])
            if calculada is None:  # sin paradas pendientes: el borrador la deja vacía y, al confirmar, la ruta termina
                filas_rutas.append({
                    "ruta_id": ruta_id, "lote_id": lote_id, "vehiculo_id": r["vehiculo_id"], "conductor_id": r["conductor_id"],
                    "fecha_jornada": fecha, "hora_salida": _hora(ahora_s), "hora_regreso": _hora(ahora_s), "distancia_km": 0.0,
                    "tiempo_min": 0, "reemplaza_ruta_id": r["ruta_id"],
                })
                continue
            it = calculada.itinerario
            filas_rutas.append({
                "ruta_id": ruta_id, "lote_id": lote_id, "vehiculo_id": r["vehiculo_id"], "conductor_id": r["conductor_id"],
                "fecha_jornada": fecha, "hora_salida": _hora(it.salida_s), "hora_regreso": _hora(it.regreso_s),
                "distancia_km": it.distancia_m / 1000.0, "tiempo_min": int(round(it.duracion_s / 60)),
                "reemplaza_ruta_id": r["ruta_id"],
            })
            for parada in it.paradas:
                filas_paradas.append({
                    "ruta_id": ruta_id, "pedido_id": parada.pedido_id, "orden_entrega": parada.orden,
                    "hora_estimada": _hora(parada.llegada_s), "minutos_retraso": int(round(parada.retraso_s / 60)),
                })
            a_tiempo = sum(1 for p in it.paradas if p.retraso_s <= 0)
            proporcion = it.litros / resultado.litros if resultado.litros else 0.0
            filas_metricas.append({
                "ruta_id": ruta_id, "emision_co2_kg": it.co2_kg, "combustible_l": it.litros,
                "combustible_ahorrado_l": ahorro_total_l * proporcion, "distancia_optimizada_km": it.distancia_m / 1000.0,
                "cumplimiento_ventanas_pct": 100.0 * a_tiempo / len(it.paradas),
            })
        self.repo.crear_rutas_de_reemplazo(filas_rutas)
        self.repo.crear_paradas(filas_paradas)
        self.repo.crear_metricas(filas_metricas)
        self.auditoria.registrar(usuario_id, "ruta_reoptimizada", "rutas", lote_id)

        borradores = self._rutas_con_paradas(self.repo.rutas_del_lote(lote_id))
        sin_cobertura = [{"pedido_id": s.pedido_id, "motivo": s.motivo, "sugerencia": s.sugerencia} for s in resultado.sin_cobertura]
        total_s = reloj.perf_counter() - inicio
        sin_nada_que_hacer = not pedidos
        return base | {
            "lote_id": lote_id, "sin_rutas_activas": False, "rutas": borradores, "sin_cobertura": sin_cobertura,
            "mensaje": "No quedan paradas pendientes: al confirmar, las rutas terminan." if sin_nada_que_hacer else resultado.mensaje,
            "hora_considerada": _hora(ahora_s), "pedidos_nuevos": pedidos_nuevos, "pedidos_retirados": retirados,
            "incidentes_aplicados": sorted({i["calle"] for i in incidentes}),
            "comparativa": None if sin_nada_que_hacer else {
                "costo_base": resultado.costo_base, "costo": resultado.costo,
                "distancia_base_km": resultado.distancia_base_m / 1000.0, "distancia_km": resultado.distancia_m / 1000.0,
            },
            "fuente_distancias": matrices.fuente, "iteraciones": resultado.iteraciones, "tiempo_ejecucion_s": total_s,
            "dentro_del_limite": total_s <= LIMITE_REOPTIMIZACION_S,
            "tiempos": {"matrices_s": matrices_s, "motor_s": motor_s, "persistencia_s": reloj.perf_counter() - t_persistencia},
        }

    # ------------------------------------------------------------------ entregas (HU-012)
    def marcar_entrega(self, ruta_id: str, pedido_id: str, estado: str, usuario_id: str) -> dict:
        parada = self.repo.obtener_parada(ruta_id, pedido_id)
        if parada is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Parada no encontrada en esa ruta")
        if parada["estado_ruta"] not in ("CONFIRMADA", "EN_EJECUCION"):
            raise HTTPException(status.HTTP_409_CONFLICT, "La ruta no está activa: solo se registran entregas de rutas confirmadas")
        if parada["estado_entrega"] != "PENDIENTE":
            raise HTTPException(status.HTTP_409_CONFLICT, f"La parada ya fue registrada como {parada['estado_entrega']}")
        if not self.repo.marcar_entrega(ruta_id, pedido_id, estado):
            raise HTTPException(status.HTTP_409_CONFLICT, "La parada cambió mientras se registraba; vuelva a consultarla")
        if estado == "ENTREGADO":
            self.repo.marcar_pedido_entregado(pedido_id)
        estado_ruta = self.repo.actualizar_estado_de_ruta(ruta_id)
        self.auditoria.registrar(usuario_id, "entrega_registrada", "rutas", f"{ruta_id}:{pedido_id}:{estado}")
        return {"ruta_id": ruta_id, "pedido_id": pedido_id, "estado_entrega": estado, "estado_ruta": estado_ruta}

    # ------------------------------------------------------------------ incidentes de tráfico (RN-012)
    def registrar_incidente(self, calle: str, factor: float, descripcion: str | None, usuario_id: str) -> dict:
        incidente = self.repo.crear_incidente(usuario_id, calle, factor, descripcion)
        self.auditoria.registrar(usuario_id, "incidente_registrado", "rutas", incidente["incidente_id"])
        return incidente

    def listar_incidentes(self, solo_activos: bool) -> list[dict]:
        return self.repo.incidentes(solo_activos)

    def resolver_incidente(self, incidente_id: str, usuario_id: str) -> dict:
        incidente = self.repo.resolver_incidente(incidente_id)
        if incidente is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Incidente no encontrado o ya resuelto")
        self.auditoria.registrar(usuario_id, "incidente_resuelto", "rutas", incidente_id)
        return incidente

    # ------------------------------------------------------------------ mapa (HU-013)
    def mapa(self, fecha: date) -> dict:
        """Rutas de la jornada con sus paradas y el trazado por calles de cada tramo, para dibujarlas."""
        cfg = self.config
        rutas = [r for r in self.repo.rutas_de_la_fecha(fecha) if r["estado"] != "CANCELADA"]
        paradas = self.repo.paradas_de([r["ruta_id"] for r in rutas])
        incidentes = self.repo.incidentes(True)
        deposito = (cfg.deposito_latitud, cfg.deposito_longitud)
        atencion_s = cfg.tiempo_atencion_min * 60
        salida_defecto = _segundos(cfg.hora_inicio_jornada)
        grafo = self.red_vial.grafo
        salida = []
        for r in rutas:
            ps = paradas.get(r["ruta_id"], [])
            vigentes = [p for p in ps]
            clave = (r["ruta_id"], congestion.firma(incidentes), tuple((p["pedido_id"], p["orden_entrega"]) for p in vigentes), id(grafo))
            tramos = _CACHE_TRAZADOS.get(clave)
            if tramos is None:
                puntos = [deposito] + [(float(p["latitud"]), float(p["longitud"])) for p in vigentes] + [deposito]
                salidas = [float(_segundos(r["hora_salida"])) if r["hora_salida"] else float(salida_defecto)]
                salidas += [_segundos(p["hora_estimada"]) + atencion_s if p["hora_estimada"] else salidas[-1] for p in vigentes]
                tramos = trazar(grafo, puntos, salidas, incidentes, cfg.factor_velocidad_urbana)
                for i, t in enumerate(tramos):
                    t["desde"] = 0 if i == 0 else vigentes[i - 1]["orden_entrega"]
                    t["hasta"] = vigentes[i]["orden_entrega"] if i < len(vigentes) else 0
                if len(_CACHE_TRAZADOS) >= _MAX_TRAZADOS_EN_CACHE:
                    _CACHE_TRAZADOS.clear()
                _CACHE_TRAZADOS[clave] = tramos
            ruta = self._a_ruta_out(r, ps)
            salida.append({
                "ruta_id": r["ruta_id"], "lote_id": r["lote_id"], "estado": r["estado"], "reemplaza_ruta_id": r["reemplaza_ruta_id"],
                "vehiculo": ruta["vehiculo"], "conductor": ruta["conductor"], "hora_salida": r["hora_salida"],
                "hora_regreso": r["hora_regreso"], "paradas": ruta["paradas"], "tramos": tramos,
            })
        return {"fecha_jornada": fecha, "deposito": {"latitud": deposito[0], "longitud": deposito[1]}, "rutas": salida}

    def congestion(self, hora: time | None) -> dict:
        """Estado de las tres vías de la RN-012 a una hora (por defecto, la actual): nivel, motivo y su geometría."""
        segundos = _segundos(hora) if hora is not None else _segundos(datetime.now(PERU).time())
        incidentes = self.repo.incidentes(True)
        grafo = self.red_vial.grafo
        vias = []
        for via in congestion.VIAS:
            factor, motivos = congestion.factor_efectivo(via, segundos, incidentes)
            vias.append({
                "calle": via, "nivel": congestion.nivel(factor), "factor": round(factor, 2), "motivos": motivos,
                "segmentos": _segmentos_de_via(grafo, congestion.CLAVE_EN_GRAFO[via]),
            })
        return {"hora": _hora(segundos), "en_punta": congestion.en_punta(segundos), "vias": vias}


@lru_cache(maxsize=8)
def _segmentos_de_via_cache(grafo, clave: str) -> tuple:
    return tuple(
        ((round(float(a[0]), 5), round(float(a[1]), 5)), (round(float(b[0]), 5), round(float(b[1]), 5)))
        for a, b in grafo.tramos_de_calle(clave)
    )


def _segmentos_de_via(grafo, clave: str) -> list:
    """Segmentos de la vía como [[lat, lon], [lat, lon]]; la geometría no cambia, se calcula una vez por proceso."""
    if grafo is None:
        return []
    return [[list(a), list(b)] for a, b in _segmentos_de_via_cache(grafo, clave)]
