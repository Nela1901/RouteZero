"""Reporte de sostenibilidad en PDF (HU-016). Recibe los datos ya calculados por el servicio y devuelve los bytes.

Usa las fuentes básicas del PDF (Helvetica), que solo cubren Latin-1: por eso se escribe «CO2» sin subíndice y
todo texto pasa por `_t`, que reemplaza lo que no se pueda representar en vez de fallar."""

from fpdf import FPDF
from fpdf.enums import XPos, YPos

EMPRESA = "Andina Reparto S.A.C."
GRIS = (90, 90, 90)
VERDE = (22, 101, 52)
AVISO = (146, 64, 14)


def _t(texto: object) -> str:
    return str(texto).encode("latin-1", "replace").decode("latin-1")


def _n(valor: float | None, decimales: int = 1) -> str:
    return "sin dato" if valor is None else f"{valor:,.{decimales}f}"


def _soles(valor: float | None) -> str:
    return "sin dato" if valor is None else f"S/ {valor:,.2f}"


class _Documento(FPDF):
    def footer(self) -> None:
        self.set_y(-14)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*GRIS)
        self.cell(0, 8, _t(f"RouteZero - {EMPRESA} - Página {self.page_no()} de {{nb}}"), align="C")


def _titulo(pdf: FPDF, texto: str) -> None:
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(*VERDE)
    pdf.cell(0, 8, _t(texto), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 9.5)


