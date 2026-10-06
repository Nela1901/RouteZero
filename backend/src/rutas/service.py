import threading
import time as reloj
import uuid
from datetime import date, datetime, time, timedelta, timezone
from functools import lru_cache

from fastapi import HTTPException, status

from src.algoritmo.modelo import Conductor, Parametros, Pedido, Problema, Vehiculo
from src.algoritmo.motor import resolver
from src.auditoria.repository import RepositorioAuditoria
from src.core.config import Settings, settings
from src.core.security import reaplicar_contexto_rls
from src.red_vial.matrices import RedVial
from src.rutas.repository import RepositorioRutas

PERU = timezone(timedelta(hours=-5))  # Perú no usa horario de verano
PRESUPUESTO_MINIMO_S = 1.0
# Tiempo que se deja dentro del presupuesto total para guardar las rutas y responder (RN-015: 45 s en total)
RESERVA_PERSISTENCIA_S = 5.0

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
        # Se libera la conexión antes del cálculo, que puede durar hasta 40 s (ver design.md, D3)
        self.repo.session.commit()

        puntos = [(cfg.deposito_latitud, cfg.deposito_longitud)] + [(float(p["latitud"]), float(p["longitud"])) for p in pedidos]
        t_matrices = reloj.perf_counter()
        matrices = self.red_vial.matrices(puntos)
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
            ),
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
            "tiempo_min": r["tiempo_min"], "cantidad_paradas": r["cantidad_paradas"],
            "metricas": {
                "emision_co2_kg": r["emision_co2_kg"], "combustible_l": r["combustible_l"],
                "combustible_ahorrado_l": r["combustible_ahorrado_l"], "distancia_km": r["distancia_optimizada_km"],
                "cumplimiento_ventanas_pct": r["cumplimiento_ventanas_pct"],
            } if tiene_metricas else None,
            "paradas": [
                {"orden": p["orden_entrega"], "pedido_id": p["pedido_id"], "cliente": p["cliente"], "descripcion": p["descripcion"],
                 "peso_kg": p["peso_kg"], "prioridad": p["prioridad"], "latitud": p["latitud"], "longitud": p["longitud"],
                 "hora_estimada": p["hora_estimada"], "minutos_retraso": p["minutos_retraso"]}
                for p in paradas
            ],
        }