def _parrafo(pdf: FPDF, texto: str, color: tuple[int, int, int] = (0, 0, 0)) -> None:
    pdf.set_text_color(*color)
    pdf.multi_cell(0, 5, _t(texto), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_text_color(0, 0, 0)


def _tabla(pdf: FPDF, cabecera: list[str], filas: list[list[str]], anchos: tuple[float, ...], derecha_desde: int = 1) -> None:
    pdf.set_font("Helvetica", "", 8.5)
    alineacion = tuple("LEFT" if i < derecha_desde else "RIGHT" for i in range(len(cabecera)))
    with pdf.table(col_widths=anchos, text_align=alineacion, line_height=5.5) as tabla:  # la primera fila es el encabezado
        encabezado = tabla.row()
        for c in cabecera:
            encabezado.cell(_t(c))
        for fila in filas:
            r = tabla.row()
            for c in fila:
                r.cell(_t(c))
    pdf.set_font("Helvetica", "", 9.5)


def generar_pdf(datos: dict) -> bytes:
    """Dibuja el reporte completo. `datos` es lo que devuelve `ServicioSostenibilidad.datos_del_reporte`."""
    t, plan = datos["totales"], datos["plan"]
    pdf = _Documento(format="A4")
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.set_margins(16, 16, 16)
    pdf.alias_nb_pages()
    pdf.set_title("Reporte de sostenibilidad")
    pdf.set_author("RouteZero")
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 17)
    pdf.cell(0, 9, "Reporte de sostenibilidad", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*GRIS)
    pdf.cell(0, 6, _t(f"{EMPRESA} - Huancayo, Perú"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(
        0, 6,
        _t(f"Periodo: {datos['desde']:%d/%m/%Y} al {datos['hasta']:%d/%m/%Y} ({datos['dias']} días) - "
           f"Generado el {datos['generado_en']:%d/%m/%Y %H:%M}"),
        new_x=XPos.LMARGIN, new_y=YPos.NEXT,
    )
    pdf.set_text_color(0, 0, 0)
    if datos["parcial"]:
        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 9.5)
        _parrafo(
            pdf,
            "REPORTE PARCIAL: el periodo incluye jornadas que todavía no se completan. Las cifras corresponden a "
            "los datos disponibles hasta el momento y pueden cambiar.",
            AVISO,
        )
        pdf.set_font("Helvetica", "", 9.5)

    _titulo(pdf, "1. Resumen del periodo")
    _tabla(
        pdf, ["Indicador", "Valor"],
        [
            ["Rutas realizadas", str(t["rutas"])],
            ["Distancia recorrida", f"{_n(t['distancia_km'])} km"],
            ["Emisiones de CO2", f"{_n(t['emision_co2_kg'])} kg"],
            ["Combustible gastado", f"{_n(t['combustible_l'])} L"],
            ["Combustible ahorrado", f"{_n(t['combustible_ahorrado_l'])} L"],
            ["Ahorro en combustible", _soles(t["ahorro_soles"])],
            ["Cumplimiento de ventanas de tiempo", f"{_n(t['cumplimiento_ventanas_pct'])} %"],
        ],
        (110, 66),
    )

    _titulo(pdf, "2. Emisiones de CO2 por ruta")
    _tabla(
        pdf, ["Fecha", "Vehículo", "Conductor", "Paradas", "Distancia (km)", "CO2 (kg)"],
        [[f"{r['fecha']:%d/%m/%Y}", r["placa"], r["conductor"], str(r["paradas"]), _n(r["distancia_km"]), _n(r["emision_co2_kg"], 2)] for r in datos["rutas"]],
        (24, 24, 58, 18, 28, 24), derecha_desde=3,
    )
    if datos["rutas_omitidas"]:
        pdf.ln(1)
        _parrafo(pdf, f"Se muestran las {len(datos['rutas'])} rutas más recientes; faltan {datos['rutas_omitidas']} rutas más antiguas, incluidas en los totales.", GRIS)

    _titulo(pdf, "3. Costo del ciclo de vida de la flota")
    flota = datos["flota"]
    _tabla(
        pdf, ["Vehículo", "Tipo", "Precio de compra", "Vida útil", "Depreciación", "Combustible", "Total"],
        [
            [v["placa"], v["tipo"], _soles(v["precio_compra_soles"]), "sin dato" if v["vida_util_anios"] is None else f"{v['vida_util_anios']} años",
             _soles(v["depreciacion_soles"]), _soles(v["combustible_soles"]), _soles(v["costo_total_soles"])]
            for v in flota
        ],
        (22, 22, 30, 20, 28, 26, 28), derecha_desde=2,
    )
    con_dato = [v for v in flota if v["costo_total_soles"] is not None]
    pdf.ln(1)
    _parrafo(pdf, f"Costo estimado de los {len(con_dato)} vehículos con datos de compra en el periodo: {_soles(sum(v['costo_total_soles'] for v in con_dato))}.")
    if datos["flota_sin_datos"]:
        _parrafo(pdf, f"{datos['flota_sin_datos']} vehículo(s) no tienen precio de compra y vida útil registrados; no suman al total. Se completan en el módulo de Flota.", AVISO)
    _parrafo(pdf, "Depreciación = precio de compra / (vida útil en años x 365) x días del periodo. Combustible = litros gastados x precio del litro.", GRIS)

    _titulo(pdf, "4. Metas de sostenibilidad y compensación")
    mes = plan["mes_evaluado"]
    _parrafo(
        pdf,
        f"Meta mensual de emisiones: {_n(mes['emision_co2_kg'])} de {_n(mes['meta_kg'], 0)} kg de CO2 "
        f"({_n(mes['porcentaje_meta'], 0)} %) en el mes de {mes['hasta']:%m/%Y}. "
        + ("La meta se supera." if mes["excede_meta"] else "La meta se cumple."),
        AVISO if mes["excede_meta"] else (0, 0, 0),
    )
    for accion in plan["acciones"]:
        _parrafo(pdf, f"  - {accion}")
    _parrafo(
        pdf,
        f"Plan de compensación: {plan['arboles_necesarios']} árboles para absorber en un año los {_n(plan['emision_co2_kg'])} kg de CO2 del periodo "
        f"({_n(plan['kg_co2_por_arbol_anio'], 0)} kg por árbol al año).",
    )

    _titulo(pdf, "5. Supuestos y notas")
    s = datos["supuestos"]
    for linea in (
        f"Precio del combustible: S/ {s['precio_combustible_soles_l']:.2f} por litro (supuesto configurable).",
        f"Absorción de CO2 por árbol: {s['kg_co2_por_arbol_anio']:.0f} kg al año (supuesto configurable).",
        "Solo cuentan las rutas confirmadas, en ejecución o completadas; los borradores no se incluyen.",
        "El combustible ahorrado se mide frente a la solución inicial del optimizador. En rutas re-optimizadas, las métricas cubren solo el tramo restante.",
    ):
        _parrafo(pdf, f"- {linea}", GRIS)

    return bytes(pdf.output())
